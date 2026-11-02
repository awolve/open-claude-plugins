---
description: List programmes — projects that hold member projects and plan them on one Gantt
---

# /awolve-spec:programmes

List the programmes you can see. A programme is a project of kind `programme`: it has everything a project has (phases, milestones, items) and also a list of member projects, planned together on one Gantt. Programmes are visible to internal users only.

## Instructions

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py programmes [--json]
```

Each row shows the programme id, its name and client, and how many member projects it has. To see where one stands, use `/awolve-spec:programme <id>`.
