---
description: Show full details of a single backlog item (description, parent, children, comments)
---

# /awolve-spec:view-backlog

Show the complete description, metadata, parent, children (for epics), and comments for a backlog item. The list view (`backlog`) deliberately elides description to stay scannable; this command surfaces everything you need to implement an item.

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
- header — priority marker, status, item number, title, `[EPIC]` tag if applicable
- author, assignee (or `(unassigned)`), promoted-feature link (if any), parent reference, child counts (if epic)
- created/updated timestamps and the portal URL
- the full **Description** in markdown
- the **Children** list (epics only) — each child's `#N`, priority, title, status
- the **Comments** list — author, timestamp, comment id, body

After viewing, mention that the item can be edited via `/awolve-spec:backlog-update` or commented on via `/awolve-spec:backlog-comment`.
