---
description: Upload a binary file as an attachment to a feature, bug, or backlog item
argument-hint: <file-path> [<project-id>/<feature-name> | --bug <project> <#N> | --backlog <project> <#N>]
---

# /awolve-spec:attach

Upload a local binary file (image, PDF, Excel, etc.) as an attachment. Three target entities are supported: **feature** (default), **bug**, and **backlog item**. The file is stored in Azure Blob Storage via the spec service. Feature attachments are mirrored back to every team member's local feature folder on the next `/awolve-spec:pull`; bug + backlog attachments live only in the portal/server.

## When to use

- You have a mockup, PDF, Excel, or other binary file that belongs to a **spec feature** and should be shared with the team
- You need to **add a screenshot to a bug** after creation (bug-create supports `--attach` for the initial screenshots; `attach` adds more later)
- You want to **pin a reference document to a backlog item** while it's still being scoped

## Instructions

Parse `$ARGUMENTS`. The first arg is always the local file path. The remainder selects the target:

| Form | What it does |
|------|--------------|
| `attach <file>` | Infer feature from the file's path (file must live inside a configured specs directory, under a feature subfolder) |
| `attach <file> <project-id>/<feature-name>` | Attach to a feature explicitly |
| `attach <file> --bug <project-id> <bug-#N>` | Attach to an existing bug |
| `attach <file> --backlog <project-id> <backlog-#N>` | Attach to a backlog item |

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py attach $ARGUMENTS
```

## Notes

- Any content type accepted (images render inline in the portal, other files download)
- Uploading a file with the same name on the same entity replaces the existing attachment automatically (per bug #8 fix) — no duplicate accumulation
- Feature attachments sync to disk on the next `/awolve-spec:pull`; bug/backlog attachments do not
- Use `/awolve-spec:list-attachments`, `/awolve-spec:download-attachment`, and `/awolve-spec:delete-attachment` to inspect or remove attachments after upload

If the user is not authenticated, tell them to run `/awolve-spec:login` first.
