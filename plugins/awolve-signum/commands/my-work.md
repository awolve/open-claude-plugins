---
description: Your own order of work across every project — the first item is your Now
---

# /my-work

Show a person's open bugs and items from every project, in their own order. The first one is their **Now**. Items nobody has placed by hand sit where the service's landing rule puts them: in progress first, then the soonest date (an item's own due date, else its milestone's), then priority, then the oldest.

## Instructions

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py my-work [--person EMAIL] [--json]
```

- **No `--person`:** your own order.
- **`--person EMAIL`:** someone else's, exactly as they see it.
- **`--json`:** the service's answer, `{ person, items }`. Each item has `rank` (1-based, the real place), `now`, `placed` (`hand` or `rule`), `projectId`, `number`, `kind`, `status`, `date`, `dateSource` (`own` or `milestone`) and `warning` (set when a dated item sits below a later date). It is for tooling, so never scrape the text layout.

Lead with the Now, then the next few items. Call out any warnings: a warning means an item with a date sits below one due later. If the list is empty, say there are no open items.

To change the order, use `/awolve-signum:order-move`. (At Awolve the portal's My work page shows the same order, with drag and drop.)

Needs a Signum service with personal work order (spec-service spec 053).
