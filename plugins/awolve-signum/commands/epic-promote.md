---
description: Turn a backlog item with sub-items (an old-style epic) into a real epic
argument-hint: [project-id] [#item]
---

# /awolve-signum:epic-promote

Promote a top-level item that has sub-items to a real epic. Its sub-items move under the new epic (directly, or with their feature), features that are not under another epic move with them, and the item is archived. It keeps its number, comments and history, and points on to the epic, so old links still open. Internal users only.

## Instructions

Always look at the plan first. Without `--yes` the command changes nothing:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py epic-promote <project-id> '#N'
```

It prints what would happen: the epic it would create, which sub-items move and how, which features move and which stay under the epic they already have, and that the item is archived.

Show that plan to the user and ask for confirmation. Only after they say yes, run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py epic-promote <project-id> '#N' --yes
```

The CLI prints the new epic's number (`E<n>`) and portal link.

## Refusals

- `promote_needs_sub_items` — the item has no sub-items. For a new epic, use `/awolve-signum:epic-create`.
- `promote_sub_item` — the item is itself a sub-item; promote its parent.
- `promote_archived` — the item is archived.
- A non-internal user is refused by the service.

**A Signum service from before real epics** has no epic API: the CLI says so and changes nothing.
