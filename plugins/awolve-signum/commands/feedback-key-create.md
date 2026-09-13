---
description: Mint an API key for a feedback user — printed once, for the app's backend secret store
---

# /awolve-signum:feedback-key-create

Creates a key for a feedback user. The plaintext is printed **once**; the service keeps only a hash. Up to 10 active keys per feedback user, which is what makes rotation possible: create the new key, switch the app, revoke the old one.

## Instructions

Parse `<project> <user-ref> [--label <text>]`. Label the key with where it lives (`prod container`, `staging slot`), so a later `feedback-users` listing says which one to revoke.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py feedback-key-create <project-id> <user-ref> --label "<where it lives>"
```

## Handling the key

- Show the user the command's output and tell them to store the key now. Do not paste it into a spec, a comment, a commit, or chat.
- It belongs in the app's backend secret store (at Awolve: the project's Key Vault, named in the project's SIGL). Never in page JavaScript.
- The key authenticates as the feedback user and can only create bugs, backlog items and attachments in this project. It cannot read anything.

Requires project admin access.
