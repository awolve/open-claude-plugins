---
description: Add a project to a programme as a member
argument-hint: [programme-id] [project-id]
---

# /awolve-spec:programme-add

Add a project to a programme. Only the membership changes: the project's phases, milestones and items stay as they are, and who can read it does not change. Internal users only.

## Instructions

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py programme-add <programme-id> <project-id>
```

- A project may be in several programmes, and a programme may hold projects from different clients.
- A programme can't be a member (`member_is_programme`).
- Adding a project that is already a member changes nothing.

The new member is added last; the order of member groups is set by dragging them on the programme's Plan tab.
