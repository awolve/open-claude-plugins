---
description: List spec-sync conflicts staged out-of-tree (per-machine cache)
---

# /awolve-spec:conflicts

List sync conflicts where your local edits collided with a remote change. The
remote side is staged in the per-machine cache (never beside your files), so
nothing pollutes the synced specs tree.

## Instructions

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py conflicts
```

Optionally scope to one project: `... conflicts <project-id>` (or `--json`).

For each conflict you can:

```bash
# inspect
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py conflict show <doc>   # staged remote
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py conflict diff <doc>   # local vs remote

# resolve (<doc> is a doc_id or the local file path)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py conflict resolve <doc> --theirs          # take remote
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py conflict resolve <doc> --mine            # push local
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py conflict resolve <doc> --merged <file>   # push a hand-merged file
```

Resolving clears the staged copy. If a resolve reports "remote moved again",
run `/awolve-spec:pull` and resolve once more.
