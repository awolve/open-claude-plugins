#!/usr/bin/env python3
"""
Specs CLI — sync, review, and manage spec documents.

Usage:
    specs-cli.py pull [project-id] [--prune|--keep] [--force-full]
                                       — Pull latest specs (all projects, or specific one)
                                         --prune        permanently delete orphaned local files
                                         --keep         leave orphans alone (no trash)
                                         --force-full   bypass delta sync, always fetch manifest
    specs-cli.py log <project-id|--all> [--since DUR] [--author EMAIL] [--entity TYPE]
                                       [--limit N] [--json] [--since-last-visit] [--mark-read]
                                       — Stream audit events (one project, or --all for every configured project)
    specs-cli.py push <file_path>      — Push a single spec file
    specs-cli.py conflicts [project-id] [--json]
                                       — List sync conflicts staged out-of-tree (per-machine cache)
    specs-cli.py conflict show <doc>   — Print the staged remote side of a conflict (doc_id or local path)
    specs-cli.py conflict diff <doc>   — Unified diff: local doc vs staged remote
    specs-cli.py conflict resolve <doc> --theirs|--mine|--merged <file>
                                       — Resolve a conflict: take remote, push local, or push a merged file
    specs-cli.py cleanup-synced-tree [--dry-run] [--include-venv]
                                       — Purge legacy in-tree sync/build artifacts (.remote, conflict copies,
                                         .specs-trash/, and with --include-venv, _gen/.venv/)
    specs-cli.py status                — Show sync status of local spec files
    specs-cli.py set-status <id> <status> — Set feature or document status
    specs-cli.py set-description <feature-id> <text>
                                       — Set or clear a feature's shortDescription (pass "" to clear)
    specs-cli.py set-title <feature-id> <text>
                                       — Update a feature's display title without renaming the slug
    specs-cli.py create-feature <project-id> <name> [--status STATUS] [--description TEXT]
                                       — Create a new feature in a project
    specs-cli.py create-doc <project-id> <feature-name> <filename>
                                       — Add a document to an existing feature
    specs-cli.py rename-feature <project-id> <old-name> <new-name>
                                       — Rename a feature folder and update the service
    specs-cli.py rename-doc <file-path> <new-filename>
                                       — Rename a document file and update the service
    specs-cli.py delete-doc <file-path>
                                       — Delete a document from filesystem and service
    specs-cli.py delete-feature <project-id> <feature-name>
                                       — Delete a feature and all its documents
    specs-cli.py list-features <project-id>
                                       — List all features in a project
    specs-cli.py list-docs <project-id> <feature-name>
                                       — List all documents in a feature
    specs-cli.py feature-snapshot <project-id> <feature-name> [--json]
                                       — One-call snapshot: feature status, doc statuses, unresolved comment counts
    specs-cli.py backlog [project-id] [--epics|--flat] [--status STATUS] [--priority PRIORITY] [--assignee EMAIL|--unassigned] [--tag TAG ...] [--untagged]
                                       — List backlog items (default: tree view, grouped by epic;
                                         --assignee and --tag force flat view so no match is hidden
                                         under a filtered-out epic; --tag is repeatable and OR-ed)
    specs-cli.py view-backlog <project-id> <item-id-or-#N> [--json]
                                       — Show full details of a single backlog item (description, parent, etc.)
    specs-cli.py backlog-add <project-id> <title> [description] [priority] [--parent <id-or-#N>] [--assignee EMAIL] [--tags a,b]
                                       — Create a backlog item; optional --parent makes it a child of an epic.
                                         --tags applies existing tags (create them first with tag-create)
    specs-cli.py backlog-set-parent <project-id> <item-id-or-#N> <parent-id-or-#N|none>
                                       — Reparent a backlog item (or pass 'none' to clear the parent)
    specs-cli.py backlog-update <project-id> <item-id-or-#N> [--title T] [--description T] [--priority P] [--status S] [--epic true|false] [--assignee EMAIL|--unassign]
                                       [--tags a,b | --add-tag T | --remove-tag T | --clear-tags]
                                       [--deployed-stage preview|staging|production --deployed-url U | --clear-deployment]
                                       — Update fields on an existing backlog item.
                                         --tags replaces the set; --add-tag/--remove-tag are repeatable deltas.
                                         --deployed-stage/--deployed-url record where the fix runs (set together)
    specs-cli.py --version
                                       — Print the installed plugin version (compare it with the
                                         one the portal changelog names as latest)
    specs-cli.py backlog-depend <project-id> <item-id-or-#N> <blocker-id-or-#N>
                                       — Make an item wait for another. The service sets its status to
                                         blocked, and clears it when the last blocker is done
    specs-cli.py backlog-undepend <project-id> <item-id-or-#N> <blocker-id-or-#N>
                                       — Drop a dependency (restores the status the item had before)
    specs-cli.py backlog-delete <project-id> <item-id-or-#N>
                                       — Soft-delete a backlog item (cascades to children)
    specs-cli.py backlog-comments <project-id> <item-id-or-#N> [--json]
                                       — List comments on a backlog item
    specs-cli.py backlog-comment <project-id> <item-id-or-#N> <body>
                                       — Add a comment to a backlog item
    specs-cli.py edit-backlog-comment <project-id> <item-id-or-#N> <comment-id> <body>
    specs-cli.py delete-backlog-comment <project-id> <item-id-or-#N> <comment-id>
                                       — Delete a backlog comment (author only)
    specs-cli.py restore-backlog <project-id> <item-uuid>
                                       — Restore a soft-deleted backlog item (internal users only)
    specs-cli.py bugs [project-id] [--assignee EMAIL|--unassigned] [--tag TAG ...] [--untagged]
                                       — List open bugs for a project (or all configured projects);
                                         --tag is repeatable and OR-ed
    specs-cli.py bug <project-id> <title> <description> [severity] [--attach file ...] [--tags a,b]
                                       — Create a bug
    specs-cli.py view-bug <project-id> <bug-number> [--json] [--images [dir]]
                                       — Show full details of a single bug (description, severity, repro, etc.)
    specs-cli.py set-bug-status <project-id> <bug-number> <status>
                                       — Change a bug's status (open|triaged|in_progress|ready_for_retest|resolved|closed)
    specs-cli.py update-bug <project-id> <bug-number> [--title T] [--description T] [--severity S] [--assignee EMAIL|--unassign]
                                       [--tags a,b | --add-tag T | --remove-tag T | --clear-tags]
                                       [--deployed-stage preview|staging|production --deployed-url U | --clear-deployment]
                                       — Edit a bug's title, description, severity, assignee, tags, or deployment info
    specs-cli.py bug-comments <project-id> <bug-number> [--json]
                                       — List comments on a bug
    specs-cli.py bug-comment <project-id> <bug-number> <body>
                                       — Add a comment to a bug
    specs-cli.py edit-bug-comment <project-id> <bug-number> <comment-id> <body>
                                       — Edit a bug comment (author only). Audited.
    specs-cli.py delete-bug-comment <project-id> <bug-number> <comment-id>
                                       — Delete a bug comment (author only). Hard delete, audited.
    specs-cli.py delete-bug <project-id> <bug-number>
                                       — Soft-delete a bug (internal users only)
    specs-cli.py tags <project-id> [--json]
                                       — List a project's tags with how many items wear each one
    specs-cli.py tag-create <project-id> <name> [--color C] [--description D] [--force]
                                       — Create a tag. Refuses (exit 2) and lists close matches when a
                                         similar tag already exists; --force creates it anyway
    specs-cli.py tag-update <project-id> <tag> [--name N] [--color C] [--description D] [--force]
                                       — Rename, recolour, or re-describe a tag. Assignments are kept
    specs-cli.py tag-delete <project-id> <tag> [--force]
                                       — Delete a tag. A tag in use needs --force, which detaches it everywhere
    specs-cli.py comments <file-path>  — List comments on a spec document
    specs-cli.py comment <file-path> <body> [--inline --anchor <text>]
                                       — Add a comment to a spec document
    specs-cli.py resolve-comment <comment-id> — Resolve a comment
    specs-cli.py edit-comment <comment-id> <body>
                                       — Edit a spec-doc comment (author only). Audited.
    specs-cli.py delete-comment <comment-id>
                                       — Delete a spec-doc comment (author only). Hard delete, audited.
    specs-cli.py reviews <file-path>   — List reviews on a spec document
    specs-cli.py review <file-path> <verdict> [body]
                                       — Submit a review (approved|changes_requested)
    specs-cli.py versions <file-path>  — List version history
    specs-cli.py save <file-path> <summary> [--source <source>]
                                       — Save current file as a named version
    specs-cli.py service-status        — Check spec service health
    specs-cli.py post-tool-use         — Hook: read tool use JSON from stdin, push if spec
    specs-cli.py attach <file-path> [<project-id>/<feature-name>]
                                       — Upload a binary file as an attachment to a feature
                                         (if no feature id given, inferred from file path)
    specs-cli.py attach <file-path> --bug <project-id> <bug-#N>
                                       — Attach a file to an existing bug (post-creation)
    specs-cli.py attach <file-path> --backlog <project-id> <backlog-#N>
                                       — Attach a file to a backlog item
    specs-cli.py list-attachments <feature|bug|backlog> <entity-uuid> [--json]
                                       — List attachments on an entity
    specs-cli.py download-attachment <attachment-id> <out-path>
                                       — Download an attachment by id (out_path may be a dir or file)
    specs-cli.py delete-attachment <attachment-id>
                                       — Delete an attachment by id
    specs-cli.py --help                — Show this help
"""

import hashlib
import json
import base64
import binascii
import os
import random
import re
import shutil
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta

# Add scripts dir to path for sibling imports
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import auth
import config
import conflict_store


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

# Tolerant: optional BOM, \r\n or \n, optional trailing whitespace on delimiter lines
FM_PATTERN = re.compile(
    r"^\ufeff?"           # optional BOM
    r"---[ \t]*\r?\n"     # opening ---
    r"(.*?)\r?\n"         # frontmatter body (lazy)
    r"---[ \t]*\r?\n?",   # closing ---
    re.DOTALL,
)


def parse_frontmatter(content):
    """Parse YAML frontmatter. Returns (metadata_dict, body_without_frontmatter).

    Tolerates BOM, \\r\\n line endings, and trailing whitespace on delimiters.
    """
    m = FM_PATTERN.match(content)
    if not m:
        return {}, content
    fm_text = m.group(1)
    body = content[m.end():]
    meta = {}
    for line in fm_text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([\w_]+)\s*:\s*(.+)$", line)
        if match:
            key = match.group(1)
            val = match.group(2).strip().strip("\"'")
            try:
                val = int(val)
            except (ValueError, TypeError):
                pass
            meta[key] = val
    return meta, body


def render_frontmatter(meta, body):
    """Render metadata dict and body back into markdown with frontmatter.

    Normalises the join: body always starts with exactly one blank line.
    """
    lines = ["---"]
    for k, v in meta.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    # Ensure exactly one blank line between frontmatter and body
    body = body.lstrip("\r\n")
    lines.append("")
    return "\n".join(lines) + "\n" + body


def strip_frontmatter(content):
    """Remove any leading frontmatter block(s) from content.

    Handles the case where frontmatter leaked into body (double frontmatter).
    """
    while True:
        m = FM_PATTERN.match(content)
        if not m:
            return content
        content = content[m.end():]


def file_content_hash(content):
    """SHA-256 hash of body content (without frontmatter)."""
    _, body = parse_frontmatter(content)
    return hashlib.sha256(body.strip().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def api_request(url, method="GET", headers=None, data=None):
    """Make an HTTP request with transient-failure retries.

    Returns (status_code, response_body_str).

    Retry policy (spec 010 phase 3b):
    - GET: retry on ConnectionError and 502/503/504, up to 3 attempts total.
      Backoff 0.5s → 1s → 2s with ±25% jitter.
    - PUT/POST/PATCH/DELETE: retry on ConnectionError only, once, and only
      if the error happened *before* the request was sent. After the server
      has returned any status code we trust it and do not retry.
    - 409 Conflict and 401 Unauthorized are never retried — they're semantic
      signals the caller needs to handle.
    """
    headers = headers or {}
    headers.setdefault("User-Agent", "awolve-specs-plugin/1.0.0")

    body_bytes = None
    if data is not None:
        if isinstance(data, str):
            body_bytes = data.encode("utf-8")
            headers.setdefault("Content-Type", "text/markdown; charset=utf-8")
        elif isinstance(data, dict):
            body_bytes = json.dumps(data).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        else:
            # Fail loud: a non-None data of any other type (e.g. pre-encoded
            # bytes) would otherwise leave body_bytes=None and silently send an
            # empty body — the trap behind the 0.17.2 backlog-comment bug. Pass
            # a dict (JSON) or str (markdown); use data=None for a body-less POST.
            raise TypeError(
                f"api_request: unsupported data type {type(data).__name__}; "
                "pass a dict (JSON), str (markdown), or None (no body)"
            )

    is_get = method.upper() == "GET"
    max_attempts = 3 if is_get else 2
    backoff_base = 0.5

    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")
            except Exception:
                pass
            # Only retry GETs on 502/503/504, and only if attempts remain.
            if is_get and e.code in (502, 503, 504) and attempt + 1 < max_attempts:
                _sleep_with_jitter(backoff_base * (2 ** attempt))
                continue
            return e.code, body
        except urllib.error.URLError as e:
            last_exc = ConnectionError(f"Network error: {e.reason}")
            # URLError before we got any response — safe to retry for both
            # GET and mutating methods (the request was never accepted).
            if attempt + 1 < max_attempts:
                _sleep_with_jitter(backoff_base * (2 ** attempt))
                continue
            raise last_exc from e

    # Unreachable, but keeps mypy happy
    raise last_exc or ConnectionError("Network error (no attempts made)")


def _sleep_with_jitter(base_seconds):
    """Sleep for `base_seconds` ± 25% jitter. Used by the retry backoff."""
    jitter = base_seconds * 0.25
    time.sleep(max(0.05, base_seconds + random.uniform(-jitter, jitter)))


# ---------------------------------------------------------------------------
# Atomic file writes (spec 010 phase 3b)
# ---------------------------------------------------------------------------

def atomic_write(path, content, binary=False):
    """Write `content` to `path` atomically: tempfile → fsync → os.replace.

    Prevents half-written files if the process crashes or the disk fills up
    mid-write. The tempfile is created in the same directory as the target
    so the final `os.replace` is a same-filesystem rename (atomic on POSIX
    and modern Windows).
    """
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    mode = "wb" if binary else "w"
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=d)
    try:
        if binary:
            os.close(fd)
            with open(tmp, mode) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
        else:
            with os.fdopen(fd, mode, encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# State file — per-project sync + visit cursors (spec 010 phase 4)
# ---------------------------------------------------------------------------

_STATE_FILENAME = "specs.state.json"
_FULL_SYNC_INTERVAL = timedelta(days=7)


def _state_path(project_root):
    """Return the absolute path to .claude/specs.state.json for a project root."""
    return os.path.join(project_root, ".claude", _STATE_FILENAME)


def state_load(project_root):
    """Load the state file. Returns a dict; empty if missing or corrupt."""
    path = _state_path(project_root)
    if not os.path.isfile(path):
        return {"version": 1, "projects": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "projects" not in data:
            return {"version": 1, "projects": {}}
        return data
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "projects": {}}


def state_save(project_root, state):
    """Persist the state file atomically."""
    path = _state_path(project_root)
    atomic_write(path, json.dumps(state, indent=2, sort_keys=True))


def state_get_project(state, project_id):
    """Get the state record for a project, creating an empty one if missing."""
    projects = state.setdefault("projects", {})
    return projects.setdefault(project_id, {})


def state_update_project(state, project_id, **kwargs):
    """Shallow-merge kwargs into the project's state record."""
    rec = state_get_project(state, project_id)
    rec.update(kwargs)
    return rec


def state_needs_full_sync(project_state):
    """True if the project has never been fully synced or is past the interval."""
    last = project_state.get("last_full_sync")
    if not last:
        return True
    try:
        dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
    except ValueError:
        return True
    return (datetime.now(timezone.utc) - dt) > _FULL_SYNC_INTERVAL


# Trash relocation now lives in conflict_store.trash_move (feature 016): orphans
# move to the per-machine cache, never into the synced specs tree. The legacy
# in-tree implementation (spec 010 phase 3b) was removed here.


# ---------------------------------------------------------------------------
# Doc ID resolution
# ---------------------------------------------------------------------------

def resolve_doc_id(file_path):
    """Resolve a local spec file path to a spec service document ID.

    Returns (cfg, headers, service_url, doc_id, project_id, feature_name, filename).
    Exits on error.
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    abs_path = os.path.abspath(file_path)

    # Try frontmatter first
    if os.path.isfile(abs_path):
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read(2048)
            meta, _ = parse_frontmatter(content)
            if meta.get("spec_doc_id"):
                proj = config.find_project_for_file(cfg, abs_path)
                project_id = proj["id"] if proj else "unknown"
                return cfg, headers, service_url, meta["spec_doc_id"], project_id, "", os.path.basename(abs_path)
        except (IOError, OSError):
            pass

    # Fall back to API lookup
    proj = config.find_project_for_file(cfg, abs_path)
    if not proj:
        print(f"specs: {file_path} is not inside any configured specs path", file=sys.stderr)
        sys.exit(1)

    # Extract feature name from path: .../specs/{feature-name}/{filename}
    rel = os.path.relpath(abs_path, proj["path"])
    parts = rel.replace("\\", "/").split("/")
    if len(parts) < 2:
        print(f"specs: cannot determine feature from path {file_path}", file=sys.stderr)
        sys.exit(1)

    feature_name = parts[0]
    filename = parts[-1]
    feature_id = f"{proj['id']}/{feature_name}"

    import urllib.parse
    encoded_id = urllib.parse.quote(feature_id, safe="")

    try:
        status_code, body = api_request(
            f"{service_url}/api/features/lookup?id={encoded_id}",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to look up feature — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: feature '{feature_id}' not found (HTTP {status_code})", file=sys.stderr)
        sys.exit(1)

    feature_data = json.loads(body)
    documents = feature_data.get("documents", [])
    for doc in documents:
        if doc.get("filename") == filename:
            return cfg, headers, service_url, doc["id"], proj["id"], feature_name, filename

    print(f"specs: document '{filename}' not found in feature '{feature_id}'", file=sys.stderr)
    sys.exit(1)


def _init_and_auth():
    """Common init: read config, get auth headers. Returns (cfg, headers, service_url)."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    return cfg, headers, cfg["service_url"]


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(file_path, as_json=False):
    """List comments on a spec document."""
    _, headers, service_url, doc_id, *_ = resolve_doc_id(file_path)

    try:
        status_code, body = api_request(
            f"{service_url}/api/documents/{doc_id}/comments",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to fetch comments — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: failed to fetch comments (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    comments = json.loads(body)

    if as_json:
        print(json.dumps(comments, indent=2))
        return

    unresolved = [c for c in comments if not c.get("resolved")]
    resolved = [c for c in comments if c.get("resolved")]

    if not comments:
        print("specs: no comments")
        return

    if unresolved:
        print(f"=== Unresolved ({len(unresolved)}) ===\n")
        for c in unresolved:
            _print_comment(c)

    if resolved:
        print(f"=== Resolved ({len(resolved)}) ===\n")
        for c in resolved:
            _print_comment(c)


def _print_comment(c):
    """Print a single comment."""
    author = c.get("author", "?")
    date = c.get("createdAt", "?")[:10]
    body = c.get("body", "")
    ctype = c.get("type", "thread")
    anchor = c.get("anchorText", "")
    comment_id = c.get("id", "?")

    prefix = f"  [{ctype}]" if ctype == "inline" else "  "
    print(f"{prefix} {author} ({date}) [{comment_id}]")
    if anchor:
        print(f"    anchor: \"{anchor}\"")
    print(f"    {body}")
    print()


def add_comment(file_path, body, inline=False, anchor_text=None):
    """Add a comment to a spec document."""
    _, headers, service_url, doc_id, *_ = resolve_doc_id(file_path)

    payload = {"body": body, "type": "inline" if inline else "thread"}
    if inline and anchor_text:
        payload["anchorText"] = anchor_text

    try:
        status_code, resp = api_request(
            f"{service_url}/api/documents/{doc_id}/comments",
            method="POST",
            headers={**headers, "Content-Type": "application/json"},
            data=payload,
        )
    except ConnectionError as e:
        print(f"specs: failed to add comment — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 201):
        print(f"specs: failed to add comment (HTTP {status_code}): {resp}", file=sys.stderr)
        sys.exit(1)

    print("specs: comment added")


def resolve_comment(comment_id):
    """Mark a comment as resolved."""
    _, headers, service_url = _init_and_auth()

    try:
        status_code, resp = api_request(
            f"{service_url}/api/comments/{comment_id}",
            method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"resolved": True},
        )
    except ConnectionError as e:
        print(f"specs: failed to resolve comment — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 201):
        print(f"specs: failed to resolve comment (HTTP {status_code}): {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: comment {comment_id} resolved")


def edit_comment(comment_id, body_text):
    """Edit the body of a spec-doc comment. Author-only on the server."""
    if not body_text or not body_text.strip():
        print("specs: comment body is required", file=sys.stderr)
        sys.exit(1)

    _, headers, service_url = _init_and_auth()

    try:
        status_code, resp = api_request(
            f"{service_url}/api/comments/{comment_id}",
            method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"body": body_text},
        )
    except ConnectionError as e:
        print(f"specs: failed to edit comment — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 403:
        print(f"specs: only the author can edit comment {comment_id}", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 201):
        try:
            err = json.loads(resp).get("error", resp)
        except (json.JSONDecodeError, AttributeError):
            err = resp
        print(f"specs: failed to edit comment (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: comment {comment_id} edited")


def delete_comment(comment_id):
    """Delete a spec-doc comment. Author-only on the server. Hard delete."""
    _, headers, service_url = _init_and_auth()

    try:
        status_code, resp = api_request(
            f"{service_url}/api/comments/{comment_id}",
            method="DELETE",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to delete comment — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 403:
        print(f"specs: only the author can delete comment {comment_id}", file=sys.stderr)
        sys.exit(1)
    if status_code == 404:
        print(f"specs: comment {comment_id} not found", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 204):
        try:
            err = json.loads(resp).get("error", resp)
        except (json.JSONDecodeError, AttributeError):
            err = resp
        print(f"specs: failed to delete comment (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: comment {comment_id} deleted")


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

def list_reviews(file_path, as_json=False):
    """List reviews on a spec document."""
    _, headers, service_url, doc_id, *_ = resolve_doc_id(file_path)

    try:
        status_code, body = api_request(
            f"{service_url}/api/documents/{doc_id}/reviews",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to fetch reviews — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: failed to fetch reviews (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    reviews = json.loads(body)

    if as_json:
        print(json.dumps(reviews, indent=2))
        return

    if not reviews:
        print("specs: no reviews")
        return

    for r in reviews:
        author = r.get("author", "?")
        date = r.get("createdAt", "?")[:10]
        verdict = r.get("verdict", "?")
        rbody = r.get("body", "")
        version = r.get("version", "?")
        marker = "+" if verdict == "approved" else "!"
        print(f"  [{marker}] {author} ({date}) — {verdict} (v{version})")
        if rbody:
            print(f"      {rbody}")
        print()


def submit_review(file_path, verdict, body=None):
    """Submit a review on a spec document."""
    _, headers, service_url, doc_id, *_ = resolve_doc_id(file_path)

    if verdict not in ("approved", "changes_requested"):
        print(f"specs: verdict must be 'approved' or 'changes_requested', got '{verdict}'", file=sys.stderr)
        sys.exit(1)

    payload = {"verdict": verdict}
    if body:
        payload["body"] = body

    try:
        status_code, resp = api_request(
            f"{service_url}/api/documents/{doc_id}/reviews",
            method="POST",
            headers={**headers, "Content-Type": "application/json"},
            data=payload,
        )
    except ConnectionError as e:
        print(f"specs: failed to submit review — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 201):
        print(f"specs: failed to submit review (HTTP {status_code}): {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: review submitted — {verdict}")


# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------

def list_versions(file_path, as_json=False):
    """List version history of a spec document."""
    _, headers, service_url, doc_id, *_ = resolve_doc_id(file_path)

    try:
        status_code, body = api_request(
            f"{service_url}/api/documents/{doc_id}/versions",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to fetch versions — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: failed to fetch versions (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    versions = json.loads(body)

    if as_json:
        print(json.dumps(versions, indent=2))
        return

    if not versions:
        print("specs: no versions")
        return

    for v in versions:
        num = v.get("version", "?")
        author = v.get("author", "?")
        date = v.get("createdAt", "?")[:10]
        summary = v.get("summary", "")
        source = v.get("source", "?")
        print(f"  v{num}  {author} ({date})  [{source}]")
        if summary:
            print(f"    {summary}")
        print()


def save_version(file_path, summary, source="manual"):
    """Save the current file as a new named version in the spec service."""
    _, headers, service_url, doc_id, *_ = resolve_doc_id(file_path)

    abs_path = os.path.abspath(file_path)
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (IOError, OSError) as e:
        print(f"specs: cannot read {file_path} — {e}", file=sys.stderr)
        sys.exit(1)

    _, body = parse_frontmatter(content)

    payload = {
        "content": body.strip(),
        "summary": summary,
        "source": source,
    }

    try:
        status_code, resp = api_request(
            f"{service_url}/api/documents/{doc_id}/versions",
            method="POST",
            headers={**headers, "Content-Type": "application/json"},
            data=payload,
        )
    except ConnectionError as e:
        print(f"specs: failed to save version — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 201):
        print(f"specs: failed to save version (HTTP {status_code}): {resp}", file=sys.stderr)
        sys.exit(1)

    try:
        resp_data = json.loads(resp)
        version_num = resp_data.get("version", "?")
    except (json.JSONDecodeError, AttributeError):
        version_num = "?"

    print(f"specs: saved version v{version_num} — {summary}")


# ---------------------------------------------------------------------------
# Service status
# ---------------------------------------------------------------------------

def service_status():
    """Check spec service health."""
    _, headers, service_url = _init_and_auth()

    try:
        status_code, body = api_request(f"{service_url}/api/status", headers=headers)
    except ConnectionError as e:
        print(f"specs: service unreachable — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: service returned HTTP {status_code}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: service OK")
    try:
        data = json.loads(body)
        for k, v in data.items():
            print(f"  {k}: {v}")
    except json.JSONDecodeError:
        pass


# ---------------------------------------------------------------------------
# Pull (single project)
# ---------------------------------------------------------------------------

def _scan_local_specs(specs_path):
    """Walk a specs directory and index existing files by spec_doc_id.

    Returns a dict: { doc_id: absolute_path }. Files without a spec_doc_id
    in their frontmatter are skipped — they're either draft specs not yet
    registered with the service, or unrelated markdown.
    """
    index = {}
    if not os.path.isdir(specs_path):
        return index
    for root, dirs, files in os.walk(specs_path):
        # Never recurse into the trash
        if ".specs-trash" in dirs:
            dirs.remove(".specs-trash")
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read(4096)
            except (IOError, OSError):
                continue
            meta, _ = parse_frontmatter(content)
            doc_id = meta.get("spec_doc_id")
            if doc_id:
                index[doc_id] = fpath
    return index


def _migrate_in_tree_sidecars(specs_path, project_id, quiet=False):
    """Relocate any legacy in-tree `*.remote` sidecars into the conflict store.

    Feature 016: older plugin versions wrote `<doc>.md.remote` beside the local
    doc, inside the synced tree. On the first pull after upgrade we read each
    one, stage it out-of-tree (keyed by its `spec_doc_id`), and delete the
    in-tree file — so OneDrive stops forking it. Best-effort: anything we can't
    parse is left for `cleanup-synced-tree` to remove.

    Returns the number of sidecars migrated.
    """
    if not os.path.isdir(specs_path):
        return 0
    migrated = 0
    for root, dirs, files in os.walk(specs_path):
        if ".specs-trash" in dirs:
            dirs.remove(".specs-trash")
        for fname in files:
            if not fname.endswith(".remote"):
                continue
            sidecar = os.path.join(root, fname)
            try:
                with open(sidecar, "r", encoding="utf-8") as f:
                    remote_text = f.read()
            except (IOError, OSError):
                continue
            meta, _ = parse_frontmatter(remote_text)
            doc_id = meta.get("spec_doc_id")
            local_path = sidecar[: -len(".remote")]  # strip the suffix
            if not doc_id or not conflict_store.ensure_writable():
                continue
            # base_hash = the local doc's last-synced hash at conflict time, if
            # we can still read it; otherwise fall back to the remote hash.
            base_hash = meta.get("last_synced_hash", "")
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    lmeta, _ = parse_frontmatter(f.read())
                base_hash = lmeta.get("last_synced_hash", base_hash)
            except (IOError, OSError):
                pass
            try:
                conflict_store.stage(
                    doc_id, remote_text,
                    local_path=local_path,
                    project_id=project_id,
                    remote_hash=meta.get("last_synced_hash", ""),
                    base_hash=base_hash,
                )
                os.unlink(sidecar)
                migrated += 1
            except OSError:
                continue
    if migrated and not quiet:
        print(f"specs: {project_id} — migrated {migrated} in-tree .remote sidecar(s) to the conflict store")
    return migrated


def pull_project(
    project_id,
    specs_path,
    service_url,
    headers,
    state=None,
    delete_mode="trash",
    force_full=False,
    quiet=False,
):
    """Pull specs for a single project.

    Returns a dict with counts and outcomes:
        {
            "synced": int,          # files written (new or updated)
            "unchanged": int,       # hash matched, possibly frontmatter retouched
            "trashed": int,         # local files orphaned by remote deletion
            "conflicts": list[str], # local paths whose remote side was staged out-of-tree
            "skipped_errors": int,  # transient failures mid-pull
            "cursor": str | None,   # advanced if the manifest returned one
        }

    Parameters (spec 010 phase 3b + 4):
      state        — the loaded state dict (from state_load); mutated in place
                     to record last_sync_cursor and last_full_sync. Pass None
                     to skip state management.
      delete_mode  — "trash" (default), "prune" (hard delete), or "keep"
                     (leave orphans alone)
      force_full   — bypass delta sync and always fetch the full manifest
    """
    report = {
        "synced": 0,
        "unchanged": 0,
        "trashed": 0,
        "conflicts": [],
        "skipped_errors": 0,
        "cursor": None,
    }

    manifest_url = f"{service_url}/api/sync/projects/{project_id}/manifest"
    try:
        status, body = api_request(manifest_url, headers=headers)
    except ConnectionError as e:
        if not quiet:
            print(f"specs: pull failed for '{project_id}' — {e}", file=sys.stderr)
        return report

    if status == 401:
        if not quiet:
            print("specs: authentication expired — run /awolve-spec:login", file=sys.stderr)
        return report
    if status == 404:
        if not quiet:
            print(f"specs: project '{project_id}' not found", file=sys.stderr)
        return report
    if status != 200:
        if not quiet:
            print(f"specs: manifest failed for '{project_id}' (HTTP {status})", file=sys.stderr)
        return report

    manifest = json.loads(body)
    documents = manifest.get("documents", [])
    remote_attachments = manifest.get("attachments", [])
    manifest_cursor = manifest.get("cursor")

    os.makedirs(specs_path, exist_ok=True)

    # Feature 016: relocate any legacy in-tree `.remote` sidecars before we
    # process docs, then pre-load the set of staged conflicts so the self-heal
    # below (clear-on-reconcile) costs no I/O for the common no-conflict doc.
    _migrate_in_tree_sidecars(specs_path, project_id, quiet=quiet)
    staged_conflicts = conflict_store.staged_ids()

    # Index remote doc ids so we can find local orphans at the end.
    remote_doc_ids = {doc["id"] for doc in documents}

    for doc in documents:
        doc_id = doc["id"]
        feature_name = doc.get("feature", "general")
        filename = doc.get("filename", f"{doc_id}.md")
        remote_hash = doc.get("content_hash", "")
        version = doc.get("version", 1)
        feature_status = doc.get("feature_status", "")
        doc_status = doc.get("doc_status", "")
        source_url = doc.get("source_url", "")

        local_dir = os.path.join(specs_path, feature_name)
        local_path = os.path.join(local_dir, filename)

        # ---- Hash-match fast path ----
        if os.path.isfile(local_path):
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    local_content = f.read()
                local_hash = file_content_hash(local_content)
                if local_hash == remote_hash:
                    # Content matches — update frontmatter if version/status drifted
                    local_meta, local_body = parse_frontmatter(local_content)
                    if (local_meta.get("spec_version") != version or
                        local_meta.get("feature_status", "") != feature_status or
                        local_meta.get("doc_status", "") != doc_status or
                        local_meta.get("last_synced_hash") != remote_hash):
                        local_meta["spec_version"] = version
                        local_meta["last_synced_hash"] = remote_hash
                        if feature_status:
                            local_meta["feature_status"] = feature_status
                        if doc_status:
                            local_meta["doc_status"] = doc_status
                        atomic_write(local_path, render_frontmatter(local_meta, local_body))
                    # Self-heal: local now matches remote, so any previously
                    # staged conflict for this doc is reconciled — clear it.
                    if doc_id in staged_conflicts:
                        conflict_store.clear(doc_id)
                    report["unchanged"] += 1
                    continue

                # ---- Hash mismatch: check for local drift before overwriting ----
                local_meta, _ = parse_frontmatter(local_content)
                last_synced_hash = local_meta.get("last_synced_hash")
                if last_synced_hash and last_synced_hash != local_hash:
                    # Local was modified since last sync AND remote has also
                    # changed. Feature 016: stage the remote side OUT OF TREE
                    # (in the per-machine cache, keyed by doc_id), leave local
                    # alone, report the conflict. We never write beside the
                    # local doc — that is what OneDrive forks across machines.
                    content_url = f"{service_url}/api/sync/documents/{doc_id}/content"
                    try:
                        dl_status, dl_body = api_request(content_url, headers=headers)
                    except ConnectionError:
                        report["skipped_errors"] += 1
                        continue
                    if dl_status != 200:
                        report["skipped_errors"] += 1
                        continue
                    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    sidecar_meta = {
                        "spec_version": version,
                        "spec_doc_id": doc_id,
                        "last_synced": now,
                        "last_synced_hash": remote_hash,
                    }
                    if feature_status:
                        sidecar_meta["feature_status"] = feature_status
                    if doc_status:
                        sidecar_meta["doc_status"] = doc_status
                    if source_url:
                        sidecar_meta["source"] = source_url
                    remote_text = render_frontmatter(sidecar_meta, dl_body)
                    if conflict_store.ensure_writable():
                        try:
                            conflict_store.stage(
                                doc_id, remote_text,
                                local_path=local_path,
                                project_id=project_id,
                                remote_hash=remote_hash,
                                base_hash=last_synced_hash,
                            )
                            staged_conflicts.add(doc_id)
                        except OSError:
                            # Cache write failed — never fall back to an
                            # in-tree write; just report the conflict.
                            report["conflict_unstaged"] = report.get("conflict_unstaged", 0) + 1
                    else:
                        report["conflict_unstaged"] = report.get("conflict_unstaged", 0) + 1
                    report["conflicts"].append(local_path)
                    continue
            except (IOError, OSError):
                pass

        # ---- Download + write (new file or remote-newer, no local drift) ----
        content_url = f"{service_url}/api/sync/documents/{doc_id}/content"
        try:
            dl_status, dl_body = api_request(content_url, headers=headers)
        except ConnectionError:
            report["skipped_errors"] += 1
            continue

        if dl_status != 200:
            report["skipped_errors"] += 1
            continue

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        meta = {
            "spec_version": version,
            "spec_doc_id": doc_id,
            "last_synced": now,
            "last_synced_hash": remote_hash,
        }
        if feature_status:
            meta["feature_status"] = feature_status
        if doc_status:
            meta["doc_status"] = doc_status
        if source_url:
            meta["source"] = source_url

        atomic_write(local_path, render_frontmatter(meta, dl_body))
        # Self-heal: we just wrote remote over local, so any staged conflict
        # for this doc is now reconciled — clear it.
        if doc_id in staged_conflicts:
            conflict_store.clear(doc_id)
        report["synced"] += 1

    # ---- Binary attachments ----
    for att in remote_attachments:
        att_id = att.get("id")
        feature_name = att.get("feature")
        filename = att.get("filename")
        size = att.get("size_bytes", 0)
        if not att_id or not feature_name or not filename:
            continue

        local_dir = os.path.join(specs_path, feature_name)
        local_path = os.path.join(local_dir, filename)

        if os.path.isfile(local_path):
            try:
                if os.path.getsize(local_path) == size:
                    report["unchanged"] += 1
                    continue
            except OSError:
                pass

        dl_url = f"{service_url}/api/sync/attachments/{att_id}"
        try:
            req = urllib.request.Request(dl_url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=60) as resp:
                content = resp.read()
        except (urllib.error.HTTPError, urllib.error.URLError, ConnectionError) as e:
            if not quiet:
                print(f"specs: attachment download failed for '{filename}' — {e}", file=sys.stderr)
            report["skipped_errors"] += 1
            continue

        try:
            atomic_write(local_path, content, binary=True)
            report["synced"] += 1
        except OSError as e:
            if not quiet:
                print(f"specs: failed to write attachment '{local_path}' — {e}", file=sys.stderr)
            report["skipped_errors"] += 1
            continue

    # ---- Deletion handling: trash / prune / keep ----
    if delete_mode != "keep":
        local_index = _scan_local_specs(specs_path)
        for doc_id, local_path in local_index.items():
            if doc_id in remote_doc_ids:
                continue
            # Orphan — not in remote manifest
            try:
                if delete_mode == "prune":
                    os.unlink(local_path)
                else:
                    # Feature 016: trash lands in the per-machine cache, never
                    # in the synced tree.
                    conflict_store.trash_move(project_id, local_path, specs_path)
                report["trashed"] += 1
            except OSError as e:
                if not quiet:
                    print(f"specs: could not {delete_mode} orphan '{local_path}' — {e}", file=sys.stderr)

    # ---- Advance sync cursor + full-sync timestamp ----
    if manifest_cursor:
        report["cursor"] = manifest_cursor
        if state is not None:
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            state_update_project(
                state,
                project_id,
                last_sync_cursor=manifest_cursor,
                last_full_sync=now_iso,
                last_pulled_at=now_iso,
            )

    return report


# ---------------------------------------------------------------------------
# Pull (all projects)
# ---------------------------------------------------------------------------

def pull(project_filter=None, quiet=False, delete_mode="trash", force_full=False):
    """Pull specs for all configured projects (or a specific one)."""
    cfg = config.read_config()
    if not cfg:
        if not quiet:
            print("specs: no config found — create .claude/specs.md or .claude/specs.local.md", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        if not quiet:
            print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    projects = cfg["projects"]
    project_root = cfg["project_root"]

    if project_filter:
        projects = [p for p in projects if p["id"] == project_filter]
        if not projects:
            print(f"specs: project '{project_filter}' not in config", file=sys.stderr)
            sys.exit(1)

    # Load the sync state file once; pull_project mutates it per project.
    state = state_load(project_root)

    total_synced = 0
    total_unchanged = 0
    total_trashed = 0
    total_conflicts = []
    total_errors = 0

    for proj in projects:
        report = pull_project(
            proj["id"], proj["path"], service_url, headers,
            state=state,
            delete_mode=delete_mode,
            force_full=force_full,
            quiet=quiet,
        )
        total_synced += report["synced"]
        total_unchanged += report["unchanged"]
        total_trashed += report["trashed"]
        total_conflicts.extend(report["conflicts"])
        total_errors += report["skipped_errors"]

        if not quiet:
            parts = []
            if report["synced"]:
                parts.append(f"{report['synced']} updated")
            if report["unchanged"]:
                parts.append(f"{report['unchanged']} unchanged")
            if report["trashed"]:
                label = "pruned" if delete_mode == "prune" else "trashed"
                parts.append(f"{report['trashed']} {label}")
            if report["conflicts"]:
                parts.append(f"{len(report['conflicts'])} conflict{'s' if len(report['conflicts']) != 1 else ''}")
            if report["skipped_errors"]:
                parts.append(f"{report['skipped_errors']} errors")
            if parts:
                print(f"specs: {proj['id']} — {', '.join(parts)}")

    # Persist state after all projects processed so partial failures don't
    # leave a stale cursor (we still advance per-project in pull_project).
    try:
        state_save(project_root, state)
    except OSError as e:
        if not quiet:
            print(f"specs: warning — failed to save state: {e}", file=sys.stderr)

    if not quiet:
        if total_conflicts:
            print()
            print(f"specs: {len(total_conflicts)} conflict{'s' if len(total_conflicts) != 1 else ''} — local drift + remote change:", file=sys.stderr)
            for path in total_conflicts:
                print(f"  {path}", file=sys.stderr)
            print("  The remote side is staged out-of-tree (nothing written beside your files).", file=sys.stderr)
            print("  Inspect with:  specs-cli.py conflicts", file=sys.stderr)
            print("  Resolve with:  specs-cli.py conflict resolve <doc> --theirs|--mine|--merged <file>", file=sys.stderr)
        if total_synced == 0 and total_unchanged == 0 and total_trashed == 0 and not total_conflicts:
            print(f"specs: pulled {len(projects)} project(s) — no changes")


# ---------------------------------------------------------------------------
# Log — stream audit events for a project (spec 010 phase 4)
# ---------------------------------------------------------------------------

_ENTITY_BADGES = {
    "feature":        ("feat",   "\033[35m"),
    "document":       ("doc",    "\033[34m"),
    "version":        ("ver",    "\033[32m"),
    "comment":        ("cmt",    "\033[33m"),
    "review":         ("rev",    "\033[95m"),
    "backlog":        ("bklg",   "\033[36m"),
    "bug":            ("bug",    "\033[31m"),
    "bug_comment":    ("bug·c",  "\033[31m"),
    "attachment":     ("att",    "\033[37m"),
    "project":        ("proj",   "\033[96m"),
    "project_access": ("access", "\033[91m"),
    "project_domain": ("domain", "\033[92m"),
    "client":         ("client", "\033[35m"),
    "portal_user":    ("user",   "\033[95m"),
    "api_key":        ("key",    "\033[33m"),
    "auth_token":     ("token",  "\033[33m"),
    "system":         ("sys",    "\033[90m"),
}
_RESET = "\033[0m"
_DIM = "\033[2m"
_BOLD = "\033[1m"


def _parse_since(since_str):
    """Parse '--since' into a duration or absolute date.

    Accepts:
      '7d', '24h', '30m'  — durations relative to now
      '2026-04-01'         — absolute ISO date

    Returns a datetime in UTC, or None if the string can't be parsed.
    """
    if not since_str:
        return None
    s = since_str.strip()
    # Duration: Nd, Nh, Nm, Nw
    m = re.match(r"^(\d+)([smhdw])$", s)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        delta = {
            "s": timedelta(seconds=n),
            "m": timedelta(minutes=n),
            "h": timedelta(hours=n),
            "d": timedelta(days=n),
            "w": timedelta(weeks=n),
        }[unit]
        return datetime.now(timezone.utc) - delta
    # Absolute ISO date/datetime
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _relative_time(iso_str):
    """Relative time for log display — e.g. '3m ago', '2h ago', '5d ago'."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except ValueError:
        return iso_str
    diff = datetime.now(timezone.utc) - dt
    secs = int(diff.total_seconds())
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{secs // 60}m ago"
    if secs < 86400:
        return f"{secs // 3600}h ago"
    if secs < 86400 * 7:
        return f"{secs // 86400}d ago"
    return dt.strftime("%Y-%m-%d")


def specs_log(
    project_id,
    since=None,
    author=None,
    entity_type=None,
    limit=50,
    as_json=False,
    since_last_visit=False,
    mark_read=False,
):
    """Stream audit events for a project, or for all configured projects when
    project_id is None (`--all`). Events from every project are merged and
    sorted by timestamp so "what happened yesterday" works across the whole
    workspace.
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found — create .claude/specs.md or .claude/specs.local.md", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    # Pick the project list: one specific project, or all configured ones
    if project_id is None:
        projects_to_query = cfg["projects"]
        if not projects_to_query:
            print("specs: no projects configured", file=sys.stderr)
            sys.exit(1)
    else:
        if not any(p["id"] == project_id for p in cfg["projects"]):
            print(f"specs: project '{project_id}' not in config", file=sys.stderr)
            sys.exit(1)
        projects_to_query = [p for p in cfg["projects"] if p["id"] == project_id]

    service_url = cfg["service_url"]
    project_root = cfg["project_root"]
    state = state_load(project_root)

    # Build the per-project query params (same for each project except since-cursor)
    base_qs = {"limit": str(min(max(limit, 1), 1000))}

    # Only apply current-user filter for --since-last-visit (matches prior behavior)
    if since_last_visit:
        base_qs["order"] = "asc"  # chronological so we can find the newest event
        current_actor = headers.get("X-Actor") or _current_user_email(headers)
        if current_actor:
            base_qs["actor_not"] = current_actor
    else:
        base_qs["order"] = "desc"

    if author:
        base_qs["actor"] = author
    if entity_type:
        base_qs["entity_type"] = entity_type

    from urllib.parse import urlencode

    # Fetch from every selected project, attach project_id to each event so
    # the display can call it out, and merge.
    all_events = []
    per_project_newest = {}  # project_id → newest event id (for --mark-read)
    errors = []

    for proj in projects_to_query:
        pid = proj["id"]
        qs = dict(base_qs)
        if since_last_visit:
            proj_state = state_get_project(state, pid)
            cursor = proj_state.get("last_visit_cursor")
            if cursor:
                qs["since"] = cursor

        url = f"{service_url}/api/sync/projects/{pid}/changes?{urlencode(qs)}"
        try:
            status, body = api_request(url, headers=headers)
        except ConnectionError as e:
            errors.append(f"{pid}: {e}")
            continue

        if status == 401:
            print("specs: authentication expired — run /awolve-spec:login", file=sys.stderr)
            sys.exit(1)
        if status != 200:
            errors.append(f"{pid}: HTTP {status}")
            continue

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            errors.append(f"{pid}: invalid JSON response")
            continue

        project_events = data.get("events", [])
        # Tag each event with its project id so multi-project output can show it
        for ev in project_events:
            ev["_projectId"] = pid
        all_events.extend(project_events)

        if project_events:
            # Record newest id for --mark-read regardless of order direction
            ids = [e["id"] for e in project_events]
            per_project_newest[pid] = max(ids)

    # Client-side --since filter (display convenience; server pages on ids, not timestamps)
    since_dt = _parse_since(since)
    if since_dt:
        all_events = [
            e for e in all_events
            if _parse_iso(e.get("createdAt", "")) and _parse_iso(e["createdAt"]) >= since_dt
        ]

    # Merge: sort by id (ULIDs sort lexicographically by time). Display order
    # matches the per-project order chosen above.
    all_events.sort(key=lambda e: e["id"], reverse=(base_qs["order"] == "desc"))

    # Apply the combined limit after the merge — otherwise "--limit 50 --all"
    # would return up to 50 × N projects events.
    all_events = all_events[: int(base_qs["limit"])]

    if as_json:
        print(json.dumps(all_events, indent=2))
    else:
        multi_project = len(projects_to_query) > 1
        _print_log_events(all_events, since_last_visit=since_last_visit, multi_project=multi_project)

    # --mark-read: advance the visit cursor per project
    if mark_read and per_project_newest:
        for pid, newest_id in per_project_newest.items():
            state_update_project(state, pid, last_visit_cursor=newest_id)
        try:
            state_save(project_root, state)
            if project_id is None:
                print(f"\nspecs: marked {len(per_project_newest)} project(s) read", file=sys.stderr)
            else:
                print(f"\nspecs: marked read up to {per_project_newest[project_id]}", file=sys.stderr)
        except OSError as e:
            print(f"specs: warning — failed to save state: {e}", file=sys.stderr)

    # Surface per-project errors at the end so they don't drown out successes
    for err in errors:
        print(f"specs: log skipped {err}", file=sys.stderr)


def _print_log_events(events, since_last_visit=False, multi_project=False):
    """Render log events in human-readable colored output.

    When `multi_project` is True, each row is prefixed with the originating
    project id so a merged cross-project feed stays legible.
    """
    if not events:
        if since_last_visit:
            print("(no new events since your last visit)")
        else:
            print("(no events)")
        return

    # Compute column width for project id so the output stays aligned
    proj_width = 0
    if multi_project:
        proj_width = max((len(ev.get("_projectId", "")) for ev in events), default=0)

    # Group by day
    last_day = None
    for ev in events:
        try:
            dt = datetime.fromisoformat(ev["createdAt"].replace("Z", "+00:00"))
        except ValueError:
            continue
        day = dt.strftime("%Y-%m-%d")
        if day != last_day:
            if last_day is not None:
                print()
            print(f"{_BOLD}{day}{_RESET}")
            last_day = day

        badge_label, badge_color = _ENTITY_BADGES.get(
            ev["entityType"], (ev["entityType"][:6], "\033[37m"),
        )
        time_str = dt.strftime("%H:%M")
        relative = _relative_time(ev["createdAt"])
        proj_prefix = ""
        if multi_project:
            proj_prefix = f"{_DIM}[{ev.get('_projectId', '?'):{proj_width}}]{_RESET}  "
        print(
            f"  {_DIM}{time_str}{_RESET}  "
            f"{proj_prefix}"
            f"{badge_color}{badge_label:>8}{_RESET}  "
            f"{ev['summary']}  "
            f"{_DIM}— {ev['actor']} · {relative}{_RESET}"
        )


def _parse_iso(s):
    """Parse an ISO timestamp, returning None on failure."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _current_user_email(headers):
    """Best-effort lookup of the current user's email from the auth state.

    Used by `--since-last-visit` to set actor_not. Falls back to None if we
    can't determine it — in which case the user will see their own events
    in the feed, but nothing breaks.
    """
    try:
        return auth.get_current_user_email()  # type: ignore[attr-defined]
    except AttributeError:
        return None


# ---------------------------------------------------------------------------
# Push
# ---------------------------------------------------------------------------

def push(file_path, base_version_override=None):
    """Push a single spec file to the service.

    Returns True on success (or a no-op skip — server already has this exact
    content), False on a 409 conflict. `base_version_override` forces the
    base_version sent to the server (used by `conflict resolve --mine/--merged`
    to push the local side over a remote that advanced past the local
    frontmatter's recorded version).
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found — create .claude/specs.md or .claude/specs.local.md", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    abs_path = os.path.abspath(file_path)

    # Find which project this file belongs to
    proj = config.find_project_for_file(cfg, abs_path)
    if not proj:
        print(f"specs: {file_path} is not inside any configured specs path", file=sys.stderr)
        sys.exit(1)

    # Read file
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (IOError, OSError) as e:
        print(f"specs: cannot read {file_path} — {e}", file=sys.stderr)
        sys.exit(1)

    meta, body = parse_frontmatter(content)
    doc_id = meta.get("spec_doc_id")
    base_version = meta.get("spec_version")

    if not doc_id:
        print(f"specs: {file_path} has no spec_doc_id — skipping", file=sys.stderr)
        return False

    if base_version_override is not None:
        base_version = base_version_override

    if base_version is None:
        print(f"specs: {file_path} has no spec_version — skipping", file=sys.stderr)
        return False

    # Safety: strip any leaked frontmatter from body (e.g. double frontmatter)
    body = strip_frontmatter(body)

    # Bug #2: skip push + writeback when body hash matches last_synced_hash.
    # Server already has this exact content; pushing anyway re-runs the
    # frontmatter writeback (atomic_write of tempfile + rename), which OneDrive
    # observes as a write event. Concurrent writers + repeated no-op writes are
    # exactly what produces .remote conflict copies. This skip-on-no-change
    # gate cuts the rate of OneDrive-visible writes to roughly the rate of
    # *real* content changes.
    body_hash = hashlib.sha256(body.strip().encode("utf-8")).hexdigest()
    last_hash = meta.get("last_synced_hash")
    if last_hash and last_hash == body_hash:
        return True

    # Push
    push_url = f"{service_url}/api/sync/documents/{doc_id}/content?base_version={base_version}"
    headers["Content-Type"] = "text/markdown; charset=utf-8"

    try:
        status_code, resp_body = api_request(push_url, method="PUT", headers=headers, data=body.strip())
    except ConnectionError as e:
        print(f"specs: push failed — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 409:
        print(f"specs: CONFLICT — remote has newer version. Pull first.", file=sys.stderr)
        return False
    if status_code == 401:
        print("specs: authentication expired — run /awolve-spec:login", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 201, 204):
        print(f"specs: push failed (HTTP {status_code}): {resp_body}", file=sys.stderr)
        sys.exit(1)

    # Update local frontmatter
    try:
        resp_data = json.loads(resp_body) if resp_body.strip() else {}
    except json.JSONDecodeError:
        resp_data = {}

    new_version = resp_data.get("version", base_version + 1)
    meta["spec_version"] = new_version
    meta["last_synced"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Record the body hash we just pushed so future pulls can detect local
    # drift correctly. Without this, a subsequent manual edit would look
    # indistinguishable from an unmodified synced file.
    meta["last_synced_hash"] = hashlib.sha256(body.strip().encode("utf-8")).hexdigest()

    atomic_write(abs_path, render_frontmatter(meta, body))

    rel = os.path.relpath(abs_path, proj["path"])
    print(f"specs: pushed {proj['id']}/{rel} (v{new_version})")
    return True


# ---------------------------------------------------------------------------
# Conflicts — staged out-of-tree (feature 016)
# ---------------------------------------------------------------------------

def list_conflicts_cmd(project_filter=None, as_json=False):
    """List staged conflicts from the out-of-tree store."""
    entries = conflict_store.list_conflicts(project_filter=project_filter)
    if as_json:
        out = [
            {"doc_id": doc_id, **entry}
            for doc_id, entry in entries
        ]
        print(json.dumps(out, indent=2))
        return
    if not entries:
        print("specs: no staged conflicts")
        return
    print(f"specs: {len(entries)} staged conflict{'s' if len(entries) != 1 else ''}:")
    for doc_id, entry in entries:
        local = entry.get("local_path", "?")
        proj = entry.get("project_id", "?")
        staged = entry.get("staged_at", "?")
        print(f"  [{proj}] {local}")
        print(f"      doc {doc_id} · staged {staged}")
    print()
    print("  conflict show <doc> | conflict diff <doc> | conflict resolve <doc> --theirs|--mine|--merged <file>")


def _resolve_conflict_ref(ref):
    """Resolve a conflict command arg to (doc_id, entry, remote_text). Exits on miss."""
    doc_id = conflict_store.find_by_ref(ref)
    if not doc_id:
        print(f"specs: no staged conflict for '{ref}' — run 'specs-cli.py conflicts' to list", file=sys.stderr)
        sys.exit(1)
    entry, remote_text = conflict_store.get(doc_id)
    if remote_text is None:
        print(f"specs: staged remote for '{ref}' is missing — re-run 'specs-cli.py pull'", file=sys.stderr)
        sys.exit(1)
    return doc_id, entry, remote_text


def conflict_show(ref):
    """Print the staged remote side of a conflict."""
    _doc_id, _entry, remote_text = _resolve_conflict_ref(ref)
    sys.stdout.write(remote_text)
    if not remote_text.endswith("\n"):
        sys.stdout.write("\n")


def conflict_diff(ref):
    """Print a unified diff: local doc vs staged remote."""
    import difflib
    _doc_id, entry, remote_text = _resolve_conflict_ref(ref)
    local_path = entry.get("local_path", "")
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            local_text = f.read()
    except (IOError, OSError):
        local_text = ""
    diff = difflib.unified_diff(
        local_text.splitlines(keepends=True),
        remote_text.splitlines(keepends=True),
        fromfile=f"{local_path} (local)",
        tofile=f"{local_path} (remote/staged)",
    )
    sys.stdout.writelines(diff)


def conflict_resolve(ref, mode, merged_file=None):
    """Resolve a staged conflict.

    --theirs   overwrite the local doc with the staged remote, clear the entry.
    --mine     push the local doc over the remote (advancing past its version).
    --merged   write a hand-merged file into the local doc, then push it.
    """
    doc_id, entry, remote_text = _resolve_conflict_ref(ref)
    local_path = entry.get("local_path", "")

    if mode == "theirs":
        atomic_write(local_path, remote_text)
        conflict_store.clear(doc_id)
        print(f"specs: resolved {doc_id} with the remote copy ({local_path})")
        return

    # --mine / --merged both push the local side. The remote advanced past the
    # local frontmatter's spec_version, so push with the staged remote version
    # as the base (parsed from the staged remote text).
    remote_meta, _ = parse_frontmatter(remote_text)
    remote_version = remote_meta.get("spec_version")
    if remote_version is None:
        print("specs: staged remote has no spec_version — re-run pull", file=sys.stderr)
        sys.exit(1)

    if mode == "merged":
        if not merged_file:
            print("specs: --merged requires a file path", file=sys.stderr)
            sys.exit(1)
        try:
            with open(merged_file, "r", encoding="utf-8") as f:
                merged_content = f.read()
        except (IOError, OSError) as e:
            print(f"specs: cannot read merged file '{merged_file}' — {e}", file=sys.stderr)
            sys.exit(1)
        # Write the merged body into the local doc, preserving its identity
        # frontmatter (spec_doc_id), so push() sends the merged content.
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                local_meta, _ = parse_frontmatter(f.read())
        except (IOError, OSError):
            local_meta = {}
        merged_meta, merged_body = parse_frontmatter(merged_content)
        # Caller may pass either a full doc or just a body; prefer the local
        # identity fields, fall back to whatever the merged file carried.
        local_meta.setdefault("spec_doc_id", merged_meta.get("spec_doc_id", doc_id))
        atomic_write(local_path, render_frontmatter(local_meta, merged_body))

    ok = push(local_path, base_version_override=remote_version)
    if ok:
        conflict_store.clear(doc_id)
        print(f"specs: resolved {doc_id} with the local copy")
    else:
        print("specs: remote moved again — run 'specs-cli.py pull' then resolve once more.", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# cleanup-synced-tree — purge legacy in-tree artifacts (feature 016)
# ---------------------------------------------------------------------------

def cleanup_synced_tree(dry_run=False, include_venv=False):
    """Remove sync/build artifacts wrongly left inside the synced tree.

    Targets: `*.remote` sidecars, OneDrive conflict copies, legacy
    `.specs-trash/` dirs, and (with --include-venv) `_gen/.venv/` build dirs in
    the wider libraries. Canonical docs, `_gen/*.py` scripts, and generated
    outputs are never matched (classification is anchored in conflict_store).

    Single-machine deletion loses the race against peers' session-start pulls,
    so this prints a coordination warning — a durable purge needs peers'
    OneDrive paused (or a server-side delete).
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    # Roots: every configured specs path; with --include-venv also the wider
    # synced libraries that sit beside the repo (files/, *-context/), reached
    # via the project_root's siblings if present.
    roots = [p["path"] for p in cfg["projects"]]
    if include_venv:
        project_root = cfg.get("project_root", "")
        for name in ("files", "founders-files", "awolve-context",
                     "founders-context", "handbook-context", "my-cortex"):
            candidate = os.path.join(project_root, name)
            if os.path.isdir(candidate) and candidate not in roots:
                roots.append(candidate)

    counts = {"remote_sidecar": 0, "conflict_copy": 0, "artifact_dir": 0}
    targets = []  # (category, path, is_dir)
    seen_roots = set()

    for root in roots:
        if not os.path.isdir(root) or root in seen_roots:
            continue
        seen_roots.add(root)
        for dirpath, dirnames, filenames in os.walk(root):
            # Match artifact dirs and prune them from the walk so we don't
            # descend into a .venv with thousands of files.
            for d in list(dirnames):
                # `.venv` only counts when --include-venv (it's a build dir,
                # not a specs artifact); `.specs-trash` always counts.
                if conflict_store.is_artifact_dir(d) and (include_venv or d == ".specs-trash"):
                    targets.append(("artifact_dir", os.path.join(dirpath, d), True))
                    counts["artifact_dir"] += 1
                    dirnames.remove(d)
            for fname in filenames:
                cat = conflict_store.classify(fname, is_dir=False)
                if cat:
                    targets.append((cat, os.path.join(dirpath, fname), False))
                    counts[cat] += 1

    total = len(targets)
    label = "Would remove" if dry_run else "Removed"
    if total == 0:
        print("specs: synced tree is clean — no artifacts found")
        return

    for cat, path, is_dir in targets:
        if not dry_run:
            try:
                if is_dir:
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
            except OSError as e:
                print(f"specs: could not remove {path} — {e}", file=sys.stderr)
                continue
        kind = "dir " if is_dir else "file"
        print(f"  {kind} [{cat}] {path}")

    print()
    print(f"specs: {label} {total} artifact(s) — "
          f"{counts['remote_sidecar']} .remote, "
          f"{counts['conflict_copy']} conflict copies, "
          f"{counts['artifact_dir']} dirs")
    if not dry_run:
        print()
        print("  NOTE: single-machine deletion loses the race against peers' session-start", file=sys.stderr)
        print("  pulls. For a durable purge, run with every peer's OneDrive paused (or", file=sys.stderr)
        print("  delete server-side), then confirm with /cortex-doctor-content.", file=sys.stderr)


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def show_status():
    """Show sync status of all configured projects."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found — create .claude/specs.md or .claude/specs.local.md — create .claude/specs.md (shared) or .claude/specs.local.md (personal)", file=sys.stderr)
        sys.exit(1)

    print(f"specs: {len(cfg['projects'])} project(s) configured")
    print(f"  service: {cfg['service_url']}")
    print()

    for proj in cfg["projects"]:
        specs_path = proj["path"]
        print(f"  {proj['id']}")
        print(f"    path: {specs_path}")

        if not os.path.isdir(specs_path):
            print(f"    (directory not found)")
            print()
            continue

        found = 0
        for root, _dirs, files in os.walk(specs_path):
            for fname in sorted(files):
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read(2048)
                except (IOError, OSError):
                    continue
                meta, _ = parse_frontmatter(content)
                if not meta.get("spec_doc_id"):
                    continue
                rel = os.path.relpath(fpath, specs_path)
                version = meta.get("spec_version", "?")
                last_synced = meta.get("last_synced", "never")
                print(f"    {rel:40s}  v{version}  synced: {last_synced}")
                found += 1

        if found == 0:
            print(f"    (no synced spec files)")
        print()


# ---------------------------------------------------------------------------
# PostToolUse hook
# ---------------------------------------------------------------------------

def handle_post_tool_use():
    """Read PostToolUse JSON from stdin. Push if a spec file was edited."""
    try:
        raw = sys.stdin.read()
    except Exception:
        return

    if not raw.strip():
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return

    cfg = config.read_config()
    if not cfg:
        return

    # Check if file is inside any configured project's specs path
    proj = config.find_project_for_file(cfg, file_path)
    if not proj:
        return

    # Check that file has spec frontmatter
    abs_file = os.path.abspath(file_path)
    if not os.path.isfile(abs_file):
        return
    try:
        with open(abs_file, "r", encoding="utf-8") as f:
            content = f.read(2048)
    except (IOError, OSError):
        return

    meta, _ = parse_frontmatter(content)
    if not meta.get("spec_doc_id"):
        return

    try:
        push(file_path)
    except SystemExit as e:
        # push() calls sys.exit(1) on errors — catch it so the error
        # message (already printed to stderr by push()) is visible
        # instead of silently dying
        if e.code != 0:
            print(f"specs: auto-push failed for {os.path.basename(file_path)} — see error above", file=sys.stderr)
    except Exception as e:
        print(f"specs: auto-push failed for {os.path.basename(file_path)} — {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Set status
# ---------------------------------------------------------------------------

FEATURE_STATUSES = ["idea", "specifying", "in_progress", "completed", "archived"]
DOCUMENT_STATUSES = ["specifying", "ready", "approved"]
# Backlog items have their own lifecycle (mirror of BACKLOG_STATUSES in the
# service's StatusBadge.tsx). Order is the workflow order — the histograms below
# render in this sequence.
BACKLOG_STATUSES = ["idea", "planned", "blocked", "in_progress", "ready_for_testing", "completed", "archived"]
# "blocked" is settable by hand like any other status, but it is also maintained
# by the service: adding a dependency moves an item to blocked, and finishing
# the last blocker puts back whatever it was before. So a manual --status on an
# item that has unfinished dependencies will not stick.

# ---------------------------------------------------------------------------
# Timing (spec 023) — start date, due date, effort estimate.
#
# These rules MIRROR src/lib/timing.ts in the spec service. The service does
# not expose an overdue filter (deliberately — "today" belongs to the viewer,
# and baking a timezone into the API would be wrong for external
# collaborators), so the CLI derives it locally from the returned date
# strings. That means two implementations, and they must move together.
# ---------------------------------------------------------------------------

CLEAR_TIMING_FLAGS = {
    "--clear-start": "startDate",
    "--clear-due": "dueDate",
    "--clear-estimate": "estimateHours",
}

# Spec 033 — deployment tracking. The stage is a machine-maintained fact about
# where a fix currently runs; it is deliberately not a status, so automation
# never fights the item's owner over workflow state.
DEPLOY_STAGES = ["preview", "staging", "production"]

DEPLOY_FLAGS = {
    "--deployed-stage": "deployedStage",
    "--deployed-url": "deployedUrl",
}


def _deployed_line(item):
    """Textual version of the portal's stage chip + URL button, or None.

    Rendering nothing when the stage is null keeps output unchanged for
    projects that don't use deployment tracking (spec 033's invisibility rule).
    """
    stage = item.get("deployedStage")
    if not stage:
        return None
    parts = [f"[{stage}]"]
    if item.get("deployedUrl"):
        parts.append(item["deployedUrl"])
    if item.get("deployedAt"):
        parts.append(f"({item['deployedAt']})")
    return " ".join(parts)


def validate_deployment_fields(fields):
    """Guard the spec-033 deploy fields before the PATCH round-trip.

    Stage and URL are always written together — a stage flip that kept the old
    URL would point at a torn-down preview host — and every write stamps
    deployedAt so the chip can say how fresh it is. A --clear-deployment parse
    puts explicit nulls in all three, which passes through untouched.
    """
    if "deployedStage" not in fields and "deployedUrl" not in fields:
        return
    stage = fields.get("deployedStage")
    url = fields.get("deployedUrl")
    if stage is None and url is None:
        return
    if not stage or not url:
        print("specs: --deployed-stage and --deployed-url must be set together (or use --clear-deployment)", file=sys.stderr)
        sys.exit(1)
    if stage not in DEPLOY_STAGES:
        print(f"specs: invalid deployment stage '{stage}'. Valid: {', '.join(DEPLOY_STAGES)}", file=sys.stderr)
        sys.exit(1)
    fields["deployedAt"] = datetime.now(timezone.utc).isoformat()

# Statuses meaning "finished" — finished work is never late.
TIMING_TERMINAL = {
    "backlog": ("completed", "archived"),
    "feature": ("completed", "archived"),
    "bug": ("resolved", "closed"),
}

# Statuses meaning "nobody has picked this up yet" — the precondition for
# late-to-start. Features have no `planned`, and `specifying` is real work.
TIMING_NOT_STARTED = {
    "backlog": ("idea", "planned"),
    "feature": ("idea", "draft"),
    "bug": ("open", "triaged"),
}


def _today_iso():
    """Today in the caller's own timezone, matching lib/timing.ts's todayISO()."""
    return datetime.now().date().isoformat()


def _valid_iso_date(value):
    """YYYY-MM-DD and an actual calendar date (rejects 2026-02-30)."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(value)):
        return False
    try:
        # NB: this module does `from datetime import datetime`, so `datetime`
        # is the class — strptime, not the date module's fromisoformat.
        datetime.strptime(str(value), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_timing_fields(fields):
    """Client-side guard so a bad value fails fast instead of round-tripping a 400."""
    for key, flag in (("startDate", "--start"), ("dueDate", "--due")):
        v = fields.get(key)
        if key in fields and v is not None and not _valid_iso_date(v):
            print(f"specs: {flag} must be a YYYY-MM-DD date; got '{v}'", file=sys.stderr)
            sys.exit(1)
    if "estimateHours" in fields and fields["estimateHours"] is not None:
        raw = fields["estimateHours"]
        try:
            hours = float(raw)
        except (TypeError, ValueError):
            print(f"specs: --estimate must be a number of hours; got '{raw}'", file=sys.stderr)
            sys.exit(1)
        if hours < 0 or hours > 9999.99 or round(hours, 2) != hours:
            print(f"specs: --estimate must be 0..9999.99 with at most two decimals; got '{raw}'", file=sys.stderr)
            sys.exit(1)
        fields["estimateHours"] = hours
    start, due = fields.get("startDate"), fields.get("dueDate")
    if start and due and start > due:
        print(f"specs: --start {start} is after --due {due}", file=sys.stderr)
        sys.exit(1)


def timing_state(kind, item, today=None):
    """'overdue' | 'late_to_start' | None. Overdue wins when both apply."""
    today = today or _today_iso()
    status = item.get("status") or ""
    if status in TIMING_TERMINAL.get(kind, ()):
        return None
    due = item.get("dueDate")
    if due and due < today:
        return "overdue"
    start = item.get("startDate")
    if start and start < today and status in TIMING_NOT_STARTED.get(kind, ()):
        return "late_to_start"
    return None


def matches_timing_filter(kind, item, want_overdue, want_late, today=None):
    """
    Tests the predicates directly rather than via timing_state: an item that is
    both only *displays* as overdue, but --late-to-start must still find it.
    """
    if not want_overdue and not want_late:
        return True
    today = today or _today_iso()
    status = item.get("status") or ""
    if status in TIMING_TERMINAL.get(kind, ()):
        return False
    due, start = item.get("dueDate"), item.get("startDate")
    if want_overdue and due and due < today:
        return True
    if want_late and start and start < today and status in TIMING_NOT_STARTED.get(kind, ()):
        return True
    return False


def format_timing(item):
    """A compact ` · due 2026-08-28 (overdue) · 8h` suffix for list rows."""
    bits = []
    if item.get("startDate"):
        bits.append(f"start {item['startDate']}")
    if item.get("dueDate"):
        bits.append(f"due {item['dueDate']}")
    hours = item.get("estimateHours")
    if hours is not None:
        h = float(hours)
        bits.append(f"{int(h) if h == int(h) else round(h, 2)}h")
    return (" · " + " · ".join(bits)) if bits else ""


def set_status(identifier, new_status):
    """
    Set the status of a feature or document.

    identifier can be:
    - A feature ID like "my-project/001-feature-name"
    - A document UUID (spec_doc_id from frontmatter)
    - A local file path (reads doc_id from frontmatter)
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]

    # Determine if this is a feature or document
    is_file_path = os.path.isfile(identifier)
    is_feature_id = "/" in identifier and not is_file_path

    if is_file_path:
        # Read doc_id from frontmatter
        with open(identifier, "r", encoding="utf-8") as f:
            content = f.read()
        meta, _ = parse_frontmatter(content)
        doc_id = meta.get("spec_doc_id")
        if not doc_id:
            print(f"specs: {identifier} has no spec_doc_id in frontmatter", file=sys.stderr)
            sys.exit(1)

        if new_status not in DOCUMENT_STATUSES:
            print(f"specs: invalid document status '{new_status}'. Must be one of: {', '.join(DOCUMENT_STATUSES)}", file=sys.stderr)
            sys.exit(1)

        status_code, resp_body = api_request(
            f"{service_url}/api/documents/{doc_id}",
            method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"status": new_status},
        )
        if status_code not in (200, 201):
            print(f"specs: failed to update document status (HTTP {status_code}): {resp_body}", file=sys.stderr)
            sys.exit(1)

        rel = os.path.basename(identifier)
        print(f"specs: document {rel} → {new_status}")

    elif is_feature_id:
        if new_status not in FEATURE_STATUSES:
            print(f"specs: invalid feature status '{new_status}'. Must be one of: {', '.join(FEATURE_STATUSES)}", file=sys.stderr)
            sys.exit(1)

        import urllib.parse
        encoded_id = urllib.parse.quote(identifier, safe="")
        status_code, resp_body = api_request(
            f"{service_url}/api/features/lookup?id={encoded_id}",
            method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"status": new_status},
        )
        if status_code not in (200, 201):
            print(f"specs: failed to update feature status (HTTP {status_code}): {resp_body}", file=sys.stderr)
            sys.exit(1)

        print(f"specs: feature {identifier} → {new_status}")

    else:
        # Try as document UUID
        if new_status in DOCUMENT_STATUSES:
            status_code, resp_body = api_request(
                f"{service_url}/api/documents/{identifier}",
                method="PATCH",
                headers={**headers, "Content-Type": "application/json"},
                data={"status": new_status},
            )
            if status_code in (200, 201):
                print(f"specs: document {identifier} → {new_status}")
                return

        # Try as feature ID without slash — collect all matches first to
        # detect ambiguity (bug #9: same feature name in multiple projects).
        if new_status in FEATURE_STATUSES:
            import urllib.parse
            matches = []  # [(feature_id, project_id, entry), ...]
            for proj in cfg["projects"]:
                specs_path = proj["path"]
                if not os.path.isdir(specs_path):
                    continue
                for entry in os.listdir(specs_path):
                    if entry == identifier or entry.endswith(identifier):
                        matches.append((f"{proj['id']}/{entry}", proj["id"], entry))

            if len(matches) > 1:
                projects_list = ", ".join(m[1] for m in matches)
                print(
                    f"specs: feature name '{identifier}' exists in multiple projects: {projects_list}\n"
                    f"  Use the qualified form: specs-cli.py set-status <project>/<feature> <status>",
                    file=sys.stderr,
                )
                sys.exit(1)

            if len(matches) == 1:
                feature_id = matches[0][0]
                encoded_id = urllib.parse.quote(feature_id, safe="")
                status_code, resp_body = api_request(
                    f"{service_url}/api/features/lookup?id={encoded_id}",
                    method="PATCH",
                    headers={**headers, "Content-Type": "application/json"},
                    data={"status": new_status},
                )
                if status_code in (200, 201):
                    print(f"specs: feature {feature_id} → {new_status}")
                    return

        print(f"specs: could not find feature or document '{identifier}'", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Bugs
# ---------------------------------------------------------------------------

BUG_SEVERITIES = ["low", "medium", "high", "critical"]
BUG_STATUSES = ["open", "triaged", "in_progress", "ready_for_retest", "resolved", "closed"]


# --- Tags (spec 027) ---
#
# Tags are per-project labels shared by backlog items and bugs. The service
# owns the vocabulary and the near-duplicate check; the CLI's job is to make
# the nudge readable in a terminal and to turn --add-tag/--remove-tag into the
# replace-set the API actually takes.

TAG_COLORS = ["slate", "blue", "teal", "green", "amber", "orange", "red", "pink", "violet"]


def _slugify_tag(raw):
    """Identity form of a tag name. Mirrors slugifyTag() in the service."""
    s = unicodedata.normalize("NFC", str(raw or "").lower())
    s = re.sub(r"[^\w]+", "-", s, flags=re.UNICODE)
    s = s.replace("_", "-")
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def _tag_names(item):
    """The tag names on a backlog item or bug, in display order."""
    return [t.get("name") or t.get("slug") or "" for t in (item.get("tags") or [])]


def _tag_suffix(item):
    """Compact one-line tag rendering for list rows: '  #billing #auth'."""
    names = _tag_names(item)
    if not names:
        return ""
    return "  " + " ".join(f"#{n}" for n in names)


def _matches_tag_filter(item, tag_filters, untagged=False):
    """Client-side tag filter, matching the portal's OR semantics.

    Filters are compared on slug, so `--tag "Needs UX"` and `--tag needs-ux`
    behave the same. `untagged` ORs in the rows carrying no labels at all.
    """
    if not tag_filters and not untagged:
        return True
    present = {t.get("slug") for t in (item.get("tags") or [])}
    if untagged and not present:
        return True
    return any(_slugify_tag(f) in present for f in tag_filters)


def _fetch_project_tags(headers, service_url, project_id, usage=False):
    """The project's tag vocabulary. Returns (tags, can_manage) or (None, False)."""
    suffix = "?usage=1" if usage else ""
    url = f"{service_url}/api/portal/projects/{project_id}/tags{suffix}"
    try:
        status_code, body = api_request(url, headers=headers)
    except ConnectionError as e:
        print(f"specs: failed to fetch tags for '{project_id}' — {e}", file=sys.stderr)
        return None, False
    if status_code != 200:
        print(f"specs: failed to fetch tags for '{project_id}' (HTTP {status_code})", file=sys.stderr)
        return None, False
    payload = json.loads(body)
    return payload.get("tags", []), bool(payload.get("canManage"))


def _resolve_tag(headers, service_url, project_id, ref):
    """Resolve a tag reference (uuid, slug, or display name) to its row."""
    tags, _ = _fetch_project_tags(headers, service_url, project_id)
    if tags is None:
        return None
    slug = _slugify_tag(ref)
    for t in tags:
        if t.get("id") == ref or t.get("slug") == slug:
            return t
    print(f"specs: no tag '{ref}' in '{project_id}'", file=sys.stderr)
    close = [t for t in tags if slug and (slug in t.get("slug", "") or t.get("slug", "") in slug)]
    if close:
        print(f"  did you mean: {', '.join(t.get('name', '') for t in close[:5])}", file=sys.stderr)
    return None


def _print_tag_suggestions(payload, prefix="  "):
    """Render the service's similar-tag nudge as readable terminal output."""
    suggestions = payload.get("suggestions") or []
    if not suggestions:
        return
    print(f"{prefix}similar tags already exist:", file=sys.stderr)
    for s in suggestions:
        tag = s.get("tag") or {}
        reason = s.get("reason", "")
        print(f"{prefix}  #{tag.get('name', tag.get('slug', '?'))}  ({reason})", file=sys.stderr)


def _require_config_and_auth():
    """Config + auth headers, or exit. Every tag command starts with this."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    return cfg, headers


def list_tags(project_id, as_json=False):
    """List a project's tags with how many items wear each one."""
    cfg, headers = _require_config_and_auth()
    service_url = cfg["service_url"]

    tags, can_manage = _fetch_project_tags(headers, service_url, project_id, usage=True)
    if tags is None:
        sys.exit(1)

    if as_json:
        print(json.dumps({"tags": tags, "canManage": can_manage}, indent=2, ensure_ascii=False))
        return

    print(f"specs: {len(tags)} tag(s) in '{project_id}'")
    if not tags:
        print("  (none yet — create one with tag-create)")
        return
    print()
    width = max((len(t.get("name", "")) for t in tags), default=4)
    for t in tags:
        name = t.get("name", "?")
        usage = t.get("usageCount", 0)
        backlog = t.get("backlogCount", 0)
        bugs = t.get("bugCount", 0)
        breakdown = f"{backlog} backlog · {bugs} bug(s)" if usage else "unused"
        print(f"  #{name.ljust(width)}  {t.get('color', '?'):<7} {breakdown}")
        desc = t.get("description")
        if desc:
            print(f"   {' ' * width}  {desc}")
    if not can_manage:
        print("\n  (read-only — creating and renaming tags needs the developer or admin role)")


def create_tag(project_id, name, color=None, description=None, force=False):
    """Create a tag, surfacing the service's near-duplicate nudge."""
    cfg, headers = _require_config_and_auth()
    service_url = cfg["service_url"]

    payload = {"name": name}
    if color:
        if color not in TAG_COLORS:
            print(f"specs: --color must be one of {', '.join(TAG_COLORS)}", file=sys.stderr)
            sys.exit(1)
        payload["color"] = color
    if description:
        payload["description"] = description
    if force:
        payload["force"] = True

    url = f"{service_url}/api/portal/projects/{project_id}/tags"
    try:
        status_code, body = api_request(url, method="POST", headers=headers, data=payload)
    except ConnectionError as e:
        print(f"specs: failed to create tag — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 409:
        # The whole point of the feature: stop, show what already exists, and
        # let the human decide. Exit non-zero so a script doesn't sail past it.
        data = json.loads(body)
        print(f"specs: not creating '{name}' — a similar tag already exists", file=sys.stderr)
        _print_tag_suggestions(data)
        print("  reuse one of those, or repeat with --force to create it anyway", file=sys.stderr)
        sys.exit(2)

    if status_code not in (200, 201):
        print(f"specs: failed to create tag (HTTP {status_code}): {body[:300]}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(body)
    tag = data.get("tag", {})
    if data.get("created") is False:
        print(f"specs: tag '#{tag.get('name')}' already exists in '{project_id}'")
    else:
        print(f"specs: created tag '#{tag.get('name')}' ({tag.get('color')}) in '{project_id}'")


def update_tag(project_id, ref, name=None, color=None, description=None, force=False):
    """Rename, recolour, or re-describe a tag. Assignments are preserved."""
    cfg, headers = _require_config_and_auth()
    service_url = cfg["service_url"]

    tag = _resolve_tag(headers, service_url, project_id, ref)
    if not tag:
        sys.exit(1)

    payload = {}
    if name is not None:
        payload["name"] = name
    if color is not None:
        if color not in TAG_COLORS:
            print(f"specs: --color must be one of {', '.join(TAG_COLORS)}", file=sys.stderr)
            sys.exit(1)
        payload["color"] = color
    if description is not None:
        payload["description"] = description
    if not payload:
        print("specs: nothing to update — pass --name, --color, or --description", file=sys.stderr)
        sys.exit(1)
    if force:
        payload["force"] = True

    url = f"{service_url}/api/portal/tags/{tag['id']}"
    try:
        status_code, body = api_request(url, method="PATCH", headers=headers, data=payload)
    except ConnectionError as e:
        print(f"specs: failed to update tag — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 409:
        data = json.loads(body)
        if data.get("error") == "tag_slug_taken":
            print(f"specs: {data.get('detail', 'that name is already taken')}", file=sys.stderr)
        else:
            print(f"specs: not renaming '{tag.get('name')}' — a similar tag already exists", file=sys.stderr)
            _print_tag_suggestions(data)
            print("  repeat with --force to rename anyway", file=sys.stderr)
        sys.exit(2)

    if status_code != 200:
        print(f"specs: failed to update tag (HTTP {status_code}): {body[:300]}", file=sys.stderr)
        sys.exit(1)

    updated = json.loads(body)
    print(f"specs: updated tag '#{updated.get('name')}' in '{project_id}'")


def delete_tag(project_id, ref, force=False):
    """Delete a tag. A tag in use needs --force, which detaches it everywhere."""
    cfg, headers = _require_config_and_auth()
    service_url = cfg["service_url"]

    tag = _resolve_tag(headers, service_url, project_id, ref)
    if not tag:
        sys.exit(1)

    url = f"{service_url}/api/portal/tags/{tag['id']}" + ("?force=1" if force else "")
    try:
        status_code, body = api_request(url, method="DELETE", headers=headers)
    except ConnectionError as e:
        print(f"specs: failed to delete tag — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 409:
        data = json.loads(body)
        print(f"specs: {data.get('detail', 'tag is in use')}", file=sys.stderr)
        sys.exit(2)
    if status_code != 200:
        print(f"specs: failed to delete tag (HTTP {status_code}): {body[:300]}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(body)
    detached = data.get("detachedFrom", 0)
    tail = f" (removed from {detached} item(s))" if detached else ""
    print(f"specs: deleted tag '#{tag.get('name')}' from '{project_id}'{tail}")


def _resolve_tag_edit(current_tags, replace=None, add=None, remove=None, clear=False):
    """Turn --tags/--add-tag/--remove-tag/--clear-tags into a replace-set.

    The API takes the resulting set, not a delta, so add/remove are applied
    against whatever the item wears right now. Returns a list of slugs/names
    the service will resolve, or None when no tag flag was passed at all
    (which must leave the item's tags untouched).
    """
    if clear:
        return []
    if replace is not None:
        return [v for v in (s.strip() for s in replace.split(",")) if v]
    if not add and not remove:
        return None

    current = [t.get("slug") for t in (current_tags or [])]
    removed = {_slugify_tag(r) for r in (remove or [])}
    result = [s for s in current if s not in removed]
    for a in (add or []):
        slug = _slugify_tag(a)
        if slug not in result:
            # Keep what the user typed: an unknown name should come back as a
            # `tag_not_found` naming their word, not a slug they never wrote.
            result.append(a)
    return result


def _print_tag_error(status_code, body):
    """Explain a tag_not_found rejection, with the service's suggestions."""
    if status_code != 400:
        return False
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return False
    if data.get("error") != "tag_not_found":
        return False
    unknown = ", ".join(data.get("unknown") or [])
    print(f"specs: no such tag: {unknown}", file=sys.stderr)
    _print_tag_suggestions(data)
    print("  create it first with `tag-create`, or use an existing tag", file=sys.stderr)
    return True


def list_bugs(project_id=None, assignee_filter=None, tag_filters=None, untagged=False,
              status_filter=None, include_all=False, as_json=False):
    """List bugs for a project or all configured projects.

    Default is open bugs only (everything but `resolved`/`closed`). `status_filter`
    shows exactly that status — including `resolved` and `closed`, which is how a
    "what did the tester sign off?" question gets answered — and `include_all`
    shows every bug regardless of status. The CLI never hides something you
    asked for by name.

    `assignee_filter` (spec 022) is an email or name fragment, or the literal
    'none'/'unassigned' for bugs nobody owns.

    `tag_filters` (spec 027) is a list of tag slugs or names, OR-ed together;
    `untagged` ORs in the bugs carrying no labels. Filtered here rather than
    server-side, like every other filter in this CLI — the list is already in
    hand, and the service has no tag query parameter by design.
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    projects = cfg["projects"]

    if project_id:
        projects = [p for p in projects if p["id"] == project_id]
        if not projects:
            print(f"specs: project '{project_id}' not in config", file=sys.stderr)
            sys.exit(1)

    json_out = {}
    for proj in projects:
        url = f"{service_url}/api/portal/projects/{proj['id']}/bugs"
        try:
            status_code, body = api_request(url, headers=headers)
        except ConnectionError as e:
            print(f"specs: failed to fetch bugs for '{proj['id']}' — {e}", file=sys.stderr)
            continue

        if status_code != 200:
            print(f"specs: failed to fetch bugs for '{proj['id']}' (HTTP {status_code})", file=sys.stderr)
            continue

        bugs = json.loads(body)
        if include_all:
            open_bugs = list(bugs)
        elif status_filter:
            open_bugs = [b for b in bugs if b.get("status") == status_filter]
        else:
            open_bugs = [b for b in bugs if b.get("status") not in ("closed", "resolved")]
        scope = "" if include_all else (status_filter or "open")
        if assignee_filter:
            open_bugs = _filter_by_assignee(open_bugs, assignee_filter)
        if tag_filters or untagged:
            open_bugs = [b for b in open_bugs if _matches_tag_filter(b, tag_filters or [], untagged)]
        if as_json:
            # Machine-readable: the filtered rows, verbatim from the service,
            # so tooling never has to scrape the text layout. One array per
            # project; a multi-project run prints one object keyed by id.
            json_out.setdefault(proj["id"], open_bugs)
            continue

        label = f"{scope} " if scope else ""
        if len(projects) > 1:
            print(f"\n{proj['id']} ({len(open_bugs)} {label.strip() or 'total'})")
        else:
            print(f"specs: {len(open_bugs)} {label}bug(s) in '{proj['id']}'")

        if not open_bugs:
            print(f"  (no {label}bugs)")
            continue

        print()
        for bug in open_bugs:
            severity = bug.get("severity", "?")
            status = bug.get("status", "?")
            number = bug.get("number", "?")
            title = bug.get("title", "untitled")
            reporter = bug.get("reporterName") or bug.get("reporterEmail", "?")
            sev_marker = {"critical": "!!!", "high": "!!", "medium": "!", "low": "."}.get(severity, "?")
            assignee = _assignee_label(bug)
            assigned = f"  · @{assignee}" if assignee else ""
            dep_stage = bug.get("deployedStage")
            dep = f" [{dep_stage}]" if dep_stage else ""
            print(f"  #{number:<4} [{sev_marker}] {title}{_tag_suffix(bug)}")
            print(f"        {status}{dep} — reported by {reporter}{assigned}")


# Markdown image carrying an inline base64 data URI:
# ![alt](data:image/png;base64,AAAA...)
    if as_json:
        print(json.dumps(json_out[project_id] if project_id and project_id in json_out else json_out,
                         indent=2, ensure_ascii=False))

_INLINE_IMG_RE = re.compile(
    r"!\[([^\]]*)\]\(data:image/([A-Za-z0-9.+-]+);base64,([A-Za-z0-9+/=\s]+?)\)"
)


def _strip_inline_images(text, collect=None):
    """Replace inline base64 data-URI images with a compact placeholder.

    Bug/backlog bodies often carry pasted screenshots inline in the
    description as `![alt](data:image/png;base64,...)` — hundreds of KB each.
    Dumping the raw base64 to the terminal is useless and floods the reader,
    so each becomes a one-line marker carrying the alt text and decoded size.

    Pass a list as `collect` to also capture the images themselves as
    (alt, fmt, base64) tuples. The marker used to end with "open portal to
    view", which is no help at all to the reader most likely to be looking:
    a terminal session that cannot open a browser. `--images` writes them to
    files instead, and the marker now says so.

    Returns (clean_text, image_count).
    """
    if not text:
        return text, 0
    count = 0

    def _repl(m):
        nonlocal count
        count += 1
        alt = (m.group(1) or "").strip() or "image"
        fmt = m.group(2)
        b64 = re.sub(r"\s+", "", m.group(3))
        kb = max(1, (len(b64) * 3 // 4) // 1024)
        if collect is not None:
            collect.append((alt, fmt, b64))
        return f"[image {count}: {alt} — inline {fmt}, ~{kb} KB — save with --images]"

    return _INLINE_IMG_RE.sub(_repl, text), count


def _bug_image_dir(project_id, number, requested):
    """Where saved bug images go.

    A directory under the system temp dir by default: these are scratch copies
    for reading, and they must not land inside a synced folder where a file
    manager would try to replicate them.
    """
    if requested:
        return requested
    return os.path.join(
        tempfile.gettempdir(), "awolve-spec-images", f"{project_id}-bug-{number}"
    )


def _save_bug_images(project_id, number, bug_id, inline_images, out_dir):
    """Write every image the bug carries to disk and print the paths.

    Two sources, and both used to be invisible from the terminal: screenshots
    pasted inline into the body as data URIs, and files uploaded as
    attachments. A reader who cannot open the portal could see that an image
    existed but had no way to look at it.
    """
    target = _bug_image_dir(project_id, number, out_dir)
    try:
        os.makedirs(target, exist_ok=True)
    except OSError as e:
        print(f"specs: could not create image directory '{target}' — {e}", file=sys.stderr)
        return

    written = []

    for index, (alt, fmt, b64) in enumerate(inline_images, start=1):
        ext = "jpg" if fmt.lower() in ("jpeg", "jpg") else re.sub(r"[^a-z0-9]", "", fmt.lower()) or "png"
        path = os.path.join(target, f"inline-{index}.{ext}")
        try:
            with open(path, "wb") as f:
                f.write(base64.b64decode(b64))
        except (OSError, ValueError, binascii.Error) as e:
            print(f"specs: could not save inline image {index} — {e}", file=sys.stderr)
            continue
        written.append((path, f"inline: {alt}"))

    # Uploaded attachments. Non-images are saved too — a reader asking for the
    # pictures usually wants whatever else was attached to the report.
    for att in _bug_attachments(bug_id):
        name = att.get("filename") or f"attachment-{att.get('id', '')}"
        path = os.path.join(target, re.sub(r"[/\\]", "_", name))
        try:
            data, _server_name = _fetch_attachment(att["id"])
            with open(path, "wb") as f:
                f.write(data)
        except SystemExit:
            print(f"specs: could not download attachment '{name}'", file=sys.stderr)
            continue
        except OSError as e:
            print(f"specs: could not save attachment '{name}' — {e}", file=sys.stderr)
            continue
        written.append((path, f"attachment: {att.get('contentType', '?')}"))

    if not written:
        print("\nImages: none")
        return

    print(f"\nImages ({len(written)}) saved to {target}:")
    for path, label in written:
        print(f"  {path}   ({label})")


def _bug_attachments(bug_id):
    """Attachments on a bug, or [] if they cannot be fetched.

    Never fatal: a bug should still render when the attachment listing fails.
    """
    if not bug_id:
        return []
    cfg = config.read_config()
    headers = auth.get_headers()
    if not cfg or not headers:
        return []
    url = (
        f"{cfg['service_url']}/api/portal/attachments"
        f"?entityType=bug&entityId={urllib.parse.quote(str(bug_id), safe='')}"
    )
    try:
        sc, body = api_request(url, headers=headers)
    except ConnectionError:
        return []
    if sc != 200:
        return []
    try:
        atts = json.loads(body)
    except json.JSONDecodeError:
        return []
    return atts if isinstance(atts, list) else []


def view_bug(project_id, bug_number, as_json=False, save_images=False, images_dir=None):
    """Show full details for a single bug by its short number."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    projects = [p for p in cfg["projects"] if p["id"] == project_id]
    if not projects:
        print(f"specs: project '{project_id}' not in config", file=sys.stderr)
        sys.exit(1)

    try:
        number = int(str(bug_number).lstrip("#"))
    except ValueError:
        print(f"specs: bug number must be an integer, got '{bug_number}'", file=sys.stderr)
        sys.exit(1)

    url = f"{service_url}/api/portal/projects/{project_id}/bugs"
    try:
        status_code, body = api_request(url, headers=headers)
    except ConnectionError as e:
        print(f"specs: failed to fetch bugs — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: failed to fetch bugs (HTTP {status_code})", file=sys.stderr)
        sys.exit(1)

    bugs = json.loads(body)
    match = next((b for b in bugs if b.get("number") == number), None)
    if not match:
        print(f"specs: bug #{number} not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)

    # The list endpoint returns a deliberately slim shape — it omits the body
    # fields (description, steps, expected, actual, environment), which can be
    # hundreds of KB of inline base64 screenshots. Fetch the detail endpoint
    # for the full record; without this every bug rendered "(no description)"
    # and pasted screenshots were invisible to the CLI.
    bug_id = match.get("id")
    detail = match
    if bug_id:
        try:
            d_status, d_body = api_request(
                f"{service_url}/api/portal/bugs/{bug_id}", headers=headers
            )
            if d_status == 200:
                detail = json.loads(d_body)
            else:
                print(
                    f"specs: could not fetch bug body (HTTP {d_status}); showing metadata only",
                    file=sys.stderr,
                )
        except ConnectionError as e:
            print(
                f"specs: could not fetch bug body ({e}); showing metadata only",
                file=sys.stderr,
            )

    if as_json:
        print(json.dumps(detail, indent=2))
        return

    severity = detail.get("severity", "?")
    sev_marker = {"critical": "!!!", "high": "!!", "medium": "!", "low": "."}.get(severity, "?")
    reporter = detail.get("reporterName") or detail.get("reporterEmail", "?")
    title = detail.get("title", "untitled")
    status = detail.get("status", "?")
    created = detail.get("createdAt", "?")
    updated = detail.get("updatedAt", "?")
    # Collect the inline screenshots rather than only counting them, so
    # --images can write them out.
    inline_images = []
    description, _desc_imgs = _strip_inline_images(detail.get("description") or "", inline_images)
    if not description:
        description = "(no description)"
    steps, _ = _strip_inline_images(detail.get("steps"), inline_images)
    expected, _ = _strip_inline_images(detail.get("expected"), inline_images)
    actual, _ = _strip_inline_images(detail.get("actual"), inline_images)
    attachments = _bug_attachments(bug_id)
    environment = detail.get("environment")
    comments = detail.get("comments")
    comment_count = len(comments) if isinstance(comments, list) else match.get("commentCount", 0)

    print(f"#{number} [{sev_marker} {severity}] {title}")
    print(f"  status:    {status}")
    print(f"  reporter:  {reporter}")
    print(f"  assignee:  {_assignee_label(detail) or '(unassigned)'}")
    tag_names = _tag_names(detail)
    if tag_names:
        print(f"  tags:      {' '.join('#' + n for n in tag_names)}")
    print(f"  created:   {created}")
    if updated != created:
        print(f"  updated:   {updated}")
    if environment:
        print(f"  env:       {environment}")
    deployed = _deployed_line(detail)
    if deployed:
        print(f"  deployed:  {deployed}")
    print(f"  comments:  {comment_count}")
    print(f"  portal:    {service_url}/portal/{project_id}/bugs/{match.get('id', '')}")
    print()
    print("Description:")
    print(description)
    if steps:
        print("\nSteps to reproduce:")
        print(steps)
    if expected:
        print("\nExpected:")
        print(expected)
    if actual:
        print("\nActual:")
        print(actual)

    if attachments:
        print(f"\nAttachments ({len(attachments)}):")
        for att in attachments:
            size = att.get("sizeBytes")
            size_label = f"{size // 1024} KB" if isinstance(size, int) and size >= 1024 else f"{size} B" if isinstance(size, int) else "?"
            print(f"  {att.get('filename', '?')}  [{att.get('contentType', '?')}, {size_label}]  id: {att.get('id', '?')}")

    total_images = len(inline_images) + len(attachments)
    if save_images:
        _save_bug_images(project_id, number, bug_id, inline_images, images_dir)
    elif total_images:
        # Say how to actually look at them. Pointing at the portal is no use
        # to a terminal session, which is where this command is usually read.
        print(
            f"\n{total_images} image/attachment(s) — re-run with --images to save them locally:"
            f"\n  specs-cli.py view-bug {project_id} {number} --images"
        )


def set_bug_status(project_id, bug_number, status):
    """Update a bug's status by its short number."""
    if status not in BUG_STATUSES:
        print(f"specs: invalid status '{status}'. Valid: {', '.join(BUG_STATUSES)}", file=sys.stderr)
        sys.exit(1)

    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    projects = [p for p in cfg["projects"] if p["id"] == project_id]
    if not projects:
        print(f"specs: project '{project_id}' not in config", file=sys.stderr)
        sys.exit(1)

    try:
        number = int(str(bug_number).lstrip("#"))
    except ValueError:
        print(f"specs: bug number must be an integer, got '{bug_number}'", file=sys.stderr)
        sys.exit(1)

    # Resolve short number to UUID by fetching the project's bug list.
    list_url = f"{service_url}/api/portal/projects/{project_id}/bugs"
    try:
        status_code, body = api_request(list_url, headers=headers)
    except ConnectionError as e:
        print(f"specs: failed to fetch bugs — {e}", file=sys.stderr)
        sys.exit(1)
    if status_code != 200:
        print(f"specs: failed to fetch bugs (HTTP {status_code})", file=sys.stderr)
        sys.exit(1)

    bugs = json.loads(body)
    match = next((b for b in bugs if b.get("number") == number), None)
    if not match:
        print(f"specs: bug #{number} not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)

    bug_id = match["id"]
    patch_url = f"{service_url}/api/portal/bugs/{bug_id}"
    try:
        status_code, body = api_request(patch_url, method="PATCH", headers=headers, data={"status": status})
    except ConnectionError as e:
        print(f"specs: failed to update bug — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: failed to update bug #{number} (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: bug #{number} '{match.get('title', '')}' → {status}")


def _resolve_bug(project_id, bug_number):
    """Resolve a bug short number to its full row. Returns (cfg, headers, service_url, bug).

    Exits with a helpful error if config/auth/project/number are wrong or the bug
    is missing. Used by every bug command that takes a `#N` argument.
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    projects = [p for p in cfg["projects"] if p["id"] == project_id]
    if not projects:
        print(f"specs: project '{project_id}' not in config", file=sys.stderr)
        sys.exit(1)

    try:
        number = int(str(bug_number).lstrip("#"))
    except ValueError:
        print(f"specs: bug number must be an integer, got '{bug_number}'", file=sys.stderr)
        sys.exit(1)

    list_url = f"{service_url}/api/portal/projects/{project_id}/bugs"
    try:
        status_code, body = api_request(list_url, headers=headers)
    except ConnectionError as e:
        print(f"specs: failed to fetch bugs — {e}", file=sys.stderr)
        sys.exit(1)
    if status_code != 200:
        print(f"specs: failed to fetch bugs (HTTP {status_code})", file=sys.stderr)
        sys.exit(1)

    bugs = json.loads(body)
    match = next((b for b in bugs if b.get("number") == number), None)
    if not match:
        print(f"specs: bug #{number} not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)

    return cfg, headers, service_url, match


def update_bug(project_id, bug_number, fields, tag_edit=None):
    """Update title/description/severity/assignedTo on an existing bug.

    `fields` is a dict of {api_key: value} to PATCH. Status changes go via
    set_bug_status for clearer audit semantics. assignedTo=None unassigns
    (spec 022); assigning needs bug:write:any on the project.

    `tag_edit` (spec 027) is {replace, add, remove, clear} — see
    update_backlog_item for why it is folded after the bug is resolved.
    """
    if not fields and not tag_edit:
        print("specs: nothing to update — pass at least one of --title/--description/--severity/--assignee/--unassign", file=sys.stderr)
        sys.exit(1)

    if "severity" in fields and fields["severity"] not in BUG_SEVERITIES:
        print(f"specs: invalid severity '{fields['severity']}'. Valid: {', '.join(BUG_SEVERITIES)}", file=sys.stderr)
        sys.exit(1)

    _, headers, service_url, bug = _resolve_bug(project_id, bug_number)
    bug_id = bug["id"]
    number = bug["number"]

    if tag_edit:
        next_tags = _resolve_tag_edit(bug.get("tags"), **tag_edit)
        if next_tags is not None:
            fields = {**fields, "tags": next_tags}

    url = f"{service_url}/api/portal/bugs/{bug_id}"
    try:
        status_code, body = api_request(
            url, method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data=fields,
        )
    except ConnectionError as e:
        print(f"specs: failed to update bug — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 201):
        _print_assignee_error(status_code, body, fields.get("assignedTo"))
        if _print_tag_error(status_code, body):
            sys.exit(1)
        try:
            err = json.loads(body).get("error", body)
        except (json.JSONDecodeError, AttributeError):
            err = body
        print(f"specs: failed to update bug #{number} (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    changed = ", ".join(f"{k}={v!r}" for k, v in fields.items())
    print(f"specs: updated bug #{number} ({changed})")


def add_bug_comment(project_id, bug_number, body_text):
    """Add a comment to a bug by its short number."""
    _require_comment_body(body_text, "bug-comment")

    _, headers, service_url, bug = _resolve_bug(project_id, bug_number)
    bug_id = bug["id"]
    number = bug["number"]

    url = f"{service_url}/api/portal/bugs/{bug_id}/comments"
    try:
        status_code, resp = api_request(
            url, method="POST",
            headers={**headers, "Content-Type": "application/json"},
            data={"body": body_text},
        )
    except ConnectionError as e:
        print(f"specs: failed to add comment — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 201):
        try:
            err = json.loads(resp).get("error", resp)
        except (json.JSONDecodeError, AttributeError):
            err = resp
        print(f"specs: failed to add comment (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: comment added to bug #{number}")


def list_bug_comments(project_id, bug_number, as_json=False):
    """List comments on a bug by its short number.

    Uses the bug detail endpoint which bundles comments into the response.
    """
    _, headers, service_url, bug = _resolve_bug(project_id, bug_number)
    bug_id = bug["id"]
    number = bug["number"]

    url = f"{service_url}/api/portal/bugs/{bug_id}"
    try:
        status_code, body = api_request(url, headers=headers)
    except ConnectionError as e:
        print(f"specs: failed to fetch bug — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: failed to fetch bug #{number} (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    detail = json.loads(body)
    comments = detail.get("comments") or []
    # Always oldest-first, so the thread reads chronologically. Sorted by
    # createdAt rather than reversed: this used to be a blind reversal of a
    # server that returned newest-first, which meant the CLI's correctness
    # depended on the server's ordering never changing. It changed (bugs now
    # match backlog items and come back oldest-first), and a reversal would
    # have quietly started showing every thread backwards. Sorting is right
    # against either server.
    comments = sorted(comments, key=lambda c: c.get("createdAt") or "")

    if as_json:
        print(json.dumps(comments, indent=2))
        return

    if not comments:
        print(f"specs: no comments on bug #{number}")
        return

    print(f"specs: {len(comments)} comment(s) on bug #{number}")
    print()
    for c in comments:
        author = c.get("author", "?")
        author_type = c.get("authorType", "?")
        date = (c.get("createdAt") or "?")[:19].replace("T", " ")
        body_text = c.get("body", "")
        comment_id = c.get("id", "?")
        tag = "internal" if author_type == "internal" else "external"
        print(f"  {author} ({tag}) — {date}  [{comment_id}]")
        for line in body_text.splitlines() or [""]:
            print(f"    {line}")
        print()


def edit_bug_comment(project_id, bug_number, comment_id, body_text):
    """Edit a bug comment by its UUID. Author only on the server."""
    _require_comment_body(body_text, "edit-bug-comment")

    _, headers, service_url, bug = _resolve_bug(project_id, bug_number)
    bug_id = bug["id"]
    number = bug["number"]

    url = f"{service_url}/api/portal/bugs/{bug_id}/comments/{comment_id}"
    try:
        status_code, resp = api_request(
            url, method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"body": body_text},
        )
    except ConnectionError as e:
        print(f"specs: failed to edit comment — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 403:
        print("specs: you can only edit your own comments", file=sys.stderr)
        sys.exit(1)
    if status_code == 404:
        print(f"specs: comment {comment_id} not found on bug #{number}", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 201):
        try:
            err = json.loads(resp).get("error", resp)
        except (json.JSONDecodeError, AttributeError):
            err = resp
        print(f"specs: failed to edit comment (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: comment {comment_id} on bug #{number} edited")


def delete_bug_comment(project_id, bug_number, comment_id):
    """Delete a bug comment by its UUID. Author only. Hard delete."""
    _, headers, service_url, bug = _resolve_bug(project_id, bug_number)
    bug_id = bug["id"]
    number = bug["number"]

    url = f"{service_url}/api/portal/bugs/{bug_id}/comments/{comment_id}"
    try:
        status_code, resp = api_request(url, method="DELETE", headers=headers)
    except ConnectionError as e:
        print(f"specs: failed to delete comment — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 403:
        print("specs: you can only delete your own comments", file=sys.stderr)
        sys.exit(1)
    if status_code == 404:
        print(f"specs: comment {comment_id} not found on bug #{number}", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 204):
        try:
            err = json.loads(resp).get("error", resp)
        except (json.JSONDecodeError, AttributeError):
            err = resp
        print(f"specs: failed to delete comment (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: comment {comment_id} on bug #{number} deleted")


def list_backlog(project_id=None, view="tree", status_filter=None, priority_filter=None, assignee_filter=None,
                 overdue=False, late_to_start=False, tag_filters=None, untagged=False, include_all=False,
                 as_json=False):
    """List backlog items for a project or all configured projects.

    Spec 013:
      view='tree'  (default) — group items by parent: epic header + indented children
      view='epics' — show only top-level items that have at least one child
      view='flat'  — flat list, no grouping (legacy behavior)
    Filters: optional status (single value), priority (single value),
    assignee (spec 022 — an email, or the literal 'none' for unassigned),
    spec 023's overdue / late-to-start, which are derived here rather than
    server-side because "today" belongs to whoever is looking, and spec 027's
    tags (slugs or names, OR-ed; `untagged` ORs in the unlabelled).
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    projects = cfg["projects"]

    if project_id:
        projects = [p for p in projects if p["id"] == project_id]
        if not projects:
            print(f"specs: project '{project_id}' not in config", file=sys.stderr)
            sys.exit(1)

    # Tree view renders children only underneath a surviving parent, so an
    # assignee filter would silently swallow any match whose epic doesn't also
    # match. Flat view answers "what is on X's plate" honestly.
    if assignee_filter and view == "tree":
        view = "flat"
    # Same trap as the assignee filter: in tree view a matching child is only
    # rendered under a surviving parent, so a tag filter would silently drop
    # matches whose epic isn't tagged.
    if (tag_filters or untagged) and view == "tree":
        view = "flat"

    json_out = {}
    for proj in projects:
        url = f"{service_url}/api/portal/projects/{proj['id']}/backlog"
        try:
            status_code, body = api_request(url, headers=headers)
        except ConnectionError as e:
            print(f"specs: failed to fetch backlog for '{proj['id']}' — {e}", file=sys.stderr)
            continue

        if status_code != 200:
            print(f"specs: failed to fetch backlog for '{proj['id']}' (HTTP {status_code})", file=sys.stderr)
            continue

        items = json.loads(body)
        # `--status completed` used to return nothing: the default exclusion of
        # completed/archived ran BEFORE the status filter. A status you name is
        # what you get; `--all` lifts the exclusion without naming one.
        if include_all:
            active = list(items)
        elif status_filter:
            active = [i for i in items if i.get("status") == status_filter]
        else:
            active = [i for i in items if i.get("status") not in ("completed", "archived")]
        if priority_filter:
            active = [i for i in active if i.get("priority") == priority_filter]
        if assignee_filter:
            active = _filter_by_assignee(active, assignee_filter)
        if overdue or late_to_start:
            active = [i for i in active if matches_timing_filter("backlog", i, overdue, late_to_start)]
        if tag_filters or untagged:
            active = [i for i in active if _matches_tag_filter(i, tag_filters or [], untagged)]
        if as_json:
            json_out.setdefault(proj["id"], active)
            continue

        if len(projects) > 1:
            print(f"\n{proj['id']} ({len(active)} active)")
        else:
            scope = "" if include_all else (status_filter or "active")
            print(f"specs: {len(active)} {scope + ' ' if scope else ''}backlog item(s) in '{proj['id']}'")

        if not active:
            print("  (no active items)")
            continue

        print()
        if view == "flat":
            for item in active:
                _print_backlog_row(item, indent=0)
        elif view == "epics":
            epics = [i for i in active if i.get("isEpic")]
            if not epics:
                print("  (no epics)")
            for item in epics:
                _print_backlog_row(item, indent=0)
        else:  # tree
            children_by_parent = {}
            for it in active:
                pid = it.get("parentId")
                if pid:
                    children_by_parent.setdefault(pid, []).append(it)
            for item in active:
                if item.get("parentId"):
                    continue
                _print_backlog_row(item, indent=0)
                kids = children_by_parent.get(item.get("id"), [])
                for k in kids:
                    _print_backlog_row(k, indent=2)
    if as_json:
        print(json.dumps(json_out[project_id] if project_id and project_id in json_out else json_out,
                         indent=2, ensure_ascii=False))

def _assignee_label(item):
    """Human label for an item's assignee, or None when unassigned (spec 022)."""
    return item.get("assignedToName") or item.get("assignedToEmail")


def _print_assignee_error(status_code, body, assignee):
    """Turn the server's short assignee error codes into an actionable message.

    Only prints when the failure really is about the assignee — the caller still
    prints its own generic error afterwards for everything else.
    """
    if not assignee or status_code not in (400, 403):
        return
    try:
        err = (json.loads(body) or {}).get("error")
    except (json.JSONDecodeError, TypeError):
        return
    if err == "assignee_not_found":
        print(f"specs: no portal user found for '{assignee}' — they need to have signed in at least once", file=sys.stderr)
    elif err == "assignee_no_access":
        print(f"specs: '{assignee}' has no access to this project — grant access first, then assign", file=sys.stderr)


def _filter_by_assignee(items, assignee_filter):
    """Keep items matching an assignee filter.

    `assignee_filter` is an email (matched case-insensitively against the
    assignee's email, or as a substring of their display name so '--assignee
    bjorn' works) or the literal 'none'/'unassigned' for items nobody owns.
    """
    needle = assignee_filter.strip().lower()
    if needle in ("none", "unassigned"):
        return [i for i in items if not i.get("assignedTo")]
    out = []
    for i in items:
        email = (i.get("assignedToEmail") or "").lower()
        name = (i.get("assignedToName") or "").lower()
        if (email and (email == needle or needle in email)) or (name and needle in name):
            out.append(i)
    return out


def _print_backlog_row(item, indent=0):
    pad = " " * indent
    priority = item.get("priority", "?")
    status = item.get("status", "?")
    title = item.get("title", "untitled")
    number = item.get("number")
    feature_id = item.get("featureId")
    is_epic = item.get("isEpic", False)
    pri_marker = {"high": "!!!", "medium": "!!", "low": "!"}.get(priority, "?")
    promoted = f" → {feature_id}" if feature_id else ""
    histogram = ""
    counts = item.get("childStatusCounts") or {}
    if counts:
        order = BACKLOG_STATUSES
        parts = [f"{counts[s]} {s}" for s in order if counts.get(s)]
        histogram = " · children: " + " · ".join(parts) if parts else ""
    elif is_epic:
        histogram = " · (no items yet)"
    num_str = f"#{number} " if number else ""
    epic_tag = "[EPIC] " if is_epic else ""
    assignee = _assignee_label(item)
    assigned = f"  · @{assignee}" if assignee else ""
    # Spec 023: dates + estimate, with the derived state spelled out. Computed
    # locally — the service has no overdue filter by design.
    timing = format_timing(item)
    state = timing_state("backlog", item)
    if state == "overdue":
        timing += " (OVERDUE)"
    elif state == "late_to_start":
        timing += " (late to start)"
    dep_stage = item.get("deployedStage")
    dep = f" [{dep_stage}]" if dep_stage else ""
    print(f"  {pad}[{pri_marker}] {num_str}{epic_tag}{title}{_tag_suffix(item)}{histogram}")
    print(f"       {pad}{status}{dep}{promoted}{assigned}{timing}")


def _plugin_version():
    """This plugin's version, read from the manifest beside the script.

    The portal shows the latest published version; without this there was no
    way to find out whether the copy you are running is that one.
    """
    manifest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            ".claude-plugin", "plugin.json")
    try:
        with open(manifest, encoding="utf-8") as fh:
            return json.load(fh).get("version", "unknown")
    except Exception:
        return "unknown"


def _resolve_backlog_id(headers, service_url, project_id, ref):
    """Resolve a backlog reference (uuid, '#42', or '42') to its uuid id within a project.

    Returns (id, item_dict) or (None, None) if not found.
    """
    if not ref:
        return (None, None)
    s = str(ref).lstrip("#").strip()
    # If it looks like a UUID (has dashes), treat as id
    if "-" in s and len(s) >= 32:
        # Fetch via list (single round-trip, project-scoped)
        url = f"{service_url}/api/portal/projects/{project_id}/backlog"
        sc, body = api_request(url, headers=headers)
        if sc != 200:
            return (None, None)
        for it in json.loads(body):
            if it.get("id") == s:
                return (s, it)
        return (None, None)
    # Otherwise treat as numeric #N
    try:
        n = int(s)
    except ValueError:
        return (None, None)
    url = f"{service_url}/api/portal/projects/{project_id}/backlog"
    sc, body = api_request(url, headers=headers)
    if sc != 200:
        return (None, None)
    for it in json.loads(body):
        if it.get("number") == n:
            return (it.get("id"), it)
    return (None, None)


def _fetch_backlog_detail(headers, service_url, project_id, ref):
    """Fetch a full backlog item (with parent/children/comments) by ref.

    Uses the `by-number` endpoint which returns the richer payload; falls
    back to the list+filter path for UUID refs. Returns (item_dict, error_str)
    where item_dict is None on miss.
    """
    s = str(ref).lstrip("#").strip()
    # UUID path: list lookup (no single-item-by-uuid portal route)
    if "-" in s and len(s) >= 32:
        _id, item = _resolve_backlog_id(headers, service_url, project_id, ref)
        return (item, None) if item else (None, f"backlog item '{ref}' not found")
    try:
        n = int(s)
    except ValueError:
        return (None, f"invalid backlog reference '{ref}'")
    url = f"{service_url}/api/portal/projects/{project_id}/backlog/by-number/{n}"
    sc, body = api_request(url, headers=headers)
    if sc == 404:
        return (None, f"backlog item #{n} not found in '{project_id}'")
    if sc != 200:
        return (None, f"fetch failed (HTTP {sc})")
    return (json.loads(body), None)


def view_backlog(project_id, ref, as_json=False):
    """Show full details for a single backlog item by uuid, '#N', or 'N'.

    The listing view (`backlog`) intentionally elides description and
    metadata to stay scannable. Anyone implementing an item needs the
    full description — that's what this command surfaces, along with
    parent, children (for epics), and comments.
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    projects = [p for p in cfg["projects"] if p["id"] == project_id]
    if not projects:
        print(f"specs: project '{project_id}' not in config", file=sys.stderr)
        sys.exit(1)

    item, err = _fetch_backlog_detail(headers, service_url, project_id, ref)
    if not item:
        print(f"specs: {err}", file=sys.stderr)
        sys.exit(1)

    if as_json:
        print(json.dumps(item, indent=2, ensure_ascii=False))
        return

    number = item.get("number")
    title = item.get("title", "untitled")
    status = item.get("status", "?")
    priority = item.get("priority", "?")
    pri_marker = {"high": "!!!", "medium": "!!", "low": "!"}.get(priority, "?")
    is_epic = item.get("isEpic", False)
    epic_tag = "[EPIC] " if is_epic else ""
    description, _ = _strip_inline_images(item.get("description") or "")
    if not description:
        description = "(no description)"
    feature_id = item.get("featureId")
    feature_title = item.get("featureTitle")
    feature_status = item.get("featureStatus")
    parent = item.get("parent")
    children = item.get("children") or []
    comments = item.get("comments") or []
    created_by = item.get("createdByName") or item.get("createdByEmail") or item.get("createdBy", "?")
    created = item.get("createdAt", "?")
    updated = item.get("updatedAt", "?")

    num_str = f"#{number} " if number else ""
    print(f"{num_str}[{pri_marker} {priority}] {epic_tag}{title}")
    print(f"  status:    {status}")
    print(f"  author:    {created_by}")
    print(f"  assignee:  {_assignee_label(item) or '(unassigned)'}")
    tag_names = _tag_names(item)
    if tag_names:
        print(f"  tags:      {' '.join('#' + n for n in tag_names)}")
    if feature_id:
        ft = f" — {feature_title}" if feature_title else ""
        fs = f" [{feature_status}]" if feature_status else ""
        print(f"  promoted:  feature → {feature_id}{ft}{fs}")
    if parent:
        p_num = parent.get("number")
        p_label = f"#{p_num} {parent.get('title', '')}".strip()
        print(f"  parent:    {p_label}")

    # Dependencies. Printed with each one's own status, because "blocked" on
    # its own tells you that you are stuck without telling you on what — and
    # the whole reason to look is to find out what to chase.
    depends_on = item.get("dependsOn") or []
    if depends_on:
        print("  depends on:")
        for d in depends_on:
            done = d.get("status") in ("completed", "archived")
            tick = "x" if done else " "
            print(f"    [{tick}] #{d.get('number')} {d.get('title', '')} — {d.get('status')}")

    blocks = item.get("blocks") or []
    if blocks:
        refs = ", ".join(f"#{b.get('number')}" for b in blocks)
        print(f"  blocking:  {refs}")
    if children:
        order = BACKLOG_STATUSES
        cstat = {s: 0 for s in order}
        for c in children:
            s = c.get("status")
            if s in cstat:
                cstat[s] += 1
        parts = [f"{cstat[s]} {s}" for s in order if cstat[s]]
        if parts:
            print(f"  children:  {' · '.join(parts)}")
    deployed = _deployed_line(item)
    if deployed:
        print(f"  deployed:  {deployed}")
    print(f"  created:   {created}")
    if updated != created:
        print(f"  updated:   {updated}")
    # The portal detail route is /backlog/[number] (it does Number(params.number)),
    # so the link must use the item number, not its uuid. Legacy items without a
    # number have no detail page — skip the link rather than print a 404.
    if number:
        print(f"  portal:    {service_url}/portal/{project_id}/backlog/{number}")
    print()
    print("Description:")
    print(description)

    if children:
        print()
        print(f"Children ({len(children)}):")
        for c in children:
            cn = c.get("number")
            cpri = {"high": "!!!", "medium": "!!", "low": "!"}.get(c.get("priority", ""), "?")
            print(f"  [{cpri}] #{cn} {c.get('title', 'untitled')}  ({c.get('status', '?')})")

    if comments:
        print()
        print(f"Comments ({len(comments)}):")
        for c in comments:
            author = c.get("author") or c.get("authorType", "anonymous")
            print(f"  · {author} — {c.get('createdAt', '?')}  [id: {c.get('id', '')}]")
            body = (c.get("body") or "").strip()
            for line in body.splitlines() or [""]:
                print(f"      {line}")


def _require_comment_body(body_text, command):
    """Validate a comment body, rejecting the flag-shaped ones.

    Comment bodies are positional, so `backlog-comment <proj> #18 --body "..."`
    puts the literal string "--body" in the comment and throws the real text
    away without complaint. That is not hypothetical — it happened, and the
    comment sat there reading "--body" until someone listed the thread.
    A body that starts with "--" is a mistyped flag far more often than it is
    something a person meant to say.
    """
    if body_text is None or not body_text.strip():
        print("specs: comment body is required", file=sys.stderr)
        sys.exit(1)
    if body_text.strip().startswith("--"):
        print(
            f"specs: '{body_text.strip().split()[0]}' looks like a flag, not a comment.\n"
            f"       The body is positional — pass it directly:\n"
            f'         specs-cli.py {command} <project> <ref> "your comment"',
            file=sys.stderr,
        )
        sys.exit(1)
    return body_text


def add_backlog_comment(project_id, ref, body_text):
    """Add a comment to a backlog item."""
    _require_comment_body(body_text, "backlog-comment")
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    item_id, item = _resolve_backlog_id(headers, service_url, project_id, ref)
    if not item_id:
        print(f"specs: backlog item '{ref}' not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)

    url = f"{service_url}/api/portal/backlog/{item_id}/comments"
    # Pass a dict, not pre-encoded bytes: api_request only attaches the JSON
    # body + Content-Type for dict/str data (bytes falls through both branches,
    # sending an empty body → server 400 "body is required").
    sc, body = api_request(url, method="POST", headers=headers, data={"body": body_text})
    if sc not in (200, 201):
        print(f"specs: comment failed (HTTP {sc}): {body[:200] if body else ''}", file=sys.stderr)
        sys.exit(1)
    resp = json.loads(body) if body else {}
    print(f"specs: comment added to #{item.get('number')} — id {resp.get('id', '?')}")


def depend_backlog(project_id, ref, on_ref, remove=False):
    """Add or remove 'this item waits for that one'.

    The service owns the consequences: it rejects a dependency that would make
    two items wait for each other, and it moves the item's status to blocked
    (or back off it) in the same transaction. This end only resolves the two
    references and reports what the service decided.
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    item_id, item = _resolve_backlog_id(headers, service_url, project_id, ref)
    if not item_id:
        print(f"specs: backlog item '{ref}' not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)
    on_id, on_item = _resolve_backlog_id(headers, service_url, project_id, on_ref)
    if not on_id:
        print(f"specs: backlog item '{on_ref}' not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)

    base = f"{service_url}/api/portal/backlog/{item_id}/dependencies"
    if remove:
        sc, body = api_request(f"{base}?dependsOnId={on_id}", method="DELETE", headers=headers)
    else:
        sc, body = api_request(base, method="POST", headers=headers, data={"dependsOnId": on_id})
    if sc not in (200, 201):
        # The cycle check and the same-project rule both come back as 400 with
        # a sentence worth showing verbatim — it names both items.
        detail = ""
        try:
            detail = (json.loads(body) or {}).get("error", "")
        except Exception:
            detail = (body or "")[:200]
        print(f"specs: dependency change failed (HTTP {sc}): {detail}", file=sys.stderr)
        sys.exit(1)

    a, b = item.get("number"), on_item.get("number")
    if remove:
        print(f"specs: #{a} no longer depends on #{b}")
    else:
        print(f"specs: #{a} now depends on #{b} — {on_item.get('title', '')}")
    print("specs: run 'view-backlog' to see the status the service settled on")


def list_backlog_comments(project_id, ref, as_json=False):
    """List comments on a backlog item. Uses the by-number endpoint which
    already returns embedded comments — saves a round trip."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    item, err = _fetch_backlog_detail(headers, service_url, project_id, ref)
    if not item:
        print(f"specs: {err}", file=sys.stderr)
        sys.exit(1)

    comments = item.get("comments") or []
    if as_json:
        print(json.dumps(comments, indent=2, ensure_ascii=False))
        return

    if not comments:
        print(f"specs: no comments on backlog #{item.get('number')}")
        return
    print(f"specs: {len(comments)} comment(s) on backlog #{item.get('number')}")
    print()
    for c in comments:
        author = c.get("author") or c.get("authorType", "anonymous")
        print(f"· {author} — {c.get('createdAt', '?')}  [id: {c.get('id', '')}]")
        body = (c.get("body") or "").strip()
        for line in body.splitlines() or [""]:
            print(f"    {line}")
        print()


def edit_backlog_comment(project_id, ref, comment_id, body_text):
    """Edit a comment on a backlog item. Author only on the server."""
    _require_comment_body(body_text, "edit-backlog-comment")

    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    item_id, item = _resolve_backlog_id(headers, service_url, project_id, ref)
    if not item_id:
        print(f"specs: backlog item '{ref}' not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)

    url = f"{service_url}/api/portal/backlog/{item_id}/comments/{comment_id}"
    try:
        status_code, resp = api_request(
            url, method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"body": body_text},
        )
    except ConnectionError as e:
        print(f"specs: failed to edit comment — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 403:
        print("specs: you can only edit your own comments", file=sys.stderr)
        sys.exit(1)
    if status_code == 404:
        print(f"specs: comment {comment_id} not found on backlog #{item.get('number')}", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 201):
        try:
            err = json.loads(resp).get("error", resp)
        except (json.JSONDecodeError, AttributeError):
            err = resp
        print(f"specs: failed to edit comment (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: comment {comment_id} on backlog #{item.get('number')} edited")


def delete_backlog_comment(project_id, ref, comment_id):
    """Delete a comment from a backlog item."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    item_id, item = _resolve_backlog_id(headers, service_url, project_id, ref)
    if not item_id:
        print(f"specs: backlog item '{ref}' not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)

    url = f"{service_url}/api/portal/backlog/{item_id}/comments/{comment_id}"
    sc, body = api_request(url, method="DELETE", headers=headers)
    if sc not in (200, 204):
        print(f"specs: delete failed (HTTP {sc}): {body[:200] if body else ''}", file=sys.stderr)
        sys.exit(1)
    print(f"specs: deleted comment {comment_id} from backlog #{item.get('number')}")


# Spec 023: `promote_backlog` removed along with the endpoint it called. There
# is no hard link between a backlog item and a feature any more — the
# relationship lives in comments and descriptive text. To spec an item:
#
#   specs-cli.py create-feature <project> <NNN-name>
#   specs-cli.py create-doc     <project> <NNN-name> spec.md
#   specs-cli.py backlog-comment <project> #N "Specced as <NNN-name>"


def restore_backlog(project_id, ref):
    """Restore a soft-deleted backlog item (internal users only)."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    item_id, _item = _resolve_backlog_id(headers, service_url, project_id, ref)
    if not item_id:
        print(f"specs: backlog item '{ref}' not found in '{project_id}' (deleted items aren't in the active list — pass the uuid)", file=sys.stderr)
        sys.exit(1)

    url = f"{service_url}/api/portal/backlog/{item_id}/restore"
    sc, body = api_request(url, method="POST", headers=headers, data=None)
    if sc not in (200, 201):
        print(f"specs: restore failed (HTTP {sc}): {body[:200] if body else ''}", file=sys.stderr)
        sys.exit(1)
    resp = json.loads(body) if body else {}
    print(f"specs: restored backlog #{resp.get('number', '?')} — {resp.get('title', '?')}")


def create_backlog_item(project_id, title, description=None, priority="medium", parent=None, is_epic=False, assignee=None, tags=None):
    """Create a new backlog item. `parent` may be a uuid or a numeric #N reference.
    `is_epic=True` marks this item as an epic (can have children, can't have a parent).
    `assignee` is an email (spec 022) — optional, omitted means unassigned.
    `tags` (spec 027) is a list of existing tag slugs or names; coining a new
    tag is a separate, permission-gated act, so an unknown name fails here
    rather than quietly growing the project's vocabulary."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    if is_epic and parent:
        print("specs: --epic and --parent are mutually exclusive (epics can't have a parent)", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]

    parent_id = None
    if parent:
        parent_id, parent_item = _resolve_backlog_id(headers, service_url, project_id, parent)
        if not parent_id:
            print(f"specs: parent '{parent}' not found in project '{project_id}'", file=sys.stderr)
            sys.exit(1)
        if not parent_item.get("isEpic"):
            print(f"specs: '#{parent_item.get('number')}' is not an epic — only epics can have children", file=sys.stderr)
            sys.exit(1)

    url = f"{service_url}/api/portal/projects/{project_id}/backlog"
    payload = {"title": title, "description": description, "priority": priority}
    if parent_id:
        payload["parentId"] = parent_id
    if is_epic:
        payload["isEpic"] = True
    if assignee:
        payload["assignedTo"] = assignee
    if tags:
        payload["tags"] = tags

    try:
        status_code, body = api_request(
            url, method="POST",
            headers={**headers, "Content-Type": "application/json"},
            data=payload,
        )
    except ConnectionError as e:
        print(f"specs: failed to create backlog item — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 404:
        try:
            err_body = json.loads(body)
        except (json.JSONDecodeError, TypeError):
            err_body = {}
        if err_body.get("error") == "project_not_found":
            print(
                f"specs: project '{project_id}' is not registered with the spec service.\n"
                f"       Your local config lists it, but the server doesn't know about it.\n"
                f"       Run `python3 scripts/bootstrap-specs.py {project_id} <specs-path>` from ops-cortex-core,\n"
                f"       or check the canonical list via the portal at /api/portal/projects.",
                file=sys.stderr,
            )
            sys.exit(1)
    if status_code not in (200, 201):
        _print_assignee_error(status_code, body, assignee)
        if _print_tag_error(status_code, body):
            sys.exit(1)
        print(f"specs: failed to create backlog item (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    item = json.loads(body)
    kind = "epic" if is_epic else "backlog item"
    parent_note = f" under epic '{parent}'" if parent_id else ""
    assigned_note = f", assigned to {_assignee_label(item) or assignee}" if assignee else ""
    tag_note = f", tagged {' '.join('#' + n for n in _tag_names(item))}" if _tag_names(item) else ""
    print(f"specs: created {kind} '{item.get('title')}' in '{project_id}' (priority: {item.get('priority')}){parent_note}{assigned_note}{tag_note}")


def set_backlog_parent(project_id, item_ref, parent_ref):
    """Set or clear the parent of a backlog item. parent_ref of 'none' clears."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]

    item_id, item = _resolve_backlog_id(headers, service_url, project_id, item_ref)
    if not item_id:
        print(f"specs: item '{item_ref}' not found in project '{project_id}'", file=sys.stderr)
        sys.exit(1)

    if str(parent_ref).lower() in ("none", "null", ""):
        new_parent_id = None
    else:
        new_parent_id, new_parent_item = _resolve_backlog_id(headers, service_url, project_id, parent_ref)
        if not new_parent_id:
            print(f"specs: parent '{parent_ref}' not found in project '{project_id}'", file=sys.stderr)
            sys.exit(1)
        if not new_parent_item.get("isEpic"):
            print(f"specs: '#{new_parent_item.get('number')}' is not an epic — only epics can have children", file=sys.stderr)
            sys.exit(1)

    url = f"{service_url}/api/portal/backlog/{item_id}"
    try:
        status_code, body = api_request(
            url, method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"parentId": new_parent_id},
        )
    except ConnectionError as e:
        print(f"specs: failed to update parent — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 201):
        try:
            err = json.loads(body).get("error", body)
        except (json.JSONDecodeError, AttributeError):
            err = body
        print(f"specs: failed to update parent (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    if new_parent_id:
        print(f"specs: '#{item.get('number')}' is now a child of '{parent_ref}'")
    else:
        print(f"specs: '#{item.get('number')}' parent cleared (now top-level)")


def update_backlog_item(project_id, item_ref, fields, tag_edit=None):
    """Update title/description/priority/status/isEpic/assignedTo on an item.

    `fields` is a dict of {api_key: value} to PATCH. Caller is responsible for
    only passing keys the server understands. parentId changes go via
    set_backlog_parent for clearer error reporting; isEpic and assignedTo flip
    through here (assignedTo=None unassigns — spec 022).

    `tag_edit` (spec 027) is {replace, add, remove, clear}. The API takes the
    resulting set rather than a delta, so add/remove are folded against the
    item's current tags once it has been resolved — which is why this can't be
    done by the caller before the round-trip.
    """
    if not fields and not tag_edit:
        print("specs: nothing to update — pass at least one of --title/--description/--priority/--status/--epic/--assignee/--unassign", file=sys.stderr)
        sys.exit(1)

    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]

    item_id, item = _resolve_backlog_id(headers, service_url, project_id, item_ref)
    if not item_id:
        print(f"specs: item '{item_ref}' not found in project '{project_id}'", file=sys.stderr)
        sys.exit(1)

    if tag_edit:
        next_tags = _resolve_tag_edit(item.get("tags"), **tag_edit)
        if next_tags is not None:
            fields = {**fields, "tags": next_tags}

    url = f"{service_url}/api/portal/backlog/{item_id}"
    try:
        status_code, body = api_request(
            url, method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data=fields,
        )
    except ConnectionError as e:
        print(f"specs: failed to update item — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 201):
        _print_assignee_error(status_code, body, fields.get("assignedTo"))
        if _print_tag_error(status_code, body):
            sys.exit(1)
        try:
            err = json.loads(body).get("error", body)
        except (json.JSONDecodeError, AttributeError):
            err = body
        print(f"specs: failed to update item (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    changed = ", ".join(f"{k}={v!r}" for k, v in fields.items())
    print(f"specs: updated '#{item.get('number')}' ({changed})")


def delete_backlog_item(project_id, item_ref):
    """Soft-delete a backlog item. The server cascades to active children."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]

    item_id, item = _resolve_backlog_id(headers, service_url, project_id, item_ref)
    if not item_id:
        print(f"specs: item '{item_ref}' not found in project '{project_id}'", file=sys.stderr)
        sys.exit(1)

    url = f"{service_url}/api/portal/backlog/{item_id}"
    try:
        status_code, body = api_request(
            url, method="DELETE",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to delete item — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 204):
        try:
            err = json.loads(body).get("error", body)
        except (json.JSONDecodeError, AttributeError):
            err = body
        print(f"specs: failed to delete item (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    cascaded = 0
    try:
        cascaded = int(json.loads(body).get("cascadedChildren", 0))
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
        pass
    suffix = f" (cascaded {cascaded} child item(s))" if cascaded else ""
    print(f"specs: deleted '#{item.get('number')}: {item.get('title')}'{suffix}")


def _embed_images(description, image_paths):
    """Append base64-encoded images to the description markdown."""
    import base64
    import mimetypes
    for path in image_paths:
        abs_path = os.path.abspath(path)
        if not os.path.isfile(abs_path):
            print(f"specs: image not found: {path}", file=sys.stderr)
            continue
        mime = mimetypes.guess_type(abs_path)[0] or "image/png"
        with open(abs_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        name = os.path.basename(abs_path)
        description += f"\n\n![{name}](data:{mime};base64,{data})"
    return description


def create_bug(project_id, title, description, severity="medium", image_paths=None, tags=None):
    """Create a bug report, optionally with attached images and tags (spec 027)."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    if severity not in BUG_SEVERITIES:
        print(f"specs: invalid severity '{severity}'. Must be one of: {', '.join(BUG_SEVERITIES)}", file=sys.stderr)
        sys.exit(1)

    # Embed images into description
    if image_paths:
        description = _embed_images(description, image_paths)

    service_url = cfg["service_url"]

    url = f"{service_url}/api/portal/projects/{project_id}/bugs"
    payload = {"title": title, "description": description, "severity": severity}
    if tags:
        payload["tags"] = tags
    try:
        status_code, body = api_request(
            url, method="POST", headers={**headers, "Content-Type": "application/json"},
            data=payload,
        )
    except ConnectionError as e:
        print(f"specs: failed to create bug — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 404:
        try:
            err_body = json.loads(body)
        except (json.JSONDecodeError, TypeError):
            err_body = {}
        if err_body.get("error") == "project_not_found":
            print(
                f"specs: project '{project_id}' is not registered with the spec service.\n"
                f"       Your local config lists it, but the server doesn't know about it.\n"
                f"       Run `python3 scripts/bootstrap-specs.py {project_id} <specs-path>` from ops-cortex-core,\n"
                f"       or check the canonical list via the portal at /api/portal/projects.",
                file=sys.stderr,
            )
            sys.exit(1)
    if status_code not in (200, 201):
        if _print_tag_error(status_code, body):
            sys.exit(1)
        print(f"specs: failed to create bug (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    bug = json.loads(body)
    tag_note = f"  tags: {' '.join('#' + n for n in _tag_names(bug))}" if _tag_names(bug) else ""
    print(f"specs: bug #{bug.get('number', '?')} created — {title}")
    if tag_note:
        print(tag_note)
    print(f"  view: {service_url}/portal/{project_id}/bugs/{bug['id']}")


# ---------------------------------------------------------------------------
# Feature management
# ---------------------------------------------------------------------------

def _next_spec_number(specs_path):
    """Determine the next spec number by scanning existing folders."""
    if not os.path.isdir(specs_path):
        return 1
    max_num = 0
    for entry in os.listdir(specs_path):
        m = re.match(r"^(\d+)-", entry)
        if m:
            max_num = max(max_num, int(m.group(1)))
    return max_num + 1


def _find_project(cfg, project_id):
    """Find a project in config by ID. Returns project dict or exits."""
    for proj in cfg["projects"]:
        if proj["id"] == project_id:
            return proj
    print(f"specs: project '{project_id}' not in config", file=sys.stderr)
    sys.exit(1)


def set_description(feature_id, description):
    """Set or clear a feature's shortDescription. Pass "" to clear."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    if "/" not in feature_id:
        print(f"specs: feature id must be 'project/name' (got '{feature_id}')", file=sys.stderr)
        sys.exit(1)

    import urllib.parse
    service_url = cfg["service_url"]
    encoded_id = urllib.parse.quote(feature_id, safe="")
    status_code, resp_body = api_request(
        f"{service_url}/api/features/lookup?id={encoded_id}",
        method="PATCH",
        headers={**headers, "Content-Type": "application/json"},
        data={"short_description": description},
    )
    if status_code not in (200, 201):
        print(f"specs: failed to update description (HTTP {status_code}): {resp_body}", file=sys.stderr)
        sys.exit(1)

    if description == "":
        print(f"specs: feature {feature_id} description cleared")
    else:
        print(f"specs: feature {feature_id} description updated")


def set_title(feature_id, title):
    """Update a feature's display title without renaming the slug.

    The portal's feature list and detail headers read from `title`, not from
    the slug — so this is the right command when the slug is fine but the
    human-readable name needs a touch-up (e.g. fixing the every-word-capitalized
    output of the auto-derivation during rename).
    """
    if not title or not title.strip():
        print("specs: title must be non-empty (use rename-feature to change the slug)", file=sys.stderr)
        sys.exit(1)

    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    if "/" not in feature_id:
        print(f"specs: feature id must be 'project/name' (got '{feature_id}')", file=sys.stderr)
        sys.exit(1)

    import urllib.parse
    service_url = cfg["service_url"]
    encoded_id = urllib.parse.quote(feature_id, safe="")
    try:
        status_code, resp_body = api_request(
            f"{service_url}/api/features/lookup?id={encoded_id}",
            method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"title": title},
        )
    except ConnectionError as e:
        print(f"specs: failed to update title — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 404:
        print(f"specs: feature '{feature_id}' not found", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 201):
        try:
            err = json.loads(resp_body).get("error", resp_body)
        except (json.JSONDecodeError, AttributeError):
            err = resp_body
        print(f"specs: failed to update title (HTTP {status_code}): {err}", file=sys.stderr)
        sys.exit(1)

    print(f"specs: feature {feature_id} title → {title!r}")


def create_feature(project_id, name, initial_status="specifying", description=None):
    """Create a new feature in a project."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    proj = _find_project(cfg, project_id)
    specs_path = proj["path"]
    service_url = cfg["service_url"]

    # Determine folder name
    if re.match(r"^\d+-", name):
        folder_name = name
    else:
        num = _next_spec_number(specs_path)
        folder_name = f"{num:03d}-{name}"

    feature_id = f"{project_id}/{folder_name}"

    # Extract number from the folder name prefix (always present — we either
    # matched one in `name` above, or computed `num` and formatted it in).
    number_match = re.match(r"^(\d+)-", folder_name)
    feature_number = int(number_match.group(1)) if number_match else None

    # Create local folder
    local_dir = os.path.join(specs_path, folder_name)
    os.makedirs(local_dir, exist_ok=True)
    context_path = os.path.relpath(local_dir, os.getcwd())

    # Humanize folder name for title: "003-user-notifications" -> "User Notifications"
    title = re.sub(r"^\d+-", "", folder_name).replace("-", " ").title()

    # Register in service
    payload = {
        "project": project_id,
        "name": folder_name,
        "title": title,
        "contextPath": context_path,
    }
    if feature_number is not None:
        payload["number"] = feature_number

    try:
        status_code, body = api_request(
            f"{service_url}/api/features",
            method="POST",
            headers={**headers, "Content-Type": "application/json"},
            data=payload,
        )
    except ConnectionError as e:
        print(f"specs: failed to create feature — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 409:
        print(f"specs: feature '{feature_id}' already exists", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 201):
        print(f"specs: failed to create feature (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    # Set status if not the API default ("draft")
    if initial_status != "draft":
        import urllib.parse
        encoded_id = urllib.parse.quote(feature_id, safe="")
        api_request(
            f"{service_url}/api/features/lookup?id={encoded_id}",
            method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"status": initial_status},
        )

    # Set shortDescription if provided (POST /api/features doesn't accept it yet)
    if description is not None:
        import urllib.parse
        encoded_id = urllib.parse.quote(feature_id, safe="")
        status_code, resp_body = api_request(
            f"{service_url}/api/features/lookup?id={encoded_id}",
            method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"short_description": description},
        )
        if status_code not in (200, 201):
            print(f"specs: warning — feature created but description PATCH failed (HTTP {status_code}): {resp_body}", file=sys.stderr)

    print(f"specs: created feature '{feature_id}'")
    print(f"  path: {local_dir}")
    print(f"  status: {initial_status}")
    print(f"  portal: {service_url}/portal/{project_id}/specs/{folder_name}")


def create_document(project_id, feature_name, filename):
    """Add a document to an existing feature."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    proj = _find_project(cfg, project_id)
    specs_path = proj["path"]
    service_url = cfg["service_url"]

    feature_id = f"{project_id}/{feature_name}"

    if not filename.endswith(".md"):
        filename = f"{filename}.md"

    local_dir = os.path.join(specs_path, feature_name)
    if not os.path.isdir(local_dir):
        print(f"specs: feature folder not found: {local_dir}", file=sys.stderr)
        print(f"  run: specs-cli.py create-feature {project_id} {feature_name}", file=sys.stderr)
        sys.exit(1)

    local_path = os.path.join(local_dir, filename)
    if os.path.isfile(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            content = f.read()
        meta, _ = parse_frontmatter(content)
        if meta.get("spec_doc_id"):
            print(f"specs: {filename} already tracked (doc_id: {meta['spec_doc_id']})", file=sys.stderr)
            return

    # Read existing content or create placeholder
    if os.path.isfile(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            existing = f.read()
        _, initial_content = parse_frontmatter(existing)
        initial_content = initial_content.strip() or f"# {filename.replace('.md', '').replace('-', ' ').title()}"
    else:
        initial_content = f"# {filename.replace('.md', '').replace('-', ' ').title()}"

    # Register document in service
    import urllib.parse
    encoded_feature = urllib.parse.quote(feature_id, safe="")

    payload = {"filename": filename, "content": initial_content}
    try:
        status_code, body = api_request(
            f"{service_url}/api/features/lookup/documents?id={encoded_feature}",
            method="POST",
            headers={**headers, "Content-Type": "application/json"},
            data=payload,
        )
    except ConnectionError as e:
        print(f"specs: failed to create document — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 201):
        print(f"specs: failed to create document (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    resp = json.loads(body)
    doc_id = resp.get("id")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {
        "spec_doc_id": doc_id,
        "spec_version": 1,
        "last_synced": now,
    }

    if os.path.isfile(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            existing_body = f.read()
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(render_frontmatter(meta, existing_body))
    else:
        title = filename.replace(".md", "").replace("-", " ").title()
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(render_frontmatter(meta, f"\n# {title}\n"))

    print(f"specs: created document '{filename}' in '{feature_id}'")
    print(f"  path: {local_path}")
    print(f"  doc_id: {doc_id}")


def _derive_title(slug):
    """Derive a human-readable title from a feature slug.

    '003-agentic-context-service' → 'Agentic Context Service'
    'my-feature' → 'My Feature'
    """
    name = re.sub(r"^\d+-", "", slug)
    return name.replace("-", " ").replace("_", " ").strip().title()


def rename_feature(project_id, old_name, new_name, title_override=None):
    """Rename a feature folder and update the service (name + title)."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    proj = _find_project(cfg, project_id)
    specs_path = proj["path"]
    service_url = cfg["service_url"]

    # Preserve number prefix
    old_match = re.match(r"^(\d+)-", old_name)
    new_match = re.match(r"^(\d+)-", new_name)
    if old_match and not new_match:
        new_name = f"{old_match.group(1)}-{new_name}"

    old_feature_id = f"{project_id}/{old_name}"
    new_feature_id = f"{project_id}/{new_name}"
    new_title = title_override or _derive_title(new_name)

    old_dir = os.path.join(specs_path, old_name)
    new_dir = os.path.join(specs_path, new_name)

    if not os.path.isdir(old_dir):
        print(f"specs: feature folder not found: {old_dir}", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(new_dir):
        print(f"specs: target folder already exists: {new_dir}", file=sys.stderr)
        sys.exit(1)

    # Update service — send both name and title (bug #6 fix).
    import urllib.parse
    encoded_id = urllib.parse.quote(old_feature_id, safe="")

    try:
        status_code, body = api_request(
            f"{service_url}/api/features/lookup?id={encoded_id}",
            method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"name": new_name, "title": new_title},
        )
    except ConnectionError as e:
        print(f"specs: failed to rename feature — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 409:
        print(f"specs: feature '{new_feature_id}' already exists in service", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 201):
        print(f"specs: failed to rename feature (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    os.rename(old_dir, new_dir)

    print(f"specs: renamed '{old_feature_id}' → '{new_feature_id}'")
    print(f"  title: {new_title}")
    print(f"  path: {new_dir}")


def _doc_id_siblings(abs_path, doc_id):
    """Other files in the same folder carrying the same spec_doc_id.

    OneDrive conflict copies (`design-<Machine>.md`) are byte-for-byte clones
    of the original, frontmatter included, so two files can claim one document
    id. Any command that resolves its target by id — delete, rename — must
    refuse in that case, or it acts on the original while the caller is
    looking at the copy.
    """
    folder = os.path.dirname(abs_path)
    twins = []
    try:
        names = os.listdir(folder)
    except OSError:
        return twins
    for fname in sorted(names):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(folder, fname)
        if fpath == abs_path or not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                head = f.read(4096)
        except (IOError, OSError):
            continue
        meta, _ = parse_frontmatter(head)
        if meta.get("spec_doc_id") == doc_id:
            twins.append(fpath)
    return twins


def _refuse_if_ambiguous_doc_id(file_path, abs_path, doc_id, verb):
    """Exit 1 when more than one local file claims `doc_id`."""
    twins = _doc_id_siblings(abs_path, doc_id)
    if not twins:
        return
    print(
        f"specs: refusing to {verb} — {len(twins) + 1} files in this folder carry "
        f"spec_doc_id {doc_id}:",
        file=sys.stderr,
    )
    print(f"  {abs_path}  (given)", file=sys.stderr)
    for t in twins:
        print(f"  {t}", file=sys.stderr)
    print(
        "  These are sync conflict copies of one document. Acting on the id would "
        "hit the original, not the copy.\n"
        "  Remove the stray file itself instead (rm <path>), keeping the one whose "
        "filename matches the service, then retry.",
        file=sys.stderr,
    )
    sys.exit(1)


def rename_document(file_path, new_filename):
    """Rename a document file and update the service."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    abs_path = os.path.abspath(file_path)

    if not os.path.isfile(abs_path):
        print(f"specs: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not new_filename.endswith(".md"):
        new_filename = f"{new_filename}.md"

    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()
    meta, body = parse_frontmatter(content)
    doc_id = meta.get("spec_doc_id")

    if not doc_id:
        print(f"specs: {file_path} has no spec_doc_id — not tracked by service", file=sys.stderr)
        sys.exit(1)

    _refuse_if_ambiguous_doc_id(file_path, abs_path, doc_id, "rename")

    try:
        status_code, resp_body = api_request(
            f"{service_url}/api/documents/{doc_id}",
            method="PATCH",
            headers={**headers, "Content-Type": "application/json"},
            data={"filename": new_filename},
        )
    except ConnectionError as e:
        print(f"specs: failed to rename document — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code == 409:
        print(f"specs: document '{new_filename}' already exists in this feature", file=sys.stderr)
        sys.exit(1)
    if status_code not in (200, 201):
        print(f"specs: failed to rename document (HTTP {status_code}): {resp_body}", file=sys.stderr)
        sys.exit(1)

    new_path = os.path.join(os.path.dirname(abs_path), new_filename)
    os.rename(abs_path, new_path)

    print(f"specs: renamed '{os.path.basename(abs_path)}' → '{new_filename}'")
    print(f"  path: {new_path}")


def delete_document(file_path):
    """Delete a document from filesystem and service."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    abs_path = os.path.abspath(file_path)

    if not os.path.isfile(abs_path):
        print(f"specs: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()
    meta, _ = parse_frontmatter(content)
    doc_id = meta.get("spec_doc_id")

    if not doc_id:
        print(f"specs: {file_path} has no spec_doc_id — not tracked by service", file=sys.stderr)
        os.remove(abs_path)
        print(f"specs: deleted local file: {file_path}")
        return

    _refuse_if_ambiguous_doc_id(file_path, abs_path, doc_id, "delete")

    try:
        status_code, body = api_request(
            f"{service_url}/api/documents/{doc_id}",
            method="DELETE",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to delete from service — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 204, 404):
        print(f"specs: failed to delete document (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    os.remove(abs_path)
    print(f"specs: deleted '{os.path.basename(abs_path)}' (doc_id: {doc_id})")


def delete_feature(project_id, feature_name):
    """Delete a feature and all its documents."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    proj = _find_project(cfg, project_id)
    specs_path = proj["path"]
    service_url = cfg["service_url"]

    feature_id = f"{project_id}/{feature_name}"
    local_dir = os.path.join(specs_path, feature_name)

    import urllib.parse
    encoded_id = urllib.parse.quote(feature_id, safe="")

    try:
        status_code, body = api_request(
            f"{service_url}/api/features/lookup?id={encoded_id}",
            method="DELETE",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to delete from service — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code not in (200, 204, 404):
        print(f"specs: failed to delete feature (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    if os.path.isdir(local_dir):
        import shutil
        shutil.rmtree(local_dir)

    print(f"specs: deleted feature '{feature_id}'")


def list_docs(project_id, feature_name):
    """List all documents in a feature."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    feature_id = f"{project_id}/{feature_name}"

    import urllib.parse
    encoded_id = urllib.parse.quote(feature_id, safe="")

    try:
        status_code, body = api_request(
            f"{service_url}/api/features/lookup?id={encoded_id}",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to look up feature — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: feature '{feature_id}' not found (HTTP {status_code})", file=sys.stderr)
        sys.exit(1)

    feature_data = json.loads(body)
    documents = feature_data.get("documents", [])

    if not documents:
        print(f"specs: no documents in '{feature_id}'")
        return

    print(f"specs: {len(documents)} document(s) in '{feature_id}'")
    print()
    for doc in documents:
        filename = doc.get("filename", "?")
        doc_status = doc.get("status", "?")
        version = doc.get("versionCount", "?")
        print(f"  {filename:40s}  v{version}  {doc_status}")


def feature_snapshot(project_id, feature_name, as_json=False):
    """One-call feature snapshot: feature status, per-doc status, unresolved comment counts.

    Thin wrapper over /api/features/lookup/snapshot. Built for pollers
    (e.g. a watcher deriving gate state from doc statuses), so exit
    behavior is strict: auth failure, unknown feature, and transport
    errors are all distinguishable on stderr with non-zero exit.
    """
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]
    feature_id = f"{project_id}/{feature_name}"

    import urllib.parse
    encoded_id = urllib.parse.quote(feature_id, safe="")

    try:
        status_code, body = api_request(
            f"{service_url}/api/features/lookup/snapshot?id={encoded_id}",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to fetch snapshot — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code in (401, 403):
        print("specs: authentication failed — run /awolve-spec:login", file=sys.stderr)
        sys.exit(1)
    if status_code == 404:
        print(f"specs: feature '{feature_id}' not found", file=sys.stderr)
        sys.exit(1)
    if status_code != 200:
        print(f"specs: snapshot failed (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    snapshot = json.loads(body)

    if as_json:
        print(json.dumps(snapshot, indent=2))
        return

    print(f"specs: {snapshot.get('project')}/{snapshot.get('feature')} — {snapshot.get('featureStatus')}")
    docs = snapshot.get("docs", [])
    if not docs:
        print("  (no documents)")
        return
    print()
    for doc in docs:
        name = doc.get("name", "?")
        doc_status = doc.get("status", "?")
        unresolved = doc.get("unresolvedComments", 0)
        suffix = f"  {unresolved} unresolved" if unresolved else ""
        print(f"  {name:40s}  {doc_status}{suffix}")


def list_features(project_id):
    """List all features in a project."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]

    try:
        status_code, body = api_request(
            f"{service_url}/api/features?project={project_id}",
            headers=headers,
        )
    except ConnectionError as e:
        print(f"specs: failed to list features — {e}", file=sys.stderr)
        sys.exit(1)

    if status_code != 200:
        print(f"specs: failed to list features (HTTP {status_code}): {body}", file=sys.stderr)
        sys.exit(1)

    features = json.loads(body)
    if not features:
        print(f"specs: no features in '{project_id}'")
        return

    print(f"specs: {len(features)} feature(s) in '{project_id}'")
    print()
    for f in features:
        name = f.get("name", "?")
        feat_status = f.get("status", "?")
        doc_count = f.get("documentCount", 0)
        status_marker = {
            "idea": ".",
            "specifying": "*",
            "in_progress": ">",
            "completed": "+",
            "archived": "x",
        }.get(feat_status, "?")
        print(f"  [{status_marker}] {name:40s}  {feat_status:15s}  {doc_count} doc(s)")


# ---------------------------------------------------------------------------
# Attachments
# ---------------------------------------------------------------------------

def _build_multipart(entity_type, entity_id, file_path):
    """Build a multipart/form-data body for attachment upload.

    Returns (content_type, body_bytes).
    """
    import mimetypes
    import uuid
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = "application/octet-stream"

    boundary = f"----awolve-spec-{uuid.uuid4().hex}"
    crlf = b"\r\n"
    parts = []

    def add_field(name, value):
        parts.append(f"--{boundary}".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        parts.append(b"")
        parts.append(value.encode() if isinstance(value, str) else value)

    add_field("entityType", entity_type)
    add_field("entityId", entity_id)

    parts.append(f"--{boundary}".encode())
    parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode()
    )
    parts.append(f"Content-Type: {mime}".encode())
    parts.append(b"")
    parts.append(file_bytes)

    parts.append(f"--{boundary}--".encode())
    parts.append(b"")

    body = crlf.join(parts)
    content_type = f"multipart/form-data; boundary={boundary}"
    return content_type, body


def attach_file(file_path, feature_identifier=None):
    """Upload a local file as a binary attachment to a feature.

    If feature_identifier is None, infer the feature from the file path
    (file must live inside a configured specs directory).
    """
    if not os.path.isfile(file_path):
        print(f"specs: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    cfg = config.read_config()
    if not cfg:
        print("specs: no config found — run /awolve-spec:login", file=sys.stderr)
        sys.exit(1)

    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login", file=sys.stderr)
        sys.exit(1)

    service_url = cfg["service_url"]

    # Resolve the target feature
    if feature_identifier:
        # Expect "project-id/feature-name"
        if "/" not in feature_identifier:
            print(
                f"specs: feature identifier must be 'project-id/feature-name', got: {feature_identifier}",
                file=sys.stderr,
            )
            sys.exit(1)
        project_id, feature_name = feature_identifier.split("/", 1)
    else:
        # Infer from file path — find matching project and feature folder
        abs_file = os.path.abspath(file_path)
        proj = config.find_project_for_file(cfg, abs_file)
        if not proj:
            print(
                f"specs: {file_path} is not inside any configured specs directory — pass <project-id>/<feature-name> explicitly",
                file=sys.stderr,
            )
            sys.exit(1)
        project_id = proj["id"]
        # Feature is the first path component under the specs path
        specs_path = os.path.abspath(proj["path"])
        rel = os.path.relpath(abs_file, specs_path)
        parts = rel.split(os.sep)
        if len(parts) < 2:
            print(
                f"specs: {file_path} must be inside a feature folder (e.g. 001-my-feature/)",
                file=sys.stderr,
            )
            sys.exit(1)
        feature_name = parts[0]

    # Look up feature id from the service
    list_url = f"{service_url}/api/portal/projects/{project_id}/features"
    try:
        status, body = api_request(list_url, headers=headers)
    except ConnectionError as e:
        print(f"specs: {e}", file=sys.stderr)
        sys.exit(1)
    if status != 200:
        print(f"specs: failed to list features (HTTP {status})", file=sys.stderr)
        sys.exit(1)

    features_list = json.loads(body)
    feature = None
    for f in features_list:
        if f.get("name") == feature_name or f.get("id", "").endswith(f"/{feature_name}"):
            feature = f
            break
    if not feature:
        print(f"specs: feature '{feature_name}' not found in project '{project_id}'", file=sys.stderr)
        sys.exit(1)

    feature_id = feature["id"]
    upload_filename = os.path.basename(file_path)

    # Check for existing attachment with the same filename and delete it first
    # (bug #8: re-uploading the same filename previously created duplicates).
    try:
        att_status, att_body = api_request(
            f"{service_url}/api/portal/attachments?entityType=feature&entityId={urllib.parse.quote(feature_id, safe='')}",
            headers=headers,
        )
        if att_status == 200:
            existing_atts = json.loads(att_body) if isinstance(att_body, str) else att_body
            for att in existing_atts:
                if att.get("filename") == upload_filename:
                    del_status, _ = api_request(
                        f"{service_url}/api/portal/attachments/{att['id']}",
                        method="DELETE",
                        headers=headers,
                    )
                    if del_status in (200, 204):
                        print(f"specs: replaced existing attachment '{upload_filename}'")
                    break
    except Exception:
        pass  # best-effort — upload will still succeed, just may duplicate

    content_type, body_bytes = _build_multipart("feature", feature_id, file_path)

    upload_url = f"{service_url}/api/portal/attachments"
    upload_headers = dict(headers)
    upload_headers["Content-Type"] = content_type
    upload_headers["Content-Length"] = str(len(body_bytes))

    req = urllib.request.Request(upload_url, data=body_bytes, headers=upload_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            resp_body = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as e:
        msg = ""
        try:
            msg = e.read().decode("utf-8")[:200]
        except Exception:
            pass
        print(f"specs: upload failed (HTTP {e.code}): {msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"specs: upload failed — {e.reason}", file=sys.stderr)
        sys.exit(1)

    if status not in (200, 201):
        print(f"specs: upload failed (HTTP {status}): {resp_body[:200]}", file=sys.stderr)
        sys.exit(1)

    try:
        att = json.loads(resp_body)
    except json.JSONDecodeError:
        att = {}

    print(f"specs: uploaded '{os.path.basename(file_path)}' to {project_id}/{feature_name}")
    if att.get("id"):
        print(f"  id: {att['id']}")
        print(f"  size: {att.get('sizeBytes', '?')} bytes")


# ---------------------------------------------------------------------------
# Attachments (generic — features, bugs, backlog items)
# ---------------------------------------------------------------------------

def _upload_attachment(headers, service_url, entity_type, entity_id, file_path, replace_dup=True):
    """Shared multipart POST to /api/portal/attachments. Replaces a same-named
    attachment on the entity first so we don't accumulate duplicates (bug #8)."""
    if not os.path.isfile(file_path):
        print(f"specs: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    upload_filename = os.path.basename(file_path)
    if replace_dup:
        try:
            list_url = (
                f"{service_url}/api/portal/attachments"
                f"?entityType={urllib.parse.quote(entity_type)}"
                f"&entityId={urllib.parse.quote(entity_id, safe='')}"
            )
            sc, body = api_request(list_url, headers=headers)
            if sc == 200:
                existing = json.loads(body) if isinstance(body, str) else body
                for att in existing:
                    if att.get("filename") == upload_filename:
                        del_sc, _ = api_request(
                            f"{service_url}/api/portal/attachments/{att['id']}",
                            method="DELETE", headers=headers,
                        )
                        if del_sc in (200, 204):
                            print(f"specs: replaced existing attachment '{upload_filename}'")
                        break
        except Exception:
            pass

    content_type, body_bytes = _build_multipart(entity_type, entity_id, file_path)
    upload_url = f"{service_url}/api/portal/attachments"
    upload_headers = dict(headers)
    upload_headers["Content-Type"] = content_type
    upload_headers["Content-Length"] = str(len(body_bytes))

    req = urllib.request.Request(upload_url, data=body_bytes, headers=upload_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            resp_body = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as e:
        msg = ""
        try:
            msg = e.read().decode("utf-8")[:200]
        except Exception:
            pass
        print(f"specs: upload failed (HTTP {e.code}): {msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"specs: upload failed — {e.reason}", file=sys.stderr)
        sys.exit(1)

    if status not in (200, 201):
        print(f"specs: upload failed (HTTP {status}): {resp_body[:200]}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(resp_body)
    except json.JSONDecodeError:
        return {}


def _resolve_bug_id(headers, service_url, project_id, ref):
    """Resolve a bug ref (#N or numeric) to its uuid id, returning (id, item)."""
    s = str(ref).lstrip("#").strip()
    if "-" in s and len(s) >= 32:
        # uuid path — fetch detail directly
        sc, body = api_request(f"{service_url}/api/portal/bugs/{s}", headers=headers)
        if sc != 200:
            return (None, None)
        return (s, json.loads(body))
    try:
        n = int(s)
    except ValueError:
        return (None, None)
    url = f"{service_url}/api/portal/projects/{project_id}/bugs"
    sc, body = api_request(url, headers=headers)
    if sc != 200:
        return (None, None)
    for b in json.loads(body):
        if b.get("number") == n:
            return (b.get("id"), b)
    return (None, None)


def attach_to_bug(project_id, bug_ref, file_path):
    """Upload a file as an attachment on a bug. Mirrors attach_file but
    targets an existing bug — bug-creation already supports --attach for
    initial screenshots; this command lets you add more after the fact."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    bug_id, bug = _resolve_bug_id(headers, service_url, project_id, bug_ref)
    if not bug_id:
        print(f"specs: bug '{bug_ref}' not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)
    att = _upload_attachment(headers, service_url, "bug", bug_id, file_path)
    print(f"specs: uploaded '{os.path.basename(file_path)}' to bug #{bug.get('number')}")
    if att.get("id"):
        print(f"  id: {att['id']}")
        print(f"  size: {att.get('sizeBytes', '?')} bytes")


def attach_to_backlog(project_id, backlog_ref, file_path):
    """Upload a file as an attachment on a backlog item."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    item_id, item = _resolve_backlog_id(headers, service_url, project_id, backlog_ref)
    if not item_id:
        print(f"specs: backlog '{backlog_ref}' not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)
    att = _upload_attachment(headers, service_url, "backlog", item_id, file_path)
    print(f"specs: uploaded '{os.path.basename(file_path)}' to backlog #{item.get('number')}")
    if att.get("id"):
        print(f"  id: {att['id']}")
        print(f"  size: {att.get('sizeBytes', '?')} bytes")


def list_attachments(entity_type, entity_id, as_json=False):
    """List attachments on a feature/bug/backlog entity (by uuid)."""
    if entity_type not in ("feature", "bug", "backlog"):
        print(f"specs: invalid entity-type '{entity_type}' (use feature|bug|backlog)", file=sys.stderr)
        sys.exit(1)
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    url = (
        f"{service_url}/api/portal/attachments"
        f"?entityType={urllib.parse.quote(entity_type)}"
        f"&entityId={urllib.parse.quote(entity_id, safe='')}"
    )
    sc, body = api_request(url, headers=headers)
    if sc != 200:
        print(f"specs: list failed (HTTP {sc}): {body[:200] if body else ''}", file=sys.stderr)
        sys.exit(1)
    atts = json.loads(body)
    if as_json:
        print(json.dumps(atts, indent=2, ensure_ascii=False))
        return
    if not atts:
        print(f"specs: no attachments on {entity_type} {entity_id}")
        return
    print(f"specs: {len(atts)} attachment(s) on {entity_type} {entity_id}")
    for a in atts:
        size = a.get("sizeBytes", "?")
        print(f"  · {a.get('filename', '?')}  ({size} bytes, {a.get('contentType', '?')})")
        print(f"      id: {a.get('id', '?')}  uploaded: {a.get('uploadedAt', '?')} by {a.get('uploadedBy', '?')}")


def _fetch_attachment(attachment_id):
    """Fetch an attachment's binary content by id. Returns (data, server_name).
    Shared by download_attachment and the test-results evidence saver."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    url = f"{service_url}/api/portal/attachments/{attachment_id}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
            # Pull filename from Content-Disposition if present
            disp = resp.headers.get("Content-Disposition", "")
            server_name = None
            if "filename=" in disp:
                server_name = disp.split("filename=", 1)[1].strip().strip('"').split(";")[0]
    except urllib.error.HTTPError as e:
        msg = ""
        try:
            msg = e.read().decode("utf-8")[:200]
        except Exception:
            pass
        print(f"specs: download failed (HTTP {e.code}): {msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"specs: download failed — {e.reason}", file=sys.stderr)
        sys.exit(1)
    return data, server_name


def download_attachment(attachment_id, out_path):
    """Download an attachment's binary content by id. Writes to out_path
    (a directory uses the server-provided filename; a file path is taken
    literally)."""
    data, server_name = _fetch_attachment(attachment_id)
    target = out_path
    if os.path.isdir(out_path):
        if not server_name:
            print(f"specs: out_path '{out_path}' is a directory but server didn't return a filename — pass a full file path", file=sys.stderr)
            sys.exit(1)
        target = os.path.join(out_path, server_name)
    with open(target, "wb") as f:
        f.write(data)
    print(f"specs: wrote {len(data)} bytes → {target}")


def delete_attachment(attachment_id):
    """Delete an attachment by id."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    url = f"{service_url}/api/portal/attachments/{attachment_id}"
    sc, body = api_request(url, method="DELETE", headers=headers)
    if sc not in (200, 204):
        print(f"specs: delete failed (HTTP {sc}): {body[:200] if body else ''}", file=sys.stderr)
        sys.exit(1)
    print(f"specs: deleted attachment {attachment_id}")


def delete_bug(project_id, bug_ref):
    """Soft-delete a bug (internal users only). Mirrors backlog-delete."""
    cfg = config.read_config()
    if not cfg:
        print("specs: no config found", file=sys.stderr)
        sys.exit(1)
    headers = auth.get_headers()
    if not headers:
        print("specs: not authenticated — run /awolve-spec:login first", file=sys.stderr)
        sys.exit(1)
    service_url = cfg["service_url"]

    bug_id, bug = _resolve_bug_id(headers, service_url, project_id, bug_ref)
    if not bug_id:
        print(f"specs: bug '{bug_ref}' not found in '{project_id}'", file=sys.stderr)
        sys.exit(1)

    url = f"{service_url}/api/portal/bugs/{bug_id}"
    sc, body = api_request(url, method="DELETE", headers=headers)
    if sc not in (200, 204):
        print(f"specs: delete failed (HTTP {sc}): {body[:200] if body else ''}", file=sys.stderr)
        sys.exit(1)
    print(f"specs: deleted bug #{bug.get('number')} — {bug.get('title', '')}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Manual Test Runs (spec 015) — author runs/sections/cases, import matrices,
# manage testers, read coverage, sign off. Mirrors the portal admin.
# ---------------------------------------------------------------------------

TEST_RUN_TYPES = ["uat", "regression", "smoke", "exploratory", "other"]
TEST_SIGNOFF_DECISIONS = ["accepted", "accepted_with_conditions", "rejected"]


def _test_request(path, method="GET", data=None):
    _, headers, service_url = _init_and_auth()
    h = dict(headers)
    if data is not None:
        h["Content-Type"] = "application/json"
    try:
        status, body = api_request(f"{service_url}{path}", method=method, headers=h, data=data)
    except ConnectionError as e:
        print(f"specs: request failed — {e}", file=sys.stderr)
        sys.exit(1)
    if status not in (200, 201):
        print(f"specs: HTTP {status}: {body}", file=sys.stderr)
        sys.exit(1)
    return json.loads(body) if body else {}


def test_run_create(project, name, run_type, description, start, end):
    if run_type not in TEST_RUN_TYPES:
        print(f"specs: type must be one of {', '.join(TEST_RUN_TYPES)}", file=sys.stderr)
        sys.exit(1)
    run = _test_request(f"/api/portal/projects/{project}/test-runs", "POST", {
        "name": name, "type": run_type, "description": description, "targetStart": start, "targetEnd": end,
    })
    print(f"specs: test run #{run.get('number','?')} created — {name} [{run_type}]")
    print(f"  id: {run.get('id')}")


def test_run_update(run_id, name, description, status, start, end):
    body = {}
    if name is not None: body["name"] = name
    if description is not None: body["description"] = description
    if status is not None: body["status"] = status
    if start is not None: body["targetStart"] = start
    if end is not None: body["targetEnd"] = end
    if not body:
        print("specs: nothing to update (provide --name/--description/--status/--start/--end)", file=sys.stderr); sys.exit(1)
    run = _test_request(f"/api/portal/test-runs/{run_id}", "PATCH", body)
    print(f"specs: test run #{run.get('number','?')} updated — {run.get('name')} [{run.get('status')}]")
    s, e = run.get("targetStart"), run.get("targetEnd")
    if s or e:
        print(f"  window: {(s or '—')[:10]} → {(e or '—')[:10]}")


def test_run_list(project, run_type):
    q = f"?type={run_type}" if run_type else ""
    runs = _test_request(f"/api/portal/projects/{project}/test-runs{q}")
    if not runs:
        print("specs: no test runs")
        return
    for r in runs:
        print(f"  #{r['number']:<3} [{r['type']:<11}] {r['status']:<8} {r['name']}  "
              f"({r.get('caseCount',0)} cases, {r.get('testerCount',0)} testers)  id={r['id']}")


def test_run_show(run_id, as_json=False):
    run = _test_request(f"/api/portal/test-runs/{run_id}")
    if as_json:
        # Full round-trip dump as a re-importable matrix: section name + title +
        # prerequisite text + derived prerequisiteKeys (the dep edges), so a run
        # can be exported, its case text edited, and re-imported without loss.
        names = {s["id"]: s["name"] for s in run.get("sections", [])}
        cases = [{
            "section": names.get(c["sectionId"], c["sectionId"]),
            "caseKey": c["caseKey"],
            "title": c.get("title"),
            "whatYouDo": c["whatYouDo"],
            "expected": c["expected"],
            "prerequisite": c.get("prerequisite"),
            "prerequisiteKeys": c.get("prerequisiteKeys"),
        } for c in run.get("cases", [])]
        print(json.dumps({"cases": cases}, ensure_ascii=False, indent=2))
        return
    print(f"#{run['number']} {run['name']} [{run['type']}] — {run['status']}")
    by_section = {}
    for c in run.get("cases", []):
        by_section.setdefault(c["sectionId"], []).append(c)
    for s in run.get("sections", []):
        print(f"\n  {s['name']}  (id={s['id']})")
        for c in by_section.get(s["id"], []):
            print(f"    {c['caseKey']:<10} {(c.get('title') or c['whatYouDo'])[:60]}")
            if c.get("prerequisite") or c.get("prerequisiteKeys"):
                bits = []
                if c.get("prerequisiteKeys"): bits.append(f"do first: {c['prerequisiteKeys']}")
                if c.get("prerequisite"): bits.append(c["prerequisite"][:60])
                print(f"               ↳ prereq: {' — '.join(bits)}")
    print(f"\n  testers: {len(run.get('testers', []))}")


def test_section_add(run_id, name, position):
    data = {"name": name}
    if position is not None:
        data["position"] = position
    s = _test_request(f"/api/portal/test-runs/{run_id}/sections", "POST", data)
    print(f"specs: section '{name}' added — id={s.get('id')}")


def test_case_add(run_id, section_id, key, what, expected, feature_id, prerequisite=None, prereq_cases=None, title=None):
    data = {"sectionId": section_id, "caseKey": key, "whatYouDo": what, "expected": expected}
    if title:
        data["title"] = title
    if feature_id:
        data["featureId"] = feature_id
    if prerequisite:
        data["prerequisite"] = prerequisite
    if prereq_cases:
        data["prerequisiteKeys"] = prereq_cases
    c = _test_request(f"/api/portal/test-runs/{run_id}/cases", "POST", data)
    print(f"specs: case {key} added — id={c.get('id')}")


def _parse_matrix(path):
    """Parse a TSV/CSV/JSON test matrix into import rows (section/caseKey/whatYouDo/expected)."""
    if path.endswith(".json"):
        with open(path) as f:
            doc = json.load(f)
        rows = doc.get("cases", doc) if isinstance(doc, dict) else doc
        out = []
        for r in rows:
            out.append({
                "section": r.get("section"),
                "caseKey": r.get("caseKey") or r.get("case_id") or r.get("case"),
                "whatYouDo": r.get("whatYouDo") or r.get("what_you_do") or r.get("what"),
                "expected": r.get("expected"),
                "title": r.get("title") or r.get("name"),
                "prerequisite": r.get("prerequisite"),
                "prerequisiteKeys": r.get("prerequisiteKeys") or r.get("prereqCases") or r.get("prereq_cases"),
                "roles": r.get("roles"),  # list of role names (spec 018), optional
            })
        return [r for r in out if all(r.get(k) for k in ("section", "caseKey", "whatYouDo", "expected"))]
    with open(path) as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    if not lines:
        return []
    delim = "\t" if "\t" in lines[0] else ","
    header = [h.strip() for h in lines[0].split(delim)]
    idx = {h: i for i, h in enumerate(header)}

    def col(parts, *names):
        for n in names:
            if n in idx and idx[n] < len(parts):
                return parts[idx[n]].strip()
        return ""

    out = []
    for ln in lines[1:]:
        parts = ln.split(delim)
        row = {
            "section": col(parts, "section"),
            "caseKey": col(parts, "case_id", "caseKey", "case"),
            "whatYouDo": col(parts, "what_you_do", "whatYouDo", "what"),
            "expected": col(parts, "expected"),
        }
        if all(row.values()):
            ti = col(parts, "title", "name")
            if ti: row["title"] = ti
            pq = col(parts, "prerequisite")
            pk = col(parts, "prerequisite_keys", "prereq_cases")
            if pq: row["prerequisite"] = pq
            if pk: row["prerequisiteKeys"] = pk
            rl = col(parts, "roles")  # role names separated by ';' (spec 018)
            if rl: row["roles"] = [x.strip() for x in rl.split(";") if x.strip()]
            out.append(row)
    return out


def test_import_cases(run_id, path):
    rows = _parse_matrix(path)
    if not rows:
        print("specs: no rows parsed from the matrix (need columns: section, case_id, what_you_do, expected)", file=sys.stderr)
        sys.exit(1)
    res = _test_request(f"/api/portal/test-runs/{run_id}/import", "POST", {"cases": rows})
    extra = f", {res['rolesCreated']} new roles" if res.get("rolesCreated") else ""
    print(f"specs: imported — {res.get('casesNew',0)} new, {res.get('casesUpdated',0)} updated, "
          f"{res.get('sectionsCreated',0)} new sections{extra}")


def test_tester_add(run_id, name, user_email, as_token, email=None):
    if user_email and not as_token:
        data = {"kind": "user", "email": user_email}
    else:
        if not name:
            print("specs: token tester needs --name", file=sys.stderr)
            sys.exit(1)
        data = {"kind": "token", "displayName": name}
        if email:
            data["email"] = email
    t = _test_request(f"/api/portal/test-runs/{run_id}/testers", "POST", data)
    if t.get("link"):
        cfg = config.read_config()
        base = cfg["service_url"] if cfg else ""
        print(f"specs: token tester '{t.get('displayName')}' added")
        print(f"  link: {base}{t['link']}")
    else:
        print(f"specs: tester '{t.get('displayName')}' added — id={t.get('id')}")


def _tally_str(tally):
    """Compact 'ok=3, fail=1' — omits zero buckets. '' when nothing recorded."""
    return ", ".join(f"{k}={v}" for k, v in (tally or {}).items() if v)


def test_coverage(run_id, execution=None, as_json=False):
    q = f"?execution={execution}" if execution else ""
    cov = _test_request(f"/api/portal/test-runs/{run_id}/coverage{q}")
    if as_json:
        print(json.dumps(cov, ensure_ascii=False, indent=2)); return
    o = cov["overall"]
    e = cov.get("execution")
    run_lbl = f"#{cov['run']['number']} {cov['run']['name']}"
    if e:
        run_lbl += f" — run #{e['number']}{(' ' + e['label']) if e.get('label') else ''} ({e['status']})"
    print(f"{run_lbl} — {o['covered']}/{o['totalCases']} covered, {o['withFail']} with a fail")
    for s in cov.get("sections", []):
        print(f"  {s['name'][:40]:<40} {s['covered']}/{s['totalCases']} covered, {s['withFail']} fail, {s['pending']} pending")
    if cov.get("byRole"):
        print("  by role:")
        for r in cov["byRole"]:
            print(f"    {r['name'][:38]:<38} {r['covered']}/{r['totalCases']} covered, {r['withFail']} fail, {r['pending']} pending")
    # Overall verdict distribution (the raw tally coverage counts but never showed).
    overall_tally = _tally_str(o.get("tally"))
    if overall_tally:
        print(f"  verdicts: {overall_tally}")
    # Per-tester breakdown — who recorded what.
    if cov.get("testers"):
        print("  per tester:")
        for t in cov["testers"]:
            tl = _tally_str(t.get("tally"))
            print(f"    {t.get('displayName', '?')[:28]:<28} recorded={t.get('recorded', 0)}" + (f"  {tl}" if tl else ""))
    if cov.get("signoff"):
        print(f"  sign-off: {cov['signoff']['decision']} by {cov['signoff']['signedBy']}")


def test_results(run_id, execution=None, non_ok=False, as_json=False, download_dir=None):
    """Per-case result detail (status/comment/bug/tester/recordedAt + evidence
    screenshots) for a run instance — the read-back that coverage's aggregate
    tallies don't surface. Joins the /results rows (keyed by case id) with
    run-show case identity so each row shows its caseKey + section. --non-ok
    filters to non-ok verdicts; --download <dir> saves every result's photos."""
    run = _test_request(f"/api/portal/test-runs/{run_id}")
    q = f"?execution={execution}" if execution else ""
    payload = _test_request(f"/api/portal/test-runs/{run_id}/results{q}")
    rows = payload.get("results", [])
    if non_ok:
        rows = [r for r in rows if r.get("status") != "ok"]

    section_name = {s["id"]: s["name"] for s in run.get("sections", [])}
    section_pos = {s["id"]: s.get("position", 0) for s in run.get("sections", [])}
    case_by_id = {c["id"]: c for c in run.get("cases", [])}
    by_case = {}
    for r in rows:
        by_case.setdefault(r["caseId"], []).append(r)

    if as_json:
        out = []
        for cid, rs in by_case.items():
            c = case_by_id.get(cid, {})
            out.append({
                "caseId": cid,
                "caseKey": c.get("caseKey"),
                "title": c.get("title") or c.get("whatYouDo"),
                "section": section_name.get(c.get("sectionId"), c.get("sectionId")),
                "results": [{
                    "status": r.get("status"), "comment": r.get("comment"), "bugNumber": r.get("bugNumber"),
                    "tester": r.get("testerName"), "recordedAt": r.get("recordedAt"),
                    "stale": r.get("stale"),
                    "photos": [{
                        "id": p.get("id"), "filename": p.get("filename"), "caption": p.get("caption"),
                        "target": p.get("target"), "contentType": p.get("contentType"),
                    } for p in r.get("photos", [])],
                } for r in rs],
            })
        print(json.dumps({"run": run.get("number"), "results": out}, ensure_ascii=False, indent=2))
        return

    if download_dir:
        os.makedirs(download_dir, exist_ok=True)

    print(f"#{run['number']} {run['name']} [{run['type']}] — {run['status']}")
    if not rows:
        print("  (no results recorded)" + (" for non-ok verdicts" if non_ok else ""))
        return

    # Group cases by section, ordered as in the run.
    cids_by_section = {}
    for cid in by_case:
        sid = case_by_id.get(cid, {}).get("sectionId")
        cids_by_section.setdefault(sid, []).append(cid)
    for sid in sorted(cids_by_section, key=lambda s: (section_pos.get(s, 9999), section_name.get(s, ""))):
        print(f"\n  {section_name.get(sid, sid)}")
        cids = sorted(cids_by_section[sid], key=lambda cid: (case_by_id.get(cid, {}).get("position", 0), cid))
        for cid in cids:
            c = case_by_id.get(cid, {})
            key = c.get("caseKey") or cid
            for r in by_case[cid]:
                bits = [f"by {r.get('testerName', '?')}"]
                if r.get("bugNumber"): bits.append(f"bug #{r['bugNumber']}")
                if r.get("stale"): bits.append("STALE")
                print(f"    {key:<10} {(r.get('status') or 'pending'):<12} {'  '.join(bits)}")
                if r.get("comment"):
                    print(f"               ↳ {r['comment']}")
                if r.get("recordedAt"):
                    print(f"               · {r['recordedAt']}" + (f"  ({len(r['photos'])} photo(s))" if r.get("photos") else ""))
                for p in r.get("photos", []):
                    side = p.get("target") or "evidence"
                    label = p.get("caption") or p.get("filename") or "photo"
                    line = f"               📷 [{side}] {label}  id={p.get('id')}"
                    if download_dir:
                        safe = f"{key}_{r.get('status') or 'result'}_{p.get('filename') or p.get('id')}"
                        dest = os.path.join(download_dir, safe)
                        data, _ = _fetch_attachment(p["id"])
                        with open(dest, "wb") as fh:
                            fh.write(data)
                        line += f"  → {dest}"
                    print(line)


def test_signoff(run_id, decision, note):
    if decision not in TEST_SIGNOFF_DECISIONS:
        print(f"specs: decision must be one of {', '.join(TEST_SIGNOFF_DECISIONS)}", file=sys.stderr)
        sys.exit(1)
    s = _test_request(f"/api/portal/test-runs/{run_id}/signoff", "PUT", {"decision": decision, "note": note})
    print(f"specs: signed off test run — {s.get('decision')}")


def test_reset(run_id, tester_id=None, execution=None):
    """Reset recorded results for a run instance — whole run (no tester) or one tester. Destructive."""
    data = {}
    if tester_id: data["testerId"] = tester_id
    if execution: data["executionId"] = execution
    r = _test_request(f"/api/portal/test-runs/{run_id}/reset", "POST", data)
    scope = f"tester {tester_id}" if tester_id else "whole run"
    extra = ", sign-off cleared" if r.get("signoffCleared") else ""
    print(f"specs: reset {scope} — cleared {r.get('results',0)} result(s), {r.get('photos',0)} photo(s); "
          f"{r.get('testersReset',0)} tester(s) re-started{extra}")


# ── run instances (spec 019) ──
def test_exec_list(run_id):
    rows = _test_request(f"/api/portal/test-runs/{run_id}/executions")
    if not rows:
        print("specs: no runs"); return
    for e in rows:
        started = (e.get("startedAt") or "")[:10]
        print(f"  run #{e.get('number')}  {e.get('status'):<8} {started}  {e.get('label') or ''}  id={e.get('id')}")


def test_exec_start(run_id, label=None):
    data = {}
    if label: data["label"] = label
    e = _test_request(f"/api/portal/test-runs/{run_id}/executions", "POST", data)
    print(f"specs: started run #{e.get('number')}{(' ' + e['label']) if e.get('label') else ''} — id={e.get('id')}")


def test_exec_close(exec_id):
    e = _test_request(f"/api/portal/executions/{exec_id}", "PATCH", {"status": "closed"})
    print(f"specs: closed run #{e.get('number')}")


# ── runs / sections / cases — full CRUD parity with the API ──
def test_run_delete(run_id):
    _test_request(f"/api/portal/test-runs/{run_id}", "DELETE")
    print("specs: test run deleted")


def test_section_update(section_id, name, position):
    body = {}
    if name is not None: body["name"] = name
    if position is not None: body["position"] = position
    if not body:
        print("specs: nothing to update (--name / --position)", file=sys.stderr); sys.exit(1)
    s = _test_request(f"/api/portal/sections/{section_id}", "PATCH", body)
    print(f"specs: section updated — {s.get('name')}")


def test_section_delete(section_id):
    _test_request(f"/api/portal/sections/{section_id}", "DELETE")
    print("specs: section deleted")


def test_section_reorder(run_id, ids_csv):
    order = [x.strip() for x in ids_csv.split(",") if x.strip()]
    _test_request(f"/api/portal/test-runs/{run_id}/sections", "PATCH", {"order": order})
    print(f"specs: {len(order)} sections reordered")


def test_case_update(case_id, vals):
    body = {}
    if vals.get("--key"): body["caseKey"] = vals["--key"]
    if vals.get("--title") is not None: body["title"] = vals["--title"]
    if vals.get("--what") is not None: body["whatYouDo"] = vals["--what"]
    if vals.get("--expected") is not None: body["expected"] = vals["--expected"]
    if vals.get("--section"): body["sectionId"] = vals["--section"]
    if vals.get("--feature") is not None: body["featureId"] = vals["--feature"]
    if vals.get("--prerequisite") is not None: body["prerequisite"] = vals["--prerequisite"]
    if vals.get("--prereq-cases") is not None: body["prerequisiteKeys"] = vals["--prereq-cases"]
    if vals.get("--position"): body["position"] = int(vals["--position"])
    if not body:
        print("specs: nothing to update", file=sys.stderr); sys.exit(1)
    c = _test_request(f"/api/portal/cases/{case_id}", "PATCH", body)
    print(f"specs: case {c.get('caseKey')} updated")


def test_case_delete(case_id):
    _test_request(f"/api/portal/cases/{case_id}", "DELETE")
    print("specs: case deleted")


# ── roles (spec 018) ──
def test_role_add(run_id, name, description=None, key=None):
    data = {"name": name}
    if description: data["description"] = description
    if key: data["key"] = key
    r = _test_request(f"/api/portal/test-runs/{run_id}/roles", "POST", data)
    print(f"specs: role '{r.get('name')}' added — id={r.get('id')} key={r.get('key')}")


def test_role_seed(run_id):
    r = _test_request(f"/api/portal/test-runs/{run_id}/roles", "POST", {"seed": True})
    print(f"specs: seeded {r.get('created', 0)} role(s) from project templates")


def test_role_list(run_id):
    roles = _test_request(f"/api/portal/test-runs/{run_id}/roles")
    if not roles:
        print("specs: no roles"); return
    for r in roles:
        desc = f" — {r['description']}" if r.get("description") else ""
        print(f"  {str(r.get('key')):<20} {r.get('name')}{desc}  id={r.get('id')}")


def test_role_rename(role_id, name=None, description=None, key=None):
    body = {}
    if name is not None: body["name"] = name
    if description is not None: body["description"] = description
    if key: body["key"] = key
    if not body:
        print("specs: nothing to update (--name / --description / --key)", file=sys.stderr); sys.exit(1)
    r = _test_request(f"/api/portal/roles/{role_id}", "PATCH", body)
    print(f"specs: role updated — {r.get('name')}")


def test_role_remove(role_id):
    _test_request(f"/api/portal/roles/{role_id}", "DELETE")
    print("specs: role removed")


def test_case_roles(case_id, role_ids_csv):
    ids = [x.strip() for x in role_ids_csv.split(",") if x.strip()]
    _test_request(f"/api/portal/cases/{case_id}/roles", "PUT", {"roleIds": ids})
    print(f"specs: set {len(ids)} role(s) on case")


def test_role_identity_set(run_id, role_id, scope, kind, scope_ref=None, environment=None, account_ref=None, template=None):
    data = {"roleId": role_id, "scope": scope, "kind": kind}
    if scope_ref: data["scopeRef"] = scope_ref
    if environment: data["environment"] = environment
    if account_ref: data["accountRef"] = account_ref
    if template: data["generateTemplate"] = template
    b = _test_request(f"/api/portal/test-runs/{run_id}/role-identities", "POST", data)
    print(f"specs: identity binding added — id={b.get('id')} ({scope}/{kind})")


def test_role_template_add(project, name, description=None, key=None):
    data = {"name": name}
    if description: data["description"] = description
    if key: data["key"] = key
    r = _test_request(f"/api/portal/projects/{project}/test-roles", "POST", data)
    print(f"specs: project role template '{r.get('name')}' added — key={r.get('key')}")


def test_role_template_list(project):
    roles = _test_request(f"/api/portal/projects/{project}/test-roles")
    if not roles:
        print("specs: no project role templates"); return
    for r in roles:
        print(f"  {str(r.get('key')):<20} {r.get('name')}")


# ── re-test (spec 015 follow-up) ──
def test_retest(case_id, note=None):
    r = _test_request(f"/api/portal/cases/{case_id}/retest", "POST", {"note": note})
    extra = f", {len(r.get('skipped', []))} without an email" if r.get("skipped") else ""
    print(f"specs: re-test requested — {r.get('notified', 0)} tester(s) emailed{extra}")


def test_retest_clear(case_id):
    _test_request(f"/api/portal/cases/{case_id}/retest", "DELETE")
    print("specs: re-test request cleared")


def test_result_record(case_id, status, comment, bug, execution=None):
    body = {"status": status}
    if comment is not None: body["comment"] = comment
    if bug is not None: body["bugNumber"] = bug
    if execution: body["executionId"] = execution
    _test_request(f"/api/portal/cases/{case_id}/results", "POST", body)
    print(f"specs: result recorded — {status}")


# ── testers ──
def test_tester_list(run_id):
    testers = _test_request(f"/api/portal/test-runs/{run_id}/testers")
    if not testers:
        print("specs: no testers"); return
    for t in testers:
        extra = " (revoked)" if t.get("revokedAt") else ""
        print(f"  {t.get('displayName',''):<24} [{t.get('kind','?'):<5}] recorded={t.get('recorded',0)}  id={t.get('id')}{extra}")


def test_tester_update(tester_id, revoke, reissue):
    body = {}
    if revoke: body["revoke"] = True
    if reissue: body["reissue"] = True
    if not body:
        print("specs: pass --revoke or --reissue", file=sys.stderr); sys.exit(1)
    t = _test_request(f"/api/portal/testers/{tester_id}", "PATCH", body)
    print(f"specs: tester '{t.get('displayName')}' updated")
    if t.get("link"):
        print(f"  link: {t['link']}")


def test_tester_delete(tester_id):
    _test_request(f"/api/portal/testers/{tester_id}", "DELETE")
    print("specs: tester removed")


# ── case reference images ──
def test_image_list(case_id):
    imgs = _test_request(f"/api/portal/cases/{case_id}/attachments")
    if not imgs:
        print("specs: no reference images"); return
    for im in imgs:
        side = im.get("target") or "expect"
        print(f"  [{side:<6}] {im.get('caption') or im.get('filename')}  id={im.get('id')}")


def test_image_update(case_id, att_id, caption, target):
    body = {}
    if caption is not None: body["caption"] = caption
    if target is not None: body["target"] = target
    if not body:
        print("specs: pass --caption or --target", file=sys.stderr); sys.exit(1)
    _test_request(f"/api/portal/cases/{case_id}/attachments/{att_id}", "PATCH", body)
    print("specs: image updated")


def test_image_delete(case_id, att_id):
    _test_request(f"/api/portal/cases/{case_id}/attachments/{att_id}", "DELETE")
    print("specs: image deleted")


def test_image_add(case_id, file_path, caption, target):
    import uuid as _uuid, mimetypes as _mt
    if not os.path.isfile(file_path):
        print(f"specs: file not found: {file_path}", file=sys.stderr); sys.exit(1)
    _, headers, service_url = _init_and_auth()
    boundary = f"----awolve-spec-{_uuid.uuid4().hex}"
    fname = os.path.basename(file_path)
    ctype = _mt.guess_type(file_path)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        filedata = f.read()
    parts = []
    def field(name, value):
        parts.extend([f"--{boundary}".encode(), f'Content-Disposition: form-data; name="{name}"'.encode(), b"", str(value).encode()])
    if caption: field("caption", caption)
    if target: field("target", target)
    parts.extend([
        f"--{boundary}".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{fname}"'.encode(),
        f"Content-Type: {ctype}".encode(), b"", filedata,
        f"--{boundary}--".encode(), b"",
    ])
    body = b"\r\n".join(parts)
    h = dict(headers)
    h["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    h["Content-Length"] = str(len(body))
    req = urllib.request.Request(f"{service_url}/api/portal/cases/{case_id}/attachments", data=body, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            status, rb = resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"specs: upload failed (HTTP {e.code}): {e.read().decode('utf-8')[:200]}", file=sys.stderr); sys.exit(1)
    if status not in (200, 201):
        print(f"specs: upload failed (HTTP {status})", file=sys.stderr); sys.exit(1)
    im = json.loads(rb) if rb else {}
    print(f"specs: image added — id={im.get('id')} [{im.get('target') or 'expect'}]")


def _parse_flags(rest, value_flags, bool_flags=()):
    """Split a token list into positionals, --flag values, and present --bools."""
    vals, bools, pos, i = {}, set(), [], 0
    while i < len(rest):
        a = rest[i]
        if a in value_flags and i + 1 < len(rest):
            vals[a] = rest[i + 1]; i += 2
        elif a in bool_flags:
            bools.add(a); i += 1
        elif a.startswith("--"):
            i += 1
        else:
            pos.append(a); i += 1
    return pos, vals, bools


def handle_test(args):
    sub = args[0] if args else None
    pos, vals, bools = _parse_flags(
        args[1:],
        value_flags={"--name", "--type", "--description", "--start", "--end", "--section", "--key",
                     "--what", "--expected", "--feature", "--user", "--position", "--decision", "--note", "--status",
                     "--comment", "--bug", "--caption", "--target", "--prerequisite", "--prereq-cases", "--title",
                     "--scope", "--kind", "--scope-ref", "--environment", "--account-ref", "--template", "--email",
                     "--execution", "--label", "--download"},
        bool_flags={"--token", "--json", "--revoke", "--reissue", "--yes", "--non-ok"},
    )
    if sub == "run-create":
        if not pos or not vals.get("--name"):
            print("Usage: specs-cli.py test run-create <project> --name <name> [--type uat] [--description ..] [--start YYYY-MM-DD] [--end YYYY-MM-DD]", file=sys.stderr); sys.exit(1)
        test_run_create(pos[0], vals["--name"], vals.get("--type", "uat"), vals.get("--description"), vals.get("--start"), vals.get("--end"))
    elif sub == "run-list":
        if not pos:
            print("Usage: specs-cli.py test run-list <project> [--type T]", file=sys.stderr); sys.exit(1)
        test_run_list(pos[0], vals.get("--type"))
    elif sub == "run-update":
        if not pos:
            print("Usage: specs-cli.py test run-update <run-id> [--name ..] [--description ..] "
                  "[--status draft|active|closed|archived] [--start YYYY-MM-DD] [--end YYYY-MM-DD]", file=sys.stderr); sys.exit(1)
        test_run_update(pos[0], vals.get("--name"), vals.get("--description"),
                        vals.get("--status"), vals.get("--start"), vals.get("--end"))
    elif sub == "run-show":
        if not pos:
            print("Usage: specs-cli.py test run-show <run-id> [--json]", file=sys.stderr); sys.exit(1)
        test_run_show(pos[0], as_json="--json" in bools)
    elif sub == "section-add":
        if not pos or not vals.get("--name"):
            print("Usage: specs-cli.py test section-add <run-id> --name <name> [--position N]", file=sys.stderr); sys.exit(1)
        test_section_add(pos[0], vals["--name"], int(vals["--position"]) if vals.get("--position") else None)
    elif sub == "case-add":
        if not pos or not all(vals.get(k) for k in ("--section", "--key", "--what", "--expected")):
            print("Usage: specs-cli.py test case-add <run-id> --section <section-id> --key NAV-01 --what '..' --expected '..' [--feature <feature-id>]", file=sys.stderr); sys.exit(1)
        test_case_add(pos[0], vals["--section"], vals["--key"], vals["--what"], vals["--expected"], vals.get("--feature"), vals.get("--prerequisite"), vals.get("--prereq-cases"), vals.get("--title"))
    elif sub == "import-cases":
        if len(pos) < 2:
            print("Usage: specs-cli.py test import-cases <run-id> <matrix.tsv|.csv|.json>", file=sys.stderr); sys.exit(1)
        test_import_cases(pos[0], pos[1])
    elif sub == "tester-add":
        if not pos:
            print("Usage: specs-cli.py test tester-add <run-id> (--user <email> | --name '<Name>' --token [--email <addr>])", file=sys.stderr); sys.exit(1)
        test_tester_add(pos[0], vals.get("--name"), vals.get("--user"), "--token" in bools, vals.get("--email"))
    elif sub == "coverage":
        if not pos:
            print("Usage: specs-cli.py test coverage <run-id> [--execution <id>] [--json]", file=sys.stderr); sys.exit(1)
        test_coverage(pos[0], vals.get("--execution"), as_json="--json" in bools)
    elif sub == "results":
        if not pos:
            print("Usage: specs-cli.py test results <run-id> [--non-ok] [--execution <id>] [--download <dir>] [--json]   (per-case status/comment/bug/tester + evidence screenshots)", file=sys.stderr); sys.exit(1)
        test_results(pos[0], vals.get("--execution"), non_ok="--non-ok" in bools, as_json="--json" in bools, download_dir=vals.get("--download"))
    elif sub == "exec-list":
        if not pos: print("Usage: specs-cli.py test exec-list <test-id>", file=sys.stderr); sys.exit(1)
        test_exec_list(pos[0])
    elif sub == "exec-start":
        if not pos: print("Usage: specs-cli.py test exec-start <test-id> [--label '..']", file=sys.stderr); sys.exit(1)
        test_exec_start(pos[0], vals.get("--label"))
    elif sub == "exec-close":
        if not pos: print("Usage: specs-cli.py test exec-close <execution-id>", file=sys.stderr); sys.exit(1)
        test_exec_close(pos[0])
    elif sub == "signoff":
        if not pos or not vals.get("--decision"):
            print("Usage: specs-cli.py test signoff <run-id> --decision accepted|accepted_with_conditions|rejected [--note ..]", file=sys.stderr); sys.exit(1)
        test_signoff(pos[0], vals["--decision"], vals.get("--note"))
    elif sub == "run-delete":
        if not pos: print("Usage: specs-cli.py test run-delete <run-id>", file=sys.stderr); sys.exit(1)
        test_run_delete(pos[0])
    elif sub == "section-update":
        if not pos: print("Usage: specs-cli.py test section-update <section-id> [--name ..] [--position N]", file=sys.stderr); sys.exit(1)
        test_section_update(pos[0], vals.get("--name"), int(vals["--position"]) if vals.get("--position") else None)
    elif sub == "section-delete":
        if not pos: print("Usage: specs-cli.py test section-delete <section-id>", file=sys.stderr); sys.exit(1)
        test_section_delete(pos[0])
    elif sub == "section-reorder":
        if len(pos) < 2: print("Usage: specs-cli.py test section-reorder <run-id> <section-id1,section-id2,...>", file=sys.stderr); sys.exit(1)
        test_section_reorder(pos[0], pos[1])
    elif sub == "case-update":
        if not pos: print("Usage: specs-cli.py test case-update <case-id> [--key ..] [--what ..] [--expected ..] [--prerequisite ..] [--prereq-cases ..] [--section ..] [--feature ..] [--position N]", file=sys.stderr); sys.exit(1)
        test_case_update(pos[0], vals)
    elif sub == "case-delete":
        if not pos: print("Usage: specs-cli.py test case-delete <case-id>", file=sys.stderr); sys.exit(1)
        test_case_delete(pos[0])
    elif sub == "result-record":
        if not pos or not vals.get("--status"): print("Usage: specs-cli.py test result-record <case-id> --status ok|ok_with_bug|fail|blocked|na [--comment ..] [--bug ..]  (you must be a tester on the run)", file=sys.stderr); sys.exit(1)
        test_result_record(pos[0], vals["--status"], vals.get("--comment"), vals.get("--bug"), vals.get("--execution"))
    elif sub == "reset-run":
        if not pos: print("Usage: specs-cli.py test reset-run <run-id> --yes [--execution <id>]   (deletes ALL results + photos for the run instance, re-starts every tester, clears sign-off)", file=sys.stderr); sys.exit(1)
        if "--yes" not in bools: print("specs: reset-run is destructive (deletes ALL results + photos, clears sign-off) — re-run with --yes to confirm", file=sys.stderr); sys.exit(1)
        test_reset(pos[0], None, vals.get("--execution"))
    elif sub == "reset-tester":
        if len(pos) < 2: print("Usage: specs-cli.py test reset-tester <run-id> <tester-id> --yes [--execution <id>]   (deletes that tester's results + photos in the run instance, re-starts them)", file=sys.stderr); sys.exit(1)
        if "--yes" not in bools: print("specs: reset-tester is destructive (deletes that tester's results + photos) — re-run with --yes to confirm", file=sys.stderr); sys.exit(1)
        test_reset(pos[0], pos[1], vals.get("--execution"))
    elif sub == "tester-list":
        if not pos: print("Usage: specs-cli.py test tester-list <run-id>", file=sys.stderr); sys.exit(1)
        test_tester_list(pos[0])
    elif sub == "tester-update":
        if not pos: print("Usage: specs-cli.py test tester-update <tester-id> (--revoke | --reissue)", file=sys.stderr); sys.exit(1)
        test_tester_update(pos[0], "--revoke" in bools, "--reissue" in bools)
    elif sub == "tester-delete":
        if not pos: print("Usage: specs-cli.py test tester-delete <tester-id>", file=sys.stderr); sys.exit(1)
        test_tester_delete(pos[0])
    elif sub == "image-list":
        if not pos: print("Usage: specs-cli.py test image-list <case-id>", file=sys.stderr); sys.exit(1)
        test_image_list(pos[0])
    elif sub == "image-add":
        if len(pos) < 2: print("Usage: specs-cli.py test image-add <case-id> <file> [--caption ..] [--target do|expect]", file=sys.stderr); sys.exit(1)
        test_image_add(pos[0], pos[1], vals.get("--caption"), vals.get("--target"))
    elif sub == "image-update":
        if len(pos) < 2: print("Usage: specs-cli.py test image-update <case-id> <attachment-id> [--caption ..] [--target do|expect]", file=sys.stderr); sys.exit(1)
        test_image_update(pos[0], pos[1], vals.get("--caption"), vals.get("--target"))
    elif sub == "image-delete":
        if len(pos) < 2: print("Usage: specs-cli.py test image-delete <case-id> <attachment-id>", file=sys.stderr); sys.exit(1)
        test_image_delete(pos[0], pos[1])
    elif sub == "role-add":
        if not pos or not vals.get("--name"):
            print("Usage: specs-cli.py test role-add <run-id> --name <name> [--description ..] [--key ..]", file=sys.stderr); sys.exit(1)
        test_role_add(pos[0], vals["--name"], vals.get("--description"), vals.get("--key"))
    elif sub == "role-seed":
        if not pos: print("Usage: specs-cli.py test role-seed <run-id>  (copy project role templates into the run)", file=sys.stderr); sys.exit(1)
        test_role_seed(pos[0])
    elif sub == "role-list":
        if not pos: print("Usage: specs-cli.py test role-list <run-id>", file=sys.stderr); sys.exit(1)
        test_role_list(pos[0])
    elif sub == "role-rename":
        if not pos: print("Usage: specs-cli.py test role-rename <role-id> [--name ..] [--description ..] [--key ..]", file=sys.stderr); sys.exit(1)
        test_role_rename(pos[0], vals.get("--name"), vals.get("--description"), vals.get("--key"))
    elif sub == "role-remove":
        if not pos: print("Usage: specs-cli.py test role-remove <role-id>", file=sys.stderr); sys.exit(1)
        test_role_remove(pos[0])
    elif sub == "case-roles":
        if len(pos) < 2: print("Usage: specs-cli.py test case-roles <case-id> <role-id1,role-id2,...>", file=sys.stderr); sys.exit(1)
        test_case_roles(pos[0], pos[1])
    elif sub == "role-identity-set":
        if len(pos) < 2 or not vals.get("--scope") or not vals.get("--kind"):
            print("Usage: specs-cli.py test role-identity-set <run-id> <role-id> --scope environment|tester|case --kind account|generated "
                  "[--scope-ref ID] [--environment staging] [--account-ref <kv-label>] [--template 'cand+{run}-{n}@x']", file=sys.stderr); sys.exit(1)
        test_role_identity_set(pos[0], pos[1], vals["--scope"], vals["--kind"], vals.get("--scope-ref"), vals.get("--environment"), vals.get("--account-ref"), vals.get("--template"))
    elif sub == "role-template-add":
        if not pos or not vals.get("--name"):
            print("Usage: specs-cli.py test role-template-add <project> --name <name> [--description ..] [--key ..]", file=sys.stderr); sys.exit(1)
        test_role_template_add(pos[0], vals["--name"], vals.get("--description"), vals.get("--key"))
    elif sub == "role-template-list":
        if not pos: print("Usage: specs-cli.py test role-template-list <project>", file=sys.stderr); sys.exit(1)
        test_role_template_list(pos[0])
    elif sub == "retest":
        if not pos: print("Usage: specs-cli.py test retest <case-id> [--note '..']  (flags the whole case + emails testers)", file=sys.stderr); sys.exit(1)
        test_retest(pos[0], vals.get("--note"))
    elif sub == "retest-clear":
        if not pos: print("Usage: specs-cli.py test retest-clear <case-id>", file=sys.stderr); sys.exit(1)
        test_retest_clear(pos[0])
    else:
        print("Usage: specs-cli.py test <subcommand> ...\n"
              "  runs:     run-create | run-list | run-update | run-delete | run-show | coverage | results | signoff\n"
              "  instances: exec-list <test-id> | exec-start <test-id> [--label ..] | exec-close <exec-id>  (--execution <id> on coverage/result-record/reset)\n"
              "  sections: section-add | section-update | section-delete | section-reorder\n"
              "  cases:    case-add | case-update | case-delete | import-cases\n"
              "  images:   image-list | image-add | image-update | image-delete\n"
              "  testers:  tester-add | tester-list | tester-update | tester-delete\n"
              "  roles:    role-add | role-list | role-rename | role-remove | role-seed | case-roles |\n"
              "            role-identity-set | role-template-add | role-template-list\n"
              "  re-test:  retest <case-id> [--note ..] | retest-clear <case-id>\n"
              "  results:  results <run-id> [--non-ok] (read per-case detail) | result-record (write a verdict)\n"
              "  reset:    reset-run <run-id> --yes | reset-tester <run-id> <tester-id> --yes", file=sys.stderr)
        sys.exit(1)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        print(__doc__.strip())
        sys.exit(0)

    if args[0] in ("--version", "-V", "version"):
        print(_plugin_version())
        sys.exit(0)

    cmd = args[0]
    quiet = "--quiet" in args

    if cmd == "pull":
        project_filter = None
        delete_mode = "trash"
        force_full = False
        for a in args[1:]:
            if a == "--prune":
                delete_mode = "prune"
            elif a == "--keep":
                delete_mode = "keep"
            elif a == "--force-full":
                force_full = True
            elif a == "--quiet":
                pass
            elif not a.startswith("-") and project_filter is None:
                project_filter = a
        pull(project_filter=project_filter, quiet=quiet, delete_mode=delete_mode, force_full=force_full)
    elif cmd == "log":
        project_id = None
        since_arg = None
        author_arg = None
        entity_arg = None
        limit_arg = 50
        json_out = False
        since_last_visit = False
        mark_read = False
        all_projects = False
        i = 1
        while i < len(args):
            a = args[i]
            if a == "--all":
                all_projects = True; i += 1
            elif a == "--since" and i + 1 < len(args):
                since_arg = args[i + 1]; i += 2
            elif a == "--author" and i + 1 < len(args):
                author_arg = args[i + 1]; i += 2
            elif a == "--entity" and i + 1 < len(args):
                entity_arg = args[i + 1]; i += 2
            elif a == "--limit" and i + 1 < len(args):
                try:
                    limit_arg = int(args[i + 1])
                except ValueError:
                    print(f"specs: invalid --limit '{args[i + 1]}'", file=sys.stderr)
                    sys.exit(1)
                i += 2
            elif a == "--json":
                json_out = True; i += 1
            elif a == "--since-last-visit":
                since_last_visit = True; i += 1
            elif a == "--mark-read":
                mark_read = True; i += 1
            elif not a.startswith("-") and project_id is None:
                project_id = a; i += 1
            else:
                i += 1

        if not all_projects and project_id is None:
            print("Usage: specs-cli.py log <project-id|--all> [--since DUR] [--author EMAIL] [--entity TYPE] [--limit N] [--json] [--since-last-visit] [--mark-read]", file=sys.stderr)
            sys.exit(1)
        if all_projects and project_id is not None:
            print("specs: cannot combine --all with a project id", file=sys.stderr)
            sys.exit(1)

        specs_log(
            project_id,  # None when --all is passed
            since=since_arg,
            author=author_arg,
            entity_type=entity_arg,
            limit=limit_arg,
            as_json=json_out,
            since_last_visit=since_last_visit,
            mark_read=mark_read,
        )
    elif cmd == "push":
        if len(args) < 2:
            print("Usage: specs-cli.py push <file_path>", file=sys.stderr)
            sys.exit(1)
        push(args[1])
    elif cmd == "conflicts":
        as_json = "--json" in args
        project_filter = None
        i = 1
        while i < len(args):
            a = args[i]
            if a == "--project" and i + 1 < len(args):
                project_filter = args[i + 1]; i += 2
            elif not a.startswith("-") and project_filter is None:
                project_filter = a; i += 1
            else:
                i += 1
        list_conflicts_cmd(project_filter=project_filter, as_json=as_json)
    elif cmd == "conflict":
        sub = args[1] if len(args) > 1 else None
        if sub == "show" and len(args) >= 3:
            conflict_show(args[2])
        elif sub == "diff" and len(args) >= 3:
            conflict_diff(args[2])
        elif sub == "resolve" and len(args) >= 3:
            ref = args[2]
            if "--theirs" in args:
                conflict_resolve(ref, "theirs")
            elif "--mine" in args:
                conflict_resolve(ref, "mine")
            elif "--merged" in args:
                i = args.index("--merged")
                if i + 1 >= len(args):
                    print("specs: --merged requires a file path", file=sys.stderr)
                    sys.exit(1)
                conflict_resolve(ref, "merged", merged_file=args[i + 1])
            else:
                print("Usage: specs-cli.py conflict resolve <doc> --theirs|--mine|--merged <file>", file=sys.stderr)
                sys.exit(1)
        else:
            print(
                "Usage:\n"
                "  specs-cli.py conflict show <doc>\n"
                "  specs-cli.py conflict diff <doc>\n"
                "  specs-cli.py conflict resolve <doc> --theirs|--mine|--merged <file>",
                file=sys.stderr,
            )
            sys.exit(1)
    elif cmd == "cleanup-synced-tree":
        dry_run = "--dry-run" in args
        include_venv = "--include-venv" in args
        cleanup_synced_tree(dry_run=dry_run, include_venv=include_venv)
    elif cmd == "test":
        handle_test(args[1:])
    elif cmd == "status":
        show_status()
    elif cmd == "set-status":
        if len(args) < 3:
            print("Usage: specs-cli.py set-status <feature-or-doc-id> <status>", file=sys.stderr)
            print(f"  Feature statuses: {', '.join(FEATURE_STATUSES)}", file=sys.stderr)
            print(f"  Document statuses: {', '.join(DOCUMENT_STATUSES)}", file=sys.stderr)
            sys.exit(1)
        set_status(args[1], args[2])
    elif cmd == "bugs":
        proj = args[1] if len(args) > 1 and not args[1].startswith("-") else None
        VALUE_FLAGS_BUGS = {"--assignee", "--tag", "--status"}
        if proj is None:
            for i, a in enumerate(args[1:], 1):
                if a.startswith("-"): continue
                if args[i - 1] in VALUE_FLAGS_BUGS: continue
                proj = a
                break
        assignee_filter = None
        tag_filters = []
        for i, a in enumerate(args):
            if a == "--assignee" and i + 1 < len(args): assignee_filter = args[i + 1]
            # Spec 027: repeatable, OR-ed — `--tag billing --tag auth`.
            if a == "--tag" and i + 1 < len(args): tag_filters.append(args[i + 1])
        if "--unassigned" in args: assignee_filter = "none"
        status_filter = None
        for i, a in enumerate(args):
            if a == "--status" and i + 1 < len(args): status_filter = args[i + 1]
        list_bugs(proj, assignee_filter=assignee_filter, tag_filters=tag_filters,
                  untagged="--untagged" in args, status_filter=status_filter,
                  include_all="--all" in args, as_json="--json" in args)
    elif cmd == "view-bug":
        as_json = "--json" in args
        save_images = "--images" in args
        # --images may be followed by a directory; anything else after it is
        # positional as usual.
        images_dir = None
        rest = args[1:]
        positional = []
        i = 0
        while i < len(rest):
            token = rest[i]
            if token == "--json":
                i += 1
                continue
            if token == "--images":
                if i + 1 < len(rest) and not rest[i + 1].startswith("--"):
                    images_dir = rest[i + 1]
                    i += 2
                else:
                    i += 1
                continue
            positional.append(token)
            i += 1
        if len(positional) < 2:
            print("Usage: specs-cli.py view-bug <project-id> <bug-number> [--json] [--images [dir]]", file=sys.stderr)
            sys.exit(1)
        view_bug(positional[0], positional[1], as_json=as_json,
                 save_images=save_images, images_dir=images_dir)
    elif cmd == "set-bug-status":
        if len(args) < 4:
            print("Usage: specs-cli.py set-bug-status <project-id> <bug-number> <status>", file=sys.stderr)
            print(f"  Statuses: {', '.join(BUG_STATUSES)}", file=sys.stderr)
            sys.exit(1)
        set_bug_status(args[1], args[2], args[3])
    elif cmd == "update-bug":
        # Bug #15: edit affordance on the CLI to match the portal. Mirrors
        # `backlog-update` so the two flows feel consistent.
        positional = []
        flag_map = {"--title": "title", "--description": "description", "--severity": "severity", "--assignee": "assignedTo",
                    "--start": "startDate", "--due": "dueDate", "--estimate": "estimateHours", **DEPLOY_FLAGS}
        fields = {}
        tag_edit = {"replace": None, "add": [], "remove": [], "clear": False}
        skip_next = False
        for i, a in enumerate(args[1:], 1):
            if skip_next:
                skip_next = False
                continue
            # Valueless twin of --assignee — an explicit null is the only way to
            # say "clear" (spec 022).
            if a == "--unassign":
                fields["assignedTo"] = None
                continue
            # Spec 023: same trick per timing field.
            if a in CLEAR_TIMING_FLAGS:
                fields[CLEAR_TIMING_FLAGS[a]] = None
                continue
            # Spec 033: clear the whole deployment fact — the three fields
            # only mean anything together.
            if a == "--clear-deployment":
                fields["deployedStage"] = None
                fields["deployedUrl"] = None
                fields["deployedAt"] = None
                continue
            # Spec 027: tag flags. --tags replaces the set; --add-tag and
            # --remove-tag are repeatable deltas folded against the bug's
            # current tags once it has been resolved.
            if a == "--clear-tags":
                tag_edit["clear"] = True
                continue
            if a in ("--tags", "--add-tag", "--remove-tag"):
                if i + 1 >= len(args):
                    print(f"specs: {a} requires a value", file=sys.stderr)
                    sys.exit(1)
                if a == "--tags":
                    tag_edit["replace"] = args[i + 1]
                elif a == "--add-tag":
                    tag_edit["add"].append(args[i + 1])
                else:
                    tag_edit["remove"].append(args[i + 1])
                skip_next = True
                continue
            if a in flag_map:
                if i + 1 >= len(args):
                    print(f"specs: {a} requires a value", file=sys.stderr)
                    sys.exit(1)
                fields[flag_map[a]] = args[i + 1]
                skip_next = True
                continue
            if a.startswith("--"):
                print(f"specs: unknown flag '{a}' for update-bug", file=sys.stderr)
                sys.exit(1)
            positional.append(a)
        if len(positional) < 2:
            print("Usage: specs-cli.py update-bug <project-id> <bug-number> [--title T] [--description T] [--severity S] [--assignee EMAIL | --unassign] [--start YYYY-MM-DD] [--due YYYY-MM-DD] [--estimate HOURS] [--clear-start|--clear-due|--clear-estimate] [--tags a,b | --add-tag T | --remove-tag T | --clear-tags] [--deployed-stage S --deployed-url U | --clear-deployment]", file=sys.stderr)
            print(f"  Severities: {', '.join(BUG_SEVERITIES)}", file=sys.stderr)
            print(f"  Deployment stages: {', '.join(DEPLOY_STAGES)}", file=sys.stderr)
            sys.exit(1)
        if "--assignee" in args and "--unassign" in args:
            print("specs: --assignee and --unassign are mutually exclusive", file=sys.stderr)
            sys.exit(1)
        if "--clear-deployment" in args and ("--deployed-stage" in args or "--deployed-url" in args):
            print("specs: --clear-deployment and --deployed-stage/--deployed-url are mutually exclusive", file=sys.stderr)
            sys.exit(1)
        if tag_edit["replace"] is not None and (tag_edit["add"] or tag_edit["remove"]):
            print("specs: --tags replaces the whole set; combine --add-tag/--remove-tag instead", file=sys.stderr)
            sys.exit(1)
        validate_timing_fields(fields)
        validate_deployment_fields(fields)
        has_tag_edit = tag_edit["clear"] or tag_edit["replace"] is not None or tag_edit["add"] or tag_edit["remove"]
        update_bug(positional[0], positional[1], fields, tag_edit=tag_edit if has_tag_edit else None)
    elif cmd == "bug-comments":
        as_json = "--json" in args
        positional = [a for a in args[1:] if a != "--json"]
        if len(positional) < 2:
            print("Usage: specs-cli.py bug-comments <project-id> <bug-number> [--json]", file=sys.stderr)
            sys.exit(1)
        list_bug_comments(positional[0], positional[1], as_json=as_json)
    elif cmd == "bug-comment":
        if len(args) < 4:
            print("Usage: specs-cli.py bug-comment <project-id> <bug-number> <body>", file=sys.stderr)
            sys.exit(1)
        add_bug_comment(args[1], args[2], args[3])
    elif cmd == "edit-bug-comment":
        if len(args) < 5:
            print("Usage: specs-cli.py edit-bug-comment <project-id> <bug-number> <comment-id> <body>", file=sys.stderr)
            sys.exit(1)
        edit_bug_comment(args[1], args[2], args[3], args[4])
    elif cmd == "delete-bug-comment":
        if len(args) < 4:
            print("Usage: specs-cli.py delete-bug-comment <project-id> <bug-number> <comment-id>", file=sys.stderr)
            sys.exit(1)
        delete_bug_comment(args[1], args[2], args[3])
    elif cmd == "bug":
        # Parse --attach flags
        images = []
        filtered = []
        tags_val = None
        i = 1
        while i < len(args):
            if args[i] == "--attach" and i + 1 < len(args):
                images.append(args[i + 1])
                i += 2
            elif args[i] == "--tags" and i + 1 < len(args):
                tags_val = args[i + 1]
                i += 2
            else:
                filtered.append(args[i])
                i += 1
        if len(filtered) < 3:
            print("Usage: specs-cli.py bug <project-id> <title> <description> [severity] [--attach file ...] [--tags a,b]", file=sys.stderr)
            sys.exit(1)
        sev = filtered[3] if len(filtered) > 3 else "medium"
        tag_list = [t for t in (v.strip() for v in (tags_val or "").split(",")) if t] or None
        create_bug(filtered[0], filtered[1], filtered[2], sev, images or None, tags=tag_list)
    elif cmd == "view-backlog":
        as_json = "--json" in args
        positional = [a for a in args[1:] if a != "--json"]
        if len(positional) < 2:
            print("Usage: specs-cli.py view-backlog <project-id> <item-id-or-#N> [--json]", file=sys.stderr)
            sys.exit(1)
        view_backlog(positional[0], positional[1], as_json=as_json)
    elif cmd == "tags":
        as_json = "--json" in args
        positional = [a for a in args[1:] if not a.startswith("-")]
        if not positional:
            print("Usage: specs-cli.py tags <project-id> [--json]", file=sys.stderr)
            sys.exit(1)
        list_tags(positional[0], as_json=as_json)
    elif cmd == "tag-create":
        VALUE_FLAGS = {"--color", "--description"}
        positional = []
        color_val = None
        desc_val = None
        skip_next = False
        for i, a in enumerate(args[1:], 1):
            if skip_next:
                skip_next = False
                continue
            if a.startswith("--"):
                if a in VALUE_FLAGS:
                    if i + 1 >= len(args):
                        print(f"specs: {a} requires a value", file=sys.stderr)
                        sys.exit(1)
                    if a == "--color":
                        color_val = args[i + 1]
                    else:
                        desc_val = args[i + 1]
                    skip_next = True
                continue
            positional.append(a)
        if len(positional) < 2:
            print("Usage: specs-cli.py tag-create <project-id> <name> [--color C] [--description D] [--force]", file=sys.stderr)
            print(f"  Colours: {', '.join(TAG_COLORS)}", file=sys.stderr)
            sys.exit(1)
        create_tag(positional[0], positional[1], color=color_val, description=desc_val, force="--force" in args)
    elif cmd == "tag-update":
        VALUE_FLAGS = {"--name", "--color", "--description"}
        positional = []
        name_val = None
        color_val = None
        desc_val = None
        skip_next = False
        for i, a in enumerate(args[1:], 1):
            if skip_next:
                skip_next = False
                continue
            if a.startswith("--"):
                if a in VALUE_FLAGS:
                    if i + 1 >= len(args):
                        print(f"specs: {a} requires a value", file=sys.stderr)
                        sys.exit(1)
                    if a == "--name":
                        name_val = args[i + 1]
                    elif a == "--color":
                        color_val = args[i + 1]
                    else:
                        desc_val = args[i + 1]
                    skip_next = True
                continue
            positional.append(a)
        if len(positional) < 2:
            print("Usage: specs-cli.py tag-update <project-id> <tag-slug-or-name> [--name N] [--color C] [--description D] [--force]", file=sys.stderr)
            sys.exit(1)
        update_tag(positional[0], positional[1], name=name_val, color=color_val,
                   description=desc_val, force="--force" in args)
    elif cmd == "tag-delete":
        positional = [a for a in args[1:] if not a.startswith("-")]
        if len(positional) < 2:
            print("Usage: specs-cli.py tag-delete <project-id> <tag-slug-or-name> [--force]", file=sys.stderr)
            sys.exit(1)
        delete_tag(positional[0], positional[1], force="--force" in args)
    elif cmd == "backlog":
        # Spec 013: --epics / --flat / --status / --priority. Spec 022: --assignee.
        #
        # Value-taking flags must be skipped when collecting positionals — the
        # old comprehension treated the *value* of a leading flag as the project
        # id, so `backlog --status idea` (no project) looked for a project called
        # "idea". That bites much harder now that `backlog --assignee <email>`
        # across all projects is a thing people will type.
        VALUE_FLAGS = {"--status", "--priority", "--assignee", "--tag"}
        positional = []
        skip_next = False
        for i, a in enumerate(args[1:], 1):
            if skip_next:
                skip_next = False
                continue
            if a.startswith("--"):
                if a in VALUE_FLAGS:
                    skip_next = True
                continue
            positional.append(a)
        proj = positional[0] if positional else None
        view = "tree"
        if "--epics" in args: view = "epics"
        elif "--flat" in args: view = "flat"
        status_filter = None
        priority_filter = None
        assignee_filter = None
        tag_filters = []
        for i, a in enumerate(args):
            if a == "--status" and i + 1 < len(args): status_filter = args[i + 1]
            if a == "--priority" and i + 1 < len(args): priority_filter = args[i + 1]
            if a == "--assignee" and i + 1 < len(args): assignee_filter = args[i + 1]
            # Spec 027: repeatable, OR-ed.
            if a == "--tag" and i + 1 < len(args): tag_filters.append(args[i + 1])
        if "--unassigned" in args: assignee_filter = "none"
        # Spec 023: derived locally from the returned dates.
        overdue_filter = "--overdue" in args
        late_filter = "--late-to-start" in args
        list_backlog(proj, view=view, status_filter=status_filter, priority_filter=priority_filter,
                     assignee_filter=assignee_filter, overdue=overdue_filter, late_to_start=late_filter,
                     tag_filters=tag_filters, untagged="--untagged" in args, include_all="--all" in args,
                     as_json="--json" in args)
    elif cmd == "backlog-add":
        # Spec 013: --parent <id-or-#N> and --epic
        skip_next = False
        positional = []
        for i, a in enumerate(args[1:], 1):
            if skip_next:
                skip_next = False
                continue
            if a.startswith("--"):
                if a in ("--parent", "--assignee", "--tags") and i + 1 < len(args):
                    skip_next = True
                continue
            positional.append(a)
        if len(positional) < 2:
            print("Usage: specs-cli.py backlog-add <project-id> <title> [description] [priority] [--parent <id-or-#N>] [--epic] [--assignee <email>] [--tags a,b]", file=sys.stderr)
            sys.exit(1)
        desc = positional[2] if len(positional) > 2 else None
        pri = positional[3] if len(positional) > 3 else "medium"
        parent_val = None
        assignee_val = None
        tags_val = None
        for i, a in enumerate(args):
            if a == "--parent" and i + 1 < len(args): parent_val = args[i + 1]
            if a == "--assignee" and i + 1 < len(args): assignee_val = args[i + 1]
            if a == "--tags" and i + 1 < len(args): tags_val = args[i + 1]
        is_epic_flag = "--epic" in args
        tag_list = [t for t in (v.strip() for v in (tags_val or "").split(",")) if t] or None
        create_backlog_item(positional[0], positional[1], desc, pri, parent=parent_val, is_epic=is_epic_flag,
                            assignee=assignee_val, tags=tag_list)
    elif cmd == "backlog-set-parent":
        if len(args) < 4:
            print("Usage: specs-cli.py backlog-set-parent <project-id> <item-id-or-#N> <parent-id-or-#N|none>", file=sys.stderr)
            sys.exit(1)
        set_backlog_parent(args[1], args[2], args[3])
    elif cmd == "backlog-update":
        # Bug #14: edit/delete affordance on the CLI to match the portal.
        # Positional: <project-id> <item-id-or-#N>. Then one or more --title/--description/--priority/--status/--epic flags.
        positional = []
        flag_map = {"--title": "title", "--description": "description", "--priority": "priority", "--status": "status", "--epic": "isEpic", "--assignee": "assignedTo",
                    "--start": "startDate", "--due": "dueDate", "--estimate": "estimateHours", **DEPLOY_FLAGS}
        fields = {}
        tag_edit = {"replace": None, "add": [], "remove": [], "clear": False}
        skip_next = False
        for i, a in enumerate(args[1:], 1):
            if skip_next:
                skip_next = False
                continue
            # --unassign is the valueless twin of --assignee; the API reads an
            # explicit null as "clear", which no flag value could express.
            if a == "--unassign":
                fields["assignedTo"] = None
                continue
            # Spec 023: the same valueless-twin trick for each timing field.
            if a in CLEAR_TIMING_FLAGS:
                fields[CLEAR_TIMING_FLAGS[a]] = None
                continue
            # Spec 033: clear the whole deployment fact — the three fields
            # only mean anything together.
            if a == "--clear-deployment":
                fields["deployedStage"] = None
                fields["deployedUrl"] = None
                fields["deployedAt"] = None
                continue
            # Spec 027: tag flags. --tags replaces the set; --add-tag and
            # --remove-tag are repeatable deltas folded against the item's
            # current tags once it has been resolved.
            if a == "--clear-tags":
                tag_edit["clear"] = True
                continue
            if a in ("--tags", "--add-tag", "--remove-tag"):
                if i + 1 >= len(args):
                    print(f"specs: {a} requires a value", file=sys.stderr)
                    sys.exit(1)
                if a == "--tags":
                    tag_edit["replace"] = args[i + 1]
                elif a == "--add-tag":
                    tag_edit["add"].append(args[i + 1])
                else:
                    tag_edit["remove"].append(args[i + 1])
                skip_next = True
                continue
            if a in flag_map:
                if i + 1 >= len(args):
                    print(f"specs: {a} requires a value", file=sys.stderr)
                    sys.exit(1)
                fields[flag_map[a]] = args[i + 1]
                skip_next = True
                continue
            if a.startswith("--"):
                print(f"specs: unknown flag '{a}' for backlog-update", file=sys.stderr)
                sys.exit(1)
            positional.append(a)
        if len(positional) < 2:
            print("Usage: specs-cli.py backlog-update <project-id> <item-id-or-#N> [--title T] [--description T] [--priority P] [--status S] [--epic true|false] [--assignee EMAIL | --unassign] [--start YYYY-MM-DD] [--due YYYY-MM-DD] [--estimate HOURS] [--clear-start|--clear-due|--clear-estimate] [--tags a,b | --add-tag T | --remove-tag T | --clear-tags] [--deployed-stage S --deployed-url U | --clear-deployment]", file=sys.stderr)
            sys.exit(1)
        if "--assignee" in args and "--unassign" in args:
            print("specs: --assignee and --unassign are mutually exclusive", file=sys.stderr)
            sys.exit(1)
        if "--clear-deployment" in args and ("--deployed-stage" in args or "--deployed-url" in args):
            print("specs: --clear-deployment and --deployed-stage/--deployed-url are mutually exclusive", file=sys.stderr)
            sys.exit(1)
        # Coerce --epic value to a real bool — backend rejects strings here.
        if "isEpic" in fields:
            v = str(fields["isEpic"]).lower()
            if v not in ("true", "false"):
                print(f"specs: --epic must be 'true' or 'false', got '{fields['isEpic']}'", file=sys.stderr)
                sys.exit(1)
            fields["isEpic"] = (v == "true")
        # Guard the status enum client-side (the API also rejects it) so a bad
        # value fails fast with the valid set, instead of a round-trip 400.
        if "status" in fields and fields["status"] not in BACKLOG_STATUSES:
            print(f"specs: --status must be one of {', '.join(BACKLOG_STATUSES)}; got '{fields['status']}'", file=sys.stderr)
            sys.exit(1)
        if tag_edit["replace"] is not None and (tag_edit["add"] or tag_edit["remove"]):
            print("specs: --tags replaces the whole set; combine --add-tag/--remove-tag instead", file=sys.stderr)
            sys.exit(1)
        validate_timing_fields(fields)
        validate_deployment_fields(fields)
        has_tag_edit = tag_edit["clear"] or tag_edit["replace"] is not None or tag_edit["add"] or tag_edit["remove"]
        update_backlog_item(positional[0], positional[1], fields, tag_edit=tag_edit if has_tag_edit else None)
    elif cmd == "backlog-delete":
        if len(args) < 3:
            print("Usage: specs-cli.py backlog-delete <project-id> <item-id-or-#N>", file=sys.stderr)
            sys.exit(1)
        delete_backlog_item(args[1], args[2])
    elif cmd == "backlog-depend":
        if len(args) < 4:
            print("Usage: specs-cli.py backlog-depend <project-id> <item-id-or-#N> <blocker-id-or-#N>", file=sys.stderr)
            sys.exit(1)
        depend_backlog(args[1], args[2], args[3])
    elif cmd == "backlog-undepend":
        if len(args) < 4:
            print("Usage: specs-cli.py backlog-undepend <project-id> <item-id-or-#N> <blocker-id-or-#N>", file=sys.stderr)
            sys.exit(1)
        depend_backlog(args[1], args[2], args[3], remove=True)
    elif cmd == "backlog-comment":
        if len(args) < 4:
            print("Usage: specs-cli.py backlog-comment <project-id> <item-id-or-#N> <body>", file=sys.stderr)
            sys.exit(1)
        add_backlog_comment(args[1], args[2], args[3])
    elif cmd == "backlog-comments":
        as_json = "--json" in args
        positional = [a for a in args[1:] if a != "--json"]
        if len(positional) < 2:
            print("Usage: specs-cli.py backlog-comments <project-id> <item-id-or-#N> [--json]", file=sys.stderr)
            sys.exit(1)
        list_backlog_comments(positional[0], positional[1], as_json=as_json)
    elif cmd == "edit-backlog-comment":
        if len(args) < 5:
            print("Usage: specs-cli.py edit-backlog-comment <project-id> <item-id-or-#N> <comment-id> <body>", file=sys.stderr)
            sys.exit(1)
        edit_backlog_comment(args[1], args[2], args[3], args[4])
    elif cmd == "delete-backlog-comment":
        if len(args) < 4:
            print("Usage: specs-cli.py delete-backlog-comment <project-id> <item-id-or-#N> <comment-id>", file=sys.stderr)
            sys.exit(1)
        delete_backlog_comment(args[1], args[2], args[3])
    elif cmd == "promote-backlog":
        # Spec 023: removed. Fail with directions rather than "unknown command",
        # since this was the documented way to turn an item into a spec.
        print("specs: 'promote-backlog' was removed in spec 023 — there is no hard link", file=sys.stderr)
        print("       between a backlog item and a feature any more. Instead:", file=sys.stderr)
        print("         specs-cli.py create-feature <project> <NNN-name>", file=sys.stderr)
        print("         specs-cli.py create-doc     <project> <NNN-name> spec.md", file=sys.stderr)
        print("         specs-cli.py backlog-comment <project> #N \"Specced as <NNN-name>\"", file=sys.stderr)
        sys.exit(1)
    elif cmd == "restore-backlog":
        if len(args) < 3:
            print("Usage: specs-cli.py restore-backlog <project-id> <item-id-or-uuid>", file=sys.stderr)
            sys.exit(1)
        restore_backlog(args[1], args[2])
    elif cmd == "delete-bug":
        if len(args) < 3:
            print("Usage: specs-cli.py delete-bug <project-id> <bug-id-or-#N>", file=sys.stderr)
            sys.exit(1)
        delete_bug(args[1], args[2])
    elif cmd == "list-attachments":
        as_json = "--json" in args
        positional = [a for a in args[1:] if a != "--json"]
        if len(positional) < 2:
            print("Usage: specs-cli.py list-attachments <feature|bug|backlog> <entity-uuid> [--json]", file=sys.stderr)
            sys.exit(1)
        list_attachments(positional[0], positional[1], as_json=as_json)
    elif cmd == "download-attachment":
        if len(args) < 3:
            print("Usage: specs-cli.py download-attachment <attachment-id> <out-path>", file=sys.stderr)
            sys.exit(1)
        download_attachment(args[1], args[2])
    elif cmd == "delete-attachment":
        if len(args) < 2:
            print("Usage: specs-cli.py delete-attachment <attachment-id>", file=sys.stderr)
            sys.exit(1)
        delete_attachment(args[1])
    elif cmd == "create-feature":
        if len(args) < 3:
            print("Usage: specs-cli.py create-feature <project-id> <name> [--status STATUS] [--description TEXT]", file=sys.stderr)
            sys.exit(1)
        status_val = "specifying"
        description_val = None
        for i, a in enumerate(args):
            if a == "--status" and i + 1 < len(args):
                status_val = args[i + 1]
            elif a == "--description" and i + 1 < len(args):
                description_val = args[i + 1]
        create_feature(args[1], args[2], initial_status=status_val, description=description_val)
    elif cmd == "set-description":
        if len(args) < 3:
            print("Usage: specs-cli.py set-description <feature-id> <text>", file=sys.stderr)
            sys.exit(1)
        set_description(args[1], args[2])
    elif cmd == "set-title":
        if len(args) < 3:
            print("Usage: specs-cli.py set-title <feature-id> <text>", file=sys.stderr)
            sys.exit(1)
        set_title(args[1], args[2])
    elif cmd == "create-doc":
        if len(args) < 4:
            print("Usage: specs-cli.py create-doc <project-id> <feature-name> <filename>", file=sys.stderr)
            sys.exit(1)
        create_document(args[1], args[2], args[3])
    elif cmd == "rename-feature":
        if len(args) < 4:
            print("Usage: specs-cli.py rename-feature <project-id> <old-name> <new-name> [--title TEXT]", file=sys.stderr)
            sys.exit(1)
        title_val = None
        for i, a in enumerate(args):
            if a == "--title" and i + 1 < len(args):
                title_val = args[i + 1]
        rename_feature(args[1], args[2], args[3], title_override=title_val)
    elif cmd == "rename-doc":
        if len(args) < 3:
            print("Usage: specs-cli.py rename-doc <file-path> <new-filename>", file=sys.stderr)
            sys.exit(1)
        rename_document(args[1], args[2])
    elif cmd == "delete-doc":
        if len(args) < 2:
            print("Usage: specs-cli.py delete-doc <file-path>", file=sys.stderr)
            sys.exit(1)
        delete_document(args[1])
    elif cmd == "delete-feature":
        if len(args) < 3:
            print("Usage: specs-cli.py delete-feature <project-id> <feature-name>", file=sys.stderr)
            sys.exit(1)
        delete_feature(args[1], args[2])
    elif cmd == "list-features":
        if len(args) < 2:
            print("Usage: specs-cli.py list-features <project-id>", file=sys.stderr)
            sys.exit(1)
        list_features(args[1])
    elif cmd == "list-docs":
        if len(args) < 3:
            print("Usage: specs-cli.py list-docs <project-id> <feature-name>", file=sys.stderr)
            sys.exit(1)
        list_docs(args[1], args[2])
    elif cmd == "feature-snapshot":
        if len(args) < 3:
            print("Usage: specs-cli.py feature-snapshot <project-id> <feature-name> [--json]", file=sys.stderr)
            sys.exit(1)
        feature_snapshot(args[1], args[2], as_json="--json" in args)
    elif cmd == "comments":
        if len(args) < 2:
            print("Usage: specs-cli.py comments <file-path> [--json]", file=sys.stderr)
            sys.exit(1)
        list_comments(args[1], as_json="--json" in args)
    elif cmd == "comment":
        if len(args) < 3:
            print("Usage: specs-cli.py comment <file-path> <body> [--inline --anchor <text>]", file=sys.stderr)
            sys.exit(1)
        inline = "--inline" in args
        anchor = None
        for i, a in enumerate(args):
            if a == "--anchor" and i + 1 < len(args):
                anchor = args[i + 1]
        add_comment(args[1], args[2], inline=inline, anchor_text=anchor)
    elif cmd == "resolve-comment":
        if len(args) < 2:
            print("Usage: specs-cli.py resolve-comment <comment-id>", file=sys.stderr)
            sys.exit(1)
        resolve_comment(args[1])
    elif cmd == "edit-comment":
        if len(args) < 3:
            print("Usage: specs-cli.py edit-comment <comment-id> <body>", file=sys.stderr)
            sys.exit(1)
        edit_comment(args[1], args[2])
    elif cmd == "delete-comment":
        if len(args) < 2:
            print("Usage: specs-cli.py delete-comment <comment-id>", file=sys.stderr)
            sys.exit(1)
        delete_comment(args[1])
    elif cmd == "reviews":
        if len(args) < 2:
            print("Usage: specs-cli.py reviews <file-path> [--json]", file=sys.stderr)
            sys.exit(1)
        list_reviews(args[1], as_json="--json" in args)
    elif cmd == "review":
        if len(args) < 3:
            print("Usage: specs-cli.py review <file-path> <approved|changes_requested> [body]", file=sys.stderr)
            sys.exit(1)
        review_body = args[3] if len(args) > 3 and not args[3].startswith("-") else None
        submit_review(args[1], args[2], body=review_body)
    elif cmd == "versions":
        if len(args) < 2:
            print("Usage: specs-cli.py versions <file-path> [--json]", file=sys.stderr)
            sys.exit(1)
        list_versions(args[1], as_json="--json" in args)
    elif cmd == "save":
        if len(args) < 3:
            print("Usage: specs-cli.py save <file-path> <summary> [--source <source>]", file=sys.stderr)
            sys.exit(1)
        source = "manual"
        for i, a in enumerate(args):
            if a == "--source" and i + 1 < len(args):
                source = args[i + 1]
        save_version(args[1], args[2], source=source)
    elif cmd == "service-status":
        service_status()
    elif cmd == "post-tool-use":
        handle_post_tool_use()
    elif cmd == "attach":
        # Three forms:
        #   attach <file> [<project-id>/<feature-name>]      — feature (legacy, infers from path)
        #   attach <file> --bug <project-id> <#N>            — attach to a bug
        #   attach <file> --backlog <project-id> <#N>        — attach to a backlog item
        if len(args) < 2:
            print(
                "Usage:\n"
                "  specs-cli.py attach <file-path> [<project-id>/<feature-name>]\n"
                "  specs-cli.py attach <file-path> --bug <project-id> <bug-#N>\n"
                "  specs-cli.py attach <file-path> --backlog <project-id> <backlog-#N>",
                file=sys.stderr,
            )
            sys.exit(1)
        file_path = args[1]
        if "--bug" in args:
            i = args.index("--bug")
            if i + 2 >= len(args):
                print("specs: --bug requires <project-id> <bug-#N>", file=sys.stderr)
                sys.exit(1)
            attach_to_bug(args[i + 1], args[i + 2], file_path)
        elif "--backlog" in args:
            i = args.index("--backlog")
            if i + 2 >= len(args):
                print("specs: --backlog requires <project-id> <backlog-#N>", file=sys.stderr)
                sys.exit(1)
            attach_to_backlog(args[i + 1], args[i + 2], file_path)
        else:
            feature_id = args[2] if len(args) >= 3 else None
            attach_file(file_path, feature_id)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
