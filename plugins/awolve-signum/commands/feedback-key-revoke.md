---
description: Revoke one of a feedback user's keys — the kill switch for a leaked or rotated key
---

# /awolve-signum:feedback-key-revoke

Revokes one key. Every request the app makes with it fails with 401 from the next request on. The feedback user and its other keys are untouched.

## Instructions

Parse `<project> <user-ref> <key>` where `<key>` is the key id, a prefix of the id, or the key prefix shown by `/awolve-signum:feedback-users` (`sk_ab12cd…`).

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py feedback-key-revoke <project-id> <user-ref> <key-id-or-prefix>
```

If the reference matches more than one key the command lists them and stops; use the id.

## Rotation

1. `/awolve-signum:feedback-key-create` — mint the replacement.
2. Put the new key in the app's secret store and roll the app.
3. `/awolve-signum:feedback-key-revoke` — kill the old one.

Requires project admin access.
