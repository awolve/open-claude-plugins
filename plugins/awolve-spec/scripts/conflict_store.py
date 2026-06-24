"""Out-of-tree staging for spec-sync conflicts, trash, and artifact cleanup.

Feature 016 (spec-service: sync-sidecars-outside-synced-tree).

The awolve-spec sync client used to write its conflict `.remote` sidecars and
`.specs-trash/` directory *inside* the OneDrive-synced specs tree. That tree
is a SharePoint library synced across many machines, so every sidecar became
fork-bait: OneDrive conflict-copied it with machine suffixes and peers
re-uploaded after deletes, producing hundreds of junk files and wedging sync.

This module relocates all per-machine sync bookkeeping into the per-machine
cache Cortex already mandates for calendar/task/session state
(`~/Library/Caches/com.awolve.cortex/`, override `CORTEX_OFFLINE_CACHE`), so
the only files OneDrive ever sees in the specs tree are canonical spec docs.

It is intentionally self-contained (stdlib only, no import of `specs-cli.py`,
which can't be imported anyway because of its hyphenated name) so its logic is
unit-testable. The spec service stays the source of truth: anything staged
here is re-derivable via `pull`, so losing the cache is always safe.

Layout under the cache root:

    <cache>/specs/
      conflicts/
        index.json              doc_id -> { local_path, project_id, ... }
        <doc_id>.remote         remote content + frontmatter (the old sidecar)
      trash/
        <project_id>/YYYY-MM-DD/...   relocated .specs-trash
"""

import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Cache paths
# ---------------------------------------------------------------------------

DEFAULT_CACHE_ROOT = "~/Library/Caches/com.awolve.cortex"


def cache_root():
    """Resolve the per-machine cache root (honours $CORTEX_OFFLINE_CACHE)."""
    override = os.environ.get("CORTEX_OFFLINE_CACHE")
    base = override if override else DEFAULT_CACHE_ROOT
    return os.path.expanduser(base)


def specs_cache_dir():
    return os.path.join(cache_root(), "specs")


def conflicts_dir():
    return os.path.join(specs_cache_dir(), "conflicts")


def trash_root(project_id):
    return os.path.join(specs_cache_dir(), "trash", project_id)


def _index_path():
    return os.path.join(conflicts_dir(), "index.json")


def _remote_path(doc_id):
    return os.path.join(conflicts_dir(), f"{doc_id}.remote")


# ---------------------------------------------------------------------------
# Atomic write (self-contained — must not depend on specs-cli.py)
# ---------------------------------------------------------------------------

def _atomic_write(path, text):
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def ensure_writable():
    """True if the conflict store can be created and written.

    The whole point of this module is to never fall back to an in-tree write,
    so callers check this first and skip staging (still reporting the conflict)
    when the cache is unavailable.
    """
    try:
        os.makedirs(conflicts_dir(), exist_ok=True)
        probe = os.path.join(conflicts_dir(), ".write-probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("")
        os.unlink(probe)
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Conflict index
# ---------------------------------------------------------------------------

def index_load():
    """Load the conflict index. Returns {} if missing or corrupt."""
    try:
        with open(_index_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def index_save(index):
    _atomic_write(_index_path(), json.dumps(index, indent=2, sort_keys=True))


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stage(doc_id, remote_text, *, local_path, project_id, remote_hash, base_hash):
    """Write the remote side of a conflict to the store + upsert the index.

    `remote_text` is the fully rendered frontmatter+body the in-tree sidecar
    used to hold. Raises OSError if the cache is unwritable (callers gate on
    ensure_writable() first). Returns the staged `.remote` path.
    """
    _atomic_write(_remote_path(doc_id), remote_text)
    index = index_load()
    index[doc_id] = {
        "local_path": os.path.abspath(local_path),
        "project_id": project_id,
        "remote_hash": remote_hash,
        "base_hash": base_hash,
        "staged_at": _now_iso(),
    }
    index_save(index)
    return _remote_path(doc_id)


def clear(doc_id):
    """Remove a staged conflict (file + index entry). Idempotent."""
    index = index_load()
    if doc_id in index:
        del index[doc_id]
        index_save(index)
    try:
        os.unlink(_remote_path(doc_id))
    except OSError:
        pass


def get(doc_id):
    """Return (entry, remote_text) for a staged conflict, or (None, None)."""
    index = index_load()
    entry = index.get(doc_id)
    if not entry:
        return None, None
    try:
        with open(_remote_path(doc_id), "r", encoding="utf-8") as f:
            return entry, f.read()
    except OSError:
        return entry, None


def staged_ids():
    """Set of doc_ids that currently have a staged conflict (cheap pre-check)."""
    return set(index_load().keys())


def find_by_ref(ref):
    """Resolve a `conflict` command argument to a doc_id.

    Accepts a doc_id directly, or a path to the local doc whose conflict was
    staged. Returns the doc_id or None.
    """
    index = index_load()
    if ref in index:
        return ref
    ref_abs = os.path.abspath(ref)
    for doc_id, entry in index.items():
        if entry.get("local_path") == ref_abs:
            return doc_id
    return None


def list_conflicts(project_filter=None, prune=True):
    """List staged conflicts as [(doc_id, entry), ...].

    When `prune` is set, entries whose staged file or local doc has vanished
    are dropped (lazy cleanup, AC's "pruned when conflicts/resolve touches it").
    """
    index = index_load()
    changed = False
    out = []
    for doc_id in list(index.keys()):
        entry = index[doc_id]
        remote_exists = os.path.isfile(_remote_path(doc_id))
        local_exists = os.path.isfile(entry.get("local_path", ""))
        if prune and (not remote_exists or not local_exists):
            del index[doc_id]
            try:
                os.unlink(_remote_path(doc_id))
            except OSError:
                pass
            changed = True
            continue
        if project_filter and entry.get("project_id") != project_filter:
            continue
        out.append((doc_id, entry))
    if changed:
        index_save(index)
    return out


# ---------------------------------------------------------------------------
# Trash relocation
# ---------------------------------------------------------------------------

def trash_move(project_id, file_path, specs_path=None):
    """Move an orphaned local file into the out-of-tree trash.

    Lands at `<cache>/specs/trash/<project_id>/YYYY-MM-DD/<rel>`. When
    `specs_path` is given the file's path relative to it is preserved (so the
    trash mirrors the spec layout); otherwise just the basename is used.
    Collisions get a numeric suffix so nothing in the trash is overwritten.
    """
    if specs_path:
        rel = os.path.relpath(file_path, specs_path)
    else:
        rel = os.path.basename(file_path)
    today = datetime.now().strftime("%Y-%m-%d")
    dest_dir = os.path.join(trash_root(project_id), today, os.path.dirname(rel))
    os.makedirs(dest_dir, exist_ok=True)
    base = os.path.basename(rel)
    target = os.path.join(dest_dir, base)
    if os.path.exists(target):
        stem, ext = os.path.splitext(base)
        n = 1
        while os.path.exists(os.path.join(dest_dir, f"{stem}-{n}{ext}")):
            n += 1
        target = os.path.join(dest_dir, f"{stem}-{n}{ext}")
    shutil.move(file_path, target)
    return target


# ---------------------------------------------------------------------------
# Artifact classification (cleanup + doctor backstop)
# ---------------------------------------------------------------------------

# OneDrive appends the *full* machine name to conflict copies, so the hyphen
# precedes the owner's name, not "MacBook" — e.g. `plan-Björn's MacBook Pro.md`,
# `requirements-MacBook Pro som tillhör Mattias.md`. Match on the machine-name
# tokens (case-insensitive). Canonical spec names (requirements.md, design.md,
# plan.md, spec.md, tasks.md, _index.md) never contain any of these, which is
# what makes the cleanup canonical-safe.
_MACHINE_TOKENS = ("macbook", "imac", "mac mini", "som tillhör", "som tillhor")

# Build/sync artifact directory names that must never live in a synced library.
_ARTIFACT_DIRS = (".venv", ".specs-trash")


def is_remote_sidecar(name):
    """A `.remote` spec-sync sidecar (any name ending in .remote)."""
    return name.endswith(".remote")


def is_conflict_copy(name):
    """An OneDrive/Dropbox machine-named conflict copy of a doc.

    Deliberately conservative: a "conflict" marker, or a machine-name token that
    appears **after a hyphen** — OneDrive always appends `-<machine name>` to the
    base name, so the token follows a hyphen (`design-Björn's MacBook Pro.md`).
    Requiring the hyphen means a legit doc whose own name contains a token
    (`macbook-pricing.md`, `mac-mini-setup.md`) is NOT matched, and so is never
    deleted by cleanup. Numeric-only suffixes (`phase-2.md`) are also not matched
    — ambiguous with real content, left to report-only review.
    """
    stem = name.rsplit(".", 1)[0] if "." in name else name
    low = stem.lower()
    if "conflict" in low:
        return True
    if "-" not in stem:
        return False
    after_hyphen = low.split("-", 1)[1]
    return any(tok in after_hyphen for tok in _MACHINE_TOKENS)


def is_artifact_dir(name):
    """A build/sync artifact directory (`.venv`, `.specs-trash`)."""
    return name in _ARTIFACT_DIRS


def classify(name, is_dir=False):
    """Classify a basename into an artifact category, or None if canonical.

    Categories: "artifact_dir", "remote_sidecar", "conflict_copy". Returns None
    for anything that should be left untouched (canonical docs, `_gen/*.py`
    scripts, generated outputs).
    """
    if is_dir:
        return "artifact_dir" if is_artifact_dir(name) else None
    if is_remote_sidecar(name):
        return "remote_sidecar"
    if is_conflict_copy(name):
        return "conflict_copy"
    return None
