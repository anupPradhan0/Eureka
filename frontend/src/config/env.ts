/**
 * Centralized access to environment configuration.
 * No other module reads import.meta.env directly.
 */
export const env = {
  apiUrl: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
} as const;
