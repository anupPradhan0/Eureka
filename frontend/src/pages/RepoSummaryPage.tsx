/** Step 3: the repository summary — stats, file tree, and documentation. */
import { useClearRepository, useRefreshRepository } from "../hooks/useRepository";
import { StatBadge } from "../components/StatBadge";
import { FileTree } from "../components/FileTree";
import { DocList } from "../components/DocList";
import { MarkdownView } from "../components/MarkdownView";
import type { RepoSummary } from "../types/repository";

export function RepoSummaryPage({ repo }: { repo: RepoSummary }) {
  const refresh = useRefreshRepository();
  const clear = useClearRepository();

  return (
    <div className="summary">
      <div className="summary__head">
        <div>
          <h2>
            <a href={repo.html_url} target="_blank" rel="noreferrer">
              {repo.full_name}
            </a>
          </h2>
          {repo.description && <p className="muted">{repo.description}</p>}
        </div>
        <div className="summary__actions">
          <button type="button" onClick={() => refresh.mutate()} disabled={refresh.isPending}>
            {refresh.isPending ? "Refreshing…" : "Refresh"}
          </button>
          <button type="button" className="btn-secondary" onClick={() => clear.mutate()}>
            Import a different repo
          </button>
        </div>
      </div>

      {/* Each badge hides itself when GitHub didn't provide the stat. */}
      <div className="stats">
        <StatBadge label="Stars" value={repo.stars} />
        <StatBadge label="Contributors" value={repo.contributors_count} />
        <StatBadge label="Files" value={repo.file_count} />
      </div>

      <div className="summary__grid">
        <section className="card">
          <h3>
            File structure{" "}
            {repo.tree_truncated && <span className="muted">(truncated — large repo)</span>}
          </h3>
          <FileTree entries={repo.tree} />
        </section>

        <section className="card">
          <h3>Documentation</h3>
          <DocList docs={repo.docs} />
          {repo.readme && (
            <>
              <h3>README</h3>
              <MarkdownView content={repo.readme} />
            </>
          )}
        </section>
      </div>
    </div>
  );
}
