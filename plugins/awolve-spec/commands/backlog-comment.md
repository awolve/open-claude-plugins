---
description: Add a comment to a backlog item
---

# /awolve-spec:backlog-comment

Post a comment on a backlog item. Useful for clarifying scope, recording a decision, or capturing implementation notes that don't belong in the description proper.

## Instructions

Gather:
1. **Project** — which project? Check config; if only one configured, use it.
2. **Item reference** — `#N` or UUID.
3. **Body** — the comment text. Markdown is supported.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-comment <project-id> <item-id-or-#N> "<body>"
```

The command prints the new comment id on success.

After commenting, mention that comments can be listed with `/awolve-spec:backlog-comments` and removed with `/awolve-spec:delete-backlog-comment`.
