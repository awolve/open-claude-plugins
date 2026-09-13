# Specs Plugin

Claude Code plugin for spec-driven development with Awolve Signum (specs.awolve.ai).

## How it works

- **Session start hook** pulls the latest specs automatically
- **PostToolUse hook** detects when a spec file is written/edited and pushes changes
- **Sync commands** (`/awolve-signum:pull`, `/awolve-signum:login`, `/awolve-signum:status`) for manual sync control
- **Review commands** (`/awolve-signum:comments`, `/awolve-signum:review`, `/awolve-signum:save`, `/awolve-signum:update`) for the collaboration loop
- **Creation commands** (`/awolve-signum:design`, `/awolve-signum:req`, `/awolve-signum:plan`) for phased spec writing

## Configuration files

Two config files, different purposes:

- **`.claude/specs.md`** — Committed to git. Shared config for all team members. Use for client repos where everyone has the same paths.
- **`.claude/specs.local.md`** — NOT committed (.gitignore). Personal override for machine-specific paths. Overrides specs.md entirely when present.

Resolution: `specs.local.md` > `specs.md`. Only one is used, never merged.

## Project structure

- `.claude-plugin/plugin.json` — Plugin manifest
- `hooks/` — Hook definitions (SessionStart, PostToolUse)
- `commands/` — Slash commands (/awolve-signum:pull, /awolve-signum:login, /awolve-signum:status)
- `skills/` — Skill trigger description
- `scripts/` — Python 3 scripts (no external dependencies)

## Development

```bash
python3 scripts/specs-cli.py --help
python3 scripts/auth.py status
python3 scripts/config.py  # (no CLI, imported by specs-cli.py)
```
