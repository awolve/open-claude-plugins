---
description: Show full details of a single backlog item (description, parent, epic, sub-items, comments)
---

# /awolve-signum:view-backlog

Show the complete description, metadata, parent, epic, sub-items, and comments for a backlog item. The list view (`backlog`) deliberately elides description to stay scannable; this command surfaces everything you need to implement an item.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask.

Determine the backlog item. Accept either `#N` (the short number from `backlog`) or a UUID. If the user just gives a number, treat it as `#N`.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py view-backlog <project-id> <item-id-or-#N>
```

Pass `--json` to get the raw payload (parent, children, comments included) when you need to feed it into further processing.

### Output

Shows:
- header — priority marker, status, item number, title (and, on a service from before real epics, an `[EPIC]` tag for an item marked as one)
- author, assignee (or `(unassigned)`), the feature it delivers (if any — its number, title and the feature's own status), parent reference, sub-item counts
- the **epic** it belongs to (`E3 Title`), with `(via its feature)` or `(via its parent)` when it takes the epic from there — then it can only move by moving the feature or parent. An item promoted to an epic says which one it became.
- created/updated timestamps and the portal URL
- the full **Description** in markdown
- the **Children** list (its sub-items, if any) — each one's `#N`, priority, title, status
- the **Comments** list — author, timestamp, comment id, body

After viewing, mention that the item can be edited via `/awolve-signum:backlog-update` or commented on via `/awolve-signum:backlog-comment`.
