/** Auth endpoint functions — one per backend route. */
import { apiClient } from "./client";
import type { AuthResponse, Credentials, User } from "../types/auth";

export const authApi = {
  register: (credentials: Credentials) =>
    apiClient.post<AuthResponse>("/api/auth/register", credentials),

  login: (credentials: Credentials) =>
    apiClient.post<AuthResponse>("/api/auth/login", credentials),

  me: () => apiClient.get<User>("/api/auth/me", true),
};
