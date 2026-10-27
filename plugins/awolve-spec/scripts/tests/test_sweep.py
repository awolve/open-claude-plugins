"""Unit tests for the sweep: spec files edited by Bash or a script get pushed.

Run from the scripts dir:  python3 -m unittest discover -s tests
"""

import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import time
import unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("specs_cli", os.path.join(SCRIPTS_DIR, "specs-cli.py"))
specs_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(specs_cli)


def _hash(body):
    return hashlib.sha256(body.strip().encode("utf-8")).hexdigest()


class SweepTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="sweep-proj-")
        self.cache = tempfile.mkdtemp(prefix="sweep-cache-")
        os.environ["CORTEX_OFFLINE_CACHE"] = self.cache
        self.specs = os.path.join(self.root, "docs", "specs")
        os.makedirs(os.path.join(self.specs, "001-thing"))
        self.cfg = {
            "service_url": "https://example.invalid",
            "projects": [{"id": "demo", "path": self.specs}],
            "project_root": self.root,
        }
        self.pushed = []
        self._push = specs_cli.push
        specs_cli.push = lambda path, base_version_override=None: self.pushed.append(path) or True

    def tearDown(self):
        specs_cli.push = self._push
        os.environ.pop("CORTEX_OFFLINE_CACHE", None)
        shutil.rmtree(self.root, ignore_errors=True)
        shutil.rmtree(self.cache, ignore_errors=True)

    def _doc(self, name, body, synced_body=None, doc_id="d1"):
        path = os.path.join(self.specs, "001-thing", name)
        synced = _hash(synced_body if synced_body is not None else body)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"---\nspec_version: 3\nspec_doc_id: {doc_id}\nlast_synced_hash: {synced}\n---\n\n{body}\n")
        return path

    def _sweep(self):
        err = io.StringIO()
        prev, sys.stderr = sys.stderr, err
        try:
            specs_cli.sweep_changed_specs(self.cfg)
        finally:
            sys.stderr = prev
        return err.getvalue()

    def test_pushes_a_spec_changed_since_last_sync(self):
        path = self._doc("design.md", "# New body", synced_body="# Old body")
        out = self._sweep()
        self.assertEqual(self.pushed, [path])
        self.assertIn("edited outside Write/Edit", out)

    def test_skips_unchanged_spec(self):
        self._doc("design.md", "# Same body")
        self._sweep()
        self.assertEqual(self.pushed, [])

    def test_skips_markdown_without_spec_doc_id(self):
        with open(os.path.join(self.specs, "001-thing", "notes.md"), "w", encoding="utf-8") as f:
            f.write("# scratch\n")
        self._sweep()
        self.assertEqual(self.pushed, [])

    def test_second_sweep_only_sees_newer_edits(self):
        self._doc("design.md", "# New body", synced_body="# Old body")
        self._sweep()
        self.pushed.clear()
        self._sweep()  # nothing touched since the marker
        self.assertEqual(self.pushed, [])

    def test_cold_start_ignores_old_edits(self):
        path = self._doc("plan.md", "# Edited in June", synced_body="# Synced")
        old = time.time() - 3600
        os.utime(path, (old, old))
        self._sweep()
        self.assertEqual(self.pushed, [])

    def test_conflict_copy_twin_is_never_pushed(self):
        self._doc("requirements.md", "# Original", doc_id="same")
        copy = self._doc("requirements-Other Machine.md", "# Forked edit", synced_body="# Original", doc_id="same")
        out = self._sweep()
        self.assertEqual(self.pushed, [])
        self.assertIn("same spec_doc_id", out)
        self.assertIn(os.path.basename(copy), out)

    def test_failed_push_is_reported_not_raised(self):
        specs_cli.push = lambda path, base_version_override=None: False
        self._doc("design.md", "# New", synced_body="# Old")
        out = self._sweep()
        self.assertIn("could not push", out)

    def test_command_gate_uses_configured_paths_only(self):
        self.assertTrue(specs_cli._command_mentions_specs(self.cfg, "sed -i '' s/a/b/ docs/specs/001-thing/design.md"))
        self.assertTrue(specs_cli._command_mentions_specs(self.cfg, f"cat > {self.specs}/001-thing/plan.md <<EOF"))
        self.assertFalse(specs_cli._command_mentions_specs(self.cfg, "python3 specs-cli.py backlog demo"))
        self.assertFalse(specs_cli._command_mentions_specs(self.cfg, "echo hi > /tmp/x"))

    def test_bash_post_tool_use_sweeps_when_command_names_specs(self):
        path = self._doc("design.md", "# New", synced_body="# Old")
        prev_cfg = specs_cli.config.read_config
        specs_cli.config.read_config = lambda: self.cfg
        prev_in = sys.stdin
        sys.stdin = io.StringIO(json.dumps({"tool_name": "Bash", "tool_input": {"command": f"sed -i '' s/Old/New/ {path}"}}))
        err, prev_err = io.StringIO(), sys.stderr
        sys.stderr = err
        try:
            specs_cli.handle_post_tool_use()
        finally:
            sys.stdin, sys.stderr = prev_in, prev_err
            specs_cli.config.read_config = prev_cfg
        self.assertEqual(self.pushed, [path])


if __name__ == "__main__":
    unittest.main()
