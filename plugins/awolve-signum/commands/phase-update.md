---
description: Change a phase's name, dates or colour
argument-hint: [project-id] [phase]
---

# /awolve-signum:phase-update

Change one phase. Only that phase changes; phases may overlap. Internal users only.

## Instructions

Determine the project as usual. Name the phase by its name (any case) or its id; if two phases share a name, the CLI lists their ids and stops, so ask which one.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py phase-update <project-id> <phase-name-or-id> [--name "<name>"] [--start YYYY-MM-DD] [--end YYYY-MM-DD | --open-ended] [--color <colour> | --auto-color]
```

- `--open-ended` removes the end date.
- `--auto-color` removes a picked colour, so the phase is coloured by its place again.
- An end before the start is refused (`end_before_start`).
