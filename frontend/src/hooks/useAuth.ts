/**
 * Auth state + actions via TanStack Query.
 * Components use these hooks and never call the api layer directly.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { authApi } from "../api/auth.api";
import { tokenStorage } from "../lib/tokenStorage";
import type { AuthResponse, Credentials, User } from "../types/auth";

const CURRENT_USER_KEY = ["auth", "me"] as const;

/** Current authenticated user; null when no/invalid token. */
export function useCurrentUser() {
  return useQuery<User | null>({
    queryKey: CURRENT_USER_KEY,
    queryFn: async () => {
      if (!tokenStorage.get()) return null;
      try {
        return await authApi.me();
      } catch {
        tokenStorage.clear();
        return null;
      }
    },
  });
}

function useAuthMutation(action: (credentials: Credentials) => Promise<AuthResponse>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: action,
    onSuccess: (data) => {
      tokenStorage.set(data.access_token);
      queryClient.setQueryData(CURRENT_USER_KEY, data.user);
    },
  });
}

export const useLogin = () => useAuthMutation(authApi.login);
export const useRegister = () => useAuthMutation(authApi.register);

export function useLogout() {
  const queryClient = useQueryClient();
  return () => {
    tokenStorage.clear();
    queryClient.setQueryData(CURRENT_USER_KEY, null);
  };
}
