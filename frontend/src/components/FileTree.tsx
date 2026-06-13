/**
 * Collapsible file tree built from the backend's flat path list.
 * The flat `TreeEntry[]` is folded into nested directory nodes for display.
 */
import { useMemo, useState } from "react";

import type { TreeEntry } from "../types/repository";

interface TreeNodeData {
  name: string;
  path: string;
  type: "blob" | "tree";
  children: Map<string, TreeNodeData>;
}

function buildTree(entries: TreeEntry[]): TreeNodeData {
  const root: TreeNodeData = { name: "", path: "", type: "tree", children: new Map() };

  for (const entry of entries) {
    const parts = entry.path.split("/");
    let current = root;
    parts.forEach((part, index) => {
      const isLeaf = index === parts.length - 1;
      let child = current.children.get(part);
      if (!child) {
        child = {
          name: part,
          path: parts.slice(0, index + 1).join("/"),
          type: isLeaf ? entry.type : "tree",
          children: new Map(),
        };
        current.children.set(part, child);
      }
      current = child;
    });
  }
  return root;
}

/** Directories first, then files, each alphabetical. */
function sortedChildren(node: TreeNodeData): TreeNodeData[] {
  return [...node.children.values()].sort((a, b) => {
    if (a.type !== b.type) return a.type === "tree" ? -1 : 1;
    return a.name.localeCompare(b.name);
  });
}

function TreeNode({ node, depth }: { node: TreeNodeData; depth: number }) {
  // Expand the top level by default; keep deeper folders collapsed.
  const [open, setOpen] = useState(depth < 1);
  const indent = { paddingLeft: `${depth * 14}px` };

  if (node.type === "blob") {
    return (
      <li className="tree__file" style={indent}>
        <span aria-hidden>📄</span> {node.name}
      </li>
    );
  }

  const children = sortedChildren(node);
  return (
    <li className="tree__dir">
      <button type="button" className="tree__toggle" style={indent} onClick={() => setOpen(!open)}>
        <span aria-hidden>{open ? "▾" : "▸"}</span> <span aria-hidden>📁</span> {node.name}
      </button>
      {open && children.length > 0 && (
        <ul className="tree__children">
          {children.map((child) => (
            <TreeNode key={child.path} node={child} depth={depth + 1} />
          ))}
        </ul>
      )}
    </li>
  );
}

export function FileTree({ entries }: { entries: TreeEntry[] }) {
  const root = useMemo(() => buildTree(entries), [entries]);
  const top = sortedChildren(root);

  if (top.length === 0) return <p className="muted">No files found.</p>;

  return (
    <ul className="tree">
      {top.map((node) => (
        <TreeNode key={node.path} node={node} depth={0} />
      ))}
    </ul>
  );
}
