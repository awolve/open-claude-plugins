---
description: Add a new idea or feature request to the project backlog (optionally under an epic, or as a sub-item of another item)
---

# /awolve-spec:backlog-add

Add a new backlog item (idea, feature request, todo) to a project. An item can be filed directly under an epic (`--epic E<n>`), or as a sub-item of any top-level item (`--parent #N`). Epics themselves are created with `/awolve-spec:epic-create`, not with this command.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one is configured, use that; otherwise ask.

Ask the user for:
- **Title** (required) — short description
- **Description** (optional) — detail about what and why
- **Priority** (optional, default: `medium`) — `low`, `medium`, or `high`
- **Epic** (optional) — if the user names an epic to file it under ("under E3", "in the onboarding epic"), pass `--epic E<n>`. `/awolve-spec:epics` lists them with their numbers.
- **Parent item** (optional) — if the user references an existing item to nest this under ("as a sub-item of #4"), pass `--parent <id-or-#N>`. A sub-item takes its parent's epic, so `--parent` and `--epic` don't combine.
- **Assignee** (optional) — if the user names someone to own it ("assign it to Michael"), pass `--assignee <email>`. Leave it off otherwise; unassigned is a perfectly good state for an idea.
- **Tags** (optional) — if the user labels it ("this is a billing thing"), pass `--tags billing` (comma-separated for several). The tags must already exist on the project; run `/awolve-spec:tags` to see them and `/awolve-spec:tag-create` to coin one first.

Then run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add <project-id> "<title>" "<description>" <priority> [--parent <id-or-#N> | --epic E<n>] [--assignee <email>] [--tags a,b]
```

Examples:

```bash
# Top-level item
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add my-project "Improve onboarding" "" high

# Filed directly under epic E3
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add my-project "Welcome screen copy" "" medium --epic E3

# Sub-item of item #4
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add my-project "Welcome screen copy" "" medium --parent 4

# Assigned on creation
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add my-project "Welcome screen copy" "" medium --assignee michael.dovland@awolve.ai

# Labelled on creation (the tags must already exist)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-add my-project "Welcome screen copy" "" medium --tags onboarding,"Needs UX"
```

`--assignee` takes an email. The person must be able to see the project — internal Awolve users always can; external users need project access first, or the create fails with `assignee_no_access`. Assignment can also be added later with `/awolve-spec:backlog-update --assignee`.

`--parent` accepts either a UUID or a numeric `#N` reference (with or without the `#`) to any top-level item. The service rejects:
- A parent that doesn't exist or belongs to a different project (`parent_not_found`, `parent_wrong_project`)
- A parent that itself has a parent (`parent_must_be_top_level`) — one level of sub-items only
- On a Signum service from before real epics: a parent that isn't marked as an epic (`parent_not_an_epic`). Newer services accept any top-level item.

`--epic` takes an epic number such as `E3`. The service rejects an epic that doesn't exist or belongs to another project (`epic_not_found`, `epic_wrong_project`). On a service from before real epics, the CLI says it has none yet and creates nothing.

The old valueless `--epic` (which created the item itself as an epic) is gone; the CLI refuses it and points to `/awolve-spec:epic-create`.

If you're adding several related items in one session, consider proposing an epic for them (`/awolve-spec:epic-create`, then `--epic E<n>` on each item), or one item with the rest as its sub-items via `--parent` — either way the user gets a natural tree in the portal.

Confirm the item was created. Mention that `/awolve-spec:backlog-update --status` flips its status as it moves through the workflow, and that if it grows into something that needs a spec, `/awolve-spec:req <project-id> <item-number>` creates a feature from it and links the item as the one that delivers it. To link it to a feature that already exists: `/awolve-spec:backlog-update <project-id> <item-number> --feature <feature-name>`.
