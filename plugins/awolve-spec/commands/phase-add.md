---
description: Add a phase to a project (a name, a start date, an optional end date and colour)
argument-hint: [project-id] [name]
---

# /awolve-spec:phase-add

Add a phase: a named stretch of time such as "Pilot" or "Wave 1". Phases may overlap, and adding one never changes another. Changing phases is for internal users only; anyone else gets `timing_forbidden`.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask. Ask for the name and start date if they were not given.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py phase-add <project-id> "<name>" --start YYYY-MM-DD [--end YYYY-MM-DD] [--color blue|teal|violet|amber|red|green|pink|slate]
```

- Without `--end` the phase is open-ended: it runs until someone sets an end.
- Without `--color` the phase is coloured by its place among the project's phases.

The CLI prints the phase and a link to the project's Plan tab.
