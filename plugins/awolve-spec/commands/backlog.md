---
description: List backlog items for a project (with optional view modes and filters)
---

# /awolve-spec:backlog

List backlog items (ideas, feature requests, todos) for a project. Spec 013 added one level of optional epic→child nesting and view modes.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask.

Run with optional flags:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog <project-id> [--epics|--flat] [--status STATUS] [--priority PRIORITY] [--assignee EMAIL|--unassigned] [--tag TAG ...] [--untagged]
```

### View modes (default: tree)

- **default (tree)** — items grouped by epic. Top-level items render at depth 0; their children appear indented underneath. Standalone items (no parent, no children) render at the top level too.
- **`--epics`** — show only items explicitly marked as epics (`isEpic = true`), including empty ones. Useful for a roadmap-level overview.
- **`--flat`** — flat list, no grouping (legacy behavior).

### Filters

- **`--status STATUS`** — only show items with this status (`idea`, `planned`, `in_progress`, `ready_for_testing`, `completed`, `archived`).
- **`--overdue`** — only items past their due date and not finished (spec 023).
- **`--late-to-start`** — only items past their start date that nobody has picked up yet (still `idea` or `planned`). An item that is both is found by either flag, though the list labels it `(OVERDUE)`.
- **`--priority PRIORITY`** — only show items with this priority (`low`, `medium`, `high`).
- **`--assignee EMAIL`** — only show items assigned to that person. Matches on email, or on a fragment of their name (`--assignee bjorn` works).
- **`--unassigned`** — only show items nobody owns.
- **`--tag TAG`** — only show items carrying that tag. Repeatable and OR-ed: `--tag billing --tag auth` shows items with either. Matches on slug or display name, so `--tag "Needs UX"` and `--tag needs-ux` are the same filter.
- **`--untagged`** — only show items with no tags at all. Combines with `--tag` as another OR arm, which answers "the ones I've labelled, plus the ones I haven't got to".

The default view filters out `completed` and `archived` items so you see active work only. Pass `--status completed` to see them explicitly.

An assignee or tag filter switches the output to flat view automatically: in tree view a matching child would be hidden whenever its epic didn't match too, which silently under-reports what someone is carrying.

Omitting the project id runs the filter across every configured project — that's the way to answer "what is on my plate everywhere".

### Output format

Each row shows priority marker (`!!!` high, `!!` medium, `!` low), the item number (`#42`), the title, any tags as `#name`, the status, and the assignee as `· @Name` when the item has one. Epic rows are prefixed with `[EPIC]` and include a child status histogram inline; empty epics (no children yet) show `· (no items yet)`:

```
  [!!] #5 [EPIC] User onboarding · children: 2 idea · 1 in_progress · 3 completed
       in_progress
    [!!] #6 Email verification flow  #auth #needs-ux
         in_progress  · @Michael Dovland
    [!] #7 Welcome screen copy
         completed
  [!!] #8 [EPIC] Payments · (no items yet)
       idea
```

Highlight high-priority items. Mention that the same backlog can be viewed and managed in the portal at `specs.awolve.ai/portal/<project>` under the Backlog tab, with richer filtering, view-mode switching, and inline editing.
