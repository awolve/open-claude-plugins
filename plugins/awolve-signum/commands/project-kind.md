---
description: Make a project a programme, or a programme a project again
argument-hint: [project-id] [programme|project]
---

# /awolve-signum:project-kind

Change a project's kind. A **programme** is a project that also holds member projects. Its phases, milestones and items stay as they are either way. Internal users only.

## Instructions

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py project-kind <project-id> programme
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py project-kind <project-id> project
```

The service refuses, and the CLI says why, when:

- the project has external users with access (`programme_has_external_access`) — programmes are internal-only for now;
- the project is itself a member of a programme (`project_is_member`) — a programme can't be a member;
- a programme still has members and should become a project (`programme_has_members`).

A new project can also be created as a programme from the portal's admin page.
