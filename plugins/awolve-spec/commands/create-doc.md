---
description: Add a document to an existing feature
argument-hint: [project-id] [feature-name] [filename]
---

# /awolve-spec:create-doc

Add a new document to an existing feature, registered in Signum with sync frontmatter.

## Instructions

If the user didn't provide all arguments, ask:
1. Which project?
2. Which feature? (list folders in specs path if needed)
3. What filename? (e.g. `design.md`, `requirements.md`, `plan.md`, or a mockup `mockups/login.html`)

A mockup is a static HTML page under `mockups/` (lower case, no subfolders). Its sync header sits in an HTML comment at the top. The `mockup` skill says how to write one.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py create-doc <project-id> <feature-name> <filename>
```

The file is created locally with sync frontmatter. If the file already exists without frontmatter, frontmatter is added. From this point, the PostToolUse hook handles auto-push on edits.
