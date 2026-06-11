/** Shared auth types — mirror the backend's response/request DTOs. */

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Credentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
