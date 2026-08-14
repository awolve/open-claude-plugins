---
description: "[REMOVED in spec 023] Turn a backlog item into a feature — use create-feature + backlog-comment instead"
---

# /awolve-spec:promote-backlog — removed

This command was removed in spec-service **0.53.0** (spec 023). There is no
longer a hard link between a backlog item and a feature.

The old command created a feature, seeded a `spec.md`, and wrote the new
feature's id into `backlog_items.feature_id` — permanently. That link was 1:1,
had no undo, and forced the item's status to `planned` and left it there, so a
promoted item's stored status drifted out of date and the portal papered over
it by displaying the *feature's* status instead. In roughly a year it was used
four times, and three of those four ended up showing a status that disagreed
with the database.

## What to do instead

A backlog item that has been specced says so in a comment. Three existing
commands, nothing new to learn:

```bash
# 1. Create the feature (pick the next NNN yourself — no auto-numbering)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py create-feature <project> 024-some-feature

# 2. Add whichever documents the work needs
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py create-doc <project> 024-some-feature spec.md

# 3. Record the connection where a human will read it
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-comment <project> '#42' \
  "Specced as 024-some-feature"
```

Then set the item's status to whatever is actually true (`in_progress`,
`completed`, …) with `/awolve-spec:backlog-update --status`.

## Why this is better, not just simpler

- **One feature can cover several items**, and one big item can spawn several
  features. The old column could express neither.
- **Nothing to undo.** A comment can be edited or deleted; a foreign key
  written by a misclick could not.
- **The item's status stays the item's own.** It no longer silently reports a
  feature's progress as its own.
- **You name the feature.** The old slug generator mangled non-ASCII titles —
  `Beskrivningsfält för sektioner` became `beskrivningsf-lt-f-r-sektioner`, and
  an all-non-ASCII title produced a feature literally named `024-`.

## The column still exists

`backlog_items.feature_id` was kept, frozen, so an older service instance can
still `SELECT` it and the migration stayed purely additive. Four legacy rows
carry a value; nothing writes it, and no UI derives anything from it. Don't
wire it back up without revisiting spec 023.
