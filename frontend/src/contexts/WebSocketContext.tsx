import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useSyncExternalStore,
  type ReactNode,
} from "react";

import {
  webSocketService,
  type WebSocketConnectOptions,
  type WebSocketService,
} from "@/services/websocket";
import type { ConnectionStatus, WebSocketMessage } from "@/types";

interface WebSocketContextValue {
  status: ConnectionStatus;
  connect: (options?: WebSocketConnectOptions) => void;
  disconnect: () => void;
  send: (data: string) => void;
  subscribe: (handler: (message: WebSocketMessage) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

interface WebSocketProviderProps {
  children: ReactNode;
  service?: WebSocketService;
  autoConnect?: boolean;
}

export function WebSocketProvider({
  children,
  service = webSocketService,
  autoConnect = false,
}: WebSocketProviderProps) {
  const status = useSyncExternalStore(
    (onStoreChange) => service.onStatusChange(() => onStoreChange()),
    () => service.status,
    () => service.status,
  );

  const connect = useCallback(
    (options?: WebSocketConnectOptions) => service.connect(options),
    [service],
  );

  const disconnect = useCallback(() => service.disconnect(), [service]);

  const send = useCallback((data: string) => service.send(data), [service]);

  const subscribe = useCallback(
    (handler: (message: WebSocketMessage) => void) =>
      service.onMessage(handler),
    [service],
  );

  const value = useMemo<WebSocketContextValue>(
    () => ({ status, connect, disconnect, send, subscribe }),
    [status, connect, disconnect, send, subscribe],
  );

  useEffect(() => {
    if (autoConnect && status === "idle") {
      connect();
    }
  }, [autoConnect, connect, status]);

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocketContext(): WebSocketContextValue {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocketContext must be used within WebSocketProvider");
  }
  return context;
}
