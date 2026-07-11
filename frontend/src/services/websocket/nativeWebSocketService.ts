import { env } from "@/config/env";
import type { ConnectionStatus, WebSocketMessage } from "@/types";

import type {
  MessageHandler,
  StatusHandler,
  WebSocketConnectOptions,
  WebSocketService,
} from "./types";

/**
 * Native WebSocket client aligned with the FastAPI backend contract.
 * Endpoint: ws://host/api/v1/ws/events[?camera_id=uuid]
 */
export class NativeWebSocketService implements WebSocketService {
  private socket: WebSocket | null = null;
  private _status: ConnectionStatus = "idle";
  private messageHandlers = new Set<MessageHandler>();
  private statusHandlers = new Set<StatusHandler>();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private connectOptions: WebSocketConnectOptions = {};

  get status(): ConnectionStatus {
    return this._status;
  }

  connect(options: WebSocketConnectOptions = {}): void {
    this.connectOptions = {
      autoReconnect: true,
      reconnectDelayMs: 3_000,
      ...options,
    };

    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.clearReconnect();
    this.setStatus("connecting");

    const url = new URL(`${env.wsBaseUrl}/events`);
    if (this.connectOptions.cameraId) {
      url.searchParams.set("camera_id", this.connectOptions.cameraId);
    }

    this.socket = new WebSocket(url.toString());

    this.socket.onopen = () => {
      this.setStatus("connected");
    };

    this.socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(String(event.data)) as WebSocketMessage;
        this.messageHandlers.forEach((handler) => handler(parsed));
      } catch {
        // Ignore malformed payloads until logging is wired in a later phase.
      }
    };

    this.socket.onerror = () => {
      this.setStatus("error");
    };

    this.socket.onclose = () => {
      this.setStatus("disconnected");
      this.scheduleReconnect();
    };
  }

  disconnect(): void {
    this.connectOptions.autoReconnect = false;
    this.clearReconnect();
    this.socket?.close();
    this.socket = null;
    this.setStatus("idle");
  }

  send(data: string): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(data);
    }
  }

  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  onStatusChange(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler);
    handler(this._status);
    return () => this.statusHandlers.delete(handler);
  }

  private setStatus(status: ConnectionStatus): void {
    this._status = status;
    this.statusHandlers.forEach((handler) => handler(status));
  }

  private scheduleReconnect(): void {
    if (!this.connectOptions.autoReconnect) {
      return;
    }

    this.clearReconnect();
    this.reconnectTimer = setTimeout(() => {
      this.connect(this.connectOptions);
    }, this.connectOptions.reconnectDelayMs ?? 3_000);
  }

  private clearReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}

export const webSocketService = new NativeWebSocketService();
