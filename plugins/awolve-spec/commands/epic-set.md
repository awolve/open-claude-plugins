---
description: Put a feature or a backlog item under an epic, or take it out of one
argument-hint: [project-id] [#item | feature] [E<n> | none]
---

# /awolve-spec:epic-set

Move a feature or a backlog item under an epic (`E<n>`), or out of any epic (`none`).

## Instructions

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py epic-set <project-id> <target> <E<n> | none>
```

`<target>` is either:
- **an item**, written `#N` (quote it in a shell: `'#142'`), or
- **a feature**: its folder name (`012-onboarding`), `project/name`, or its number (`012` or `12`).

Examples:

```bash
# Feature 019 and every item delivering it go under E3
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py epic-set my-project 019 E3

# Item #142 directly under E2
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py epic-set my-project '#142' E2

# Take feature 019 out of its epic
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py epic-set my-project 019 none
```

## Rules the service enforces

An item has one epic, and where it comes from depends on where the item sits:

- **An item that delivers a feature takes the feature's epic.** Setting its epic is refused (`epic_inherited_from_feature`); the CLI names the feature and its epic. Move the feature instead, or unlink the item first (`backlog-update … --clear-feature`).
- **A sub-item takes its parent's epic** (`epic_inherited_from_parent`). Move the parent instead, or detach the sub-item (`backlog-set-parent … none`).
- The epic must exist and belong to the same project (`epic_not_found`, `epic_wrong_project`).
- Moving a feature needs the right to edit features in the project.

Pass the CLI's refusal on to the user as it is; it already says what to do instead. Don't retry with a different target unless the user agrees.

**A Signum service from before real epics** has no epic API: the CLI says so and changes nothing.
