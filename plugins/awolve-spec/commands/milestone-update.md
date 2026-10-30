---
description: Change a milestone's name, date, kind or description
argument-hint: [project-id] [milestone]
---

# /awolve-spec:milestone-update

Change one milestone. Internal users only.

## Instructions

Determine the project as usual. Name the milestone by its name (any case) or its id.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-update <project-id> <milestone-name-or-id> [--name "<name>"] [--date YYYY-MM-DD] [--kind deadline|date] [--description "<text>" | --clear-description]
```

A deadline that still holds items cannot become a date: the service refuses with `milestone_has_items`. Move its items out first (`backlog-update … --unmilestone`, or into another deadline).
