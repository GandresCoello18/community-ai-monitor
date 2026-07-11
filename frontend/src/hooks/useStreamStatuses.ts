import { useQuery } from "@tanstack/react-query";

import { fetchStreamStatuses } from "@/api/streams";

export function useStreamStatuses() {
  return useQuery({
    queryKey: ["stream-statuses"],
    queryFn: fetchStreamStatuses,
    refetchInterval: 10_000,
  });
}
