---
name: sonnet-review
description: Review the current git changes for correctness bugs, security issues, and adherence to this project's principles (DRY, SOLID, layered architecture). Runs the review on Sonnet in an isolated context. Use when asked to review the diff/branch, check changes before committing, or before opening a PR.
context: fork
agent: sonnet-reviewer
---

Perform a code review of the current changes.

Requested scope: $ARGUMENTS

- If a scope is given above (a path, a base branch like `main`, or a keyword like
  `staged`), review that.
- If no scope is given, review this branch's diff against `main`. If there is no
  diff against `main`, fall back to the working-tree changes (staged + unstaged).

Follow your review methodology and report findings grouped by severity with
`file:line` references. This is read-only — do not modify any files.
