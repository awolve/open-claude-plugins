---
description: List open bugs for a project
---

# /bugs

List open bugs for a project.

## Instructions

First determine which project to show bugs for. If the user specifies one, use it. Otherwise:
- Check the specs config for configured projects
- If only one project, use that
- If multiple, ask which one

Then run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py bugs <project-id> [--assignee EMAIL|--unassigned]
```

Filters:
- **`--assignee EMAIL`** — only bugs assigned to that person (matches email, or a fragment of their name).
- **`--unassigned`** — only bugs nobody has picked up. Useful as a triage sweep.

Omitting the project id runs across every configured project — that's how to answer "which bugs are mine, everywhere".

Show the results. Each row carries the assignee as `· @Name` when there is one. If there are critical or high severity bugs, highlight them — and call out high-severity bugs sitting unassigned, since those are the ones nobody has picked up.

Also mention that bugs can be viewed in the portal at `specs.awolve.ai/portal/<project>/bugs`.
