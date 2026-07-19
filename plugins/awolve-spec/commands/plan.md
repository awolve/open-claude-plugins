---
description: Write plan.md for a feature — implementation approach and task breakdown
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion]
argument-hint: [project/feature-name]
---

# /awolve-spec:plan

Write `plan.md` for a feature. Covers the implementation approach, sequencing, task breakdown, and dependencies. Use this when the feature is complex enough to need a structured implementation plan.

## Instructions

### 1. Resolve project and feature

The user's argument "$ARGUMENTS" may contain a project name, feature name, or both.

Find the feature folder. It must have a `design.md` — if it doesn't, tell the user to run `/awolve-spec:design` first.

### 2. Read existing context

Read all existing spec files in the feature folder:
- `requirements.md` (if present) — what needs to be built
- `design.md` (required) — how it will be built

### 3. Write plan.md

Create `${SPEC_DIR}/{NNN}-{feature-name}/plan.md`:

```markdown
# {Feature Name} — Plan

## Approach

[Brief implementation strategy — what order, why that order, key sequencing decisions. 2-4 sentences.]

## Tasks

- [ ] 1. [Phase or major component]
  - [ ] 1.1 [Specific task]
    - Files: [files to create/modify]
  - [ ] 1.2 [Specific task]
    - Files: [files to create/modify]

- [ ] 2. [Next phase]
  - [ ] 2.1 [Task]
  ...

## Dependencies

- [External dependencies to install]
- [APIs or services to set up]
- [Other teams or repos involved]
```

**Task guidelines:**
- Each leaf task should be a few hours of work at most
- Tasks should produce testable results
- Include file paths for clarity
- Order tasks so each builds on the previous
- Include tests in the plan — unit tests for pure logic, e2e where feasible; testing is a task, not an afterthought
- Where the feature touches infrastructure or shared project knowledge, add explicit closing tasks for the project's living documents so they aren't dropped at the end (at Awolve: "update SIGL", "update taxonomy.md"; other orgs: whatever architecture/domain docs the project keeps)

Adapt the template — if dependencies aren't relevant, skip that section. If phases don't make sense for this feature, use a flat task list.

### 4. Register and push

If the document is new (no spec_doc_id frontmatter), register it:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/specs-cli.py create-doc <project-id> <feature-name> plan.md
```

Then re-read the file to pick up the sync frontmatter. The PostToolUse hook handles pushes from here.

If the file already has sync frontmatter, the PostToolUse hook handles the push automatically.

### 5. Stop

Tell the user:

```
Plan written: {path to plan.md}

Ready to implement. Start with task 1.1.
```

## During implementation — keep the plan current

The plan is the durable record that later sessions (and the portal) read to know where the work stands. Whoever implements against this plan must:

- **Flip the feature to `in_progress` at the first implementation commit** (`specs-cli.py set-status <feature> in_progress`) — one command, and the portal shows what's actually being built
- Check off tasks (`- [x]`) in the same turn the work completes — not in a batch at the end, and never only when the user asks "is the plan up to date?"
- When a decision changes the approach mid-build, update the affected tasks and `design.md` immediately — specs track reality, not intentions
- The PostToolUse hook pushes each edit automatically; no manual sync needed

When the last task is checked off, run the closure checklist in the `awolve-spec:spec` skill (docs match reality → shipped per the repo's ship cycle → statuses flipped → living docs updated).
