import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchSummaries, generateSummary } from "@/api/summaries";

export function useSummaries(limit = 3) {
  return useQuery({
    queryKey: ["summaries", limit],
    queryFn: () => fetchSummaries(1, limit),
    refetchInterval: 60_000,
  });
}

export function useGenerateSummary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: generateSummary,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["summaries"] });
    },
  });
}
