---
description: Bug SLA report for a project and period — new bugs, time to acknowledged, handled, fixed and done, and what became of each
---

# /bug-report

How a project's bugs were handled over a period: how many came in, how long each waited before someone handled it, how long until it was fixed and done, and where it is now.

## Instructions

Work out the project the same way `/awolve-spec:bugs` does: the one the user names, the only configured project, or ask. Work out the period: two days, `YYYY-MM-DD`, both included and read as Stockholm days. "Last month" means the previous calendar month; ask if the period is unclear.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py bug-report <project-id> --from YYYY-MM-DD --to YYYY-MM-DD [--json]
```

What the numbers mean:

- **Which bugs:** every item that was a bug when it was filed in the period. A bug later turned into an implementation item or an activity still counts, shown as `now implementation (...)`.
- **Acknowledged:** the first move out of `new`, to any status, or the first kind change. The team's first response.
- **Handled:** the first move past `new` and `acknowledged`, or the first kind change. A bug triaged straight from `new` is acknowledged and handled at the same moment; one filed straight into `planned` or later is both at filing.
- **Fixed:** first reached `ready_for_testing` (shown to bug users as ready for retest). **Done:** first reached `completed`. A bug moved back after either is marked `reopened`; the times keep the first time.
- **Waiting:** a time in brackets is how long a still-open bug has waited so far.
- Times are calendar time from filing. No business hours.
- History starts 2026-04-12. Bugs filed before that have no times, and the report says so.

`--json` prints the service's answer unchanged (`summary`, `summary.bySeverity`, and `bugs` with each bug's times in seconds, outcome, kind changes and status history). Use it for any further counting; never scrape the text layout.

Show the summary first. Then call out the slowest bugs, bugs still waiting to be handled, and anything reopened.
