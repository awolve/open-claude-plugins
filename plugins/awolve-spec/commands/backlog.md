---
description: List backlog items for a project (with optional view modes and filters)
---

# /awolve-spec:backlog

List backlog items (ideas, feature requests, todos) for a project, grouped the way the portal's tree shows them: epic → feature → item → sub-item.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask.

Run with optional flags:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog <project-id> [--epics|--flat] [--status STATUS] [--priority PRIORITY] [--assignee EMAIL|--unassigned] [--tag TAG ...] [--untagged]
```

### View modes (default: tree)

- **default (tree)** — one header per epic (`E3 Title [status] · N features · M items`), with the features under it (each followed by the items that deliver it) and then the items placed directly under the epic. Sub-items are indented under their item. Everything without an epic follows under `no epic`. Epics with nothing open still show their header, unless they are completed or archived.
- **`--epics`** — the project's epics only, as `/awolve-spec:epics` prints them. A roadmap-level overview.
- **`--flat`** — flat list, no grouping. Each row names its epic (`· E3`).

**A Signum service from before real epics** has no epic API. The CLI notices (the service answers 404) and falls back to the old grouping: items marked as epics are headers tagged `[EPIC]` with their children under them, and `--epics` lists those items.

### Filters

- **`--status STATUS`** — only show items with this status (`idea`, `planned`, `in_progress`, `ready_for_testing`, `completed`, `archived`). Naming `completed` or `archived` shows them even though the default list hides both.
- **`--all`** — every item regardless of status, including `completed` and `archived`.
- **`--json`** — print the filtered items as JSON (`number`, `status`, `priority`, `title`, `assignedToName`, `deployedStage`, `deployedUrl`, `parentId`, …) instead of the tree. For tooling; never scrape the text layout.
- **`--overdue`** — only items past their due date and not finished (spec 023).
- **`--late-to-start`** — only items past their start date that nobody has picked up yet (still `idea` or `planned`). An item that is both is found by either flag, though the list labels it `(OVERDUE)`.
- **`--priority PRIORITY`** — only show items with this priority (`low`, `medium`, `high`).
- **`--assignee EMAIL`** — only show items assigned to that person. Matches on email, or on a fragment of their name (`--assignee bjorn` works).
- **`--unassigned`** — only show items nobody owns.
- **`--tag TAG`** — only show items carrying that tag. Repeatable and OR-ed: `--tag billing --tag auth` shows items with either. Matches on slug or display name, so `--tag "Needs UX"` and `--tag needs-ux` are the same filter.
- **`--untagged`** — only show items with no tags at all. Combines with `--tag` as another OR arm, which answers "the ones I've labelled, plus the ones I haven't got to".

The default view filters out `completed` and `archived` items so you see active work only. Pass `--status completed` to see them explicitly.

An assignee or tag filter switches the output to flat view automatically: in tree view a matching sub-item would be hidden whenever its parent didn't match too, which silently under-reports what someone is carrying.

Omitting the project id runs the filter across every configured project — that's the way to answer "what is on my plate everywhere".

### Output format

Each row shows priority marker (`!!!` high, `!!` medium, `!` low), the item number (`#42`), the title, any tags as `#name`, the status, and the assignee as `· @Name` when the item has one. An item with sub-items shows how many, with their statuses:

```
  E1 User onboarding  [in_progress] · 1 feature · 4 items
    012 Signup flow  feature · specifying · 2 items
      [!!] #6 Email verification flow  #auth (1 sub-item: 1 idea)
           in_progress  · @Alex
        [!] #9 Resend the verification mail
             idea
    [!!!] #7 Agree data-retention period
         blocked
  E2 Payments  [idea] · 0 features · 0 items
  no epic
    [!!] #5 Future scope (23 sub-items: 23 idea)
         idea
```

On a service from before real epics, rows of items marked as epics are prefixed with `[EPIC]` and carry `· children: …` instead.

Highlight high-priority items. Mention that the same backlog can be viewed and managed in the portal at `specs.awolve.ai/portal/<project>` under the Backlog tab, with richer filtering, view-mode switching, and inline editing.

## Source filter

`--source widget` narrows the list to reports filed through a project's feedback user — an in-app widget, not a person with an account. The reporter shown on those rows is what the host app asserted; the feedback user's own name is the fallback. See `/awolve-spec:feedback-users`.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py backlog <project-id> --source widget
```
