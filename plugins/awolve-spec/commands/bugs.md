---
description: List bugs for a project — open by default, any status on request
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
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py bugs <project-id> [--status STATUS | --all] [--assignee EMAIL|--unassigned] [--tag TAG ...] [--untagged]
```

Filters:
- **`--status STATUS`** — only bugs in exactly that status (`open`, `triaged`, `in_progress`, `ready_for_retest`, `resolved`, `closed`). Without it the list is open bugs only, which excludes `resolved` and `closed`; ask for those by name — "what did the tester sign off on a preview?" is `--status resolved`.
- **`--all`** — every bug regardless of status.
- **`--assignee EMAIL`** — only bugs assigned to that person (matches email, or a fragment of their name).
- **`--unassigned`** — only bugs nobody has picked up. Useful as a triage sweep.
- **`--tag TAG`** — only bugs carrying that tag. Repeatable and OR-ed; matches on slug or display name.
- **`--untagged`** — only bugs with no tags at all, which combines with `--tag` as another OR arm.

Omitting the project id runs across every configured project — that's how to answer "which bugs are mine, everywhere".

Show the results. Each row carries its tags as `#name` after the title, and the assignee as `· @Name` when there is one. If there are critical or high severity bugs, highlight them — and call out high-severity bugs sitting unassigned, since those are the ones nobody has picked up.

Also mention that bugs can be viewed in the portal at `specs.awolve.ai/portal/<project>/bugs`.
