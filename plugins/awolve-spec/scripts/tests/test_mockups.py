"""Unit tests: mockups (`mockups/<name>.html`) sync like markdown docs, with
the header inside an HTML comment (spec 062). Markdown keeps its old form.

Run from the scripts dir:  python3 -m unittest discover -s tests
"""

import hashlib
import io
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("specs_cli", os.path.join(SCRIPTS_DIR, "specs-cli.py"))
specs_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(specs_cli)

MD_BODY = "# Design\n\nNew text."
HTML_BODY = "<!doctype html>\n<html><body><a href=\"dashboard.html\">Sign in</a></body></html>"


def _hash(body):
    return hashlib.sha256(body.strip().encode("utf-8")).hexdigest()


class HeaderFormTest(unittest.TestCase):
    META = {"spec_doc_id": "d1", "spec_version": 3}

    def test_markdown_render_is_unchanged(self):
        out = specs_cli.render_frontmatter(self.META, MD_BODY, "x/design.md")
        self.assertEqual(out, f"---\nspec_doc_id: d1\nspec_version: 3\n---\n\n{MD_BODY}")
        # No path keeps the markdown form too (old callers).
        self.assertEqual(out, specs_cli.render_frontmatter(self.META, MD_BODY))

    def test_html_render_puts_header_in_comment(self):
        out = specs_cli.render_frontmatter(self.META, HTML_BODY, "x/mockups/login.html")
        self.assertEqual(out, f"<!--\n---\nspec_doc_id: d1\nspec_version: 3\n---\n-->\n{HTML_BODY}")

    def test_round_trip_both_forms(self):
        for path, body in (("design.md", MD_BODY), ("mockups/login.html", HTML_BODY)):
            text = specs_cli.render_frontmatter(self.META, body, path)
            meta, got = specs_cli.parse_frontmatter(text)
            self.assertEqual(meta, self.META, path)
            self.assertEqual(got.strip(), body, path)
            self.assertEqual(specs_cli.file_content_hash(text), _hash(body), path)

    def test_html_header_tolerates_crlf_and_bom(self):
        text = "﻿<!--\r\n---\r\nspec_doc_id: d1\r\n---\r\n-->\r\n<p>x</p>"
        meta, body = specs_cli.parse_frontmatter(text)
        self.assertEqual(meta, {"spec_doc_id": "d1"})
        self.assertEqual(body, "<p>x</p>")

    def test_ordinary_html_comment_is_not_a_header(self):
        text = "<!-- just a note -->\n<p>x</p>"
        self.assertEqual(specs_cli.parse_frontmatter(text), ({}, text))

    def test_strip_removes_leaked_headers_of_either_form(self):
        leaked = "<!--\n---\nspec_doc_id: d1\n---\n-->\n---\nspec_doc_id: d1\n---\n<p>x</p>"
        self.assertEqual(specs_cli.strip_frontmatter(leaked), "<p>x</p>")
        self.assertEqual(specs_cli.strip_frontmatter(f"---\na: 1\n---\n{MD_BODY}"), MD_BODY)

    def test_spec_file_filter(self):
        self.assertTrue(specs_cli.is_spec_file("/s/001-x/design.md"))
        self.assertTrue(specs_cli.is_spec_file("/s/001-x/mockups/login.html"))
        self.assertFalse(specs_cli.is_spec_file("/s/001-x/login.html"))
        self.assertFalse(specs_cli.is_spec_file("/s/001-x/mockups/.tmp-login.html"))
        self.assertFalse(specs_cli.is_spec_file("/s/001-x/mockups/notes.txt"))


class SyncRoundTripTest(unittest.TestCase):
    """push and pull, against a fake service, for one .md and one mockup."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="mockup-proj-")
        self.cache = tempfile.mkdtemp(prefix="mockup-cache-")
        os.environ["CORTEX_OFFLINE_CACHE"] = self.cache
        self.specs = os.path.join(self.root, "specs")
        self.feature = os.path.join(self.specs, "001-thing")
        os.makedirs(self.feature)
        self.cfg = {
            "service_url": "https://example.invalid",
            "projects": [{"id": "demo", "path": self.specs}],
            "project_root": self.root,
        }
        self.server = {  # doc_id -> (filename, body, version)
            "d1": ("design.md", MD_BODY, 2),
            "m1": ("mockups/login.html", HTML_BODY, 2),
        }
        self.puts = []
        self._saved = (specs_cli.config.read_config, specs_cli.config.find_project_for_file,
                       specs_cli.auth.get_headers, specs_cli.api_request)
        specs_cli.config.read_config = lambda: self.cfg
        specs_cli.config.find_project_for_file = lambda cfg, p: cfg["projects"][0]
        specs_cli.auth.get_headers = lambda: {"Authorization": "Bearer x"}
        specs_cli.api_request = self._api

    def tearDown(self):
        (specs_cli.config.read_config, specs_cli.config.find_project_for_file,
         specs_cli.auth.get_headers, specs_cli.api_request) = self._saved
        os.environ.pop("CORTEX_OFFLINE_CACHE", None)
        shutil.rmtree(self.root, ignore_errors=True)
        shutil.rmtree(self.cache, ignore_errors=True)

    def _api(self, url, method="GET", headers=None, data=None):
        if method == "PUT":
            doc_id = url.split("/documents/")[1].split("/")[0]
            self.puts.append((doc_id, headers.get("Content-Type"), data))
            fn, _, v = self.server[doc_id]
            self.server[doc_id] = (fn, data, v + 1)
            return 201, json.dumps({"documentId": doc_id, "version": v + 1})
        if "/manifest" in url:
            return 200, json.dumps({"documents": [{
                "id": doc_id, "feature": "001-thing", "filename": fn,
                "feature_status": "specifying", "doc_status": "specifying",
                "version": v, "content_hash": _hash(body),
                "source_url": "/portal/demo/specs/001-thing",
            } for doc_id, (fn, body, v) in self.server.items()], "attachments": []})
        if url.endswith("/content"):
            doc_id = url.split("/documents/")[1].split("/")[0]
            return 200, self.server[doc_id][1]
        return 404, ""

    def _pull(self):
        return specs_cli.pull_project("demo", self.specs, self.cfg["service_url"],
                                      {"Authorization": "Bearer x"}, force_full=True, quiet=True)

    def _read(self, rel):
        with open(os.path.join(self.feature, rel), encoding="utf-8") as f:
            return f.read()

    def test_pull_writes_both_forms_and_creates_mockups_folder(self):
        self._pull()
        md = self._read("design.md")
        html = self._read("mockups/login.html")
        self.assertTrue(md.startswith("---\nspec_version: 2\nspec_doc_id: d1\n"))
        self.assertTrue(html.startswith("<!--\n---\nspec_version: 2\nspec_doc_id: m1\n"))
        self.assertIn("---\n-->\n<!doctype html>", html)
        self.assertEqual(specs_cli.parse_frontmatter(html)[1].strip(), HTML_BODY)

    def test_second_pull_changes_nothing(self):
        self._pull()
        before = (self._read("design.md"), self._read("mockups/login.html"))
        report = self._pull()
        self.assertEqual(report["synced"], 0)
        self.assertEqual(before, (self._read("design.md"), self._read("mockups/login.html")))

    def test_push_keeps_header_out_of_content(self):
        self._pull()
        for rel, old, new in (("design.md", "New text.", "Changed text."),
                              ("mockups/login.html", "Sign in", "Log in")):
            path = os.path.join(self.feature, rel)
            text = self._read(rel).replace(old, new)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.assertTrue(specs_cli.push(path))
        (d_id, d_type, d_body), (m_id, m_type, m_body) = self.puts
        self.assertEqual((d_id, m_id), ("d1", "m1"))
        self.assertEqual(d_body, MD_BODY.replace("New text.", "Changed text."))
        self.assertEqual(m_body, HTML_BODY.replace("Sign in", "Log in"))
        self.assertNotIn("spec_doc_id", m_body)
        self.assertNotIn("<!--", m_body)
        self.assertTrue(d_type.startswith("text/markdown"))
        self.assertTrue(m_type.startswith("text/html"))
        # Local header advanced, still in its own form.
        html = self._read("mockups/login.html")
        self.assertTrue(html.startswith("<!--\n---\n"))
        self.assertEqual(specs_cli.parse_frontmatter(html)[0]["spec_version"], 3)
        md = self._read("design.md")
        self.assertTrue(md.startswith("---\n"))
        self.assertEqual(specs_cli.parse_frontmatter(md)[0]["spec_version"], 3)

    def test_scan_indexes_mockups(self):
        self._pull()
        index = specs_cli._scan_local_specs(self.specs)
        self.assertEqual(set(index), {"d1", "m1"})


class PostToolUseHookTest(unittest.TestCase):
    """A Write/Edit on a mockup is pushed; HTML elsewhere in the tree is not."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="mockup-hook-")
        self.specs = os.path.join(self.root, "specs")
        os.makedirs(os.path.join(self.specs, "001-thing", "mockups"))
        self.cfg = {
            "service_url": "https://example.invalid",
            "projects": [{"id": "demo", "path": self.specs}],
            "project_root": self.root,
        }
        self.pushed = []
        self._saved = (specs_cli.config.read_config, specs_cli.push)
        specs_cli.config.read_config = lambda: self.cfg
        specs_cli.push = lambda path, base_version_override=None: self.pushed.append(path) or True

    def tearDown(self):
        (specs_cli.config.read_config, specs_cli.push) = self._saved
        shutil.rmtree(self.root, ignore_errors=True)

    def _write(self, rel, path_meta):
        path = os.path.join(self.specs, "001-thing", rel)
        with open(path, "w", encoding="utf-8") as f:
            f.write(specs_cli.render_frontmatter({"spec_doc_id": "x", "spec_version": 1}, HTML_BODY, path_meta))
        return path

    def _hook(self, path, tool="Write"):
        prev = sys.stdin
        sys.stdin = io.StringIO(json.dumps({"tool_name": tool, "tool_input": {"file_path": path}}))
        try:
            specs_cli.handle_post_tool_use()
        finally:
            sys.stdin = prev

    def test_mockup_edit_is_pushed(self):
        path = self._write("mockups/login.html", "mockups/login.html")
        self._hook(path, "Edit")
        self.assertEqual(self.pushed, [path])

    def test_markdown_edit_is_pushed(self):
        path = os.path.join(self.specs, "001-thing", "design.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(specs_cli.render_frontmatter({"spec_doc_id": "d", "spec_version": 1}, MD_BODY, path))
        self._hook(path)
        self.assertEqual(self.pushed, [path])

    def test_html_outside_mockups_is_ignored(self):
        path = self._write("login.html", "mockups/login.html")
        self._hook(path)
        self.assertEqual(self.pushed, [])

    def test_sweep_finds_changed_mockup(self):
        mockup = self._write("mockups/login.html", "mockups/login.html")
        self._write("login.html", "mockups/login.html")  # not a mockup
        self.assertEqual(specs_cli._changed_spec_files(self.cfg, 0), [mockup])


class CreateDocTest(unittest.TestCase):
    """create-doc registers `mockups/<name>.html` and refuses bad mockup names."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="mockup-create-")
        self.specs = os.path.join(self.root, "specs")
        self.feature = os.path.join(self.specs, "001-thing")
        os.makedirs(self.feature)
        self.cfg = {
            "service_url": "https://example.invalid",
            "projects": [{"id": "demo", "path": self.specs}],
            "project_root": self.root,
        }
        self.posts = []
        self._saved = (specs_cli.config.read_config, specs_cli.auth.get_headers, specs_cli.api_request)
        specs_cli.config.read_config = lambda: self.cfg
        specs_cli.auth.get_headers = lambda: {"Authorization": "Bearer x"}
        specs_cli.api_request = self._api

    def tearDown(self):
        (specs_cli.config.read_config, specs_cli.auth.get_headers, specs_cli.api_request) = self._saved
        shutil.rmtree(self.root, ignore_errors=True)

    def _api(self, url, method="GET", headers=None, data=None):
        if method == "POST" and "/documents" in url:
            self.posts.append(data)
            return 201, json.dumps({"id": f"doc{len(self.posts)}"})
        return 404, ""

    def test_mockup_is_registered_with_full_name(self):
        specs_cli.create_document("demo", "001-thing", "mockups/login.html")
        self.assertEqual(self.posts[0]["filename"], "mockups/login.html")
        self.assertIn('<meta name="signum:design-width" content="1280">', self.posts[0]["content"])
        self.assertNotIn("spec_doc_id", self.posts[0]["content"])
        with open(os.path.join(self.feature, "mockups", "login.html"), encoding="utf-8") as f:
            text = f.read()
        self.assertTrue(text.startswith("<!--\n---\nspec_doc_id: doc1\nspec_version: 1\n---\n-->\n"))

    def test_existing_mockup_keeps_its_html(self):
        os.makedirs(os.path.join(self.feature, "mockups"))
        path = os.path.join(self.feature, "mockups", "dashboard.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(HTML_BODY)
        specs_cli.create_document("demo", "001-thing", "mockups/dashboard")
        self.assertEqual(self.posts[0], {"filename": "mockups/dashboard.html", "content": HTML_BODY})
        with open(path, encoding="utf-8") as f:
            meta, body = specs_cli.parse_frontmatter(f.read())
        self.assertEqual(meta["spec_doc_id"], "doc1")
        self.assertEqual(body, HTML_BODY)

    def test_bad_mockup_names_are_refused(self):
        for bad in ("mockups/Login.html", "mockups/a/b.html", "login.html", "mockups/-x.html"):
            with self.assertRaises(SystemExit, msg=bad):
                specs_cli.create_document("demo", "001-thing", bad)
        self.assertEqual(self.posts, [])

    def test_markdown_create_is_unchanged(self):
        specs_cli.create_document("demo", "001-thing", "notes")
        self.assertEqual(self.posts[0], {"filename": "notes.md", "content": "# Notes"})
        with open(os.path.join(self.feature, "notes.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "---\nspec_doc_id: doc1\nspec_version: 1\n---\n\n# Notes\n")


if __name__ == "__main__":
    unittest.main()
