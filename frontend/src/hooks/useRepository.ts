/**
 * Repository state + actions via TanStack Query.
 * Components use these hooks and never call the api layer directly.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { repositoryApi } from "../api/repository.api";
import type { RepoSummary } from "../types/repository";

const REPOSITORY_KEY = ["repository"] as const;

/** The user's currently imported repo, or null when none. */
export function useCurrentRepository() {
  return useQuery<RepoSummary | null>({
    queryKey: REPOSITORY_KEY,
    queryFn: repositoryApi.getCurrent,
  });
}

/** Shared success handler: store the returned summary as the current repo. */
function useStoreRepoMutation<TArgs>(action: (args: TArgs) => Promise<RepoSummary>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: action,
    onSuccess: (data) => queryClient.setQueryData(REPOSITORY_KEY, data),
  });
}

export const useImportRepository = () => useStoreRepoMutation(repositoryApi.import);
export const useRefreshRepository = () =>
  useStoreRepoMutation<void>(() => repositoryApi.refresh());

/** Clear the current repo so the user can import a different one. */
export function useClearRepository() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: repositoryApi.clear,
    onSuccess: () => queryClient.setQueryData(REPOSITORY_KEY, null),
  });
}
