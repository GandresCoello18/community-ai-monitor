import { useQuery } from "@tanstack/react-query";

import { fetchEvents, fetchEventStatistics } from "@/api/events";
import type { ListEventsParams } from "@/types/api";

export function useEvents(params: ListEventsParams = {}) {
  return useQuery({
    queryKey: ["events", params],
    queryFn: () => fetchEvents(params),
    refetchInterval: 15_000,
  });
}

export function useEventStatistics() {
  return useQuery({
    queryKey: ["event-statistics"],
    queryFn: fetchEventStatistics,
    refetchInterval: 30_000,
  });
}
