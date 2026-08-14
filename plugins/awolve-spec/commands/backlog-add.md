---
description: Add a new idea or feature request to the project backlog (optionally as a child of an epic)
---

# /awolve-spec:backlog-add

Add a new backlog item (idea, feature request, todo) to a project. Spec 013 added optional parent linkage so an item can be created as a child of an existing epic.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one is configured, use that; otherwise ask.

Ask the user for:
- **Title** (required) — short description
- **Description** (optional) — detail about what and why
- **Priority** (optional, default: `medium`) — `low`, `medium`, or `high`
- **Parent epic** (optional) — if the user references an existing item to nest this under (e.g. "add as a child of #4" or "under the onboarding epic"), pass `--parent <id-or-#N>`
- **Assignee** (optional) — if the user names someone to own it ("assign it to Michael"), pass `--assignee <email>`. Leave it off otherwise; unassigned is a perfectly good state for an idea.

Then run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add <project-id> "<title>" "<description>" <priority> [--parent <id-or-#N>] [--epic] [--assignee <email>]
```

Examples:

```bash
# Top-level item
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add my-project "Improve onboarding" "" high

# Create an empty epic (placeholder for future children)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add my-project "User onboarding" "" high --epic

# Child of epic #4
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add my-project "Welcome screen copy" "" medium --parent 4

# Assigned on creation
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add my-project "Welcome screen copy" "" medium --assignee michael.dovland@awolve.ai
```

`--assignee` takes an email. The person must be able to see the project — internal Awolve users always can; external users need project access first, or the create fails with `assignee_no_access`. Assignment can also be added later with `/awolve-spec:backlog-update --assignee`.

`--parent` accepts either a UUID or a numeric `#N` reference (with or without the `#`). The CLI resolves it server-side and rejects:
- A parent that doesn't exist or belongs to a different project (`parent_not_found`, `parent_wrong_project`)
- A parent that itself has a parent (`parent_must_be_top_level`)
- **A parent that isn't marked as an epic** (`parent_not_an_epic`) — only items created with `--epic` (or marked Epic in the portal) can have children

`--epic` and `--parent` are **mutually exclusive** — an epic is always top-level.

If you're adding several related items in one session, consider proposing one as the epic (with `--epic`) and the rest as children pointing at it via `--parent` — that way the user gets a natural tree view in the portal Backlog tab.

Confirm the item was created. Mention they can spec it later with `/awolve-spec:create-feature` and record the link with `/awolve-spec:backlog-comment` (there is no promote action — see spec 023), and that `/awolve-spec:backlog-update --status` flips its status as it moves through the workflow.
