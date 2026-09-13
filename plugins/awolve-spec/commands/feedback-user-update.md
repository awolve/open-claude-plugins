---
description: Rename a feedback user or set its abuse controls — origin allowlist and per-minute / per-hour rate limits
---

# /awolve-spec:feedback-user-update

The two controls a project admin has over a public write surface, plus the name.

## Instructions

Parse `<project> <user-ref>` plus any of:

- `--name <text>` — display name
- `--origins a.example.com,https://b.example.com` — origin allowlist; `none` (or `any`) clears it. With a list set, a report must carry a `pageUrl` whose origin is on the list; an empty list accepts any origin.
- `--per-minute <N>` / `--per-hour <N>` — rate limits for the key as a whole (defaults 30 and 300); `default` puts the default back.

`<user-ref>` is the feedback user's id, exact name, or a unique prefix of either.

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py feedback-user-update <project-id> <user-ref> [--name N] [--origins a,b|none] [--per-minute N|default] [--per-hour N|default]
```

The command prints the user as it now stands.

## When to use

- A launch day: raise the limits for the day, put them back after.
- A key that may have leaked but cannot be rotated this minute: tighten the origin allowlist and drop the limits until you can revoke.
- Per-user throttling is the host app's job — Signum only knows the key, not which of the app's users is sending.

Requires project admin access.
