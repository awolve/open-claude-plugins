# Changelog

## 0.40.0 — 2026-08-21

- **The CLI knows about blocking.** The portal has had item dependencies and a `blocked` status since spec-service 0.85.0; this end knew neither. `BACKLOG_STATUSES` was missing `blocked`, and since both child-status histograms filter to known statuses, a blocked child did not appear as blocked — it disappeared from the count entirely. `backlog-update --status blocked` was rejected outright.

- **`view-backlog` prints dependencies in both directions**, each with its own status and a tick when it is done. "Blocked" on its own tells you that you are stuck without telling you on what, and finding what to chase is the only reason to look.

- **`backlog-depend` / `backlog-undepend`.** Dependencies could only be added in the browser, which made the feature unreachable from any session working through this script. The service keeps the consequences: it refuses a pair that would wait on each other, and it moves the status onto and off `blocked` in the same transaction. `blocked` is still settable by hand — but on an item with unfinished dependencies a manual status will not stick, and the commands say so.

## 0.39.1 — 2026-08-20

- **`bug-comments` sorts by timestamp instead of reversing the server's list.** It used to call `reversed()` on the response, with a note explaining that the server returned newest-first and the thread should read chronologically — a local fix for a problem that lived in the server. The server now returns bug comments oldest-first (spec-service 0.70.0), so that reversal would have started showing every thread backwards. Sorting by `createdAt` is correct whichever way the server orders them, which is what the original should have done: a workaround that encodes an assumption about somebody else's behaviour is a trap set for whoever changes it.

- **`delete-backlog-comment` states its permission rule.** Its description was the only one of the four comment commands not saying "author only" — accurate but vague, while its siblings were specific. Inconsistent docs are how the earlier "author or internal user" drift went unnoticed.

## 0.39.0 — 2026-08-20

**`view-bug --images` — screenshots on a bug can finally be looked at from the terminal.**

Most bug reports lead with a screenshot, and until now none of them could be read by whoever was reading the bug. They arrive two ways and both were dead ends:

- **Pasted inline** into the description as a base64 data URI. These were replaced with a placeholder ending "open portal to view" — advice that is no use at all to the reader most likely to be looking, a terminal session that cannot open a browser.
- **Uploaded as an attachment.** These were not mentioned at all. `view-bug` never listed them, so a bug whose entire evidence was an attached screenshot read as a bug with no evidence.

`view-bug` now lists attachments alongside the body, counts the inline images, and takes `--images` to write every one of them to disk and print the absolute paths — ready to be opened and read. `--images <dir>` chooses the destination; the default is a per-bug folder under the system temp directory, deliberately not anywhere a file-sync client would try to replicate it. Non-image attachments are saved too, since someone asking for the pictures usually wants the rest of the evidence as well.

The `/awolve-spec:view-bug` command now instructs the assistant to fetch and read the images whenever the output reports any, without waiting to be asked. Reasoning about a defect from its prose while a picture of it sits unopened is guesswork.

Verified against real reports: an inline screenshot and an uploaded attachment were both saved and opened successfully.

## 0.38.1 — 2026-08-20

- **Removed the `promote-backlog` command doc.** The command itself went in spec 023 (spec-service 0.53.0); the doc survived only to explain that, which meant a removed command kept appearing in the slash-command list. The CLI still answers `promote-backlog` with directions to `create-feature` + `create-doc` + `backlog-comment` rather than "unknown command", so anyone with the old muscle memory is still looked after. The full reasoning for the removal lives in spec 023.

## 0.38.0 — 2026-08-20

**`edit-backlog-comment`, and the comment permissions the docs were promising are no longer true.**

- **New: `/awolve-spec:edit-backlog-comment <project> <ref> <comment-id> "<body>"`.** Backlog comments were the only thread type the CLI could not edit — `edit-bug-comment` and `edit-comment` already existed. Deleting and re-posting was the only way to fix a typo, and it loses the comment's place in the thread.

- **Comment edit and delete are author-only, everywhere.** The service stopped letting internal users edit and delete other people's comments (spec-service 0.63.0). Five command docs, the usage text and three error messages still said "author or internal user"; they now say what the server actually does. A comment is the author's own words.

- **A flag-shaped comment body is now refused instead of posted.** Comment bodies are positional, so `backlog-comment <project> #18 --body "…"` put the literal string `--body` in the comment and discarded the real text without a word. This is not hypothetical — a comment reading exactly `--body` was found in the wild and is what prompted the check. All four comment-writing commands now reject a body starting with `--` and show the positional form.

- **`/awolve-spec:help` now lists every command.** It was missing 18 of them — all four backlog-comment commands, the backlog item commands (`view-backlog`, `backlog-update`, `backlog-set-parent`, `backlog-delete`, `restore-backlog`), `delete-bug`, all four attachment commands, `log`, and the sync-maintenance and marketplace commands (`conflicts`, `cleanup-synced-tree`, `update-plugins`). Attachments and Activity get their own sections, and `attach` is no longer described as feature-only — it has taken bugs and backlog items for some time. Verified both directions: every command file is listed, and every listed command exists and has a CLI dispatch. `promote-backlog` stays unlisted on purpose — it was removed in spec 023 and its doc survives only to redirect whoever still types it.

## 0.37.0 — 2026-08-19

**Tags (spec-service 0.58.0, spec 027).** Per-project labels on backlog items and bugs — one vocabulary shared by both kinds, so a `regression` tag means the same thing wherever it appears in that project.

- **Manage:** `/awolve-spec:tags` lists a project's tags with usage split between backlog and bugs (read this before coining a new one — it is how you spot a near-duplicate). `/awolve-spec:tag-create`, `:tag-update`, `:tag-delete` cover the rest. Renaming keeps the tag on everything it is already applied to.
- **The nudge:** `tag-create` refuses a name close to one that already exists, prints the near-matches, and exits **2** — distinct from 1 for a genuine failure, so a script can tell "stop and look at these" apart from "this broke". `--force` creates it anyway. An exact match is a no-op that reports the existing tag, not an error. The skill tells Claude to show the suggestions rather than reach straight for `--force`.
- **Apply:** `--tags a,b` on `backlog-add` and `bug`; `--tags` (replace), `--add-tag T` / `--remove-tag T` (repeatable), and `--clear-tags` on `backlog-update` and `update-bug`. Tags must already exist — an unknown name fails with `tag_not_found` and close matches, because coining one is a separate, permission-gated act.
- **Filter:** `--tag TAG` on `backlog` and `bugs`, repeatable and OR-ed, matching slug or display name (`--tag "Needs UX"` and `--tag needs-ux` are the same filter), plus `--untagged`. As with `--assignee`, a tag filter forces the backlog into flat view: in tree view a matching child is only rendered under a surviving parent, so a filter would silently drop matches whose epic is not tagged.
- **Read:** tags appear in every list row and in `view-backlog` / `view-bug`.

Applying a tag needs only the right to edit the item, so a bug reporter can label their own report; creating and renaming tags needs the developer or admin role.

## 0.36.0 — 2026-08-14

**Timing flags, and `promote-backlog` removed (spec-service 0.53.0, spec 023).**

- **Set timing:** `backlog-update` and `update-bug` gain `--start YYYY-MM-DD`, `--due YYYY-MM-DD`, `--estimate HOURS`, plus the valueless `--clear-start` / `--clear-due` / `--clear-estimate` (an explicit null is the only way to say "clear", same trick as `--unassign`). Validated client-side so a bad value fails fast instead of round-tripping a 400: real calendar dates only (`2026-02-30` is rejected), estimates 0–9999.99 with at most two decimals, and start never after due.
- **Filter:** `backlog --overdue` and `backlog --late-to-start`. Both are derived locally from the returned dates — the service deliberately exposes no overdue filter, because "today" belongs to whoever is looking. An item that is both is found by either flag, though the list labels it `(OVERDUE)`.
- **Read:** list rows and `view-backlog` / `view-bug` print the dates and estimate, with `(OVERDUE)` / `(late to start)` spelled out.
- **`promote-backlog` is removed.** It fails with directions rather than "unknown command", since it was the documented way to turn an item into a spec. The replacement is three commands that already exist: `create-feature`, `create-doc`, then `backlog-comment` to record the connection where a human will read it. `/awolve-spec:promote-backlog` now documents why.

The timing rules mirror `src/lib/timing.ts` in the service. That is two implementations of the same four-line comparison, and they must move together — noted in both files.

Requires spec-service 0.53.0.

## 0.35.0 — 2026-08-14

**Backlog status `ready_for_testing` (spec-service 0.52.0).** `backlog-update … --status ready_for_testing` marks an item whose work is done but which nobody has verified. It sorts between `in_progress` and `completed` in the child histograms on `backlog` and `view-backlog`, and counts as active, so it stays visible in the default list rather than disappearing the way `completed` does.

The four hardcoded copies of the status list (client-side validator, its error message, and two histogram orderings) collapse into one `BACKLOG_STATUSES` constant next to `FEATURE_STATUSES` and `BUG_STATUSES`.

Requires spec-service 0.52.0 — earlier deployments reject the value with a 400.

## 0.34.0 — 2026-08-13

**Assignment (spec-service 0.51.0).** Backlog items and bugs can carry an assignee, and the CLI can set, clear, and filter on it.

- **Set:** `backlog-update … --assignee <email>` / `--unassign`, `update-bug … --assignee <email>` / `--unassign`, and `backlog-add … --assignee <email>` to create with an owner. `--assignee` and `--unassign` are mutually exclusive; passing neither leaves the current assignee untouched.
- **Filter:** `backlog [project] --assignee <email>|--unassigned` and `bugs [project] --assignee <email>|--unassigned`. `--assignee` matches an email or a fragment of a display name (`--assignee bjorn` works). Omit the project id to sweep every configured project — that's how to answer "what's on my plate everywhere".
- **Read:** list rows show `· @Name`; `view-backlog` and `view-bug` print an `assignee` line that reads `(unassigned)` when nobody owns it.
- An assignee filter forces flat view on `backlog`. In tree view a matching child is only rendered under a surviving parent, so filtering by assignee silently dropped any match whose epic didn't also match — under-reporting what someone is carrying.
- Server rejections are translated instead of echoed: `assignee_not_found` → "they need to have signed in at least once", `assignee_no_access` → "grant access first, then assign".

**Fixed:** `backlog --status <x>` with no project id read the flag's *value* as the project name (the positional collector didn't skip flag values), so `backlog --status idea` looked for a project called "idea". Would have bitten constantly now that `backlog --assignee <email>` across all projects is a normal thing to type.

Requires spec-service 0.51.0 — assignee fields are absent until it's deployed.

## 0.33.1 — 2026-07-27

**`/awolve-spec:update-plugins` now actually updates the plugin.** The command only ran `claude plugin marketplace update`, which refreshes the *catalog* of available versions but never moves the installed version pin — so the command reported success while the plugin kept running its old code. It now also runs `claude plugin update` for each installed plugin from the marketplace, and documents that `claude plugin install` no-ops on an already-installed plugin.

Why this matters: the plugin's `SessionStart` hook runs `specs-cli.py pull` via `${CLAUDE_PLUGIN_ROOT}`, which resolves to the *installed* plugin. A user stuck on a pre-0.19.0 pin therefore re-created in-tree `.remote` conflict sidecars on every single session start, silently, even after running the update command and `/reload-plugins`. Observed in the field on 2026-07-27: 16 sidecars regenerated across `clients/` and `operations/tools/` within seconds of each new session, surviving two cleanup passes. The "After the Update" section now also tells users to restart Claude Code, since hooks in already-running sessions keep resolving to the old plugin root.

## 0.33.0 — 2026-07-21

**`feature-snapshot` subcommand.** New read-only command: `specs-cli.py feature-snapshot <project-id> <feature-name> [--json]` returns the feature's status plus, per document, its status and unresolved comment count — in a single service call (new `/api/features/lookup/snapshot` endpoint, spec service ≥ 0.50.0). Built for pollers that derive state from doc statuses: auth failure, unknown feature, and transport errors exit non-zero with distinct stderr messages. `--json` prints the raw response; without it, a compact table.

## 0.32.2 — 2026-07-19

**External-user pass.** The plugin is used outside Awolve (StudyAlong; more orgs coming) — Awolve-internal conventions are now parentheticals, not prerequisites:

- Closure checklist and plan tasks say "the project's living docs" generically (at Awolve: SIGL files, `shared/` docs, taxonomy.md).
- "Client visibility" reframed as **portal visibility** — everything in the synced tree is visible to every portal user with project access, whoever they are.
- `req`: "the client's `_contacts.md`" → "the project's contact records".
- `infra`: the SIGL-header checklist is explicitly self-contained; the handbook path is marked Awolve-internal.
- `/cortex-update` / `/cortex-doctor-content` mentions marked Awolve-internal.

## 0.32.1 — 2026-07-19

- **plan:** implementers flip the feature to `in_progress` at the first implementation commit — adopted as the standard flow (handbook development-lifecycle.md); gives the portal a live view of what's being built.

## 0.32.0 — 2026-07-19

**Process feedback codified.** A month of session analysis showed the same corrections repeated across desk/atrium/cellum work; the recurring ones now live in the plugin:

- **skill:** "Closing a feature" checklist — docs match reality → shipped per the repo's ship cycle → statuses flipped (feature `completed`, bugs commented + resolved, comments resolved) → SIGL drift captured. Run proactively, not when asked.
- **skill:** "Keep specs current mid-build" — update spec docs the moment a decision lands; check off plan tasks as they complete.
- **skill:** client-visibility warning — everything under the synced specs tree (incl. `specs/shared/`) is client-visible on client projects; no internal-only material there.
- **plan:** tasks must include tests (unit + e2e where feasible) and explicit closing tasks for SIGL/taxonomy/doc updates; new "During implementation" section on keeping the plan current.
- **design:** open questions are written as selected decisions (reviewer comments on disagreement only).
- **req:** style guidance — name real users, quote interviews, describe the journey, state the target role for security scope.

## 0.28.0 — 2026-07-01

**Run instances (spec-service 019).** A test now has multiple **runs** (executions) — re-run a regression weekly without resetting the last one.

- **runs:** `test exec-list <test-id>`, `test exec-start <test-id> [--label '..']`, `test exec-close <exec-id>`.
- `--execution <id>` on `coverage`, `result-record`, `reset-run`, `reset-tester` targets a specific run instance (default = the current run).
- `coverage` prints which run instance it's for.

Requires spec-service with the spec-019 endpoints deployed (the commands 404 until then).

## 0.27.0 — 2026-06-29

**Re-test requests (spec-service 0.44.0).** The `test` group can flag a case for re-test during a UAT:

- `test retest <case-id> [--note '..']` — flag the whole case for re-test; emails every tester who recorded it and has an address.
- `test retest-clear <case-id>` — clear an open re-test request.
- `tester-add … --email <addr>` — store an email on a token tester so they can be notified.

Requires spec-service ≥ 0.44.0 deployed (the commands 404 until then).

## 0.26.0 — 2026-06-29

**Test roles (spec-service 018).** The `test` group gained role management:

- **roles:** `role-add`, `role-list`, `role-rename`, `role-remove`, `role-seed` (copy project role templates into a run)
- **assignment:** `case-roles <case-id> <role-id,…>` (sets the case's roles; cardinality is the single-vs-"open" signal)
- **identity:** `role-identity-set <run-id> <role-id> --scope environment|tester|case --kind account|generated [--scope-ref ID] [--environment staging] [--account-ref <kv-label>] [--template 'cand+{run}-{n}@x']`
- **templates:** `role-template-add`, `role-template-list` (reusable per-project roles)
- `import-cases` matrices may carry a `roles` column (`;`-separated names) / JSON `roles`; `coverage` now prints a per-role breakdown.

Requires spec-service with the spec-018 endpoints deployed (the role commands 404 until then).

## 0.25.0 — 2026-06-26

**`test reset-run` / `test reset-tester`.** Reset recorded results for a manual test run so it can be re-run from scratch — deletes results + evidence photos, re-starts the affected testers, and (whole-run) clears the sign-off. Both are destructive and require `--yes`:

- `specs-cli.py test reset-run <run-id> --yes` — whole run (all testers + sign-off).
- `specs-cli.py test reset-tester <run-id> <tester-id> --yes` — one tester only.

Requires spec-service ≥ 0.40.0 (the `POST /test-runs/:id/reset` endpoint).

## 0.24.0 — 2026-06-26

**`test run-show <run-id> --json`.** Dumps the full run as a re-importable JSON matrix — section name, caseKey, title, whatYouDo, expected, prerequisite text, and derived prerequisiteKeys (the dep edges). This closes the round-trip loop with `import-cases`: export a run, edit the case text in bulk, and re-import without losing titles, structure, or prerequisite edges. (Used to rewrite all 111 Medvind UAT guided-flow cases into richer, bullet-based markdown.)

## 0.23.0 — 2026-06-25

**Test-case `title` + richer `run-show`.** Cases gained a name distinct from the instruction (spec-service 0.35.0):

- `case-add` / `case-update` take `--title`; `import-cases` matrices carry a `title` (or `name`) column / JSON key.
- `run-show` now prints each case's **title** (falling back to the instruction) and its **prerequisites** (`↳ prereq: do first: … — …`).

## 0.22.0 — 2026-06-25

**Full CLI parity with the Manual Test Runs API.** The `test` group now covers every API action, not just creation:

- **runs:** `run-delete` (was create/list/update/show only)
- **sections:** `section-update` (rename/reposition), `section-delete`, `section-reorder`
- **cases:** `case-update` (incl. the new `--prerequisite` / `--prereq-cases`), `case-delete`; `case-add` and `import-cases` now carry `prerequisite` + `prerequisiteKeys`
- **images:** `image-list`, `image-add` (multipart upload, `--caption` / `--target do|expect`), `image-update`, `image-delete`
- **testers:** `tester-list`, `tester-update` (`--revoke` / `--reissue`), `tester-delete`
- **results:** `result-record` (`--status` / `--comment` / `--bug`; you must be a tester on the run)

Run `specs-cli.py test` with no subcommand for the grouped command list.

## 0.21.0 — 2026-06-24

**`test run-update` command.** Edit an existing test run from the CLI: `specs-cli.py test run-update <run-id> [--name ..] [--description ..] [--status draft|active|closed|archived] [--start YYYY-MM-DD] [--end YYYY-MM-DD]`. Covers the gap where the window/status could only be set at creation. Prints the updated run and its window.

## 0.20.0 — 2026-06-24

**`test` CLI command group** (spec-service feature 015 — Manual Test Runs).

`specs-cli.py test <subcommand>` drives the new Manual Test Runs feature from the CLI — used to seed and inspect runs (e.g. importing the Medvind UAT matrix). Subcommands: `run-create`, `run-list`, `run-show`, `section-add`, `case-add`, `import-cases` (paste a section/case/what/expected matrix), `tester-add`, `coverage`, and `signoff`. Matrix parsing handles both tab- and comma-delimited input.

## 0.19.0 — 2026-06-24

**Keep sync sidecars & build artifacts out of the synced tree** (spec-service feature 016).

`specs-cli.py pull` used to write conflict `.remote` sidecars and a `.specs-trash/` dir *inside* the OneDrive-synced specs tree. That tree is synced across 5+ machines, so every sidecar became fork-bait — OneDrive conflict-copied them with machine suffixes and peers re-uploaded after deletes, producing hundreds of junk files and wedging sync. All per-machine sync bookkeeping now lives in the per-machine cache (`~/Library/Caches/com.awolve.cortex/`, override `CORTEX_OFFLINE_CACHE`); the only files in the specs tree are canonical docs.

- **New module `conflict_store.py`** — out-of-tree staging keyed by `doc_id` (`<cache>/specs/conflicts/<doc_id>.remote` + `index.json`) and trash relocation (`<cache>/specs/trash/<project_id>/`). Self-contained (stdlib only), unit-tested.
- **`pull`** stages the remote side of a conflict in the cache (never beside your file), self-heals staged entries once a doc reconciles, relocates orphan trash to the cache, and migrates any legacy in-tree `.remote` sidecars into the store on first run. If the cache is unwritable it reports the conflict but never falls back to an in-tree write.
- **New `conflict` commands** — `conflicts [project] [--json]` to list, `conflict show|diff <doc>`, and `conflict resolve <doc> --theirs|--mine|--merged <file>` (clears the staged copy; surfaces "remote moved again" on a 409).
- **New `cleanup-synced-tree [--dry-run] [--include-venv]`** — purges legacy in-tree artifacts: `.remote`, OneDrive conflict copies, `.specs-trash/`, and (with `--include-venv`) `_gen/.venv/`. Canonical docs, `_gen/*.py`, and outputs are never matched (anchored classification, unit-tested against real accented machine names).
- The session-start `pull` hook is unchanged — frequent pulls are now harmless because nothing lands in the synced tree.

### Manual steps

1. Update the plugin: `/awolve-spec:update-plugins` then `/reload-plugins`.
2. The churn only fully stops once **all** machines update — until then `/cortex-doctor-content` flags any machine still depositing in-tree artifacts.
3. One-time purge of existing junk: run `specs-cli.py cleanup-synced-tree --dry-run` to preview, then (with peers' OneDrive paused, or server-side) run it for real. Single-machine deletion loses the race against peers' session-start pulls.

## 0.18.0 — 2026-06-23

**Support the new `ready_for_retest` bug status.**

The spec service added a `ready_for_retest` status (between `in_progress` and `resolved`) for bugs whose fix is in and are waiting on the reporter/QA to verify. The CLI's status allowlist rejected it.

- `set-bug-status` now accepts `ready_for_retest`; added to the `BUG_STATUSES` allowlist, the usage text, and the `set-bug-status` / `spec` skill docs.

## 0.17.3 — 2026-06-20

**Harden: `api_request` raises on unsupported `data` types instead of silently sending an empty body.**

The 0.17.2 bug was invisible because `api_request` quietly left `body_bytes=None` whenever `data` was neither `str` nor `dict` (e.g. pre-encoded bytes), sending an empty body that the server rejected with a confusing `400 "body is required"`.

- `api_request` now raises `TypeError` for any non-`None` `data` that isn't a `dict` or `str`, so a mistaken caller fails loudly at the source instead of producing an empty request.
- The two body-less POSTs (`promote-backlog`, `restore-backlog`) now pass `data=None` instead of `data=b""`, matching the helper's contract (`None` = no body).

## 0.17.2 — 2026-06-20

**Fix: `backlog-comment` now actually sends the comment body.**

`add_backlog_comment` passed a pre-`json.dumps().encode()`'d **bytes** payload to `api_request`. That helper only attaches the request body + `Content-Type` when `data` is a `dict` or `str` — bytes matched neither branch, so the POST went out with an empty body and the server rejected it with `400 "body is required"`. The command had been broken since `backlog-comment` was introduced in 0.17.0.

- Pass `data={"body": body_text}` (a dict) so `api_request` serialises it and sets `Content-Type: application/json`, matching every other POST caller in the CLI.

## 0.17.1 — 2026-06-15

**Fix: `view-bug` now shows the description, body fields, and screenshots.**

`view-bug` fetched only the project bug *list* (`/api/portal/projects/:p/bugs`), which returns a deliberately slim shape — no `description`, `steps`, `expected`, `actual`, or `environment` (those are omitted server-side because pasted screenshots can push a single bug body past 500 KB). It then read those fields off the slim row, so every bug rendered `(no description)` and any inline screenshot was invisible to the CLI — even when the portal clearly showed one.

- `view-bug` now follows up with the detail endpoint (`/api/portal/bugs/:id`) for the full record, mirroring how `view-backlog` already works. `--json` emits the full detail too.
- Inline base64 data-URI images (`![alt](data:image/png;base64,…)`) in `description`/`steps`/`expected`/`actual` are replaced with a compact `[📎 alt — inline png image, ~NNN KB — open portal to view]` marker, so the body stays readable and it's obvious a screenshot exists without dumping hundreds of KB of base64 to the terminal.
- `view-backlog` gets the same image-stripping treatment (it already fetched the full detail, but printed raw base64 if an item had a pasted screenshot).
- Falls back to metadata-only (with a stderr note) if the detail fetch fails.

## 0.17.0 — 2026-06-05

**Feat: surface backlog descriptions + close the gap between CLI and backend.**

The CLI used to print backlog items as title + status only — no description, no comments, no way to read what a `#N` actually meant before implementing it. The backend had richer routes (`/backlog/:id/comments`, `/promote`, `/restore`, generic attachments) that were simply not wired into the CLI.

New subcommands:

- `view-backlog <project> <#N>` — full description, parent, children (for epics), and comments via `/api/portal/projects/:p/backlog/by-number/:n`
- `backlog-comment` / `backlog-comments` / `delete-backlog-comment` — mirror of bug-comment CRUD for backlog items
- `promote-backlog <project> <#N>` — promote a backlog item to a feature (server creates the feature, seeds a `spec.md` quick-spec, links the item)
- `restore-backlog <project> <uuid>` — restore a soft-deleted item (internal only)
- `delete-bug <project> <#N>` — soft-delete a bug (internal only)
- `list-attachments <feature|bug|backlog> <uuid>` — list attached files on any entity
- `download-attachment <id> <out-path>` — fetch a single attachment's bytes (the `pull` command is whole-project; this is the targeted variant)
- `delete-attachment <id>` — remove an attachment
- `attach <file> --bug <project> <#N>` / `--backlog <project> <#N>` — `attach` previously only targeted features; now it accepts bug and backlog targets too (the backend already supported `entityType: bug|backlog` on `/api/portal/attachments`)

Extended:

- `backlog-update --epic true|false` — flip the epic flag on an existing item (server-side constraints: epics must be top-level, can't toggle if the item has children, can't demote-with-children)

Backwards-compatible: every existing command behaves identically. Slash commands added for each new subcommand.

## 0.16.7 — 2026-05-28

**Fix: `find_project_root()` now works from inside symlinked trees.**

`config.find_project_root()` previously started from `os.getcwd()`, which on macOS returns the symlink-resolved path. When cwd was inside a symlinked tree like Cortex's `awolve-context/` (which points into SharePoint), walking up never crossed back into the actual repo where `.claude/specs.md` lives — so `read_config()` returned `None` and every `specs-cli.py` invocation failed silently with `'NoneType' object has no attribute 'get'`.

Patch tries `$PWD` (shell-tracked, preserves symlinks) before falling back to `os.getcwd()`. Both starts are walked, so behavior is unchanged when `$PWD` is unset, missing, or already resolved.

## 0.16.6 — 2026-05-16

**Fix (specs-plugin bug #2, Option 2): skip push + writeback when body content hasn't changed.**

`push()` now hashes the (frontmatter-stripped) body and compares to the frontmatter's `last_synced_hash`. If they match, the server already has this exact content — return early, no HTTP call, no `atomic_write` rewrite. Every Edit on a spec file no longer guarantees a OneDrive-visible filesystem event; only Edits that actually change body content do.

Why this matters: the unconditional writeback was a major source of OneDrive `.remote` conflict copies on collaboratively-edited specs (14 on `studyalong-genai/033-vikariehantering`, 12 on `037-utbetalningsregler` in the May audit). This patch addresses Pattern A (same-machine churn from multi-Edit Claude tasks or formatter-style rewrites). Pattern B (cross-machine concurrent edits) remains — if `.remote` files keep appearing on the active specs after a week, escalate to Option 4 (auto-pull-and-rebase on 409) per the bug's recommended sequence.

Smoke-test: pushing an unchanged spec is now a true no-op (zero stdout, exit 0, mtime + inode unchanged).

## 0.16.5 — 2026-05-14

**Fix (bug #12): add `set-title` so feature display titles can be edited without renaming the slug.**

New subcommand `set-title <feature-id> <text>` updates a feature's display title alone via `PATCH /api/features/lookup?id=...`. Mirrors the existing `set-description` shape. The backend route already supported title-only updates; this just closes the CLI gap that bug #12 flagged.

When to use which:
- `rename-feature` — slug *and* title change together (e.g. you got the slug wrong)
- `set-title` — slug is fine, just touch up the human-readable name (e.g. fix the every-word-capitalized output of the auto-derivation)
- `set-description` — short summary
- `set-status` — feature/document status

New slash command `/awolve-spec:set-title`. help.md + SKILL.md updated.

The bug's other concern — "rename-feature only updates slug, not display name" — was already addressed by v0.15.3 (sends title alongside name) + spec-service v0.22.x (accepts title on rename). Live-verified during this fix.

## 0.16.4 — 2026-05-14

**Fix (paired with spec-service v0.25.2 / bug #16): clearer error when a local project isn't registered server-side.**

When `bug` or `backlog-add` hits a project that the spec service doesn't know about (e.g. it's in your local `projects.md` but was never bootstrapped), the server now returns `404 project_not_found` instead of a generic 500. The CLI surfaces this with a multi-line explanation pointing at `scripts/bootstrap-specs.py` and `GET /api/portal/projects` for the canonical list — so a Mattias-style "regardless of payload, it 500s" report won't recur.

Requires spec-service v0.25.2.

## 0.16.3 — 2026-05-13

**Feature: edit and delete comments from the CLI, with full audit coverage.**

- New subcommand `edit-comment <comment-id> <body>` edits a spec-doc comment. Author-only on the server.
- New subcommand `delete-comment <comment-id>` deletes a spec-doc comment. Author-only, hard delete.
- New subcommand `edit-bug-comment <project> <#N> <comment-id> <body>` edits a bug comment. Author OR any internal user.
- New subcommand `delete-bug-comment <project> <#N> <comment-id>` deletes a bug comment. Author OR any internal user, hard delete.
- `bug-comments` listing now shows the comment UUID in brackets so users can copy it into edit/delete commands without going to the portal.
- New slash commands `/awolve-spec:edit-comment`, `/awolve-spec:delete-comment`, `/awolve-spec:edit-bug-comment`, `/awolve-spec:delete-bug-comment`. Delete commands instruct Claude to confirm with the user first.

Every body edit is now audited:
- Bug comments — `bug_comment.update` audit event (already existed; CLI just exposes it).
- Spec-doc comments — `comment.update` audit event. Previously body edits were silent on the doc side. **Requires spec-service v0.25.1**, which adds the audit event with a 100-char preview of the previous body in `metadata.previousBodyExcerpt`.

## 0.16.2 — 2026-05-13

**Fix (bug #15): bugs can now be edited and commented on from the CLI.**

- New subcommand `update-bug <project> <bug-number> [--title T] [--description T] [--severity S]` patches title/description/severity on an existing bug. At least one flag required. Status changes still go via `set-bug-status` so the audit log gets a dedicated `status_change` event.
- New subcommand `bug-comment <project> <bug-number> <body>` adds a comment to a bug — for attaching commit SHAs, package versions, or rollout notes without rewriting the original report.
- New subcommand `bug-comments <project> <bug-number> [--json]` lists the comment thread (oldest-first), with author + author type + timestamp on each entry.
- New slash commands `/awolve-spec:update-bug`, `/awolve-spec:bug-comment`, `/awolve-spec:bug-comments`. Shapes mirror the existing `backlog-update` / `comment` / `comments` commands so the two flows feel consistent.
- SKILL.md reference table and `/awolve-spec:help` updated.

No spec-service version bump required — backend PATCH `/api/portal/bugs/:id` and POST `/api/portal/bugs/:id/comments` already exist.

## 0.16.1 — 2026-04-28

**Fix (bug #14): backlog items can now be edited and deleted from the CLI.**

- New subcommand `backlog-update <project> <item> [--title T] [--description T] [--priority P] [--status S]` patches fields on an existing item. At least one flag required. Parent/epic changes still go via `backlog-set-parent`.
- New subcommand `backlog-delete <project> <item>` soft-deletes an item. If the item is an epic, the server cascades to all active children in one transaction. The portal already exposes both affordances; this closes the CLI gap.
- New slash commands `/awolve-spec:backlog-update` and `/awolve-spec:backlog-delete`. The delete command instructs Claude to confirm with the user before calling — destructive and visible in the audit log.
- SKILL.md reference table updated.

## 0.16.0 — 2026-04-22

**Feature (spec 013): backlog hierarchy + filters + epic flag.**

- `backlog-add` accepts `--parent <id-or-#N>` to create the item as a child of an existing epic, and `--epic` to create the item as an empty epic placeholder. Mutually exclusive.
- New subcommand `backlog-set-parent <project> <item> <parent|none>` reparents an item; `none` clears the parent. Wraps the existing PATCH endpoint.
- New slash command `/awolve-spec:backlog-set-parent`.
- `backlog` list gains `--epics` (filter to `isEpic = true`), `--flat`, `--status`, `--priority`. Default is now a tree view with epic head + indented children. Epic rows are prefixed with `[EPIC]` and show a child-status histogram inline; empty epics show `· (no items yet)`.
- All numeric `#N` references resolve server-side and report a clear error when the parent isn't an epic (`parent_not_an_epic`), still has its own children (`epic_has_children`), etc.
- SKILL.md gains a "Backlog hierarchy" section guiding Claude to propose an epic when the user is adding multiple related items in one session.

Requires spec-service v0.25.0 (adds `is_epic` column + parent validation).

## 0.15.3 — 2026-04-16

- **Fix (bug #9): set-status refuses ambiguous bare feature names.** When a feature name like `001-base-infrastructure` exists in multiple projects, `set-status` previously silently updated the first match — wrong project, no warning. Now collects all matches first and errors with: `feature name '...' exists in multiple projects: ..., ... — use <project>/<feature> form`. The qualified form (`project/feature-name`) was already supported and continues to work.
- **Fix (bug #6): rename-feature now updates the title field.** Previously only patched `name` (slug), leaving the portal showing the old human-readable title. Now derives a title from the new slug (strip numeric prefix, title-case) and sends both `name` and `title` in the PATCH. Pass `--title "Custom Title"` to override the derivation.
- **Fix (bug #8): attach replaces existing attachment with the same filename.** Previously re-uploading the same file created a duplicate row. Now checks existing attachments for the feature, and if one with the same filename exists, deletes it before uploading the replacement. Best-effort — if the check fails, upload still proceeds (may still duplicate).

## 0.15.2 — 2026-04-15

- New subcommand `set-bug-status <project-id> <bug-number> <status>` — change a bug's status from the CLI. Previously the only way to close a resolved bug was via the portal UI or a manual PATCH to the API.
- New slash command `/awolve-spec:set-bug-status`.
- SKILL.md reference table updated.

## 0.15.1 — 2026-04-15

- New subcommand `view-bug <project-id> <bug-number> [--json]` — fetch full bug details (description, severity, repro). Previously there was no way to read a bug's body without opening the portal or curling the API.
- New slash command `/awolve-spec:view-bug` — Claude-facing wrapper.
- SKILL.md now includes a full `specs-cli.py` subcommand reference so Claude doesn't have to grep the script source to discover the command surface. Also documents two sharp edges: `create-feature` rejects numeric prefixes (service auto-numbers), and `--json` is available on several list commands.

## 0.15.0 — 2026-04-13

**Feature shortDescription from the CLI.** Companion to spec-service v0.21.1 which fixed the PATCH route.

- `create-feature` learned `--description "<text>"` — sets the feature's shortDescription immediately after creation (via a follow-up PATCH to `/api/features/lookup`, since the POST endpoint doesn't accept the field yet).
- New subcommand `set-description <feature-id> <text>` — update or clear an existing feature's shortDescription. Pass `""` to clear.
- New slash command `/awolve-spec:set-description` — Claude-facing wrapper.
- Requires spec-service v0.21.1 or later (earlier versions silently drop `short_description` on the lookup PATCH).

## 0.14.3 — 2026-04-13
- `create-feature` now sends the spec number explicitly to the service as `number` in the POST body, derived from the folder name prefix. The service also accepts the prefix implicitly, but sending it explicitly keeps CLI and service consistent when the name already has a number.
- Requires spec-service v0.20.0 or later (earlier versions ignore the `number` field).

## 0.14.2 — 2026-04-12

- **New slash command `/awolve-spec:update-plugins`** — refreshes the `awolve-open-claude-plugins` marketplace and prompts the user to run `/reload-plugins`. Counterpart to `/update-awolve-plugins` (which covers `awolve-marketplace`). `/cortex-update` runs both.

## 0.14.1 — 2026-04-12

- **`specs log --all`** — query the audit feed across every configured project, merged and sorted by time. Events get a project-id prefix so the output stays legible. Makes "what happened yesterday" answerable without picking a project.
  ```bash
  specs log --all --since 1d
  specs log --all --since 7d --author bjorn.allvin@awolve.ai
  specs log --all --since-last-visit --mark-read   # advances cursor per project
  ```
  Works alongside the per-project form — pass either a project id or `--all`, not both.
- **New slash command `/awolve-spec:log`** — Claude-facing interface to the CLI that maps natural-language questions ("what happened yesterday", "did Michael do anything today", "any new bugs this week") to the right flags, runs the command, and summarizes the output with grouped bullet points per project. Advances the visit cursor when appropriate.

## 0.14.0 — 2026-04-12

**Robust pull + `specs log` command** (spec 010 phases 3b + 4, plugin side). Companion to spec-service v0.18.0 which shipped the `/changes` and `/history` endpoints.

### Pull robustness

- **Atomic writes** — every file write (.md docs and binary attachments) goes through a tempfile → fsync → os.replace. A crash mid-write can never leave a half-written file in your specs folder.
- **HTTP retries** — `api_request()` now retries transient failures:
  - GET: 3 attempts for 502/503/504 and `ConnectionError`, exponential backoff (0.5s → 1s → 2s) with ±25% jitter.
  - Mutating methods (PUT/POST/PATCH/DELETE): 1 retry for `ConnectionError` only, and only if the error happened before the request was sent. Never retry on HTTPError — we trust any status the server actually returned.
  - 401 and 409 are never retried (they're semantic signals).
- **Drift detection via `last_synced_hash`** — every synced file now carries a `last_synced_hash` frontmatter field recording the body hash the client last saw from the server. On subsequent pulls, if the local hash differs from `last_synced_hash` AND the remote hash has also changed, the pull writes the remote content to `<file>.remote` and leaves the local file untouched. The pull summary reports conflicts so you can review and reconcile them manually.
- **`push()` sets `last_synced_hash`** after a successful push so the new value is consistent — a subsequent pull will treat the just-pushed version as "clean".
- **Deletion handling** — when a local file's `spec_doc_id` isn't in the remote manifest (feature or document was deleted in the portal), `pull` moves the local file into `.specs-trash/YYYY-MM-DD/<relative-path>` by default. Three flags control this:
  - `pull --prune` — permanently delete instead of trashing
  - `pull --keep` — leave orphans alone (previous default behavior)
  - `pull` (default) — trash, recoverable
  Collisions in the trash get a numeric suffix so nothing is ever overwritten.

### State file

- New per-project state file at `.claude/specs.state.json` tracking sync and visit cursors across pulls. Shape:
  ```json
  {
    "version": 1,
    "projects": {
      "spec-service": {
        "last_sync_cursor": "01HXX...",
        "last_visit_cursor": "01HXX...",
        "last_full_sync": "2026-04-12T00:00:15Z",
        "last_pulled_at": "2026-04-12T00:00:15Z"
      }
    }
  }
  ```
- Written atomically after every pull and every `log --mark-read`. Add to `.gitignore` — it's per-clone state.

### `specs log` — new command

Stream audit events from the spec service for a project:

```bash
specs log <project>                          # 50 most recent events (desc)
specs log <project> --since 7d               # last 7 days
specs log <project> --since 2026-04-01       # since absolute date
specs log <project> --author bjorn@awolve.ai # filter by actor
specs log <project> --entity feature         # filter by entity type
specs log <project> --limit 200              # up to 1000
specs log <project> --json                   # machine-readable
specs log <project> --since-last-visit       # "what happened since I last looked"
specs log <project> --since-last-visit --mark-read  # advance the visit cursor
```

Output is colored by entity type (feature / doc / version / comment / review / bug / etc.), grouped by day, and shows actor + relative time. `--since-last-visit` reads the project's `last_visit_cursor` from the state file; `--mark-read` advances it to the newest event shown. Re-running the same command with `--mark-read` after a clean read shows "(no new events since your last visit)".

### Known soft limits

- `specs log --since <duration>` is a client-side filter applied after the server returns the window. The underlying endpoint is cursor-based (ULID), not timestamp-based, so the duration filter is a display convenience — for very old windows you'll need to paginate via `--limit`.
- `specs log --since-last-visit` relies on the state file's `last_visit_cursor`. First run with an empty state file returns everything the server has — expected, since "last visit" is undefined.

### Requires

- spec-service v0.18.0 or later. Older versions return the manifest without a `cursor` field, which the plugin tolerates but deletion detection + delta sync fall back to "full manifest every time".
## 0.13.0 — 2026-04-10
- **Binary attachments**. Completes the filesystem-sync half of the spec-service file upload feature (service side shipped in spec-service 0.13.0).
  - `pull` now also downloads feature attachments to the local feature folder alongside .md docs. Deduped by `(filename, size)` — re-downloads on size mismatch, skips otherwise.
  - New `attach` command and `/awolve-spec:attach` slash command for uploading a local binary file (image, PDF, Excel, etc.) to a feature. Feature is inferred from the file path if not specified explicitly.
  - Multipart upload built inline (no third-party deps) so the CLI stays stdlib-only.
- Requires spec-service v0.13.0 or later (earlier versions will reject the attachment API calls).

## 0.10.9 — 2026-04-02
- UX: API key login reads from clipboard (`--from-clipboard`) — copy key, run command, done
- Validates key starts with `sk_` before calling service
- Clears clipboard after successful login

## 0.10.8 — 2026-04-02
- Fix: API key login supports `SPECS_API_KEY` env var — works in Claude Code `!` commands where getpass fails
- Falls back gracefully with instructions if interactive input unavailable

## 0.10.7 — 2026-04-02
- Fix: `/specs-login` removes Bash from allowed-tools so it must ask auth method first

## 0.10.6 — 2026-04-02
- Fix: `/specs-login` now forces auth method question — cannot be skipped or assumed
- Docs: added update command to README and SKILL.md
- Docs: updated README with full command list and current setup flow

## 0.10.5 — 2026-04-02
- UX: `/specs-login` now asks user to choose auth method (Azure CLI or API key) before proceeding

## 0.10.4 — 2026-04-02
- Security: API key login now uses `getpass` (hidden prompt) — key never appears in args or conversation
- Login verifies key against service before saving
- Command instructs user to run via `!` prefix so key stays in their terminal

## 0.10.3 — 2026-04-02
- Fix: create-feature now sends required `title` and `contextPath` to API (was failing with 400)
- Fix: create-doc now sends required `content` to API (was failing with 400)
- Fix: list-features reads `documentCount` instead of missing `documents` array
- Fix: frontmatter parsing tolerates BOM, `\r\n` line endings, and trailing whitespace
- Fix: push strips any leaked/double frontmatter from body before sending
- Fix: render_frontmatter normalizes body join to prevent double-newline compounding
- Refactor: create_backlog_item passes dict instead of pre-serialized JSON string

## 0.10.2 — 2026-04-01
- Fix: specs-pull updates local frontmatter (spec_version, feature_status, doc_status) when content matches but metadata has drifted — prevents stale base_version causing false 409 conflicts on push

## 0.10.1 — 2026-03-31
- Align marketplace and plugin versions

## 0.10.0 — 2026-03-31
- Feature and document management commands (create, rename, delete features and documents)

## 0.9.1 — 2026-03-31
- Fix: remove explicit hooks reference — auto-discovered by convention

## 0.9.0 — 2026-03-31
- Phased spec commands: `/spec requirements`, `/spec design`, `/spec infra`, `/spec plan`

## 0.8.1 — 2026-03-29
- Fix: register hooks in plugin manifest
