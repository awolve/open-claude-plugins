---
description: Purge legacy in-tree sync/build artifacts from the synced specs tree
---

# /awolve-spec:cleanup-synced-tree

One-time cleanup of junk that older plugin versions left inside the
OneDrive-synced tree: `*.remote` sidecars, OneDrive conflict copies
(`*-<machine>.md`), legacy `.specs-trash/` dirs, and — with `--include-venv` —
`_gen/.venv/` build directories in the wider libraries. Canonical spec docs,
`_gen/*.py` scripts, and generated outputs are never touched.

## Instructions

Always start with a dry run and show the user the counts:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py cleanup-synced-tree --dry-run
# include build artifacts in files/ and *-context/ libraries:
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py cleanup-synced-tree --dry-run --include-venv
```

Then, only with the user's go-ahead, run for real (drop `--dry-run`).

**Coordination matters.** A single machine's deletion loses the race against
peers' session-start pulls, which re-upload the files within minutes. For a
durable purge, run this with **every peer's OneDrive paused** (or delete
server-side), then confirm the tree is clean (Awolve-internal: `/cortex-doctor-content`). Until all machines
update the plugin, stragglers will keep reappearing.
