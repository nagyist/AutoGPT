/**
 * Generated by orval v7.10.0 🍺
 * Do not edit manually.
 * AutoGPT Agent Server
 * This server is used to execute agents that are created by the AutoGPT system.
 * OpenAPI spec version: 0.1
 */
import { useMutation, useQuery } from "@tanstack/react-query";
import type {
  DataTag,
  DefinedInitialDataOptions,
  DefinedUseQueryResult,
  MutationFunction,
  QueryClient,
  QueryFunction,
  QueryKey,
  UndefinedInitialDataOptions,
  UseMutationOptions,
  UseMutationResult,
  UseQueryOptions,
  UseQueryResult,
} from "@tanstack/react-query";

import type { APIKeyWithoutHash } from "../../models/aPIKeyWithoutHash";

import type { CreateAPIKeyRequest } from "../../models/createAPIKeyRequest";

import type { CreateAPIKeyResponse } from "../../models/createAPIKeyResponse";

import type { GetV1ListUserApiKeys200 } from "../../models/getV1ListUserApiKeys200";

import type { HTTPValidationError } from "../../models/hTTPValidationError";

import type { UpdatePermissionsRequest } from "../../models/updatePermissionsRequest";

import { customMutator } from "../../../mutators/custom-mutator";

type SecondParameter<T extends (...args: never) => unknown> = Parameters<T>[1];

/**
 * List all API keys for the user
 * @summary List user API keys
 */
export type getV1ListUserApiKeysResponse200 = {
  data: GetV1ListUserApiKeys200;
  status: 200;
};

export type getV1ListUserApiKeysResponseComposite =
  getV1ListUserApiKeysResponse200;

export type getV1ListUserApiKeysResponse =
  getV1ListUserApiKeysResponseComposite & {
    headers: Headers;
  };

export const getGetV1ListUserApiKeysUrl = () => {
  return `/api/api-keys`;
};

export const getV1ListUserApiKeys = async (
  options?: RequestInit,
): Promise<getV1ListUserApiKeysResponse> => {
  return customMutator<getV1ListUserApiKeysResponse>(
    getGetV1ListUserApiKeysUrl(),
    {
      ...options,
      method: "GET",
    },
  );
};

export const getGetV1ListUserApiKeysQueryKey = () => {
  return [`/api/api-keys`] as const;
};

export const getGetV1ListUserApiKeysQueryOptions = <
  TData = Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
  TError = unknown,
>(options?: {
  query?: Partial<
    UseQueryOptions<
      Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
      TError,
      TData
    >
  >;
  request?: SecondParameter<typeof customMutator>;
}) => {
  const { query: queryOptions, request: requestOptions } = options ?? {};

  const queryKey = queryOptions?.queryKey ?? getGetV1ListUserApiKeysQueryKey();

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof getV1ListUserApiKeys>>
  > = ({ signal }) => getV1ListUserApiKeys({ signal, ...requestOptions });

  return { queryKey, queryFn, ...queryOptions } as UseQueryOptions<
    Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type GetV1ListUserApiKeysQueryResult = NonNullable<
  Awaited<ReturnType<typeof getV1ListUserApiKeys>>
>;
export type GetV1ListUserApiKeysQueryError = unknown;

export function useGetV1ListUserApiKeys<
  TData = Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
  TError = unknown,
>(
  options: {
    query: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
        TError,
        TData
      >
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
          TError,
          Awaited<ReturnType<typeof getV1ListUserApiKeys>>
        >,
        "initialData"
      >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): DefinedUseQueryResult<TData, TError> & {
  queryKey: DataTag<QueryKey, TData, TError>;
};
export function useGetV1ListUserApiKeys<
  TData = Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
  TError = unknown,
>(
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
        TError,
        TData
      >
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
          TError,
          Awaited<ReturnType<typeof getV1ListUserApiKeys>>
        >,
        "initialData"
      >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseQueryResult<TData, TError> & {
  queryKey: DataTag<QueryKey, TData, TError>;
};
export function useGetV1ListUserApiKeys<
  TData = Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
  TError = unknown,
>(
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
        TError,
        TData
      >
    >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseQueryResult<TData, TError> & {
  queryKey: DataTag<QueryKey, TData, TError>;
};
/**
 * @summary List user API keys
 */

export function useGetV1ListUserApiKeys<
  TData = Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
  TError = unknown,
>(
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
        TError,
        TData
      >
    >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseQueryResult<TData, TError> & {
  queryKey: DataTag<QueryKey, TData, TError>;
} {
  const queryOptions = getGetV1ListUserApiKeysQueryOptions(options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  query.queryKey = queryOptions.queryKey;

  return query;
}

/**
 * @summary List user API keys
 */
export const prefetchGetV1ListUserApiKeysQuery = async <
  TData = Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
  TError = unknown,
>(
  queryClient: QueryClient,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1ListUserApiKeys>>,
        TError,
        TData
      >
    >;
    request?: SecondParameter<typeof customMutator>;
  },
): Promise<QueryClient> => {
  const queryOptions = getGetV1ListUserApiKeysQueryOptions(options);

  await queryClient.prefetchQuery(queryOptions);

  return queryClient;
};

/**
 * Create a new API key
 * @summary Create new API key
 */
export type postV1CreateNewApiKeyResponse200 = {
  data: CreateAPIKeyResponse;
  status: 200;
};

export type postV1CreateNewApiKeyResponse422 = {
  data: HTTPValidationError;
  status: 422;
};

export type postV1CreateNewApiKeyResponseComposite =
  | postV1CreateNewApiKeyResponse200
  | postV1CreateNewApiKeyResponse422;

export type postV1CreateNewApiKeyResponse =
  postV1CreateNewApiKeyResponseComposite & {
    headers: Headers;
  };

export const getPostV1CreateNewApiKeyUrl = () => {
  return `/api/api-keys`;
};

export const postV1CreateNewApiKey = async (
  createAPIKeyRequest: CreateAPIKeyRequest,
  options?: RequestInit,
): Promise<postV1CreateNewApiKeyResponse> => {
  return customMutator<postV1CreateNewApiKeyResponse>(
    getPostV1CreateNewApiKeyUrl(),
    {
      ...options,
      method: "POST",
      headers: { "Content-Type": "application/json", ...options?.headers },
      body: JSON.stringify(createAPIKeyRequest),
    },
  );
};

export const getPostV1CreateNewApiKeyMutationOptions = <
  TError = HTTPValidationError,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof postV1CreateNewApiKey>>,
    TError,
    { data: CreateAPIKeyRequest },
    TContext
  >;
  request?: SecondParameter<typeof customMutator>;
}): UseMutationOptions<
  Awaited<ReturnType<typeof postV1CreateNewApiKey>>,
  TError,
  { data: CreateAPIKeyRequest },
  TContext
> => {
  const mutationKey = ["postV1CreateNewApiKey"];
  const { mutation: mutationOptions, request: requestOptions } = options
    ? options.mutation &&
      "mutationKey" in options.mutation &&
      options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey }, request: undefined };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof postV1CreateNewApiKey>>,
    { data: CreateAPIKeyRequest }
  > = (props) => {
    const { data } = props ?? {};

    return postV1CreateNewApiKey(data, requestOptions);
  };

  return { mutationFn, ...mutationOptions };
};

export type PostV1CreateNewApiKeyMutationResult = NonNullable<
  Awaited<ReturnType<typeof postV1CreateNewApiKey>>
>;
export type PostV1CreateNewApiKeyMutationBody = CreateAPIKeyRequest;
export type PostV1CreateNewApiKeyMutationError = HTTPValidationError;

/**
 * @summary Create new API key
 */
export const usePostV1CreateNewApiKey = <
  TError = HTTPValidationError,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof postV1CreateNewApiKey>>,
      TError,
      { data: CreateAPIKeyRequest },
      TContext
    >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseMutationResult<
  Awaited<ReturnType<typeof postV1CreateNewApiKey>>,
  TError,
  { data: CreateAPIKeyRequest },
  TContext
> => {
  const mutationOptions = getPostV1CreateNewApiKeyMutationOptions(options);

  return useMutation(mutationOptions, queryClient);
};
/**
 * Get a specific API key
 * @summary Get specific API key
 */
export type getV1GetSpecificApiKeyResponse200 = {
  data: APIKeyWithoutHash;
  status: 200;
};

export type getV1GetSpecificApiKeyResponse422 = {
  data: HTTPValidationError;
  status: 422;
};

export type getV1GetSpecificApiKeyResponseComposite =
  | getV1GetSpecificApiKeyResponse200
  | getV1GetSpecificApiKeyResponse422;

export type getV1GetSpecificApiKeyResponse =
  getV1GetSpecificApiKeyResponseComposite & {
    headers: Headers;
  };

export const getGetV1GetSpecificApiKeyUrl = (keyId: string) => {
  return `/api/api-keys/${keyId}`;
};

export const getV1GetSpecificApiKey = async (
  keyId: string,
  options?: RequestInit,
): Promise<getV1GetSpecificApiKeyResponse> => {
  return customMutator<getV1GetSpecificApiKeyResponse>(
    getGetV1GetSpecificApiKeyUrl(keyId),
    {
      ...options,
      method: "GET",
    },
  );
};

export const getGetV1GetSpecificApiKeyQueryKey = (keyId: string) => {
  return [`/api/api-keys/${keyId}`] as const;
};

export const getGetV1GetSpecificApiKeyQueryOptions = <
  TData = Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
  TError = HTTPValidationError,
>(
  keyId: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
        TError,
        TData
      >
    >;
    request?: SecondParameter<typeof customMutator>;
  },
) => {
  const { query: queryOptions, request: requestOptions } = options ?? {};

  const queryKey =
    queryOptions?.queryKey ?? getGetV1GetSpecificApiKeyQueryKey(keyId);

  const queryFn: QueryFunction<
    Awaited<ReturnType<typeof getV1GetSpecificApiKey>>
  > = ({ signal }) =>
    getV1GetSpecificApiKey(keyId, { signal, ...requestOptions });

  return {
    queryKey,
    queryFn,
    enabled: !!keyId,
    ...queryOptions,
  } as UseQueryOptions<
    Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
    TError,
    TData
  > & { queryKey: DataTag<QueryKey, TData, TError> };
};

export type GetV1GetSpecificApiKeyQueryResult = NonNullable<
  Awaited<ReturnType<typeof getV1GetSpecificApiKey>>
>;
export type GetV1GetSpecificApiKeyQueryError = HTTPValidationError;

export function useGetV1GetSpecificApiKey<
  TData = Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
  TError = HTTPValidationError,
>(
  keyId: string,
  options: {
    query: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
        TError,
        TData
      >
    > &
      Pick<
        DefinedInitialDataOptions<
          Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
          TError,
          Awaited<ReturnType<typeof getV1GetSpecificApiKey>>
        >,
        "initialData"
      >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): DefinedUseQueryResult<TData, TError> & {
  queryKey: DataTag<QueryKey, TData, TError>;
};
export function useGetV1GetSpecificApiKey<
  TData = Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
  TError = HTTPValidationError,
>(
  keyId: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
        TError,
        TData
      >
    > &
      Pick<
        UndefinedInitialDataOptions<
          Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
          TError,
          Awaited<ReturnType<typeof getV1GetSpecificApiKey>>
        >,
        "initialData"
      >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseQueryResult<TData, TError> & {
  queryKey: DataTag<QueryKey, TData, TError>;
};
export function useGetV1GetSpecificApiKey<
  TData = Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
  TError = HTTPValidationError,
>(
  keyId: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
        TError,
        TData
      >
    >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseQueryResult<TData, TError> & {
  queryKey: DataTag<QueryKey, TData, TError>;
};
/**
 * @summary Get specific API key
 */

export function useGetV1GetSpecificApiKey<
  TData = Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
  TError = HTTPValidationError,
>(
  keyId: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
        TError,
        TData
      >
    >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseQueryResult<TData, TError> & {
  queryKey: DataTag<QueryKey, TData, TError>;
} {
  const queryOptions = getGetV1GetSpecificApiKeyQueryOptions(keyId, options);

  const query = useQuery(queryOptions, queryClient) as UseQueryResult<
    TData,
    TError
  > & { queryKey: DataTag<QueryKey, TData, TError> };

  query.queryKey = queryOptions.queryKey;

  return query;
}

/**
 * @summary Get specific API key
 */
export const prefetchGetV1GetSpecificApiKeyQuery = async <
  TData = Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
  TError = HTTPValidationError,
>(
  queryClient: QueryClient,
  keyId: string,
  options?: {
    query?: Partial<
      UseQueryOptions<
        Awaited<ReturnType<typeof getV1GetSpecificApiKey>>,
        TError,
        TData
      >
    >;
    request?: SecondParameter<typeof customMutator>;
  },
): Promise<QueryClient> => {
  const queryOptions = getGetV1GetSpecificApiKeyQueryOptions(keyId, options);

  await queryClient.prefetchQuery(queryOptions);

  return queryClient;
};

/**
 * Revoke an API key
 * @summary Revoke API key
 */
export type deleteV1RevokeApiKeyResponse200 = {
  data: APIKeyWithoutHash;
  status: 200;
};

export type deleteV1RevokeApiKeyResponse422 = {
  data: HTTPValidationError;
  status: 422;
};

export type deleteV1RevokeApiKeyResponseComposite =
  | deleteV1RevokeApiKeyResponse200
  | deleteV1RevokeApiKeyResponse422;

export type deleteV1RevokeApiKeyResponse =
  deleteV1RevokeApiKeyResponseComposite & {
    headers: Headers;
  };

export const getDeleteV1RevokeApiKeyUrl = (keyId: string) => {
  return `/api/api-keys/${keyId}`;
};

export const deleteV1RevokeApiKey = async (
  keyId: string,
  options?: RequestInit,
): Promise<deleteV1RevokeApiKeyResponse> => {
  return customMutator<deleteV1RevokeApiKeyResponse>(
    getDeleteV1RevokeApiKeyUrl(keyId),
    {
      ...options,
      method: "DELETE",
    },
  );
};

export const getDeleteV1RevokeApiKeyMutationOptions = <
  TError = HTTPValidationError,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof deleteV1RevokeApiKey>>,
    TError,
    { keyId: string },
    TContext
  >;
  request?: SecondParameter<typeof customMutator>;
}): UseMutationOptions<
  Awaited<ReturnType<typeof deleteV1RevokeApiKey>>,
  TError,
  { keyId: string },
  TContext
> => {
  const mutationKey = ["deleteV1RevokeApiKey"];
  const { mutation: mutationOptions, request: requestOptions } = options
    ? options.mutation &&
      "mutationKey" in options.mutation &&
      options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey }, request: undefined };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof deleteV1RevokeApiKey>>,
    { keyId: string }
  > = (props) => {
    const { keyId } = props ?? {};

    return deleteV1RevokeApiKey(keyId, requestOptions);
  };

  return { mutationFn, ...mutationOptions };
};

export type DeleteV1RevokeApiKeyMutationResult = NonNullable<
  Awaited<ReturnType<typeof deleteV1RevokeApiKey>>
>;

export type DeleteV1RevokeApiKeyMutationError = HTTPValidationError;

/**
 * @summary Revoke API key
 */
export const useDeleteV1RevokeApiKey = <
  TError = HTTPValidationError,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof deleteV1RevokeApiKey>>,
      TError,
      { keyId: string },
      TContext
    >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseMutationResult<
  Awaited<ReturnType<typeof deleteV1RevokeApiKey>>,
  TError,
  { keyId: string },
  TContext
> => {
  const mutationOptions = getDeleteV1RevokeApiKeyMutationOptions(options);

  return useMutation(mutationOptions, queryClient);
};
/**
 * Suspend an API key
 * @summary Suspend API key
 */
export type postV1SuspendApiKeyResponse200 = {
  data: APIKeyWithoutHash;
  status: 200;
};

export type postV1SuspendApiKeyResponse422 = {
  data: HTTPValidationError;
  status: 422;
};

export type postV1SuspendApiKeyResponseComposite =
  | postV1SuspendApiKeyResponse200
  | postV1SuspendApiKeyResponse422;

export type postV1SuspendApiKeyResponse =
  postV1SuspendApiKeyResponseComposite & {
    headers: Headers;
  };

export const getPostV1SuspendApiKeyUrl = (keyId: string) => {
  return `/api/api-keys/${keyId}/suspend`;
};

export const postV1SuspendApiKey = async (
  keyId: string,
  options?: RequestInit,
): Promise<postV1SuspendApiKeyResponse> => {
  return customMutator<postV1SuspendApiKeyResponse>(
    getPostV1SuspendApiKeyUrl(keyId),
    {
      ...options,
      method: "POST",
    },
  );
};

export const getPostV1SuspendApiKeyMutationOptions = <
  TError = HTTPValidationError,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof postV1SuspendApiKey>>,
    TError,
    { keyId: string },
    TContext
  >;
  request?: SecondParameter<typeof customMutator>;
}): UseMutationOptions<
  Awaited<ReturnType<typeof postV1SuspendApiKey>>,
  TError,
  { keyId: string },
  TContext
> => {
  const mutationKey = ["postV1SuspendApiKey"];
  const { mutation: mutationOptions, request: requestOptions } = options
    ? options.mutation &&
      "mutationKey" in options.mutation &&
      options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey }, request: undefined };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof postV1SuspendApiKey>>,
    { keyId: string }
  > = (props) => {
    const { keyId } = props ?? {};

    return postV1SuspendApiKey(keyId, requestOptions);
  };

  return { mutationFn, ...mutationOptions };
};

export type PostV1SuspendApiKeyMutationResult = NonNullable<
  Awaited<ReturnType<typeof postV1SuspendApiKey>>
>;

export type PostV1SuspendApiKeyMutationError = HTTPValidationError;

/**
 * @summary Suspend API key
 */
export const usePostV1SuspendApiKey = <
  TError = HTTPValidationError,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof postV1SuspendApiKey>>,
      TError,
      { keyId: string },
      TContext
    >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseMutationResult<
  Awaited<ReturnType<typeof postV1SuspendApiKey>>,
  TError,
  { keyId: string },
  TContext
> => {
  const mutationOptions = getPostV1SuspendApiKeyMutationOptions(options);

  return useMutation(mutationOptions, queryClient);
};
/**
 * Update API key permissions
 * @summary Update key permissions
 */
export type putV1UpdateKeyPermissionsResponse200 = {
  data: APIKeyWithoutHash;
  status: 200;
};

export type putV1UpdateKeyPermissionsResponse422 = {
  data: HTTPValidationError;
  status: 422;
};

export type putV1UpdateKeyPermissionsResponseComposite =
  | putV1UpdateKeyPermissionsResponse200
  | putV1UpdateKeyPermissionsResponse422;

export type putV1UpdateKeyPermissionsResponse =
  putV1UpdateKeyPermissionsResponseComposite & {
    headers: Headers;
  };

export const getPutV1UpdateKeyPermissionsUrl = (keyId: string) => {
  return `/api/api-keys/${keyId}/permissions`;
};

export const putV1UpdateKeyPermissions = async (
  keyId: string,
  updatePermissionsRequest: UpdatePermissionsRequest,
  options?: RequestInit,
): Promise<putV1UpdateKeyPermissionsResponse> => {
  return customMutator<putV1UpdateKeyPermissionsResponse>(
    getPutV1UpdateKeyPermissionsUrl(keyId),
    {
      ...options,
      method: "PUT",
      headers: { "Content-Type": "application/json", ...options?.headers },
      body: JSON.stringify(updatePermissionsRequest),
    },
  );
};

export const getPutV1UpdateKeyPermissionsMutationOptions = <
  TError = HTTPValidationError,
  TContext = unknown,
>(options?: {
  mutation?: UseMutationOptions<
    Awaited<ReturnType<typeof putV1UpdateKeyPermissions>>,
    TError,
    { keyId: string; data: UpdatePermissionsRequest },
    TContext
  >;
  request?: SecondParameter<typeof customMutator>;
}): UseMutationOptions<
  Awaited<ReturnType<typeof putV1UpdateKeyPermissions>>,
  TError,
  { keyId: string; data: UpdatePermissionsRequest },
  TContext
> => {
  const mutationKey = ["putV1UpdateKeyPermissions"];
  const { mutation: mutationOptions, request: requestOptions } = options
    ? options.mutation &&
      "mutationKey" in options.mutation &&
      options.mutation.mutationKey
      ? options
      : { ...options, mutation: { ...options.mutation, mutationKey } }
    : { mutation: { mutationKey }, request: undefined };

  const mutationFn: MutationFunction<
    Awaited<ReturnType<typeof putV1UpdateKeyPermissions>>,
    { keyId: string; data: UpdatePermissionsRequest }
  > = (props) => {
    const { keyId, data } = props ?? {};

    return putV1UpdateKeyPermissions(keyId, data, requestOptions);
  };

  return { mutationFn, ...mutationOptions };
};

export type PutV1UpdateKeyPermissionsMutationResult = NonNullable<
  Awaited<ReturnType<typeof putV1UpdateKeyPermissions>>
>;
export type PutV1UpdateKeyPermissionsMutationBody = UpdatePermissionsRequest;
export type PutV1UpdateKeyPermissionsMutationError = HTTPValidationError;

/**
 * @summary Update key permissions
 */
export const usePutV1UpdateKeyPermissions = <
  TError = HTTPValidationError,
  TContext = unknown,
>(
  options?: {
    mutation?: UseMutationOptions<
      Awaited<ReturnType<typeof putV1UpdateKeyPermissions>>,
      TError,
      { keyId: string; data: UpdatePermissionsRequest },
      TContext
    >;
    request?: SecondParameter<typeof customMutator>;
  },
  queryClient?: QueryClient,
): UseMutationResult<
  Awaited<ReturnType<typeof putV1UpdateKeyPermissions>>,
  TError,
  { keyId: string; data: UpdatePermissionsRequest },
  TContext
> => {
  const mutationOptions = getPutV1UpdateKeyPermissionsMutationOptions(options);

  return useMutation(mutationOptions, queryClient);
};
