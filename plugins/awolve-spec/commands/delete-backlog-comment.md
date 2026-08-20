---
description: Delete a comment from a backlog item
---

# /awolve-spec:delete-backlog-comment

Remove a comment from a backlog item. Only the comment's original author may delete it — internal users lost this override in spec-service 0.63.0.

## Instructions

Gather:
1. **Project** — which project?
2. **Item reference** — `#N` or UUID for the backlog item.
3. **Comment id** — the UUID shown by `backlog-comments` or `view-backlog`.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py delete-backlog-comment <project-id> <item-id-or-#N> <comment-id>
```

This is a hard delete and audited on the server.
