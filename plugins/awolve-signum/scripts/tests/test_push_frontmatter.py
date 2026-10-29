"""Unit tests: push writes the frontmatter pull would write, so pull leaves the file alone.

Run from the scripts dir:  python3 -m unittest discover -s tests
"""

import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("specs_cli", os.path.join(SCRIPTS_DIR, "specs-cli.py"))
specs_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(specs_cli)

BODY = "# Design\n\nNew text."


def _hash(body):
    return hashlib.sha256(body.strip().encode("utf-8")).hexdigest()


class PushFrontmatterTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="push-proj-")
        self.cache = tempfile.mkdtemp(prefix="push-cache-")
        os.environ["CORTEX_OFFLINE_CACHE"] = self.cache
        self.specs = os.path.join(self.root, "specs")
        os.makedirs(os.path.join(self.specs, "001-thing"))
        self.path = os.path.join(self.specs, "001-thing", "design.md")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(f"---\nspec_doc_id: d1\nspec_version: 1\n---\n\n{BODY}\n")
        self.cfg = {
            "service_url": "https://example.invalid",
            "projects": [{"id": "demo", "path": self.specs}],
            "project_root": self.root,
        }
        self.manifest_status = 200
        self.writes = []
        self._saved = (specs_cli.config.read_config, specs_cli.config.find_project_for_file,
                       specs_cli.auth.get_headers, specs_cli.api_request, specs_cli.atomic_write)
        specs_cli.config.read_config = lambda: self.cfg
        specs_cli.config.find_project_for_file = lambda cfg, p: cfg["projects"][0]
        specs_cli.auth.get_headers = lambda: {"Authorization": "Bearer x"}
        specs_cli.api_request = self._api
        real_write = self._saved[4]
        specs_cli.atomic_write = lambda p, c: self.writes.append(p) or real_write(p, c)

    def tearDown(self):
        (specs_cli.config.read_config, specs_cli.config.find_project_for_file,
         specs_cli.auth.get_headers, specs_cli.api_request, specs_cli.atomic_write) = self._saved
        os.environ.pop("CORTEX_OFFLINE_CACHE", None)
        shutil.rmtree(self.root, ignore_errors=True)
        shutil.rmtree(self.cache, ignore_errors=True)

    def _api(self, url, method="GET", headers=None, data=None):
        if method == "PUT":
            return 201, json.dumps({"documentId": "d1", "version": 2})
        if url.endswith("/manifest"):
            if self.manifest_status != 200:
                return self.manifest_status, ""
            return 200, json.dumps({"documents": [{
                "id": "d1", "feature": "001-thing", "filename": "design.md",
                "feature_status": "specifying", "doc_status": "specifying",
                "version": 2, "content_hash": _hash(BODY),
                "source_url": "/portal/demo/specs/001-thing",
            }], "attachments": []})
        return 404, ""

    def _meta(self):
        with open(self.path, encoding="utf-8") as f:
            return specs_cli.parse_frontmatter(f.read())[0]

    def test_push_writes_status_fields_from_manifest(self):
        self.assertTrue(specs_cli.push(self.path))
        meta = self._meta()
        self.assertEqual(meta["spec_version"], 2)
        self.assertEqual(meta["feature_status"], "specifying")
        self.assertEqual(meta["doc_status"], "specifying")
        self.assertEqual(meta["source"], "/portal/demo/specs/001-thing")

    def test_pull_after_push_does_not_rewrite_the_file(self):
        specs_cli.push(self.path)
        self.writes.clear()
        specs_cli.pull_project("demo", self.specs, self.cfg["service_url"], {"Authorization": "Bearer x"}, quiet=True)
        self.assertEqual(self.writes, [])

    def test_unreadable_manifest_still_pushes(self):
        self.manifest_status = 500
        self.assertTrue(specs_cli.push(self.path))
        meta = self._meta()
        self.assertEqual(meta["spec_version"], 2)
        self.assertNotIn("doc_status", meta)


if __name__ == "__main__":
    unittest.main()
