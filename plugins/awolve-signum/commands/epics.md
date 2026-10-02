---
description: List a project's epics (number, title, status, owner, feature and item counts, due date)
argument-hint: [project-id]
---

# /awolve-signum:epics

List the epics of a project. An epic sits one level above features: project → epic → feature → item (→ sub-items). Epics are numbered per project and written `E<n>` (e.g. `E3`).

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py epics <project-id> [--all] [--json]
```

- `--all` includes archived epics (hidden by default).
- `--json` prints the service's epic summaries (counts, status counts, timing rollup) for tooling.

Each row: `E1 Title  status · N features · M items · @Owner · due YYYY-MM-DD`. The item count covers every item under the epic, including those under its features.

**A Signum service from before real epics** answers 404. The CLI says so and lists the items marked as epics (the old kind) instead. Tell the user these are old-style epics; an item with sub-items can be turned into a real epic with `/awolve-signum:epic-promote` once the service has real epics.

Related: `/awolve-signum:epic-create`, `/awolve-signum:epic-set`, `/awolve-signum:backlog` (the tree grouped by epic).
