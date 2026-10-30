---
description: Delete a milestone; a deadline's items go back to Unplanned
argument-hint: [project-id] [milestone]
---

# /awolve-signum:milestone-delete

Delete one milestone. A deadline's items are not deleted: they go back to Unplanned, and nothing else about them changes. Internal users only.

## Instructions

Determine the project as usual, and name the milestone by its name or id. Confirm with the user before deleting; say how many items the deadline holds (from `/awolve-signum:milestones`).

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-delete <project-id> <milestone-name-or-id>
```
