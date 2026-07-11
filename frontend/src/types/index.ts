export type ThemeMode = "light" | "dark" | "system";

export type ApiErrorCode =
  | "NETWORK_ERROR"
  | "UNKNOWN_ERROR"
  | "VALIDATION_ERROR"
  | "NOT_FOUND"
  | "UNAUTHORIZED"
  | "FORBIDDEN"
  | string;

export interface ApiErrorBody {
  error: {
    code: ApiErrorCode;
    message: string;
  };
}

export interface ApiResponse<T> {
  data: T;
  meta?: Record<string, unknown>;
}

export interface PaginatedMeta {
  page: number;
  limit: number;
  total: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginatedMeta;
}

export type ConnectionStatus =
  | "idle"
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";

export interface WebSocketMessage<T = unknown> {
  event: string;
  timestamp: string;
  data: T;
}

export type { Camera, Event, EventCreatedPayload, EventStatistics, EventStatisticsParams, HealthStatus, ListEventsParams, StreamStatus } from "./api";
