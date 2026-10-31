---
description: Move one item in your own order of work (or a person's) — right after another item, or to the top as the Now
---

# /order-move

Move one item in a person's order, the list `/awolve-spec:my-work` shows. The whole list is saved as it looks after the move, so every item keeps the place it has then. Items that become assigned later land by the service's landing rule, but never above a Now that was placed by hand.

## Instructions

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py order-move <project-id> '#N' (--after <project>/#M | --top) [--person EMAIL]
```

- **`'#N'`** is the item to move, in `<project-id>`. Write `<other-project>/#N` to name an item in another project.
- **`--after <project>/#M`** puts it right after that item. **`--top`** makes it the Now. Give exactly one of them.
- **`--person EMAIL`** moves it in someone else's order. You need the right to edit the item.

Both items must be open and assigned to that person. If the order changed in the meantime, the command says so: run `my-work` again and retry.

Confirm with the user before moving an item in someone else's order. Report where the item ended up.

Needs a Signum service with personal work order (spec-service spec 053).
