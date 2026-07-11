import { env } from "@/config/env";

export function getCameraPreviewStreamUrl(cameraId: string): string {
  return `${env.apiBaseUrl}/cameras/${cameraId}/preview/stream`;
}

export function getCameraPreviewSnapshotUrl(cameraId: string): string {
  return `${env.apiBaseUrl}/cameras/${cameraId}/preview`;
}
