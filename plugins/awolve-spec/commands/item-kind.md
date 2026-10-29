---
description: Change an item's kind (implementation, bug, activity) — it keeps its number; internal users only
---

# /item-kind

Change an item's kind, for example a bug that turns out to be a feature request, or an activity that turns out to need code.

The item keeps its number and history. Its status moves to the nearest one the new kind has (an activity has no `ready_for_testing`). Fields the new kind does not use, such as a bug's severity and repro steps, are kept hidden and come back if the kind is changed back. Only internal users may change a kind.

This needs a Signum server with item types and shared statuses. On an older one the command says so.

## Instructions

Parse the user's argument. Expected forms:

- `<number> <kind>` — e.g. `74 implementation`. Use the configured project if exactly one is in config; otherwise ask which project.
- `<project-id> <number> <kind>` — explicit project.

`<kind>` is `implementation`, `bug` or `activity`. Add `--bug` when the number is a bug number ("Bug #1") rather than an item number.

Changing to `bug` needs a description; if the item has none, the command says so — add one with `/awolve-spec:backlog-update` first.

Then run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py item-kind <project-id> <number> <kind> [--bug]
```

Report the change, including the status move if the output shows one.
