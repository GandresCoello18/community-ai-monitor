import { apiClient } from "./client";
import type { ApiResponse } from "@/types";
import type { HealthStatus } from "@/types/api";

export async function fetchHealth(): Promise<HealthStatus> {
  const { data } = await apiClient.get<ApiResponse<HealthStatus>>("/health");
  return data.data;
}
