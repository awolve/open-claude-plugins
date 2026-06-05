---
description: List attachments on a feature, bug, or backlog item
---

# /awolve-spec:list-attachments

List every file attached to a feature, bug, or backlog item — filename, size, content type, uploader, and the attachment id (used with `download-attachment` and `delete-attachment`).

## Instructions

Gather:
1. **Entity type** — one of `feature`, `bug`, `backlog`.
2. **Entity UUID** — the UUID of the parent feature/bug/backlog item. (Use `list-features`, `bugs`, or `view-backlog` to find it.)

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py list-attachments <feature|bug|backlog> <entity-uuid>
```

Pass `--json` for raw output.

When the user wants the file itself, follow up with `/awolve-spec:download-attachment <id> <out-path>`.
