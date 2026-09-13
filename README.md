# Awolve Signum Plugin

Claude Code plugin for spec-driven development with [Awolve Signum](https://specs.awolve.ai).

## What it does

- **Auto-pulls** latest spec files when you start a Claude Code session
- **Auto-pushes** spec changes when you edit a spec file
- Keeps local spec files in sync so Claude Code always has the latest context

## Install

Run these as slash commands inside Claude Code:

```
/plugin marketplace add awolve/open-claude-plugins
/plugin install awolve-signum@awolve-open-claude-plugins
/reload-plugins
```

## Moving from awolve-spec

`awolve-signum` is the same plugin under its new name. `awolve-spec` stays in the marketplace so existing installs keep working.

- Install `awolve-signum` as above and reload. Login and `.claude/specs.md` are shared, so there is nothing to set up again.
- With both enabled, `awolve-spec`'s sync hooks do nothing, so each spec edit is pushed once. Its commands keep working under `/awolve-spec:` until you remove it.
- `awolve-spec` will be retired later. Until then, nothing changes for installs that keep it.

## Update

```
/plugin marketplace update awolve-open-claude-plugins
```

## Setup

1. **Login** — run `/awolve-signum:login` in Claude Code (Azure CLI or API key)
2. **Configure project** — create `.claude/specs.md` (shared) or `.claude/specs.local.md` (personal override):

```yaml
---
service_url: https://specs.awolve.ai
projects:
  - id: my-project
    path: ./specs
---
```

3. **Done** — specs will sync automatically on each session

## Commands

Run `/awolve-signum:help` for the full list, or see below:

### Setup & Sync

| Command | Description |
|---------|-------------|
| `/awolve-signum:login` | Authenticate (Azure CLI or API key) |
| `/awolve-signum:status` | Show sync status and auth info |
| `/awolve-signum:pull` | Pull latest spec files |

### Spec Writing

| Command | Description |
|---------|-------------|
| `/awolve-signum:req` | Write requirements.md — what to build and why |
| `/awolve-signum:design` | Write design.md — how to build it |
| `/awolve-signum:plan` | Write plan.md — implementation approach and task breakdown |
| `/awolve-signum:infra` | Enrich design.md with infrastructure specifications |
| `/awolve-signum:retro` | Document work after the fact from what was built |

### Features & Documents

| Command | Description |
|---------|-------------|
| `/awolve-signum:list-features` | List all features in a project |
| `/awolve-signum:create-feature` | Create a new feature |
| `/awolve-signum:rename-feature` | Rename a feature |
| `/awolve-signum:delete-feature` | Delete a feature and all its documents |
| `/awolve-signum:create-doc` | Add a document to an existing feature |
| `/awolve-signum:rename-doc` | Rename a document |
| `/awolve-signum:delete-doc` | Delete a document |
| `/awolve-signum:set-status` | Change feature or document status |

### Backlog & Bugs

| Command | Description |
|---------|-------------|
| `/awolve-signum:backlog` | List backlog items |
| `/awolve-signum:backlog-add` | Add a new idea or feature request |
| `/awolve-signum:bugs` | List open bugs |
| `/awolve-signum:my-daily` | What was assigned to you recently, across all your projects (the daily mail's list) |
| `/awolve-signum:my-weekly` | Everything open assigned to you, across all your projects (the weekly mail's list) |
| `/awolve-signum:bug` | Report a new bug |
| `/awolve-signum:edit-backlog-comment` | Edit your own comment on a backlog item |
| `/awolve-signum:edit-bug-comment` | Edit your own comment on a bug |
| `/awolve-signum:tags` | List a project's tags and how many items use each |
| `/awolve-signum:tag-create` | Create a tag (warns when a similar one exists) |

### Feedback users

| Command | Description |
|---------|-------------|
| `/awolve-signum:feedback-users` | List a project's feedback users (write-only credentials for in-app feedback widgets) |
| `/awolve-signum:feedback-user-create` | Create one; `feedback-user-update` / `feedback-user-delete` manage it |
| `/awolve-signum:feedback-key-create` | Mint its key, shown once; `feedback-key-revoke` is the kill switch |

## How it works

- **SessionStart hook** — pulls latest specs from the service, writes them to configured paths with version metadata in YAML frontmatter
- **PostToolUse hook** — detects edits to spec files, pushes changes as new versions with optimistic locking (409 on conflict)
- **No dependencies** — pure Python 3 stdlib, works everywhere
