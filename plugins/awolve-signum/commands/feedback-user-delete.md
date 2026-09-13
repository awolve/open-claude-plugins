---
description: Delete a feedback user — revokes every key it holds; the reports it filed stay
---

# /awolve-signum:feedback-user-delete

Removes the feedback user from the project and revokes all its active keys in the same step. Bugs and backlog items it filed keep their reporter attribution and stay where they are.

## Instructions

Parse `<project> <user-ref>` (id, exact name, or a unique prefix). Confirm with the user before running — the app holding the key stops working immediately.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py feedback-user-delete <project-id> <user-ref>
```

To rotate a key without deleting the user, use `/awolve-signum:feedback-key-create` followed by `/awolve-signum:feedback-key-revoke`.

Requires project admin access.
