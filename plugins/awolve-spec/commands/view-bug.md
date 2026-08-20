---
description: Show full details of a single bug — description, severity, repro steps
---

# /view-bug

Fetch the full details of a single bug by its short number (the `#N` shown by `/awolve-spec:bugs`).

## Instructions

Parse the user's argument. Expected forms:

- `<bug-number>` — e.g. `5` or `#5`. Use the configured project if exactly one is in config; otherwise ask which project.
- `<project-id> <bug-number>` — explicit project.

Then run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py view-bug <project-id> <bug-number>
```

Add `--json` if the user asks for machine-readable output.

## Screenshots

Most bug reports carry one. They arrive two ways — pasted inline into the description as a data URI, or uploaded as an attachment — and neither can be read from a terminal on its own.

**When the output reports any image or attachment, re-run with `--images` and then open the files it writes.** Do this without being asked: a screenshot is usually the clearest statement of the defect, and reasoning about a bug from its prose while a picture of it sits unopened is guesswork.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py view-bug <project-id> <bug-number> --images
```

The files land in a temp directory and their absolute paths are printed; read them as images. Pass a directory after `--images` to choose where they go. Non-image attachments are saved too.

Show the result — including the `assignee` line, which reads `(unassigned)` when nobody owns it yet. If the bug description contains a proposed fix, offer to apply it. Do not apply without confirmation.
