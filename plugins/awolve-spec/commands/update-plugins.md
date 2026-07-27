---
description: Refresh the awolve-open-claude-plugins marketplace and reload the session
---

# /awolve-spec:update-plugins

Refresh the `awolve-open-claude-plugins` marketplace (from `awolve/open-claude-plugins`) so newer plugin versions become available locally, then prompt the user to reload the session.

> **Scope note:** this only covers `awolve-open-claude-plugins`. Awolve-internal users: `/update-awolve-plugins` covers `awolve-marketplace`, and `/cortex-update` runs both.

## Instructions

Two steps — both are required. Refreshing the marketplace only updates the *catalog* of available versions; it does not move the installed version pin. Skipping step 2 leaves the plugin running its old code.

```bash
# 1. Refresh the catalog
claude plugin marketplace update awolve-open-claude-plugins

# 2. Upgrade each installed plugin from this marketplace
claude plugin list --json \
  | python3 -c "import json,sys; [print(p['id']) for p in json.load(sys.stdin) if p['id'].endswith('@awolve-open-claude-plugins')]" \
  | xargs -n1 claude plugin update
```

Report which plugins actually moved, using the `updated from X to Y` lines from step 2 — not the marketplace refresh, which reports nothing useful about installed versions.

Note that `claude plugin install` does **not** upgrade an already-installed plugin; it exits with "already installed". `claude plugin update` is the only command that moves the pin.

## After the Update

If the plugin was upgraded, tell the user to run `/reload-plugins` in their current session to pick up the new commands and skills. Phrase it as a direct instruction — slash commands have to be invoked by the user, not by Claude.

Also tell them to **restart Claude Code**. This plugin registers a `SessionStart` hook that runs `specs-cli.py pull`, and hooks in already-running sessions keep resolving to the old plugin root until those sessions restart. A stale hook here is not cosmetic: versions before 0.19.0 wrote conflict `.remote` sidecars beside your spec files instead of staging them out-of-tree, so every session start re-littered the synced specs tree even after the update appeared to succeed.

If the plugin reported "already at the latest version", say so plainly and skip the reload suggestion.
