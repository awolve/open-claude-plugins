---
description: Create a milestone, a deadline that holds items or a plain date
argument-hint: [project-id] [name]
---

# /awolve-spec:milestone-create

Create a milestone. Internal users only.

## Instructions

Determine the project as usual. Ask for the name, the date and the kind if they were not given: a **deadline** holds the items due by then; a **date** is a day worth knowing and holds no items.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-create <project-id> "<name>" --date YYYY-MM-DD --kind deadline|date [--description "<what it is for>"]
```

The CLI prints the milestone and a link to its page. Put items in a deadline with `/awolve-spec:milestone-add`.
