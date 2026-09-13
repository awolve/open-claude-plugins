---
description: List a project's feedback users — the credentials an app's backend holds so its users can file bugs and ideas
---

# /awolve-signum:feedback-users

A **feedback user** is a project-scoped, write-only credential. An application's backend holds its key so the app's own users can file bugs and ideas into the project from an in-app widget, without any of them holding a key. The key can create bugs, create backlog items and attach files to what it created — nothing else, no reads.

## Instructions

Determine the project. If the user specifies one, use it; if exactly one project is configured, use that; otherwise ask.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py feedback-users <project-id>
```

Pass `--json` for the raw rows.

### Output

For each feedback user: name, id, its synthetic email, the limits in force (with "(defaults)" when none are set), the origin allowlist ("any" when empty), and every active key with its prefix, label, short id and last use. A user with no key is called out; create one with `/awolve-signum:feedback-key-create`.

Requires project admin access (Awolve internal users, or an admin on the project).

## Related

- `/awolve-signum:feedback-user-create`, `/awolve-signum:feedback-user-update`, `/awolve-signum:feedback-user-delete`
- `/awolve-signum:feedback-key-create`, `/awolve-signum:feedback-key-revoke`
- `bugs --source widget` / `backlog --source widget` to list what came in through a widget
