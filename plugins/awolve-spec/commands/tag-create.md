---
description: Create a tag for a project (nudges you toward an existing tag when one is close)
---

# /awolve-spec:tag-create

Coin a new tag on a project. Tags label backlog items and bugs out of one shared per-project vocabulary.

## Instructions

Determine the project (explicit argument, the single configured project, or ask).

**Look before you create.** Run `/awolve-spec:tags` first, or read the suggestions the service returns — most "new" tags are a re-spelling of one that already exists, and a split vocabulary is worse than a slightly wrong name.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-create <project-id> <name> [--color C] [--description D] [--force]
```

Colours: `slate`, `blue`, `teal`, `green`, `amber`, `orange`, `red`, `pink`, `violet`. Omit `--color` and one is picked from the name, so the same tag name always lands on the same colour.

### The near-duplicate nudge

If something close already exists, the command **creates nothing** and exits with status 2:

```
specs: not creating 'Frontend Work' — a similar tag already exists
  similar tags already exist:
    #frontend  (same words)
  reuse one of those, or repeat with --force to create it anyway
```

When you see this, stop and ask the user rather than immediately re-running with `--force`. Reusing the existing tag is almost always right; `--force` is for the case where the near-match genuinely means something else.

### Examples

```bash
# Ordinary create
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-create spec-service "Regression"

# Pick the colour and explain what it is for
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-create spec-service "Needs UX" --color violet --description "Blocked on a design decision"

# You looked at the suggestions and they are a different thing
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-create spec-service "auth-ui" --force
```

## Notes

- Tag identity is the slug: lowercase, punctuation and spaces folded to hyphens. `Needs UX`, `needs-ux` and `needs_ux` are the same tag, and creating one when it already exists is a no-op that reports the existing tag rather than an error.
- Names are at most 32 characters and must contain at least one letter or digit.
- Creating a tag needs the developer or admin role on the project.
- To apply a tag once it exists: `/awolve-spec:backlog-update --add-tag` or `/awolve-spec:update-bug --add-tag`, or the picker on any item in the portal.
