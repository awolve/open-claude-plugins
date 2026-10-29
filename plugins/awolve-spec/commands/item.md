---
description: Show one item of any kind by its number — kind, shared status, and a bug's bug number beside its item number
---

# /item

Show the full details of one item of any kind (implementation, bug or activity) by its number in the project's single series.

This needs a Signum server with item types and shared statuses. On an older one the command says so; use `/awolve-spec:view-backlog` or `/awolve-spec:view-bug` there.

## Instructions

Parse the user's argument. Expected forms:

- `<number>` — e.g. `74` or `#74`. Use the configured project if exactly one is in config; otherwise ask which project.
- `<project-id> <number>` — explicit project.

A bug keeps the number it had as a bug in every bug command (`/awolve-spec:view-bug`, `/awolve-spec:set-bug-status`…). When the user names a bug by that number ("Bug #1"), add `--bug` so the number is read as a bug number.

Then run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py item <project-id> <number> [--bug] [--json]
```

Show the result. For a bug, the `bug:` line is its bug number; mention both numbers when you refer to it. For a bug's screenshots, use `/awolve-spec:view-bug` with its bug number and `--images`.
