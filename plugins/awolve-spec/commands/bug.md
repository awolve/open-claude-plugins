---
description: Report a new bug
---

# /bug

Report a new bug for a project.

## Instructions

Gather these from the user:
1. **Project** — which project? Check config for options. If only one, use it.
2. **Title** — short summary of the bug (required)
3. **Description** — detailed description of what went wrong (required). Supports markdown.
4. **Severity** — low, medium (default), high, or critical
5. **Tags** (optional) — if the user labels the report ("this is another billing one"), pass `--tags billing`, comma-separated for several. The tags must already exist on the project: run `/awolve-spec:tags` to see them, `/awolve-spec:tag-create` to coin one first. Tags can also be added after the fact with `/awolve-spec:update-bug --add-tag`.
6. **Screenshots** — if the user pasted a screenshot in the conversation, save it to a temp file and attach it

To attach images, use `--attach`:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py bug "<project-id>" "<title>" "<description>" "<severity>" --attach /path/to/screenshot.png [--tags a,b]
```

Multiple images: add `--attach <path>` for each one. Images are base64-encoded into the bug description.

If the user pastes a screenshot in the conversation:
1. The image is available as a file — check if it was saved to a temp path
2. If so, attach it with `--attach`
3. If not available as a file, mention that screenshots can be added via the portal

After creating, show the bug number and portal link.
