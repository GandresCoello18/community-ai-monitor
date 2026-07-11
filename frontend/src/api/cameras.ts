import { apiClient } from "./client";
import type { ApiResponse, PaginatedResponse } from "@/types";
import type { Camera } from "@/types/api";

export async function fetchCameras(
  page = 1,
  limit = 50,
): Promise<PaginatedResponse<Camera>> {
  const { data } = await apiClient.get<PaginatedResponse<Camera>>("/cameras", {
    params: { page, limit },
  });
  return data;
}

export async function fetchCamera(cameraId: string): Promise<Camera> {
  const { data } = await apiClient.get<ApiResponse<Camera>>(`/cameras/${cameraId}`);
  return data.data;
}

export async function updateCamera(
  cameraId: string,
  payload: Partial<Pick<Camera, "name" | "location" | "stream_url" | "is_active">>,
): Promise<Camera> {
  const { data } = await apiClient.patch<ApiResponse<Camera>>(
    `/cameras/${cameraId}`,
    payload,
  );
  return data.data;
}

export async function deleteCamera(cameraId: string): Promise<Camera> {
  const { data } = await apiClient.delete<ApiResponse<Camera>>(`/cameras/${cameraId}`);
  return data.data;
}
