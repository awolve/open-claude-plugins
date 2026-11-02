---
description: Remove the link between a programme deadline and a member deadline
argument-hint: [programme-id] [programme-deadline] [project-id:deadline]
---

# /awolve-signum:milestone-unlink

Remove a link made with `/awolve-signum:milestone-link`. Only the link goes; both deadlines and their items stay as they are. Internal users only.

## Instructions

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-unlink <programme-id> "<programme deadline>" <project-id>:"<member deadline>"
```

Removing a link that is not there changes nothing.
