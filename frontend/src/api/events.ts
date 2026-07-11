import { apiClient } from "./client";
import type { PaginatedResponse } from "@/types";
import type { Event, EventStatistics, ListEventsParams } from "@/types/api";

export async function fetchEvents(
  params: ListEventsParams = {},
): Promise<PaginatedResponse<Event>> {
  const { data } = await apiClient.get<PaginatedResponse<Event>>("/events", {
    params: {
      page: params.page ?? 1,
      limit: params.limit ?? 20,
      camera_id: params.camera_id,
      event_type: params.event_type,
    },
  });
  return data;
}

export async function fetchEventStatistics(): Promise<EventStatistics> {
  const { data } = await apiClient.get<{ data: EventStatistics }>(
    "/events/statistics",
  );
  return data.data;
}
