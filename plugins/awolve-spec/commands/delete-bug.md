---
description: Soft-delete a bug (internal users only)
---

# /awolve-spec:delete-bug

Soft-delete a bug. Sets `status="deleted"` and records the deleter — the bug stops appearing in `bugs` listings but is recoverable server-side. Internal users only.

## Instructions

Gather:
1. **Project** — which project?
2. **Bug number** — `#N` from the `bugs` listing.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py delete-bug <project-id> <bug-number>
```

Always confirm with the user before deleting unless they've explicitly asked for it.
