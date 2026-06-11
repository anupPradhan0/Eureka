/**
 * Single place that knows how the access token is persisted.
 * Swapping storage (e.g. to cookies) only touches this file.
 */
const TOKEN_KEY = "openruki.access_token";

export const tokenStorage = {
  get(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },
  set(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  },
  clear(): void {
    localStorage.removeItem(TOKEN_KEY);
  },
};
