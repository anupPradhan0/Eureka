/** Repository summary types — mirror the backend's repository DTOs. */

export interface TreeEntry {
  path: string;
  type: "blob" | "tree";
  size: number | null;
}

export type DocCategory =
  | "readme"
  | "code_of_conduct"
  | "contributing"
  | "license"
  | "security"
  | "other";

export interface DocFile {
  category: DocCategory;
  name: string;
  path: string;
}

export interface RepoSummary {
  owner: string;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  default_branch: string;
  /** null when GitHub doesn't expose the stat — the UI hides it. */
  stars: number | null;
  contributors_count: number | null;
  file_count: number | null;
  tree_truncated: boolean;
  tree: TreeEntry[];
  docs: DocFile[];
  /** Raw README markdown, shown for context. */
  readme: string | null;
}

export interface RepoImportRequest {
  url: string;
  github_token?: string;
}
