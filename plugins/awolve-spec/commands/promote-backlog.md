---
description: Promote a backlog item to a feature (creates spec.md quick-spec doc)
---

# /awolve-spec:promote-backlog

Turn a backlog item into a full feature. The server creates a new feature in the project, writes a `spec.md` document seeded from the quick-spec template, and links the backlog item to the new feature so `view-backlog` shows the promotion.

## Instructions

Gather:
1. **Project** — which project?
2. **Item reference** — `#N` or UUID.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py promote-backlog <project-id> <item-id-or-#N>
```

On success, the command prints the new `featureId`, `documentId`, and `featureName`.

Then run `/awolve-spec:pull` to materialize the new `spec.md` locally so you can edit it. Mention this to the user — promotion alone doesn't put the file on disk.

Don't promote an item that's already promoted — the command refuses if `featureId` is set. Use `view-backlog` first if unsure.
