/**
 * AI-config state + actions via TanStack Query.
 * Components use these hooks and never call the api layer directly.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { aiConfigApi } from "../api/aiConfig.api";
import type { AiConfigStatus } from "../types/aiConfig";

const AI_CONFIG_KEY = ["ai-config"] as const;

/** Whether the user has configured a validated AI provider/model/key. */
export function useAiConfigStatus() {
  return useQuery<AiConfigStatus>({
    queryKey: AI_CONFIG_KEY,
    queryFn: aiConfigApi.getStatus,
  });
}

/** Save + live-validate the AI config; refreshes status on success. */
export function useSaveAiConfig() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: aiConfigApi.save,
    onSuccess: (data) => {
      queryClient.setQueryData(AI_CONFIG_KEY, data);
    },
  });
}
