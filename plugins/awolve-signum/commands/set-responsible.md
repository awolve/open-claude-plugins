---
description: Set or clear the person responsible for a feature
argument-hint: [feature-id] [email | --unassign]
---

# /awolve-signum:set-responsible

Set or clear who is responsible for a feature — the one person who owns it. Shown in the portal's feature list and in `list-features`.

## Instructions

If the user didn't provide arguments, ask:
1. Which feature? (format: `project-id/001-feature-name`)
2. Who should be responsible? (their email), or should it be cleared?

Then run one of:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py set-responsible <feature-id> <email>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py set-responsible <feature-id> --unassign
```

If the user refers to a feature by name (e.g. "make Anna responsible for 002-user-roles"), resolve the project from config and local files to get the full `project-id/feature-name` ID. "Me" means the logged-in user's email (`/awolve-signum:status` shows it).

The person must be able to open the project and must have signed in to Signum at least once. Setting or clearing it needs the developer or admin role on the project. The CLI prints what to do when one of these is missing; pass that on to the user rather than retrying.
