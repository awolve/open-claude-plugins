---
description: Take a project out of a programme (says first how many deadline links go with it)
argument-hint: [programme-id] [project-id]
---

# /awolve-spec:programme-remove

Take a project out of a programme. The links from the programme's deadlines to that project's deadlines are removed with it. The project's own plan is not changed. Internal users only.

## Instructions

First run it without `--yes`. It changes nothing and says how many deadline links would go:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py programme-remove <programme-id> <project-id>
```

Tell the user that count and ask. Only on a clear yes, run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py programme-remove <programme-id> <project-id> --yes
```
