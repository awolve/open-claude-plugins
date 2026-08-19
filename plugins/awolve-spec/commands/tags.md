---
description: List a project's tags and how many backlog items and bugs wear each one
---

# /awolve-spec:tags

Show the tag vocabulary for a project. Tags are free-form labels applied to backlog items and bugs — one shared vocabulary per project, so a `regression` tag means the same thing on both.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py tags <project-id> [--json]
```

### Output format

Each row shows the tag, its colour, and how many items carry it, split between backlog and bugs. Tags are ordered by usage, so the ones that actually classify anything come first:

```
specs: 4 tag(s) in 'spec-service'

  #regression   red     3 backlog · 11 bug(s)
  #billing      amber   6 backlog · 1 bug(s)
  #needs-ux     violet  2 backlog · 0 bug(s)
  #spike        slate   unused
```

## Notes

- **Read this before coining a new tag.** The usage counts are how you spot near-duplicates worth merging by hand: a tag on two items sitting next to a similar tag on ninety is a mistake, not a distinction.
- An `unused` tag is safe to delete — nothing points at it.
- Creating, renaming, and deleting tags needs the developer or admin role (internal users of the service's own tenant always have it). *Applying* an existing tag only needs whatever lets you edit the item, so a bug reporter can label their own report without being able to invent labels. If the listing ends with a read-only note, that's the role you're missing.
- Tags are per project. Two projects can both have `billing`, and they are unrelated rows — there is no global tag list.
- The same vocabulary is managed in the portal under **Settings → Tags**, which also offers colour swatches and inline rename.
