---
description: Delete a phase from a project
argument-hint: [project-id] [phase]
---

# /awolve-signum:phase-delete

Delete one phase. The other phases stay as they are; if that leaves days no phase covers, the Plan tab shows it as a finding. Internal users only.

## Instructions

Determine the project as usual, and name the phase by its name or id. Confirm with the user before deleting.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py phase-delete <project-id> <phase-name-or-id>
```
