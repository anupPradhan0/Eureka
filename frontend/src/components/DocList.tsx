/** Lists the documentation files detected in the repo, tagged by category. */
import type { DocCategory, DocFile } from "../types/repository";

const CATEGORY_LABELS: Record<DocCategory, string> = {
  readme: "README",
  code_of_conduct: "Code of Conduct",
  contributing: "Contributing",
  license: "License",
  security: "Security",
  other: "Other",
};

export function DocList({ docs }: { docs: DocFile[] }) {
  if (docs.length === 0) {
    return <p className="muted">No documentation files found.</p>;
  }

  return (
    <ul className="docs">
      {docs.map((doc) => (
        <li key={doc.path} className="docs__item">
          <span className={`docs__badge docs__badge--${doc.category}`}>
            {CATEGORY_LABELS[doc.category]}
          </span>
          <span className="docs__name">{doc.name}</span>
        </li>
      ))}
    </ul>
  );
}
