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

References accept UUIDs or `#N` numeric form (with or without `#`).

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-depend <project-id> <item-id-or-#N> <blocker-id-or-#N>
```

Example — #251 cannot be done until the field in #256 exists:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog-depend my-project 251 256
```

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
- `Dependencies must be within the same project` — cross-project blocking would
  let one client's board stall another's, with neither side able to see why
- `That would make #A and #B wait for each other` — the cycle check. From either
  item's own page a mutual block reads as perfectly reasonable; it is only
  visible from outside, which is why it is refused at write time.

## When to use this

- Splitting an item and leaving the functional half waiting on the technical one
- Recording a sequencing constraint you would otherwise put in a comment nobody
  reads before picking the item up

To drop a dependency, use `/awolve-spec:backlog-undepend`.
