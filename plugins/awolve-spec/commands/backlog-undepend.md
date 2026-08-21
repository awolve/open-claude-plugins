---
description: Remove a dependency between two backlog items
---

# /awolve-spec:backlog-undepend

Drop "this item waits for that one". If it was the last unfinished blocker, the
item goes back to whatever status it held before it became blocked — not to a
default.

## Instructions

Parse the user's argument. Expected forms:

- `<project> <item> <blocker>` — explicit project + both refs
- `<item> <blocker>` — use the configured project (only one)

References accept UUIDs or `#N` numeric form (with or without `#`).

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-undepend <project-id> <item-id-or-#N> <blocker-id-or-#N>
```

Example:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-undepend my-project 251 256
```

Removing a dependency that was never there is not an error — the delete is
idempotent, and the status is recomputed either way.

## When to use this

- The blocker turned out not to block anything after all
- The two items were merged, or the waiting item was rescoped

Both the addition and the removal are recorded in the item's history with who
did it, and an automatic status change is logged separately from a manual one —
a status that moves by itself and leaves no trace is the kind of thing people
stop trusting the tool over.

To add a dependency, use `/awolve-spec:backlog-depend`.
