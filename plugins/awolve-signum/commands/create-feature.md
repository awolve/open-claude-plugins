---
description: Create a new feature in a project
argument-hint: [project-id] [feature-name]
---

# /awolve-signum:create-feature

Create a new feature in a project, registered in both the local filesystem and Signum.

## Instructions

If the user didn't provide arguments, ask:
1. Which project? (check `.claude/specs.md` or `.claude/specs.local.md` for configured projects)
2. What's the feature name? (kebab-case, e.g. `user-notifications`)

The script auto-assigns the next spec number (e.g. `004-user-notifications`).

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py create-feature <project-id> <feature-name> [--status STATUS] [--description TEXT] [--responsible EMAIL]
```

Default status is `specifying`. Use `--status idea` for placeholder features.

Optional `--description "One or two sentences…"` sets the feature's short description (visible on the portal list view). Can also be set later via `/awolve-signum:set-description`.

Optional `--responsible <email>` names the person responsible for the feature when it is created (also works with `--from-item`). They must be able to open the project and have signed in to Signum once, and setting it needs the developer or admin role on the project. Can also be set or changed later via `/awolve-signum:set-responsible`.

After creation, suggest next steps:
- `/awolve-signum:req` to write requirements
- `/awolve-signum:design` to write the design doc
