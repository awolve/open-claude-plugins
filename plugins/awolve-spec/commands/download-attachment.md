---
description: Download an attachment by id
---

# /awolve-spec:download-attachment

Save a single attached file to disk. The `pull` command syncs whole projects; this is the targeted variant when you only need one file (or you want to grab a bug screenshot).

## Instructions

Gather:
1. **Attachment id** — UUID from `list-attachments`.
2. **Output path** — a directory (server-provided filename is used) or a full file path.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py download-attachment <attachment-id> <out-path>
```

The command prints the byte count and final path on success.
