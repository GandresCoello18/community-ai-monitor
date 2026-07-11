import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

import { useWebSocketContext } from "@/contexts/WebSocketContext";

/**
 * Connects to the backend WebSocket and refreshes event queries on new events.
 */
export function useRealtimeEvents() {
  const queryClient = useQueryClient();
  const { connect, subscribe, status } = useWebSocketContext();

  useEffect(() => {
    connect({ autoReconnect: true });
  }, [connect]);

  useEffect(() => {
    return subscribe((message) => {
      if (message.event !== "event.created") {
        return;
      }

      void queryClient.invalidateQueries({ queryKey: ["events"] });
      void queryClient.invalidateQueries({ queryKey: ["event-statistics"] });
    });
  }, [queryClient, subscribe]);

  return { status };
}
