import { useQuery } from "@tanstack/react-query";

import { fetchCameras } from "@/api/cameras";

export function useCameras() {
  return useQuery({
    queryKey: ["cameras"],
    queryFn: () => fetchCameras(),
    refetchInterval: 30_000,
  });
}
