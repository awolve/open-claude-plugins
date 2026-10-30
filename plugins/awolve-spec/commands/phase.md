---
description: Show a project's current phase(s), or every phase with its dates
argument-hint: [project-id]
---

# /awolve-spec:phase

Show which phase a project is in. A phase is a named stretch of time the project chose ("Pilot", "Wave 1", "UAT") with a start date and an optional end date. A project has none until someone adds one, and phases may overlap, so there can be no current phase, one, or several.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py phase <project-id> [--all] [--json]
```

- Without flags: the current phase(s) and their dates, or that there is none today.
- `--all` also lists every phase, with `*` beside the current ones, its state (planned, in_progress, completed) and a colour if one was picked.
- `--json` prints `{current, phases}` for tooling.

A phase sets no rules: any kind of work can be created and planned in any phase. Say which phase the project is in when it helps; don't refuse or hold back work because of it.

**A Signum service without phases** answers that it has none yet; say so rather than retrying.
