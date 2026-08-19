---
description: Delete a tag, optionally removing it from every item that carries it
---

# /awolve-spec:tag-delete

Retire a tag from a project's vocabulary.

## Instructions

Determine the project (explicit argument, the single configured project, or ask). The tag can be named by slug, display name, or id.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-delete <project-id> <tag> [--force]
```

A tag nothing uses deletes immediately. A tag **in use** refuses and tells you how many items carry it:

```
specs: 'Billing' is applied to 14 item(s) — repeat with force to remove it from all of them
```

Show that count to the user and get an explicit go-ahead before re-running with `--force`. There is no undo: the tag comes off all fourteen items in one transaction, and re-creating the tag afterwards does not put it back.

### Examples

```bash
# Clean up an unused tag
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-delete spec-service spike

# You checked the count and meant it
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tag-delete spec-service billing --force
```

## Notes

- Run `/awolve-spec:tags` first to see usage counts — that is the honest way to decide whether a tag is dead.
- To consolidate rather than destroy: retag the items onto the tag you are keeping (`--remove-tag old --add-tag keeper` on each), then delete the now-unused one.
- The deletion is recorded in the audit log, including how many items it was detached from.
- Needs the developer or admin role on the project.
