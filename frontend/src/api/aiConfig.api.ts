/** AI-config endpoint functions — one per backend route. */
import { apiClient } from "./client";
import type { AiConfigSaveRequest, AiConfigStatus } from "../types/aiConfig";

export const aiConfigApi = {
  getStatus: () => apiClient.get<AiConfigStatus>("/api/ai-config", true),

  save: (body: AiConfigSaveRequest) =>
    apiClient.put<AiConfigStatus>("/api/ai-config", body, true),
};
