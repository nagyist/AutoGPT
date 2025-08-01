import asyncio
import base64
import logging
from collections import defaultdict
from datetime import datetime
from typing import Annotated, Any, Sequence

import pydantic
import stripe
from autogpt_libs.auth.middleware import auth_middleware
from autogpt_libs.feature_flag.client import feature_flag
from autogpt_libs.utils.cache import thread_cached
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Path,
    Request,
    Response,
    UploadFile,
)
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from typing_extensions import Optional, TypedDict

import backend.server.integrations.router
import backend.server.routers.analytics
import backend.server.v2.library.db as library_db
from backend.data import execution as execution_db
from backend.data import graph as graph_db
from backend.data.api_key import (
    APIKeyError,
    APIKeyNotFoundError,
    APIKeyPermissionError,
    APIKeyWithoutHash,
    generate_api_key,
    get_api_key_by_id,
    list_user_api_keys,
    revoke_api_key,
    suspend_api_key,
    update_api_key_permissions,
)
from backend.data.block import BlockInput, CompletedBlockOutput, get_block, get_blocks
from backend.data.credit import (
    AutoTopUpConfig,
    RefundRequest,
    TransactionHistory,
    get_auto_top_up,
    get_block_costs,
    get_user_credit_model,
    set_auto_top_up,
)
from backend.data.execution import AsyncRedisExecutionEventBus
from backend.data.model import CredentialsMetaInput
from backend.data.notifications import NotificationPreference, NotificationPreferenceDTO
from backend.data.onboarding import (
    UserOnboardingUpdate,
    get_recommended_agents,
    get_user_onboarding,
    onboarding_enabled,
    update_user_onboarding,
)
from backend.data.user import (
    get_or_create_user,
    get_user_notification_preference,
    update_user_email,
    update_user_notification_preference,
)
from backend.executor import scheduler
from backend.executor import utils as execution_utils
from backend.integrations.webhooks.graph_lifecycle_hooks import (
    on_graph_activate,
    on_graph_deactivate,
)
from backend.server.model import (
    CreateAPIKeyRequest,
    CreateAPIKeyResponse,
    CreateGraph,
    ExecuteGraphResponse,
    RequestTopUp,
    SetGraphActiveVersion,
    UpdatePermissionsRequest,
    UploadFileResponse,
)
from backend.server.utils import get_user_id
from backend.util.cloud_storage import get_cloud_storage_handler
from backend.util.exceptions import NotFoundError
from backend.util.service import get_service_client
from backend.util.settings import Settings
from backend.util.virus_scanner import scan_content_safe


@thread_cached
def execution_scheduler_client() -> scheduler.SchedulerClient:
    return get_service_client(scheduler.SchedulerClient, health_check=False)


def _create_file_size_error(size_bytes: int, max_size_mb: int) -> HTTPException:
    """Create standardized file size error response."""
    return HTTPException(
        status_code=400,
        detail=f"File size ({size_bytes} bytes) exceeds the maximum allowed size of {max_size_mb}MB",
    )


@thread_cached
def execution_event_bus() -> AsyncRedisExecutionEventBus:
    return AsyncRedisExecutionEventBus()


settings = Settings()
logger = logging.getLogger(__name__)

_user_credit_model = get_user_credit_model()

# Define the API routes
v1_router = APIRouter()

v1_router.include_router(
    backend.server.integrations.router.router,
    prefix="/integrations",
    tags=["integrations"],
)

v1_router.include_router(
    backend.server.routers.analytics.router,
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(auth_middleware)],
)


########################################################
##################### Auth #############################
########################################################


@v1_router.post(
    "/auth/user",
    summary="Get or create user",
    tags=["auth"],
    dependencies=[Depends(auth_middleware)],
)
async def get_or_create_user_route(user_data: dict = Depends(auth_middleware)):
    user = await get_or_create_user(user_data)
    return user.model_dump()


@v1_router.post(
    "/auth/user/email",
    summary="Update user email",
    tags=["auth"],
    dependencies=[Depends(auth_middleware)],
)
async def update_user_email_route(
    user_id: Annotated[str, Depends(get_user_id)], email: str = Body(...)
) -> dict[str, str]:
    await update_user_email(user_id, email)

    return {"email": email}


@v1_router.get(
    "/auth/user/preferences",
    summary="Get notification preferences",
    tags=["auth"],
    dependencies=[Depends(auth_middleware)],
)
async def get_preferences(
    user_id: Annotated[str, Depends(get_user_id)],
) -> NotificationPreference:
    preferences = await get_user_notification_preference(user_id)
    return preferences


@v1_router.post(
    "/auth/user/preferences",
    summary="Update notification preferences",
    tags=["auth"],
    dependencies=[Depends(auth_middleware)],
)
async def update_preferences(
    user_id: Annotated[str, Depends(get_user_id)],
    preferences: NotificationPreferenceDTO = Body(...),
) -> NotificationPreference:
    output = await update_user_notification_preference(user_id, preferences)
    return output


########################################################
##################### Onboarding #######################
########################################################


@v1_router.get(
    "/onboarding",
    summary="Get onboarding status",
    tags=["onboarding"],
    dependencies=[Depends(auth_middleware)],
)
async def get_onboarding(user_id: Annotated[str, Depends(get_user_id)]):
    return await get_user_onboarding(user_id)


@v1_router.patch(
    "/onboarding",
    summary="Update onboarding progress",
    tags=["onboarding"],
    dependencies=[Depends(auth_middleware)],
)
async def update_onboarding(
    user_id: Annotated[str, Depends(get_user_id)], data: UserOnboardingUpdate
):
    return await update_user_onboarding(user_id, data)


@v1_router.get(
    "/onboarding/agents",
    summary="Get recommended agents",
    tags=["onboarding"],
    dependencies=[Depends(auth_middleware)],
)
async def get_onboarding_agents(
    user_id: Annotated[str, Depends(get_user_id)],
):
    return await get_recommended_agents(user_id)


@v1_router.get(
    "/onboarding/enabled",
    summary="Check onboarding enabled",
    tags=["onboarding", "public"],
    dependencies=[Depends(auth_middleware)],
)
async def is_onboarding_enabled():
    return await onboarding_enabled()


########################################################
##################### Blocks ###########################
########################################################


@v1_router.get(
    path="/blocks",
    summary="List available blocks",
    tags=["blocks"],
    dependencies=[Depends(auth_middleware)],
)
def get_graph_blocks() -> Sequence[dict[Any, Any]]:
    blocks = [block() for block in get_blocks().values()]
    costs = get_block_costs()
    return [
        {**b.to_dict(), "costs": costs.get(b.id, [])} for b in blocks if not b.disabled
    ]


@v1_router.post(
    path="/blocks/{block_id}/execute",
    summary="Execute graph block",
    tags=["blocks"],
    dependencies=[Depends(auth_middleware)],
)
async def execute_graph_block(block_id: str, data: BlockInput) -> CompletedBlockOutput:
    obj = get_block(block_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Block #{block_id} not found.")

    output = defaultdict(list)
    async for name, data in obj.execute(data):
        output[name].append(data)
    return output


@v1_router.post(
    path="/files/upload",
    summary="Upload file to cloud storage",
    tags=["files"],
    dependencies=[Depends(auth_middleware)],
)
async def upload_file(
    user_id: Annotated[str, Depends(get_user_id)],
    file: UploadFile = File(...),
    provider: str = "gcs",
    expiration_hours: int = 24,
) -> UploadFileResponse:
    """
    Upload a file to cloud storage and return a storage key that can be used
    with FileStoreBlock and AgentFileInputBlock.

    Args:
        file: The file to upload
        user_id: The user ID
        provider: Cloud storage provider ("gcs", "s3", "azure")
        expiration_hours: Hours until file expires (1-48)

    Returns:
        Dict containing the cloud storage path and signed URL
    """
    if expiration_hours < 1 or expiration_hours > 48:
        raise HTTPException(
            status_code=400, detail="Expiration hours must be between 1 and 48"
        )

    # Check file size limit before reading content to avoid memory issues
    max_size_mb = settings.config.upload_file_size_limit_mb
    max_size_bytes = max_size_mb * 1024 * 1024

    # Try to get file size from headers first
    if hasattr(file, "size") and file.size is not None and file.size > max_size_bytes:
        raise _create_file_size_error(file.size, max_size_mb)

    # Read file content
    content = await file.read()
    content_size = len(content)

    # Double-check file size after reading (in case header was missing/incorrect)
    if content_size > max_size_bytes:
        raise _create_file_size_error(content_size, max_size_mb)

    # Extract common variables
    file_name = file.filename or "uploaded_file"
    content_type = file.content_type or "application/octet-stream"

    # Virus scan the content
    await scan_content_safe(content, filename=file_name)

    # Check if cloud storage is configured
    cloud_storage = await get_cloud_storage_handler()
    if not cloud_storage.config.gcs_bucket_name:
        # Fallback to base64 data URI when GCS is not configured
        base64_content = base64.b64encode(content).decode("utf-8")
        data_uri = f"data:{content_type};base64,{base64_content}"

        return UploadFileResponse(
            file_uri=data_uri,
            file_name=file_name,
            size=content_size,
            content_type=content_type,
            expires_in_hours=expiration_hours,
        )

    # Store in cloud storage
    storage_path = await cloud_storage.store_file(
        content=content,
        filename=file_name,
        provider=provider,
        expiration_hours=expiration_hours,
        user_id=user_id,
    )

    return UploadFileResponse(
        file_uri=storage_path,
        file_name=file_name,
        size=content_size,
        content_type=content_type,
        expires_in_hours=expiration_hours,
    )


########################################################
##################### Credits ##########################
########################################################


@v1_router.get(
    path="/credits",
    tags=["credits"],
    summary="Get user credits",
    dependencies=[Depends(auth_middleware)],
)
async def get_user_credits(
    user_id: Annotated[str, Depends(get_user_id)],
) -> dict[str, int]:
    return {"credits": await _user_credit_model.get_credits(user_id)}


@v1_router.post(
    path="/credits",
    summary="Request credit top up",
    tags=["credits"],
    dependencies=[Depends(auth_middleware)],
)
async def request_top_up(
    request: RequestTopUp, user_id: Annotated[str, Depends(get_user_id)]
):
    checkout_url = await _user_credit_model.top_up_intent(
        user_id, request.credit_amount
    )
    return {"checkout_url": checkout_url}


@v1_router.post(
    path="/credits/{transaction_key}/refund",
    summary="Refund credit transaction",
    tags=["credits"],
    dependencies=[Depends(auth_middleware)],
)
async def refund_top_up(
    user_id: Annotated[str, Depends(get_user_id)],
    transaction_key: str,
    metadata: dict[str, str],
) -> int:
    return await _user_credit_model.top_up_refund(user_id, transaction_key, metadata)


@v1_router.patch(
    path="/credits",
    summary="Fulfill checkout session",
    tags=["credits"],
    dependencies=[Depends(auth_middleware)],
)
async def fulfill_checkout(user_id: Annotated[str, Depends(get_user_id)]):
    await _user_credit_model.fulfill_checkout(user_id=user_id)
    return Response(status_code=200)


@v1_router.post(
    path="/credits/auto-top-up",
    summary="Configure auto top up",
    tags=["credits"],
    dependencies=[Depends(auth_middleware)],
)
async def configure_user_auto_top_up(
    request: AutoTopUpConfig, user_id: Annotated[str, Depends(get_user_id)]
) -> str:
    if request.threshold < 0:
        raise ValueError("Threshold must be greater than 0")
    if request.amount < 500 and request.amount != 0:
        raise ValueError("Amount must be greater than or equal to 500")
    if request.amount < request.threshold:
        raise ValueError("Amount must be greater than or equal to threshold")

    current_balance = await _user_credit_model.get_credits(user_id)

    if current_balance < request.threshold:
        await _user_credit_model.top_up_credits(user_id, request.amount)
    else:
        await _user_credit_model.top_up_credits(user_id, 0)

    await set_auto_top_up(
        user_id, AutoTopUpConfig(threshold=request.threshold, amount=request.amount)
    )
    return "Auto top-up settings updated"


@v1_router.get(
    path="/credits/auto-top-up",
    summary="Get auto top up",
    tags=["credits"],
    dependencies=[Depends(auth_middleware)],
)
async def get_user_auto_top_up(
    user_id: Annotated[str, Depends(get_user_id)],
) -> AutoTopUpConfig:
    return await get_auto_top_up(user_id)


@v1_router.post(
    path="/credits/stripe_webhook", summary="Handle Stripe webhooks", tags=["credits"]
)
async def stripe_webhook(request: Request):
    # Get the raw request body
    payload = await request.body()
    # Get the signature header
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.secrets.stripe_webhook_secret
        )
    except ValueError:
        # Invalid payload
        raise HTTPException(status_code=400)
    except stripe.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(status_code=400)

    if (
        event["type"] == "checkout.session.completed"
        or event["type"] == "checkout.session.async_payment_succeeded"
    ):
        await _user_credit_model.fulfill_checkout(
            session_id=event["data"]["object"]["id"]
        )

    if event["type"] == "charge.dispute.created":
        await _user_credit_model.handle_dispute(event["data"]["object"])

    if event["type"] == "refund.created" or event["type"] == "charge.dispute.closed":
        await _user_credit_model.deduct_credits(event["data"]["object"])

    return Response(status_code=200)


@v1_router.get(
    path="/credits/manage",
    tags=["credits"],
    summary="Manage payment methods",
    dependencies=[Depends(auth_middleware)],
)
async def manage_payment_method(
    user_id: Annotated[str, Depends(get_user_id)],
) -> dict[str, str]:
    return {"url": await _user_credit_model.create_billing_portal_session(user_id)}


@v1_router.get(
    path="/credits/transactions",
    tags=["credits"],
    summary="Get credit history",
    dependencies=[Depends(auth_middleware)],
)
async def get_credit_history(
    user_id: Annotated[str, Depends(get_user_id)],
    transaction_time: datetime | None = None,
    transaction_type: str | None = None,
    transaction_count_limit: int = 100,
) -> TransactionHistory:
    if transaction_count_limit < 1 or transaction_count_limit > 1000:
        raise ValueError("Transaction count limit must be between 1 and 1000")

    return await _user_credit_model.get_transaction_history(
        user_id=user_id,
        transaction_time_ceiling=transaction_time,
        transaction_count_limit=transaction_count_limit,
        transaction_type=transaction_type,
    )


@v1_router.get(
    path="/credits/refunds",
    tags=["credits"],
    summary="Get refund requests",
    dependencies=[Depends(auth_middleware)],
)
async def get_refund_requests(
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[RefundRequest]:
    return await _user_credit_model.get_refund_requests(user_id)


########################################################
##################### Graphs ###########################
########################################################


class DeleteGraphResponse(TypedDict):
    version_counts: int


@v1_router.get(
    path="/graphs",
    summary="List user graphs",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def list_graphs(
    user_id: Annotated[str, Depends(get_user_id)],
) -> Sequence[graph_db.GraphMeta]:
    return await graph_db.list_graphs(filter_by="active", user_id=user_id)


@v1_router.get(
    path="/graphs/{graph_id}",
    summary="Get specific graph",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
@v1_router.get(
    path="/graphs/{graph_id}/versions/{version}",
    summary="Get graph version",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graph(
    graph_id: str,
    user_id: Annotated[str, Depends(get_user_id)],
    version: int | None = None,
    for_export: bool = False,
) -> graph_db.GraphModel:
    graph = await graph_db.get_graph(
        graph_id,
        version,
        user_id=user_id,
        for_export=for_export,
        include_subgraphs=True,  # needed to construct full credentials input schema
    )
    if not graph:
        raise HTTPException(status_code=404, detail=f"Graph #{graph_id} not found.")
    return graph


@v1_router.get(
    path="/graphs/{graph_id}/versions",
    summary="Get all graph versions",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graph_all_versions(
    graph_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> Sequence[graph_db.GraphModel]:
    graphs = await graph_db.get_graph_all_versions(graph_id, user_id=user_id)
    if not graphs:
        raise HTTPException(status_code=404, detail=f"Graph #{graph_id} not found.")
    return graphs


@v1_router.post(
    path="/graphs",
    summary="Create new graph",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def create_new_graph(
    create_graph: CreateGraph,
    user_id: Annotated[str, Depends(get_user_id)],
) -> graph_db.GraphModel:
    graph = graph_db.make_graph_model(create_graph.graph, user_id)
    graph.reassign_ids(user_id=user_id, reassign_graph_id=True)
    graph.validate_graph(for_run=False)

    # The return value of the create graph & library function is intentionally not used here,
    # as the graph already valid and no sub-graphs are returned back.
    await graph_db.create_graph(graph, user_id=user_id)
    await library_db.create_library_agent(graph, user_id=user_id)
    return await on_graph_activate(graph, user_id=user_id)


@v1_router.delete(
    path="/graphs/{graph_id}",
    summary="Delete graph permanently",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def delete_graph(
    graph_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> DeleteGraphResponse:
    if active_version := await graph_db.get_graph(graph_id, user_id=user_id):
        await on_graph_deactivate(active_version, user_id=user_id)

    return {"version_counts": await graph_db.delete_graph(graph_id, user_id=user_id)}


@v1_router.put(
    path="/graphs/{graph_id}",
    summary="Update graph version",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def update_graph(
    graph_id: str,
    graph: graph_db.Graph,
    user_id: Annotated[str, Depends(get_user_id)],
) -> graph_db.GraphModel:
    # Sanity check
    if graph.id and graph.id != graph_id:
        raise HTTPException(400, detail="Graph ID does not match ID in URI")

    # Determine new version
    existing_versions = await graph_db.get_graph_all_versions(graph_id, user_id=user_id)
    if not existing_versions:
        raise HTTPException(404, detail=f"Graph #{graph_id} not found")
    latest_version_number = max(g.version for g in existing_versions)
    graph.version = latest_version_number + 1

    current_active_version = next((v for v in existing_versions if v.is_active), None)
    graph = graph_db.make_graph_model(graph, user_id)
    graph.reassign_ids(user_id=user_id, reassign_graph_id=False)
    graph.validate_graph(for_run=False)

    new_graph_version = await graph_db.create_graph(graph, user_id=user_id)

    if new_graph_version.is_active:
        # Keep the library agent up to date with the new active version
        await library_db.update_agent_version_in_library(
            user_id, graph.id, graph.version
        )

        # Handle activation of the new graph first to ensure continuity
        new_graph_version = await on_graph_activate(new_graph_version, user_id=user_id)
        # Ensure new version is the only active version
        await graph_db.set_graph_active_version(
            graph_id=graph_id, version=new_graph_version.version, user_id=user_id
        )
        if current_active_version:
            # Handle deactivation of the previously active version
            await on_graph_deactivate(current_active_version, user_id=user_id)

    return new_graph_version


@v1_router.put(
    path="/graphs/{graph_id}/versions/active",
    summary="Set active graph version",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def set_graph_active_version(
    graph_id: str,
    request_body: SetGraphActiveVersion,
    user_id: Annotated[str, Depends(get_user_id)],
):
    new_active_version = request_body.active_graph_version
    new_active_graph = await graph_db.get_graph(
        graph_id, new_active_version, user_id=user_id
    )
    if not new_active_graph:
        raise HTTPException(404, f"Graph #{graph_id} v{new_active_version} not found")

    current_active_graph = await graph_db.get_graph(graph_id, user_id=user_id)

    # Handle activation of the new graph first to ensure continuity
    await on_graph_activate(new_active_graph, user_id=user_id)
    # Ensure new version is the only active version
    await graph_db.set_graph_active_version(
        graph_id=graph_id,
        version=new_active_version,
        user_id=user_id,
    )

    # Keep the library agent up to date with the new active version
    await library_db.update_agent_version_in_library(
        user_id, new_active_graph.id, new_active_graph.version
    )

    if current_active_graph and current_active_graph.version != new_active_version:
        # Handle deactivation of the previously active version
        await on_graph_deactivate(current_active_graph, user_id=user_id)


@v1_router.post(
    path="/graphs/{graph_id}/execute/{graph_version}",
    summary="Execute graph agent",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def execute_graph(
    graph_id: str,
    user_id: Annotated[str, Depends(get_user_id)],
    inputs: Annotated[dict[str, Any], Body(..., embed=True, default_factory=dict)],
    credentials_inputs: Annotated[
        dict[str, CredentialsMetaInput], Body(..., embed=True, default_factory=dict)
    ],
    graph_version: Optional[int] = None,
    preset_id: Optional[str] = None,
) -> ExecuteGraphResponse:
    current_balance = await _user_credit_model.get_credits(user_id)
    if current_balance <= 0:
        raise HTTPException(
            status_code=402,
            detail="Insufficient balance to execute the agent. Please top up your account.",
        )

    graph_exec = await execution_utils.add_graph_execution(
        graph_id=graph_id,
        user_id=user_id,
        inputs=inputs,
        preset_id=preset_id,
        graph_version=graph_version,
        graph_credentials_inputs=credentials_inputs,
    )
    return ExecuteGraphResponse(graph_exec_id=graph_exec.id)


@v1_router.post(
    path="/graphs/{graph_id}/executions/{graph_exec_id}/stop",
    summary="Stop graph execution",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def stop_graph_run(
    graph_id: str, graph_exec_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> execution_db.GraphExecutionMeta | None:
    res = await _stop_graph_run(
        user_id=user_id,
        graph_id=graph_id,
        graph_exec_id=graph_exec_id,
    )
    if not res:
        return None
    return res[0]


async def _stop_graph_run(
    user_id: str,
    graph_id: Optional[str] = None,
    graph_exec_id: Optional[str] = None,
) -> list[execution_db.GraphExecutionMeta]:
    graph_execs = await execution_db.get_graph_executions(
        user_id=user_id,
        graph_id=graph_id,
        graph_exec_id=graph_exec_id,
        statuses=[
            execution_db.ExecutionStatus.INCOMPLETE,
            execution_db.ExecutionStatus.QUEUED,
            execution_db.ExecutionStatus.RUNNING,
        ],
    )
    stopped_execs = [
        execution_utils.stop_graph_execution(graph_exec_id=exec.id, user_id=user_id)
        for exec in graph_execs
    ]
    await asyncio.gather(*stopped_execs)
    return graph_execs


@v1_router.get(
    path="/executions",
    summary="Get all executions",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graphs_executions(
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[execution_db.GraphExecutionMeta]:
    return await execution_db.get_graph_executions(user_id=user_id)


@v1_router.get(
    path="/graphs/{graph_id}/executions",
    summary="Get graph executions",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graph_executions(
    graph_id: str,
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[execution_db.GraphExecutionMeta]:
    return await execution_db.get_graph_executions(graph_id=graph_id, user_id=user_id)


@v1_router.get(
    path="/graphs/{graph_id}/executions/{graph_exec_id}",
    summary="Get execution details",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
)
async def get_graph_execution(
    graph_id: str,
    graph_exec_id: str,
    user_id: Annotated[str, Depends(get_user_id)],
) -> execution_db.GraphExecution | execution_db.GraphExecutionWithNodes:
    graph = await graph_db.get_graph(graph_id=graph_id, user_id=user_id)
    if not graph:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Graph #{graph_id} not found"
        )

    result = await execution_db.get_graph_execution(
        user_id=user_id,
        execution_id=graph_exec_id,
        include_node_executions=graph.user_id == user_id,
    )
    if not result or result.graph_id != graph_id:
        raise HTTPException(
            status_code=404, detail=f"Graph execution #{graph_exec_id} not found."
        )

    return result


@v1_router.delete(
    path="/executions/{graph_exec_id}",
    summary="Delete graph execution",
    tags=["graphs"],
    dependencies=[Depends(auth_middleware)],
    status_code=HTTP_204_NO_CONTENT,
)
async def delete_graph_execution(
    graph_exec_id: str,
    user_id: Annotated[str, Depends(get_user_id)],
) -> None:
    await execution_db.delete_graph_execution(
        graph_exec_id=graph_exec_id, user_id=user_id
    )


########################################################
##################### Schedules ########################
########################################################


class ScheduleCreationRequest(pydantic.BaseModel):
    graph_version: Optional[int] = None
    name: str
    cron: str
    inputs: dict[str, Any]
    credentials: dict[str, CredentialsMetaInput] = pydantic.Field(default_factory=dict)


@v1_router.post(
    path="/graphs/{graph_id}/schedules",
    summary="Create execution schedule",
    tags=["schedules"],
    dependencies=[Depends(auth_middleware)],
)
async def create_graph_execution_schedule(
    user_id: Annotated[str, Depends(get_user_id)],
    graph_id: str = Path(..., description="ID of the graph to schedule"),
    schedule_params: ScheduleCreationRequest = Body(),
) -> scheduler.GraphExecutionJobInfo:
    graph = await graph_db.get_graph(
        graph_id=graph_id,
        version=schedule_params.graph_version,
        user_id=user_id,
    )
    if not graph:
        raise HTTPException(
            status_code=404,
            detail=f"Graph #{graph_id} v{schedule_params.graph_version} not found.",
        )

    return await execution_scheduler_client().add_execution_schedule(
        user_id=user_id,
        graph_id=graph_id,
        graph_version=graph.version,
        name=schedule_params.name,
        cron=schedule_params.cron,
        input_data=schedule_params.inputs,
        input_credentials=schedule_params.credentials,
    )


@v1_router.get(
    path="/graphs/{graph_id}/schedules",
    summary="List execution schedules for a graph",
    tags=["schedules"],
    dependencies=[Depends(auth_middleware)],
)
async def list_graph_execution_schedules(
    user_id: Annotated[str, Depends(get_user_id)],
    graph_id: str = Path(),
) -> list[scheduler.GraphExecutionJobInfo]:
    return await execution_scheduler_client().get_execution_schedules(
        user_id=user_id,
        graph_id=graph_id,
    )


@v1_router.get(
    path="/schedules",
    summary="List execution schedules for a user",
    tags=["schedules"],
    dependencies=[Depends(auth_middleware)],
)
async def list_all_graphs_execution_schedules(
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[scheduler.GraphExecutionJobInfo]:
    return await execution_scheduler_client().get_execution_schedules(user_id=user_id)


@v1_router.delete(
    path="/schedules/{schedule_id}",
    summary="Delete execution schedule",
    tags=["schedules"],
    dependencies=[Depends(auth_middleware)],
)
async def delete_graph_execution_schedule(
    user_id: Annotated[str, Depends(get_user_id)],
    schedule_id: str = Path(..., description="ID of the schedule to delete"),
) -> dict[str, Any]:
    try:
        await execution_scheduler_client().delete_schedule(schedule_id, user_id=user_id)
    except NotFoundError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Schedule #{schedule_id} not found",
        )
    return {"id": schedule_id}


########################################################
#####################  API KEY ##############################
########################################################


@v1_router.post(
    "/api-keys",
    summary="Create new API key",
    response_model=CreateAPIKeyResponse,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
async def create_api_key(
    request: CreateAPIKeyRequest, user_id: Annotated[str, Depends(get_user_id)]
) -> CreateAPIKeyResponse:
    """Create a new API key"""
    try:
        api_key, plain_text = await generate_api_key(
            name=request.name,
            user_id=user_id,
            permissions=request.permissions,
            description=request.description,
        )
        return CreateAPIKeyResponse(api_key=api_key, plain_text_key=plain_text)
    except APIKeyError as e:
        logger.error(
            "Could not create API key for user %s: %s. Review input and permissions.",
            user_id,
            e,
        )
        raise HTTPException(
            status_code=400,
            detail={"message": str(e), "hint": "Verify request payload and try again."},
        )


@v1_router.get(
    "/api-keys",
    summary="List user API keys",
    response_model=list[APIKeyWithoutHash] | dict[str, str],
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
async def get_api_keys(
    user_id: Annotated[str, Depends(get_user_id)],
) -> list[APIKeyWithoutHash]:
    """List all API keys for the user"""
    try:
        return await list_user_api_keys(user_id)
    except APIKeyError as e:
        logger.error("Failed to list API keys for user %s: %s", user_id, e)
        raise HTTPException(
            status_code=400,
            detail={"message": str(e), "hint": "Check API key service availability."},
        )


@v1_router.get(
    "/api-keys/{key_id}",
    summary="Get specific API key",
    response_model=APIKeyWithoutHash,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
async def get_api_key(
    key_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> APIKeyWithoutHash:
    """Get a specific API key"""
    try:
        api_key = await get_api_key_by_id(key_id, user_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        return api_key
    except APIKeyError as e:
        logger.error("Error retrieving API key %s for user %s: %s", key_id, user_id, e)
        raise HTTPException(
            status_code=400,
            detail={"message": str(e), "hint": "Ensure the key ID is correct."},
        )


@v1_router.delete(
    "/api-keys/{key_id}",
    summary="Revoke API key",
    response_model=APIKeyWithoutHash,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
@feature_flag("api-keys-enabled")
async def delete_api_key(
    key_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> Optional[APIKeyWithoutHash]:
    """Revoke an API key"""
    try:
        return await revoke_api_key(key_id, user_id)
    except APIKeyNotFoundError:
        raise HTTPException(status_code=404, detail="API key not found")
    except APIKeyPermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except APIKeyError as e:
        logger.error("Failed to revoke API key %s for user %s: %s", key_id, user_id, e)
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(e),
                "hint": "Verify permissions or try again later.",
            },
        )


@v1_router.post(
    "/api-keys/{key_id}/suspend",
    summary="Suspend API key",
    response_model=APIKeyWithoutHash,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
@feature_flag("api-keys-enabled")
async def suspend_key(
    key_id: str, user_id: Annotated[str, Depends(get_user_id)]
) -> Optional[APIKeyWithoutHash]:
    """Suspend an API key"""
    try:
        return await suspend_api_key(key_id, user_id)
    except APIKeyNotFoundError:
        raise HTTPException(status_code=404, detail="API key not found")
    except APIKeyPermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except APIKeyError as e:
        logger.error("Failed to suspend API key %s for user %s: %s", key_id, user_id, e)
        raise HTTPException(
            status_code=400,
            detail={"message": str(e), "hint": "Check user permissions and retry."},
        )


@v1_router.put(
    "/api-keys/{key_id}/permissions",
    summary="Update key permissions",
    response_model=APIKeyWithoutHash,
    tags=["api-keys"],
    dependencies=[Depends(auth_middleware)],
)
@feature_flag("api-keys-enabled")
async def update_permissions(
    key_id: str,
    request: UpdatePermissionsRequest,
    user_id: Annotated[str, Depends(get_user_id)],
) -> Optional[APIKeyWithoutHash]:
    """Update API key permissions"""
    try:
        return await update_api_key_permissions(key_id, user_id, request.permissions)
    except APIKeyNotFoundError:
        raise HTTPException(status_code=404, detail="API key not found")
    except APIKeyPermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except APIKeyError as e:
        logger.error(
            "Failed to update permissions for API key %s of user %s: %s",
            key_id,
            user_id,
            e,
        )
        raise HTTPException(
            status_code=400,
            detail={"message": str(e), "hint": "Ensure permissions list is valid."},
        )
