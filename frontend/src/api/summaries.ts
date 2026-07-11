import { apiClient } from "./client";
import type { ApiResponse, PaginatedResponse } from "@/types";
import type { Summary } from "@/types/api";

export async function fetchSummaries(
  page = 1,
  limit = 5,
): Promise<PaginatedResponse<Summary>> {
  const { data } = await apiClient.get<PaginatedResponse<Summary>>("/summaries", {
    params: { page, limit },
  });
  return data;
}

export async function generateSummary(): Promise<Summary> {
  const { data } = await apiClient.post<ApiResponse<Summary>>("/summaries/generate");
  return data.data;
}
