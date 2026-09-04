---
description: Delete a document
argument-hint: [file-path]
---

# /awolve-spec:delete-doc

Delete a spec document from both the local filesystem and the spec service.

## Instructions

**Always confirm with the user before deleting.** Show the file path and ask for confirmation.

If the user didn't provide a file path, ask which document to delete.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py delete-doc <file-path>
```

This is a hard delete — the document, its version history, comments, and reviews are permanently removed.

**If the command refuses with "N files in this folder carry spec_doc_id …":** the file is a sync conflict copy (e.g. `design-<Machine>.md`) sharing its id with the real document. Do not retry — the delete would hit the original. Remove the stray file with `rm` instead, keeping the one whose filename matches the service.

Suggest archiving the feature (via `/awolve-spec:set-status`) as an alternative if the user wants to keep history.
