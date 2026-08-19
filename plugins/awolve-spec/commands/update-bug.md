---
description: Update a bug's title, description, severity, assignee, tags, or timing (start/due/estimate)
---

# /awolve-spec:update-bug

Edit fields on an existing bug. Use this when the original framing has been overtaken by what actually shipped, or when triage uncovers a different severity than the reporter assigned.

## Instructions

Parse the user's argument. Expected forms:

- `<project> <bug-number> <fields>` — explicit project + bug ref + one or more field flags
- `<bug-number> <fields>` — use the configured project (only when exactly one is in config)

Bug references accept the short numeric form (with or without `#`).

At least one field flag is required: `--title`, `--description`, `--severity` (low|medium|high|critical), `--assignee <email>`, `--unassign`, or one of the tag flags below.

**Tags:** `--tags a,b` replaces the whole set; `--add-tag T` and `--remove-tag T` are repeatable deltas applied against whatever the bug wears right now; `--clear-tags` removes them all. `--tags` cannot be combined with `--add-tag`/`--remove-tag`. Tags must already exist on the project — an unknown name fails with `tag_not_found` and a list of close matches, because coining a tag is a separate, permission-gated act (`/awolve-spec:tag-create`).

**Timing (spec 023, internal users only):** `--start YYYY-MM-DD`, `--due YYYY-MM-DD`, `--estimate HOURS` (0–9999.99, at most two decimals), plus the valueless `--clear-start`, `--clear-due`, `--clear-estimate`. Start must not fall after due — checked against the bug's resulting state, so moving either date across the other is rejected. External users get `timing_forbidden`.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py update-bug <project-id> <bug-number> [--title T] [--description T] [--severity S] [--assignee EMAIL | --unassign] [--tags a,b | --add-tag T | --remove-tag T | --clear-tags]
```

Examples:

```bash
# Correct a stale description after the fix took a different shape than the original "Proposed fix"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py update-bug myoffice 1 --description "Reverted to plain-text default; HTML opt-in via --html. See <commit-sha>."

# Bump severity after triage
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py update-bug spec-service 15 --severity high

# Tighten the title
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py update-bug spec-service 15 --title "Add update-bug and bug-comment commands to specs-cli"

# Hand it to someone during triage — or hand it back
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py update-bug spec-service 15 --assignee michael.dovland@awolve.ai
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py update-bug spec-service 15 --unassign

# Label it during triage
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py update-bug spec-service 15 --add-tag regression
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py update-bug spec-service 15 --tags regression,billing
```

## Notes

- For status changes use `/awolve-spec:set-bug-status` — it emits a dedicated `status_change` audit event.
- **Assigning is a triage action and needs developer/admin rights on the project** (`bug:write:any`). A reporter may edit the wording of their own bug but can't put it on someone else's plate. The assignee must also be able to see the project: internal Awolve users always can, external users need project access first (`assignee_no_access` if not, `assignee_not_found` if they've never signed in).
- Assignment changes get their own audit event — "assigned bug #15 to …" — so a bug's ownership history reads as a sentence.
- `--assignee` and `--unassign` are mutually exclusive; omitting both leaves the assignee untouched.
- To attach resolution context (commit SHA, rollout notes) without rewriting the description, prefer `/awolve-spec:bug-comment` so the original report stays intact.
- **Tagging only needs the right to edit the bug**, so a reporter can label their own report; it is the tag *vocabulary* that is gated. Tag changes get their own audit event naming what went on and what came off.
- Each change is recorded in the audit log.
