---
description: List the features in a project, or the features someone is responsible for
argument-hint: [project-id] [--mine | --responsible EMAIL | --unassigned] [--all]
---

# /awolve-spec:list-features

List features from Signum, with who is responsible for each.

## Instructions

**One project:** if the user didn't provide a project ID, check the config for configured projects. If there's only one, use it. Otherwise ask which project.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py list-features <project-id>
```

Shows feature name, status, document count, the responsible person (email, or `-` when nobody is), and a summary of the backlog items delivering it. A responsible person marked `(inactive)` has been deactivated; `(no access)` means their access to the project has ended.

**By responsible person:** add one filter. Use this for "what am I responsible for", "what does Anna own", "which features have no owner".

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py list-features --mine
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py list-features --responsible <email>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py list-features --unassigned
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py list-features <project-id> --responsible <email-or-name>
```

- With no project ID, a filter covers every project configured on this machine, grouped by project.
- With a project ID, `--responsible` also matches a fragment of the person's name.
- `--mine`, `--responsible` and `--unassigned` can't be combined.
- A filtered list leaves out completed features; add `--all` to include them.

To change who is responsible, use `/awolve-spec:set-responsible`.
