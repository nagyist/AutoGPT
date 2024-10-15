import * as React from "react";
import { StarIcon, StarFilledIcon } from "@radix-ui/react-icons";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface StoreCardProps {
  agentName: string;
  description: string;
  runs: number;
  rating: number;
  onClick: () => void;
  avatarSrc: string;
}

export const StoreCard: React.FC<StoreCardProps> = ({
  agentName,
  description,
  runs,
  rating,
  onClick,
  avatarSrc,
}) => {
  const [isHovered, setIsHovered] = React.useState(false);

  const handleMouseEnter = () => setIsHovered(true);
  const handleMouseLeave = () => setIsHovered(false);

  const renderStars = () => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    const stars = [];

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<StarFilledIcon key={i} className="text-black" />);
      } else if (i === fullStars && hasHalfStar) {
        stars.push(<StarIcon key={i} className="text-black" />);
      } else {
        stars.push(<StarIcon key={i} className="text-black" />);
      }
    }

    return stars;
  };

  return (
    <div
      className={`flex h-96 w-screen flex-col pb-2 lg:w-110 ${isHovered ? "shadow-lg" : ""} rounded-xl transition-shadow duration-300`}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="h-69 w-full rounded-xl bg-[#d9d9d9]" />
      <div className="-mt-8 flex flex-col px-4">
        <Avatar className="mb-2 h-16 w-16">
          <AvatarImage src={avatarSrc} alt={agentName} />
          <AvatarFallback>{agentName.charAt(0)}</AvatarFallback>
        </Avatar>
        <div className="mb-1 font-neue text-xl font-bold tracking-tight text-[#272727]">
          {agentName}
        </div>
        <div className="mb-4 font-neue text-base font-normal leading-[21px] tracking-tight text-[#282828]">
          {description}
        </div>
        <div className="flex items-center justify-between">
          <div className="font-neue text-base font-medium tracking-tight text-[#272727]">
            {runs.toLocaleString()}+ runs
          </div>
          <div className="flex items-center">
            <div className="mr-2 font-neue text-base font-medium tracking-tight text-[#272727]">
              {rating.toFixed(1)}
            </div>
            <div className="inline-flex items-center justify-start gap-px">
              {renderStars()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};