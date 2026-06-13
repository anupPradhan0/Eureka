/** Step 1 (gate): configure a BYO AI provider/model/key, validated live. */
import { useState, type FormEvent } from "react";

import { useSaveAiConfig } from "../hooks/useAiConfig";
import { ApiError } from "../api/client";
import type { AiProvider } from "../types/aiConfig";

const PROVIDERS: { value: AiProvider; label: string; modelHint: string }[] = [
  { value: "anthropic", label: "Anthropic (Claude)", modelHint: "claude-opus-4-8" },
  { value: "openai", label: "OpenAI", modelHint: "gpt-4o" },
  { value: "openrouter", label: "OpenRouter", modelHint: "anthropic/claude-opus-4-8" },
  { value: "gemini", label: "Google Gemini", modelHint: "gemini-2.0-flash" },
];

export function ConfigPage() {
  const [provider, setProvider] = useState<AiProvider>("anthropic");
  const [model, setModel] = useState("");
  const [apiKey, setApiKey] = useState("");

  const save = useSaveAiConfig();
  const modelHint = PROVIDERS.find((p) => p.value === provider)?.modelHint ?? "";

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    save.mutate({ provider, model, api_key: apiKey });
  };

  const errorMessage =
    save.error instanceof ApiError
      ? save.error.message
      : save.error
        ? "Something went wrong."
        : null;

  return (
    <div className="panel">
      <h2>Configure your AI model</h2>
      <p className="muted">
        Eureka is bring-your-own-key — it never ships its own AI access. Pick a provider,
        choose a model, and paste your API key. The key is validated against the provider,
        encrypted at rest, and never shown again.
      </p>

      <form className="form" onSubmit={onSubmit}>
        <label>
          Provider
          <select value={provider} onChange={(e) => setProvider(e.target.value as AiProvider)}>
            {PROVIDERS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Model
          <input
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder={modelHint}
            required
          />
        </label>

        <label>
          API key
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            required
            autoComplete="off"
          />
        </label>

        {errorMessage && <p className="form__error">{errorMessage}</p>}

        <button type="submit" disabled={save.isPending}>
          {save.isPending ? "Validating…" : "Validate & save"}
        </button>
      </form>
    </div>
  );
}
