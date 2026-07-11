import type { ConnectionStatus, WebSocketMessage } from "@/types";

export type MessageHandler = (message: WebSocketMessage) => void;
export type StatusHandler = (status: ConnectionStatus) => void;

export interface WebSocketConnectOptions {
  cameraId?: string;
  autoReconnect?: boolean;
  reconnectDelayMs?: number;
}

export interface WebSocketService {
  readonly status: ConnectionStatus;
  connect(options?: WebSocketConnectOptions): void;
  disconnect(): void;
  send(data: string): void;
  onMessage(handler: MessageHandler): () => void;
  onStatusChange(handler: StatusHandler): () => void;
}
