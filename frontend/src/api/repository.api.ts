/** Repository endpoint functions — one per backend route. */
import { apiClient, ApiError } from "./client";
import type { RepoImportRequest, RepoSummary } from "../types/repository";

export const repositoryApi = {
  /** Current repo, or null when none has been imported yet (404). */
  getCurrent: async (): Promise<RepoSummary | null> => {
    try {
      return await apiClient.get<RepoSummary>("/api/repository", true);
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) return null;
      throw error;
    }
  },

  import: (body: RepoImportRequest) =>
    apiClient.post<RepoSummary>("/api/repository/import", body, true),

  refresh: () => apiClient.post<RepoSummary>("/api/repository/refresh", undefined, true),

  clear: () => apiClient.del<void>("/api/repository", true),
};
