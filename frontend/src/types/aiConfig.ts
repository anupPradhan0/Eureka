/** AI provider configuration types — mirror the backend's ai-config DTOs. */

export type AiProvider = "anthropic" | "openai" | "openrouter" | "gemini";

/** Safe status of the user's AI config. Never carries the API key itself. */
export interface AiConfigStatus {
  configured: boolean;
  provider?: AiProvider;
  model?: string;
  key_hint?: string;
}

export interface AiConfigSaveRequest {
  provider: AiProvider;
  model: string;
  api_key: string;
}
