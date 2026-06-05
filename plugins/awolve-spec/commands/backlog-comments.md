---
description: List comments on a backlog item
---

# /awolve-spec:backlog-comments

Show every comment on a backlog item with author and timestamp.

## Instructions

Gather:
1. **Project** — which project?
2. **Item reference** — `#N` or UUID.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-comments <project-id> <item-id-or-#N>
```

Pass `--json` for raw output.

Each comment shows: author, ISO timestamp, comment id, and body. Use the comment id with `/awolve-spec:delete-backlog-comment` to remove one.
