---
description: Link a programme deadline to a member project's deadline that delivers it
argument-hint: [programme-id] [programme-deadline] [project-id:deadline]
---

# /awolve-spec:milestone-link

Link a programme deadline to a deadline in one of its member projects. The member's items stay in their own deadline; the programme deadline's progress counts them through the link. One member deadline may be linked from several programme deadlines. Internal users only.

## Instructions

Name the programme deadline by name or id, and the member deadline as `<project-id>:<deadline-name-or-id>`:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py milestone-link <programme-id> "<programme deadline>" <project-id>:"<member deadline>"
```

- Both ends must be deadlines; a date is refused (`milestone_is_date`).
- The second must be in a member project (`not_a_member_deadline`); add the project first with `programme-add`.
- Linking twice changes nothing.
- When the member deadline is dated after the programme deadline, the CLI says so. Neither date is changed.
