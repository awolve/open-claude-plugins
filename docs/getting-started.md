# Getting started with Awolve Signum in Claude Code

For people outside Awolve who have been invited to a project in [Awolve Signum](https://specs.awolve.ai) and use Claude Code.

**Easiest way through:** open Claude Code in an empty folder (or the repo you'll work in) and say:

> Read https://github.com/awolve/open-claude-plugins/blob/main/docs/getting-started.md and set me up for Signum project `<project-id>`.

Claude can do most of it. Three steps need you: signing in to the portal, creating the API key, and typing the slash commands that install the plugin.

## What you need

- **An invite to a Signum project.** Your Awolve contact gives you the **project id** (e.g. `acme-data-platform`) and your roles.
- **Claude Code.**
- **Python 3 on your PATH as `python3`.** The plugin is stdlib-only; nothing to `pip install`.

## 1. Sign in to the portal once

Go to https://specs.awolve.ai and sign in with the address you were invited with: **Sign in with Microsoft** if your organisation uses Microsoft 365, otherwise email and password.

Check that your project is listed. If it isn't, ask your Awolve contact to check the invite; nothing below will work until it is.

## 2. Create an API key

In the portal, open **Settings** (https://specs.awolve.ai/portal/settings) and generate an API key. It starts with `sk_`. Copy it; you'll paste it in step 4.

Treat it like a password: it acts as you on every project you can see. Don't paste it into the Claude chat.

## 3. Install the plugin

Type these in Claude Code (they're slash commands, so Claude can't run them for you):

```
/plugin marketplace add awolve/open-claude-plugins
/plugin install awolve-signum@awolve-open-claude-plugins
/reload-plugins
```

## 4. Log in with the key

Run `/awolve-signum:login` and choose **API key**.

- **macOS:** with the key on your clipboard, Claude has you run `! python3 …/auth.py login-apikey --from-clipboard`. The key is read from the clipboard, verified, saved, and the clipboard cleared.
- **Linux / Windows:** the clipboard option uses `pbpaste`, which is macOS-only. Run the login in a separate terminal instead, where it prompts for the key without echoing it:

  ```
  python3 ~/.claude/plugins/cache/awolve-open-claude-plugins/awolve-signum/<version>/scripts/auth.py login-apikey
  ```

  (`ls ~/.claude/plugins/cache/awolve-open-claude-plugins/awolve-signum/` shows the version folder.)

The login is stored per machine in your home directory, not in the project.

## 5. Point a folder at your project

In the folder you'll work from, create `.claude/specs.md`:

```yaml
---
service_url: https://specs.awolve.ai
projects:
  - id: <project-id>
    path: ./specs
---
```

- `path` is where the project's spec documents are synced to, relative to the folder. `./specs` is the usual choice.
- In a shared repo, `.claude/specs.md` is committed. For a personal setup that shouldn't be committed, use `.claude/specs.local.md`; it takes precedence when both exist.
- Several projects can sit under `projects:`.

Restart Claude Code in that folder. On every start the plugin pulls the latest specs into `./specs`; when you (or Claude) edit a spec file, the change is pushed as a new version.

## 6. Check it works

```
/awolve-signum:status          # shows who you're logged in as and the sync state
/awolve-signum:list-features <project-id>
/awolve-signum:backlog <project-id>
/awolve-signum:bugs <project-id>
```

An empty project gives empty lists. That's fine, and it's different from an error.

## Day to day

You rarely need the exact command syntax. Say what you want and Claude picks the command, or run `/awolve-signum:help` for the full list.

| You want to… | Say something like | Command |
|---|---|---|
| See what's on your plate | "What's assigned to me in Signum?" | `my-daily`, `my-weekly` |
| Capture an idea or piece of work | "Add a backlog item: nightly export of X, high priority" | `backlog-add` |
| Group work under an epic | "Make #12 an epic and put #13 and #14 under it" | `backlog-update`, `backlog-set-parent` |
| Report a bug | "File a bug: the import fails on empty rows, steps: …" | `bug` |
| Move a bug along | "Set bug #7 to in progress, with a comment that I'm on it" | `set-bug-status`, `bug-comment` |
| Start a spec from an item | "Write requirements for backlog item #12" | `req` |
| Write the design / plan | "Write the design for feature X" | `design`, `plan` |
| Attach a file | "Attach mapping.xlsx to backlog item #12" | `attach` |
| Catch up | "What happened in the project since yesterday?" | `log` |

Specs are three documents per feature: `requirements.md`, `design.md`, `plan.md`. Create them with the commands above rather than writing the files by hand. The commands register each document in Signum; a hand-made file isn't synced.

Comments and reviews on spec documents happen in the portal.

## Roles

What you can do depends on your roles on the project. The ones external collaborators usually get:

| Role | Can |
|---|---|
| `developer` | Create and edit features, spec documents, backlog items and bugs, including bug status. Create tags |
| `reviewer` | Review spec documents: approve or request changes |
| `reporter` | Report bugs and ideas, comment |
| `test_admin`, `test_runner` | Manage or execute test runs, if the project uses Signum's tests |

A few actions stay with the Awolve team whatever your roles: dates and estimates on backlog items, deleting bugs, and restoring deleted backlog items.

## When something goes wrong

| Symptom | Likely cause |
|---|---|
| `API key rejected` / `401` | Key mistyped, revoked, or from another environment. Make a new one in Settings and log in again |
| Project not found / `403` | Your access to that project isn't in place yet, or the id in `specs.md` has a typo |
| `assignee_not_found` | The person you're assigning to has never signed in to the portal |
| `assignee_no_access` | They have an account but no access to this project |
| A spec edit is refused as a conflict | Someone else changed the same document. `/awolve-signum:conflicts` shows it and how to resolve |
| Commands missing or outdated | `/awolve-signum:update-plugins` |

Anything else: ask your Awolve contact, or file it as a bug on your project with `/awolve-signum:bug`.
