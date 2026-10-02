"""Unit tests for real epics (Signum spec 049) and the fallback for services
from before them.

Run from the scripts dir:  python3 -m unittest discover -s tests
"""

import contextlib
import importlib.util
import io
import json
import os
import unittest
from unittest import mock

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("specs_cli", os.path.join(SCRIPTS_DIR, "specs-cli.py"))
specs_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(specs_cli)

SERVICE_URL = "https://specs.example.com"
CFG = {"service_url": SERVICE_URL, "projects": [{"id": "proj", "path": "./specs"}]}
HTML_404 = (404, "<!DOCTYPE html><html><body>404</body></html>")

EPICS = [
    {"id": "e1", "number": 1, "title": "Ground work", "status": "in_progress", "featureCount": 1, "itemCount": 3},
    {"id": "e2", "number": 2, "title": "Workspace", "status": "idea", "featureCount": 0, "itemCount": 0},
]

ITEMS = [
    {"id": "i141", "number": 141, "title": "Invite by email", "status": "in_progress", "priority": "medium",
     "projectId": "proj", "featureId": "proj/012-onboarding", "featureNumber": 12, "featureTitle": "Onboarding",
     "epicId": None, "effectiveEpicId": "e1", "effectiveEpicNumber": 1, "childStatusCounts": {"idea": 1}},
    {"id": "i143", "number": 143, "title": "Resend invite", "status": "idea", "priority": "low", "projectId": "proj",
     "parentId": "i141", "featureId": "proj/012-onboarding", "featureNumber": 12, "epicId": None,
     "effectiveEpicId": "e1", "effectiveEpicNumber": 1},
    {"id": "i96", "number": 96, "title": "Retention period", "status": "blocked", "priority": "high",
     "projectId": "proj", "epicId": "e1", "effectiveEpicId": "e1", "effectiveEpicNumber": 1},
    {"id": "i147", "number": 147, "title": "Future scope", "status": "idea", "priority": "medium",
     "projectId": "proj", "isEpic": True, "epicId": None, "effectiveEpicId": None,
     "childStatusCounts": {"idea": 23}},
]


def _router(routes):
    """api_request stand-in answering by (method, url suffix)."""
    calls = []

    def fake(url, method="GET", headers=None, data=None):
        calls.append((method, url, data))
        for (m, suffix), answer in routes.items():
            if m == method and url.endswith(suffix):
                return answer
        raise AssertionError(f"unexpected request {method} {url}")
    return fake, calls


@contextlib.contextmanager
def _env(routes):
    fake, calls = _router(routes)
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.object(specs_cli.config, "read_config", return_value=CFG), \
         mock.patch.object(specs_cli.auth, "get_headers", return_value={"Authorization": "Bearer x"}), \
         mock.patch.object(specs_cli, "api_request", side_effect=fake), \
         contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        yield out, err, calls


class BacklogTreeTest(unittest.TestCase):
    def test_groups_by_epic_then_feature(self):
        routes = {("GET", "/projects/proj/backlog"): (200, json.dumps(ITEMS)),
                  ("GET", "/projects/proj/epics"): (200, json.dumps(EPICS))}
        with _env(routes) as (out, _err, _calls):
            specs_cli.list_backlog("proj")
        text = out.getvalue()
        lines = text.splitlines()
        e1 = next(i for i, l in enumerate(lines) if "E1 Ground work" in l)
        e2 = next(i for i, l in enumerate(lines) if "E2 Workspace" in l)
        no_epic = next(i for i, l in enumerate(lines) if l.strip() == "no epic")
        feature = next(i for i, l in enumerate(lines) if "012 Onboarding  feature" in l)
        self.assertLess(e1, feature)
        self.assertLess(feature, e2)
        self.assertLess(e2, no_epic)
        self.assertIn("[in_progress]", lines[e1])
        self.assertIn("2 items", lines[feature])  # the item and its sub-item
        # The old-style epic is a plain item with sub-items, after "no epic".
        self.assertNotIn("[EPIC]", text)
        row = next(i for i, l in enumerate(lines) if "#147 Future scope" in l)
        self.assertGreater(row, no_epic)
        self.assertIn("(23 sub-items: 23 idea)", lines[row])
        # The sub-item is indented under its parent.
        parent = next(l for l in lines if "#141 Invite by email" in l)
        sub = next(l for l in lines if "#143 Resend invite" in l)
        self.assertGreater(len(sub) - len(sub.lstrip()), len(parent) - len(parent.lstrip()))

    def test_falls_back_to_parent_grouping_without_epic_api(self):
        old = [{"id": "a", "number": 4, "title": "Onboarding", "status": "idea", "priority": "high", "isEpic": True,
                "childStatusCounts": {"idea": 1}},
               {"id": "b", "number": 5, "title": "Child", "status": "idea", "priority": "low", "parentId": "a"}]
        routes = {("GET", "/projects/proj/backlog"): (200, json.dumps(old)),
                  ("GET", "/projects/proj/epics"): HTML_404}
        with _env(routes) as (out, err, _calls):
            specs_cli.list_backlog("proj")
        self.assertIn("[EPIC] Onboarding", out.getvalue())
        self.assertIn("children: 1 idea", out.getvalue())
        self.assertEqual(err.getvalue(), "")


class EpicsCommandTest(unittest.TestCase):
    def test_lists_epics(self):
        with _env({("GET", "/projects/proj/epics"): (200, json.dumps(EPICS))}) as (out, _err, _calls):
            specs_cli.list_epics("proj")
        self.assertIn("E1 Ground work", out.getvalue())
        self.assertIn("in_progress · 1 feature · 3 items", out.getvalue())

    def test_fallback_lists_old_style_epics(self):
        routes = {("GET", "/projects/proj/epics"): HTML_404,
                  ("GET", "/projects/proj/backlog"): (200, json.dumps(ITEMS))}
        with _env(routes) as (out, err, _calls):
            specs_cli.list_epics("proj")
        self.assertIn("no real epics yet", err.getvalue())
        self.assertIn("#147", out.getvalue())
        self.assertNotIn("#96", out.getvalue())

    def test_create_on_old_service_says_so(self):
        with _env({("POST", "/projects/proj/epics"): HTML_404}) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.create_epic("proj", "Reporting")
        self.assertIn("no real epics yet", err.getvalue())


class EpicSetTest(unittest.TestCase):
    def _routes(self, patch_answer):
        return {("GET", "/projects/proj/epics"): (200, json.dumps(EPICS)),
                ("GET", "/projects/proj/backlog"): (200, json.dumps(ITEMS)),
                ("PATCH", "/backlog/i141"): patch_answer}

    def test_item_under_feature_is_refused_with_the_way_out(self):
        answer = (400, json.dumps({"error": "epic_inherited_from_feature", "detail": "proj/012-onboarding"}))
        with _env(self._routes(answer)) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.set_epic("proj", "#141", "E2")
        self.assertIn("#141 delivers feature 012, which is under E1", err.getvalue())
        self.assertIn("--clear-feature", err.getvalue())

    def test_sets_direct_epic(self):
        answer = (200, json.dumps({"id": "i141", "epicId": "e2"}))
        with _env(self._routes(answer)) as (out, _err, calls):
            specs_cli.set_epic("proj", "#141", "E2")
        self.assertEqual(calls[-1][2], {"epicId": "e2"})
        self.assertIn("#141 is now under E2 Workspace", out.getvalue())

    def test_feature_by_number(self):
        features = {"features": [{"id": "proj/012-onboarding", "name": "012-onboarding", "number": 12}], "viewer": {}}
        routes = {("GET", "/projects/proj/epics"): (200, json.dumps(EPICS)),
                  ("GET", "/projects/proj/backlog"): (200, json.dumps(ITEMS)),
                  ("GET", "/projects/proj/features"): (200, json.dumps(features)),
                  ("PATCH", "/api/features/proj%2F012-onboarding"): (200, json.dumps({"id": "proj/012-onboarding", "epicId": "e2"}))}
        with _env(routes) as (out, _err, _calls):
            specs_cli.set_epic("proj", "012", "E2")
        self.assertIn("Feature 012 is now under E2 Workspace. 2 open items follow it.", out.getvalue())

    def test_old_service(self):
        routes = {("GET", "/projects/proj/epics"): HTML_404}
        with _env(routes) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.set_epic("proj", "#141", "E2")
        self.assertIn("no real epics yet", err.getvalue())


class CliFlagTest(unittest.TestCase):
    def _main(self, argv):
        err = io.StringIO()
        with mock.patch.object(specs_cli.sys, "argv", ["specs-cli.py", *argv]), \
             mock.patch.object(specs_cli, "create_backlog_item") as create, \
             mock.patch.object(specs_cli, "update_backlog_item") as update, \
             contextlib.redirect_stderr(err):
            try:
                specs_cli.main()
                code = 0
            except SystemExit as e:
                code = e.code
        return code, err.getvalue(), create, update

    def test_old_boolean_epic_flag_is_refused(self):
        code, err, create, _ = self._main(["backlog-add", "proj", "Onboarding", "--epic"])
        self.assertEqual(code, 1)
        self.assertIn("epic-create", err)
        create.assert_not_called()

    def test_old_flag_before_title_is_refused(self):
        code, err, create, _ = self._main(["backlog-add", "proj", "--epic", "Onboarding"])
        self.assertEqual(code, 1)
        create.assert_not_called()

    def test_epic_number_files_the_item(self):
        code, _err, create, _ = self._main(["backlog-add", "proj", "Onboarding", "--epic", "E3"])
        self.assertEqual(code, 0)
        self.assertEqual(create.call_args.kwargs["epic"], "E3")
        self.assertEqual(create.call_args.args[:2], ("proj", "Onboarding"))

    def test_backlog_update_epic_flag_is_gone(self):
        code, err, _, update = self._main(["backlog-update", "proj", "14", "--epic", "true"])
        self.assertEqual(code, 1)
        self.assertIn("epic-set", err)
        update.assert_not_called()


class PromoteTest(unittest.TestCase):
    def test_dry_run_changes_nothing(self):
        plan = {"dryRun": True, "plan": {"epic": {"title": "Future scope", "status": "idea"},
                                         "subItems": [{"id": "s1", "number": 150, "directEpic": True}],
                                         "features": []}}
        routes = {("GET", "/projects/proj/backlog"): (200, json.dumps(ITEMS)),
                  ("POST", "/backlog/i147/promote"): (200, json.dumps(plan)),
                  ("GET", "/projects/proj/epics"): (200, json.dumps(EPICS))}
        with _env(routes) as (out, _err, calls):
            specs_cli.promote_epic("proj", "#147")
        posts = [c for c in calls if c[0] == "POST"]
        self.assertEqual(posts, [("POST", f"{SERVICE_URL}/api/portal/backlog/i147/promote", {"dryRun": True})])
        self.assertIn("Run again with --yes", out.getvalue())


if __name__ == "__main__":
    unittest.main()
