---
description: Set or clear the parent item of a backlog item (make it a sub-item)
---

# /awolve-signum:backlog-set-parent

Make a backlog item a sub-item of another item, or top-level again if you pass `none`. Any top-level item can have sub-items; there is one level only. To put an item under an **epic**, use `/awolve-signum:epic-set` instead.

## Instructions

Parse the user's argument. Expected forms:

- `<project> <item> <parent>` — explicit project + both refs
- `<item> <parent>` — use the configured project (only one)

References accept UUIDs or `#N` numeric form (with or without `#`). `none` (or `null`) as the parent reference clears the existing parent.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-set-parent <project-id> <item-id-or-#N> <parent-id-or-#N|none>
```

Examples:

```bash
# Make item #7 a sub-item of #4
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-set-parent my-project 7 4

# Detach #7 from its parent (back to top-level)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-set-parent my-project 7 none
```

A sub-item takes its parent's epic. Becoming a sub-item drops an epic the item had on its own.

## Errors the API returns

The CLI prints each one with what to do next.

- `parent_not_found` — referenced parent doesn't exist or is soft-deleted
- `parent_wrong_project` — parent belongs to a different project
- `parent_must_be_top_level` — parent itself has a parent; only one level of nesting allowed
- `parent_self_reference` — trying to make an item its own parent
- `has_sub_items` — the item has sub-items of its own, so it can't become a sub-item. Move its sub-items first.
- `feature_differs_from_parent` — the item delivers a different feature from the parent; a sub-item shares its parent's feature
- `parent_not_an_epic` — only on a Signum service from before real epics, which accepts only an item marked as an epic (in the portal) as a parent

## When to use this

- Restructuring a backlog: pulling related items under one item
- Detaching a sub-item that has grown into its own thing
- Reorganizing after a planning conversation

For new items, prefer creating them with `--parent` directly via `/awolve-signum:backlog-add` rather than creating then reparenting.
