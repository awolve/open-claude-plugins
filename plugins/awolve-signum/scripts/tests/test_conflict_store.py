"""Unit tests for conflict_store (feature 016).

Run from the scripts dir:  python3 -m unittest discover -s tests
or:                         python3 tests/test_conflict_store.py
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

# Make the sibling module importable when run directly.
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

import conflict_store  # noqa: E402


class ConflictStoreBase(unittest.TestCase):
    def setUp(self):
        self.cache = tempfile.mkdtemp(prefix="cs-cache-")
        self.tree = tempfile.mkdtemp(prefix="cs-tree-")
        self._prev_env = os.environ.get("CORTEX_OFFLINE_CACHE")
        os.environ["CORTEX_OFFLINE_CACHE"] = self.cache

    def tearDown(self):
        if self._prev_env is None:
            os.environ.pop("CORTEX_OFFLINE_CACHE", None)
        else:
            os.environ["CORTEX_OFFLINE_CACHE"] = self._prev_env
        shutil.rmtree(self.cache, ignore_errors=True)
        shutil.rmtree(self.tree, ignore_errors=True)

    def _make_local_doc(self, rel="016-x/requirements.md", body="local body\n"):
        path = os.path.join(self.tree, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        return path


class TestCachePaths(ConflictStoreBase):
    def test_override_is_honoured(self):
        self.assertTrue(conflict_store.cache_root().startswith(self.cache))
        self.assertTrue(conflict_store.conflicts_dir().startswith(self.cache))

    def test_ensure_writable(self):
        self.assertTrue(conflict_store.ensure_writable())


class TestStaging(ConflictStoreBase):
    def test_stage_writes_only_to_store_not_tree(self):
        local = self._make_local_doc()
        before = _walk_files(self.tree)
        conflict_store.stage(
            "doc-1", "remote body\n",
            local_path=local, project_id="proj", remote_hash="rh", base_hash="bh",
        )
        # Nothing new under the synced tree.
        self.assertEqual(before, _walk_files(self.tree))
        # Store has the staged file + an index entry.
        entry, text = conflict_store.get("doc-1")
        self.assertEqual(text, "remote body\n")
        self.assertEqual(entry["project_id"], "proj")
        self.assertEqual(entry["remote_hash"], "rh")
        self.assertEqual(entry["base_hash"], "bh")
        self.assertEqual(entry["local_path"], os.path.abspath(local))

    def test_clear_removes_file_and_entry(self):
        local = self._make_local_doc()
        conflict_store.stage("doc-1", "r\n", local_path=local,
                             project_id="p", remote_hash="h", base_hash="b")
        conflict_store.clear("doc-1")
        self.assertEqual(conflict_store.get("doc-1"), (None, None))
        self.assertEqual(conflict_store.index_load(), {})
        # Idempotent.
        conflict_store.clear("doc-1")

    def test_staged_ids(self):
        local = self._make_local_doc()
        conflict_store.stage("doc-1", "r\n", local_path=local,
                             project_id="p", remote_hash="h", base_hash="b")
        self.assertEqual(conflict_store.staged_ids(), {"doc-1"})

    def test_find_by_ref_doc_id_and_path(self):
        local = self._make_local_doc()
        conflict_store.stage("doc-1", "r\n", local_path=local,
                             project_id="p", remote_hash="h", base_hash="b")
        self.assertEqual(conflict_store.find_by_ref("doc-1"), "doc-1")
        self.assertEqual(conflict_store.find_by_ref(local), "doc-1")
        self.assertIsNone(conflict_store.find_by_ref("nope"))

    def test_list_prunes_when_local_missing(self):
        local = self._make_local_doc()
        conflict_store.stage("doc-1", "r\n", local_path=local,
                             project_id="p", remote_hash="h", base_hash="b")
        os.unlink(local)  # local doc vanished → stale entry
        self.assertEqual(conflict_store.list_conflicts(), [])
        self.assertEqual(conflict_store.index_load(), {})

    def test_list_project_filter(self):
        a = self._make_local_doc("a/requirements.md")
        b = self._make_local_doc("b/requirements.md")
        conflict_store.stage("da", "r\n", local_path=a, project_id="pa",
                             remote_hash="h", base_hash="b")
        conflict_store.stage("db", "r\n", local_path=b, project_id="pb",
                             remote_hash="h", base_hash="b")
        only = conflict_store.list_conflicts(project_filter="pa")
        self.assertEqual([d for d, _ in only], ["da"])


class TestTrash(ConflictStoreBase):
    def test_trash_lands_in_cache_not_tree(self):
        orphan = self._make_local_doc("old/plan.md")
        target = conflict_store.trash_move("proj", orphan, self.tree)
        self.assertFalse(os.path.exists(orphan))          # moved out
        self.assertTrue(target.startswith(self.cache))     # into the cache
        self.assertIn(os.path.join("trash", "proj"), target)
        # Nothing left under the tree except the now-empty dir structure.
        self.assertEqual(_walk_files(self.tree), [])

    def test_trash_collision_suffix(self):
        o1 = self._make_local_doc("a/plan.md", body="one")
        t1 = conflict_store.trash_move("proj", o1, self.tree)
        o2 = self._make_local_doc("a/plan.md", body="two")
        t2 = conflict_store.trash_move("proj", o2, self.tree)
        self.assertNotEqual(t1, t2)
        self.assertTrue(os.path.exists(t1) and os.path.exists(t2))


class TestClassification(ConflictStoreBase):
    def test_canonical_docs_are_never_matched(self):
        for name in ("requirements.md", "design.md", "plan.md", "spec.md",
                     "tasks.md", "_index.md", "build.py", "diagram.png"):
            self.assertIsNone(conflict_store.classify(name), name)

    def test_hardware_named_docs_are_not_conflict_copies(self):
        # Tokens appear in the *base* name (before any hyphen), not as an
        # OneDrive `-<machine>` suffix → must NOT be matched (would be deleted).
        for name in ("macbook-pricing.md", "mac-mini-setup.md",
                     "imac-teardown-notes.md", "multi-tenant-design.md"):
            self.assertIsNone(conflict_store.classify(name), name)

    def test_canonical_dirs_are_never_matched(self):
        for name in ("016-sync-sidecars-outside-synced-tree", "_gen", "general"):
            self.assertIsNone(conflict_store.classify(name, is_dir=True), name)

    def test_remote_sidecars(self):
        for name in ("plan.md.remote", "requirements.md-Michael's MacBook Air.remote"):
            self.assertEqual(conflict_store.classify(name), "remote_sidecar", name)

    def test_conflict_copies(self):
        for name in (
            "plan-Björn's MacBook Pro.md",
            "requirements-MacBook Pro som tillhör Mattias.md",
            "design (conflict).md",
            "notes-iMac.md",
        ):
            self.assertEqual(conflict_store.classify(name), "conflict_copy", name)

    def test_artifact_dirs(self):
        self.assertEqual(conflict_store.classify(".venv", is_dir=True), "artifact_dir")
        self.assertEqual(conflict_store.classify(".specs-trash", is_dir=True), "artifact_dir")
        # A .venv as a *file* name is not a dir artifact.
        self.assertIsNone(conflict_store.classify(".venv", is_dir=False))


def _walk_files(root):
    out = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            out.append(os.path.relpath(os.path.join(dirpath, f), root))
    return sorted(out)


if __name__ == "__main__":
    unittest.main()
