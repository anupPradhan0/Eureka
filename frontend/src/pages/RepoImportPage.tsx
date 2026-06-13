/** Step 2: point Eureka at the GitHub repo it will build into. */
import { useState, type FormEvent } from "react";

import { useImportRepository } from "../hooks/useRepository";
import { ApiError } from "../api/client";

export function RepoImportPage() {
  const [url, setUrl] = useState("");
  const [token, setToken] = useState("");

  const importRepo = useImportRepository();

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    importRepo.mutate({ url, github_token: token || undefined });
  };

  const errorMessage =
    importRepo.error instanceof ApiError
      ? importRepo.error.message
      : importRepo.error
        ? "Something went wrong."
        : null;

  return (
    <div className="panel">
      <h2>Import your repository</h2>
      <p className="muted">
        Paste the GitHub URL of the project you'll build into. Eureka pulls a summary so
        it understands your codebase. Add a token for private repos or higher rate limits.
      </p>

      <form className="form" onSubmit={onSubmit}>
        <label>
          GitHub repository URL
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            required
          />
        </label>

        <label>
          GitHub token <span className="muted">(optional)</span>
          <input
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            autoComplete="off"
          />
        </label>

        {errorMessage && <p className="form__error">{errorMessage}</p>}

        <button type="submit" disabled={importRepo.isPending}>
          {importRepo.isPending ? "Fetching…" : "Import repository"}
        </button>
      </form>
    </div>
  );
}
