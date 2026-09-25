---
description: Make a backlog item wait for another one to finish (sets it Blocked)
---

# /awolve-spec:backlog-depend

Record that one item cannot start until another is done. The service sets the
waiting item's status to `blocked` and clears it again when the last blocker
reaches `completed` or `archived`.

## Instructions

Parse the user's argument. Expected forms:

- `<project> <item> <blocker>` — explicit project + both refs
- `<item> <blocker>` — use the configured project (only one)

References accept UUIDs or `#N` numeric form (with or without `#`). The blocker
may be in **another project** you can read: write it as `<other-project>#N`.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-depend <project-id> <item-id-or-#N> <blocker-id-or-#N-or-project#N>
```

Example — #251 cannot be done until the field in #256 exists:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-depend my-project 251 256
```

Example — #88 in the web app waits for #12 in the API project:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-depend web-app 88 api#12
```

## Across projects

- You can only link to an item in a project you can read. A blocker you cannot
  see gives the same error as one that does not exist.
- People on the waiting item's project who cannot read the blocker's project
  still see that the item is blocked, by what project, and that work's status —
  but not its number or title. `view-backlog` shows it as `(an item in <Project>)`.
- Finishing the blocker releases the waiting item exactly as within one project.

Then show the result with `/awolve-spec:view-backlog`, which prints both
directions — `depends on:` with each blocker's own status, and `blocking:` for
what is waiting on this one.

## Status is the blocked state

There is no separate "blocked" flag to drift out of step with the status. That
has two consequences worth knowing before you set a status by hand:

- Adding a dependency **moves** the item to `blocked` and remembers what it was,
  so removing the dependency puts the old status back.
- `backlog-update --status blocked` works on an item with no dependencies. On an
  item that *has* an unfinished dependency, any other status you set will be
  overridden the next time the graph is recomputed.

## Errors the API returns

- `dependsOnId is required` — the blocker reference did not resolve
- `An item cannot depend on itself`
- `No access to that project, or the item does not exist.` — deliberately one
  message for both, so it reveals nothing about projects you cannot see
- `That would make #A and #B wait for each other` — the cycle check, which
  follows links across projects (the message then names both projects). From
  either item's own page a mutual block reads as perfectly reasonable; it is
  only visible from outside, which is why it is refused at write time.

## When to use this

- Splitting an item and leaving the functional half waiting on the technical one
- Recording a sequencing constraint you would otherwise put in a comment nobody
  reads before picking the item up

To drop a dependency, use `/awolve-spec:backlog-undepend`.
