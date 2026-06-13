/**
 * Shows raw README markdown in a readable, scrollable block.
 * Rendered as plain text (not HTML) to avoid any injection risk from
 * untrusted repository content.
 */
export function MarkdownView({ content }: { content: string }) {
  return <pre className="markdown">{content}</pre>;
}
