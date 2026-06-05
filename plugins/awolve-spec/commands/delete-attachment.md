---
description: Delete an attachment by id
---

# /awolve-spec:delete-attachment

Permanently remove an attachment from the spec service. Permitted for the uploader (matched by email) or any internal user.

## Instructions

Gather:
1. **Attachment id** — UUID from `list-attachments`.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py delete-attachment <attachment-id>
```

Always confirm with the user before deleting unless they've explicitly asked for it.
