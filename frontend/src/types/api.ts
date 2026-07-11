export interface Camera {
  id: string;
  name: string;
  location: string;
  stream_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Event {
  id: string;
  camera_id: string;
  event_type: string;
  severity: string;
  occurred_at: string;
  started_at: string | null;
  ended_at: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface EventCreatedPayload {
  id: string;
  camera_id: string;
  event_type: string;
  severity: string;
  occurred_at: string;
  started_at: string | null;
  ended_at: string | null;
  metadata: Record<string, unknown> | null;
}

export interface EventStatistics {
  total: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  by_camera: Record<string, number>;
}

export interface StreamStatus {
  camera_id: string;
  status: string;
  source_type: string;
  frames_processed: number;
  fps_target: number;
  last_frame_at: string | null;
  detection_enabled: boolean;
  detections_processed: number;
  last_detection_at: string | null;
  error_message: string | null;
}

export interface HealthStatus {
  status: string;
  database: string;
}

export interface ListEventsParams {
  page?: number;
  limit?: number;
  camera_id?: string;
  event_type?: string;
}
