---
description: What was assigned to you recently — the same list as the daily notification mail
---

# /my-daily

Show the bugs and backlog items assigned to you recently, across every project you can open. It is the same list the daily notification mail sends, built by the same service code, so the two never disagree.

## Instructions

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py my-daily [--since DATE] [--kind bug|backlog] [--json]
```

- Without `--since` the window is the daily mail's: from 07:00 (Stockholm time) on the previous weekday until now, so on a Monday it covers the weekend.
- **`--since DATE`** — a date (`2026-09-01`) or an ISO date-time; at most 31 days back.
- **`--kind bug|backlog`** — only bugs, or only backlog items.
- **`--json`** — the service's rows (`eventId`, `assignedAt`, `projectName`, `kind`, `number`, `title`, `rank`, `assignerName`, `url`). For tooling; never scrape the text layout.

The rules are the mail's: an item is listed when someone else assigned it to you in the window and it is still assigned to you, not deleted, in a project you can open. Unlike the mail, the command ignores the daily-mail switches in your notification settings — asking is the switch.

Show the list grouped by project, with who assigned each item. If it is empty, say nothing new was assigned in the window.

Needs spec-service 0.127.0 or later.
