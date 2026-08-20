---
description: Edit a comment on a backlog item (author only). Audited.
---

# /awolve-spec:edit-backlog-comment

Edit the body of an existing backlog comment. Only the comment's original author may edit it. Every body change writes a `backlog_comment.update` audit event, and the comment is marked as edited wherever it is displayed.

## Instructions

Gather:

1. **Project** — which project?
2. **Item reference** — `#N` or the UUID of the backlog item.
3. **Comment id** — the UUID shown by `backlog-comments` or `view-backlog`.
4. **New body** — the full replacement text. This replaces the comment, it does not append to it.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py edit-backlog-comment <project-id> <item-id-or-#N> <comment-id> "<body>"
```

Example:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py edit-backlog-comment my-project 18 7f5d… "Shipped in 0.60.0 — starring works from the project list."
```

## Notes

- Run `/awolve-spec:backlog-comments <project> #N` first to find the comment id.
- **403 means it is not your comment.** Editing is author-only — there is no override, for internal users or anyone else. A comment is the author's own words.
- Re-sending the identical body is not treated as an edit and will not mark the comment.
- The edit is logged with the item's project as the audit scope, so it appears in `/awolve-spec:log` for that project.
