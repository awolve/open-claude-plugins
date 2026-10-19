---
description: Everything open assigned to you — the same list as the weekly mail "My current things in Signum"
---

# /my-weekly

Show every open bug and backlog item assigned to you, and every open feature you are responsible for, across every project you can open. It is the same list as the weekly notification mail, "My current things in Signum", built by the same service code.

## Instructions

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py my-weekly [--json]
```

- **`--json`** — the service's rows (`projectName`, `kind`, `number`, `title`, `rank`, `status`, `dueDate`, `overdue`, `url`). `kind` is `feature`, `bug` or `backlog`; a feature's `rank` is empty and its `id` is the feature name. For tooling; never scrape the text layout.

Open means a bug that is not `resolved` or `closed`, and a backlog item or feature that is not `completed` or `archived`. The list is sorted like the mail: by project, then features, bugs, backlog; within each, overdue first, then due date, then number. Unlike the mail it has no 100-row cap, and it works whether or not the weekly mail is switched on.

Show the list grouped by project and call out anything overdue. If it is empty, say nothing is assigned to you right now.

Needs spec-service 0.127.0 or later; features are listed from 0.158.0.
