---
description: Show where a programme stands — members, current phases, and milestones with progress and linked overdue
argument-hint: [programme-id]
---

# /awolve-signum:programme

Answer "where does this programme stand?" from one call: the programme's current phase, its milestones with progress, and each member project's current phase, next milestone and overdue count.

## Instructions

Determine the programme id. If the user names one, use it; otherwise list them with `/awolve-signum:programmes` and ask.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py programme <programme-id> [--json]
```

- A programme deadline's progress counts its own items **and** the items of every member deadline linked to it. With neither it says `not broken down yet`, never 0%.
- `!` lines flag a linked member deadline that is overdue, or dated after the programme deadline it delivers. The CLI never changes either date; say which one looks wrong and let the user decide.
- `--json` prints the full plan: the programme's own plan, `links`, and each member's plan under `members`.

Phases, milestones and items on a programme use the ordinary commands (`phase`, `milestones`, `milestone-create`, `backlog-add` …) with the programme's project id.
