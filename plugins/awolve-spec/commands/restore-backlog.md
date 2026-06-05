---
description: Restore a soft-deleted backlog item (internal users only)
---

# /awolve-spec:restore-backlog

Restore a backlog item that was soft-deleted with `backlog-delete`. Internal users only.

## Instructions

Gather:
1. **Project** — which project?
2. **Item UUID** — deleted items are not in the active list, so pass the UUID (visible in the portal's deleted-items view or in audit logs).

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py restore-backlog <project-id> <item-uuid>
```

The command prints the restored item's `#N` and title on success.

Restoring an item does NOT restore its cascade-deleted children — each child must be restored individually.
