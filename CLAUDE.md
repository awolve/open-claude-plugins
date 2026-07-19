# CLAUDE.md — awolve-open-claude-plugins

## Audience: external users without cortex access

This marketplace is **public** and consumed outside Awolve — StudyAlong uses the awolve-spec plugin today; more client orgs may follow (Jernhusen possibly fall 2026). External users have **no access to Awolve cortex**: no `awolve-context/`, no `handbook-context/`, no `/cortex-*` commands, no SIGL files, no `taxonomy.md`, no `_contacts.md`.

**Rule for every skill/command edit:** state the principle generically first; Awolve-internal conventions go in parentheses as examples — `(at Awolve: …)` or `(Awolve-internal: …)`. An instruction must never *require* an artifact only Awolve has. Litmus test: would a StudyAlong developer reading this line know what to do?

Because the repo is public: no secrets, no client names beyond what's already public, no internal strategy or cost details — in code, docs, or commit messages.

## Conventions

- Plugin version lives in `plugins/<plugin>/.claude-plugin/plugin.json`; bump it with every change (patch for docs/wording, minor for behavior).
- Add a `CHANGELOG.md` entry at repo root (newest first, `## <version> — <date>`); commit subjects end with `— <version>`.
- Users update via `/awolve-spec:update-plugins` (or `/plugin marketplace update awolve-open-claude-plugins`) — changes reach externals too, on their own schedule.
