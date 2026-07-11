import { io, type Socket } from "socket.io-client";

import { env } from "@/config/env";

/**
 * Socket.io adapter (prepared, not connected by default).
 *
 * The current backend exposes native WebSockets (FastAPI), not a Socket.io
 * server. This adapter exists so a future gateway or alternate transport can
 * be swapped in without changing UI hooks. Use NativeWebSocketService for now.
 */
export class SocketIoAdapter {
  private socket: Socket | null = null;

  createSocket(): Socket {
    if (this.socket) {
      return this.socket;
    }

    this.socket = io(env.wsBaseUrl, {
      autoConnect: false,
      transports: ["websocket"],
    });

    return this.socket;
  }

  disconnect(): void {
    this.socket?.disconnect();
    this.socket = null;
  }
}

export const socketIoAdapter = new SocketIoAdapter();
