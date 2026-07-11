import { apiClient } from "./client";
import type { ApiResponse } from "@/types";
import type { StreamStatus } from "@/types/api";

export async function fetchStreamStatuses(): Promise<StreamStatus[]> {
  const { data } = await apiClient.get<ApiResponse<{ streams: StreamStatus[] }>>(
    "/streams/status",
  );
  return data.data.streams;
}
