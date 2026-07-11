import { QueryClient } from "@tanstack/react-query";

import { env } from "./env";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: env.isDev,
    },
  },
});
