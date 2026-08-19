---
description: Rename, recolour, or re-describe a tag without disturbing what it is applied to
---

# /awolve-spec:tag-update

Edit a tag. Everything it is already applied to keeps it — the tag row is the identity, the name is a label on it, so fixing `Fronted` to `Frontend` fixes it on all forty items at once.

## Instructions

Determine the project (explicit argument, the single configured project, or ask). The tag can be named by slug, display name, or id.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-update <project-id> <tag> [--name N] [--color C] [--description D] [--force]
```

At least one of `--name`, `--color`, `--description` is required. Colours: `slate`, `blue`, `teal`, `green`, `amber`, `orange`, `red`, `pink`, `violet`.

### Examples

```bash
# Fix a typo everywhere at once
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-update spec-service fronted --name "Frontend"

# Make the urgent one look urgent
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-update spec-service regression --color red

# Say what it means
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-update spec-service spike --description "Timeboxed investigation, not a commitment"
```

## Notes

- Renaming into a name that is already taken fails with `tag_slug_taken` — there is no merge in this version. To consolidate two tags by hand: retag the items off the loser (`--remove-tag old --add-tag keeper`), then `/awolve-spec:tag-delete` the empty one.
- Renaming into something merely *similar* triggers the same nudge as creating a near-duplicate; repeat with `--force` when you meant it.
- Changing only the capitalisation or punctuation of a name keeps the same slug, so nothing else moves.
- Needs the developer or admin role on the project.
