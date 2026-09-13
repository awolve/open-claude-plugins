---
description: Create a feedback user on a project — the write-only credential an app's backend uses to file its users' bugs and ideas
---

# /awolve-spec:feedback-user-create

Creates a feedback user: a portal user of its own type, bound to one project, with one role (`feedback`) and no login. Its API keys may only create bugs, create backlog items, and attach files to those reports, in that project. Everything else is refused before any route runs.

## Instructions

Parse the argument as `<project> <name>` (the name may contain spaces). Name it after the app and environment so a key's purpose is obvious later: `Medvind app (production)`, `Field sales staging`.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py feedback-user-create <project-id> <name>
```

The command prints the new user's id and the next step. A feedback user starts with no key; mint one with `/awolve-spec:feedback-key-create`.

## What to tell the user

- The key goes in the app's **backend** secret store (Key Vault, environment). Never in page JavaScript — anything the browser sends, anyone with devtools can copy.
- The app forwards reporter name and email from its own session when it has one; anonymous reports are fine. Signum shows those fields as free text and never links them to a portal account.
- Two feedback users on one project (production and staging) are normal: separate keys, separate limits.
- The host-app side of the contract — the proxy endpoint, the payload, the errors — is documented with Signum (at Awolve: `operations/tools/signum/shared/feedback-contract.md`).

Requires project admin access.
