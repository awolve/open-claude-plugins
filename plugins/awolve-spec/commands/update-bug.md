---
description: Update a bug's title, description, severity, or assignee
---

# /awolve-spec:update-bug

Edit fields on an existing bug. Use this when the original framing has been overtaken by what actually shipped, or when triage uncovers a different severity than the reporter assigned.

## Instructions

Parse the user's argument. Expected forms:

- `<project> <bug-number> <fields>` — explicit project + bug ref + one or more field flags
- `<bug-number> <fields>` — use the configured project (only when exactly one is in config)

Bug references accept the short numeric form (with or without `#`).

At least one field flag is required: `--title`, `--description`, `--severity` (low|medium|high|critical), `--assignee <email>`, `--unassign`.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py update-bug <project-id> <bug-number> [--title T] [--description T] [--severity S] [--assignee EMAIL | --unassign]
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
```

## Notes

- For status changes use `/awolve-spec:set-bug-status` — it emits a dedicated `status_change` audit event.
- **Assigning is a triage action and needs developer/admin rights on the project** (`bug:write:any`). A reporter may edit the wording of their own bug but can't put it on someone else's plate. The assignee must also be able to see the project: internal Awolve users always can, external users need project access first (`assignee_no_access` if not, `assignee_not_found` if they've never signed in).
- Assignment changes get their own audit event — "assigned bug #15 to …" — so a bug's ownership history reads as a sentence.
- `--assignee` and `--unassign` are mutually exclusive; omitting both leaves the assignee untouched.
- To attach resolution context (commit SHA, rollout notes) without rewriting the description, prefer `/awolve-spec:bug-comment` so the original report stays intact.
- Each change is recorded in the audit log.
