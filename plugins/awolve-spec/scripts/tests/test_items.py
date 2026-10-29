"""Unit tests for item kinds and shared statuses (at Awolve: Signum spec 050):
the bug commands' by-number lookup with its fallback for older servers, the
`items`, `item` and `item-kind` commands, and the shared status values.

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
API = f"{SERVICE_URL}/api/portal"
# What a server answers for a path it has no route for, and for a record it lacks.
HTML_404 = (404, "<!DOCTYPE html><html><body>404</body></html>")
BUG_404 = (404, json.dumps({"error": "Bug not found"}))

# Bug #1, moved into the single series as item #74: the old shape keeps the
# bug number and adds the item number.
BUG_DETAIL = {"id": "b1", "number": 1, "item_number": 74, "kind": "bug", "title": "Breadcrumb shows slug",
              "status": "ready_for_retest", "state": "ready_for_testing", "severity": "medium",
              "description": "Shows the slug", "createdAt": "2026-03-29", "updatedAt": "2026-03-29"}
BUG_ROW = {"id": "b1", "number": 1, "title": "Breadcrumb shows slug", "status": "ready_for_retest", "severity": "medium"}

ITEM_BUG = {"id": "b1", "kind": "bug", "number": 74, "legacyBugNumber": 1, "title": "Breadcrumb shows slug",
            "state": "ready_for_testing", "label": "Ready for retest", "priority": "medium", "severity": "medium",
            "description": "Shows the slug", "createdAt": "2026-03-29"}
ITEM_IMPL = {"id": "i2", "kind": "implementation", "number": 75, "title": "Item page", "state": "in_progress",
             "label": "In progress", "priority": "high", "description": "One page per kind"}
ITEM_DONE = {"id": "i3", "kind": "activity", "number": 76, "title": "Champion training", "state": "completed",
             "label": "Completed", "priority": "low", "description": "", "outcome": "Done"}


def _router(routes):
    """api_request stand-in answering by (method, url): the url without the
    `/api/portal` prefix, or whole for any other path."""
    calls = []

    def fake(url, method="GET", headers=None, data=None):
        calls.append((method, url, data))
        for key in ((method, url[len(API):]), (method, url)):
            if key in routes:
                return routes[key]
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


class RouteMissingTest(unittest.TestCase):
    def test_html_404_is_a_missing_route(self):
        self.assertTrue(specs_cli._route_missing(*HTML_404))

    def test_json_404_is_a_missing_record(self):
        self.assertFalse(specs_cli._route_missing(*BUG_404))

    def test_other_statuses_are_not(self):
        self.assertFalse(specs_cli._route_missing(200, "<html></html>"))
        self.assertFalse(specs_cli._route_missing(500, "<html></html>"))


class FindBugTest(unittest.TestCase):
    def test_by_number_answers_with_the_full_record(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): (200, json.dumps(BUG_DETAIL))}
        with _env(routes) as (_out, _err, calls):
            status, bug, full = specs_cli._find_bug({}, SERVICE_URL, "proj", 1)
        self.assertEqual((status, bug["id"], full), (200, "b1", True))
        self.assertEqual(len(calls), 1)

    def test_a_missing_bug_does_not_download_the_list(self):
        routes = {("GET", "/projects/proj/bugs/by-number/9"): BUG_404}
        with _env(routes) as (_out, _err, calls):
            status, bug, _ = specs_cli._find_bug({}, SERVICE_URL, "proj", 9)
        self.assertEqual((status, bug), (404, None))
        self.assertEqual(len(calls), 1)

    def test_older_server_falls_back_to_the_list(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): HTML_404,
                  ("GET", "/projects/proj/bugs"): (200, json.dumps([BUG_ROW]))}
        with _env(routes):
            status, bug, full = specs_cli._find_bug({}, SERVICE_URL, "proj", 1)
        self.assertEqual((status, bug["id"], full), (200, "b1", False))

    def test_older_server_bug_missing_from_the_list(self):
        routes = {("GET", "/projects/proj/bugs/by-number/9"): HTML_404,
                  ("GET", "/projects/proj/bugs"): (200, json.dumps([BUG_ROW]))}
        with _env(routes):
            status, bug, _ = specs_cli._find_bug({}, SERVICE_URL, "proj", 9)
        self.assertEqual((status, bug), (404, None))

    def test_other_failures_are_passed_on(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): (403, json.dumps({"error": "No access"}))}
        with _env(routes):
            status, bug, _ = specs_cli._find_bug({}, SERVICE_URL, "proj", 1)
        self.assertEqual((status, bug), (403, None))


class BugCommandsTest(unittest.TestCase):
    def test_view_bug_needs_no_second_fetch_and_shows_the_item_number(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): (200, json.dumps(BUG_DETAIL)),
                  ("GET", "/attachments?entityType=bug&entityId=b1"): (200, "[]")}
        with _env(routes) as (out, _err, calls), \
             mock.patch.object(specs_cli, "_bug_attachments", return_value=[]):
            specs_cli.view_bug("proj", "#1")
        text = out.getvalue()
        self.assertIn("#1 [! medium] Breadcrumb shows slug", text)
        self.assertIn("item:      #74", text)
        self.assertIn("Shows the slug", text)
        self.assertNotIn(("GET", f"{API}/bugs/b1", None), calls)

    def test_view_bug_on_an_older_server_fetches_the_body(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): HTML_404,
                  ("GET", "/projects/proj/bugs"): (200, json.dumps([BUG_ROW])),
                  ("GET", "/bugs/b1"): (200, json.dumps({**BUG_ROW, "description": "Shows the slug"}))}
        with _env(routes) as (out, _err, _calls), \
             mock.patch.object(specs_cli, "_bug_attachments", return_value=[]):
            specs_cli.view_bug("proj", "1")
        self.assertIn("Shows the slug", out.getvalue())
        self.assertNotIn("item:", out.getvalue())

    def test_bug_comment_finds_the_bug_by_number(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): (200, json.dumps(BUG_DETAIL)),
                  ("POST", "/bugs/b1/comments"): (201, json.dumps({"id": "c1"}))}
        with _env(routes) as (_out, _err, calls):
            specs_cli.add_bug_comment("proj", "1", "Fixed in abc123")
        self.assertEqual(calls[-1][:2], ("POST", f"{API}/bugs/b1/comments"))

    def test_missing_bug_says_so(self):
        routes = {("GET", "/projects/proj/bugs/by-number/9"): BUG_404}
        with _env(routes) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.set_bug_status("proj", "9", "resolved")
        self.assertIn("bug #9 not found in 'proj'", err.getvalue())

    def test_shared_status_is_sent_as_its_old_twin(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): (200, json.dumps(BUG_DETAIL)),
                  ("PATCH", "/bugs/b1"): (200, "{}")}
        with _env(routes) as (out, _err, calls):
            specs_cli.set_bug_status("proj", "1", "completed")
        self.assertEqual(calls[-1], ("PATCH", f"{API}/bugs/b1", {"status": "resolved"}))
        self.assertIn("→ completed", out.getvalue())

    def test_old_status_is_sent_unchanged(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): (200, json.dumps(BUG_DETAIL)),
                  ("PATCH", "/bugs/b1"): (200, "{}")}
        with _env(routes) as (_out, _err, calls):
            specs_cli.set_bug_status("proj", "1", "ready_for_retest")
        self.assertEqual(calls[-1][2], {"status": "ready_for_retest"})

    def test_blocked_goes_through_the_item_endpoint(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): (200, json.dumps(BUG_DETAIL)),
                  ("PATCH", "/items/b1"): (200, "{}")}
        with _env(routes) as (_out, _err, calls):
            specs_cli.set_bug_status("proj", "1", "blocked")
        self.assertEqual(calls[-1], ("PATCH", f"{API}/items/b1", {"state": "blocked"}))

    def test_blocked_on_an_older_server_needs_a_newer_one(self):
        routes = {("GET", "/projects/proj/bugs/by-number/1"): HTML_404,
                  ("GET", "/projects/proj/bugs"): (200, json.dumps([BUG_ROW])),
                  ("PATCH", "/items/b1"): HTML_404}
        with _env(routes) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.set_bug_status("proj", "1", "blocked")
        self.assertIn("newer Signum", err.getvalue())

    def test_unknown_status_lists_old_and_shared(self):
        with _env({}) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.set_bug_status("proj", "1", "wontfix")
        self.assertIn("ready_for_retest", err.getvalue())
        self.assertIn("ready_for_testing", err.getvalue())


class SharedStatusTest(unittest.TestCase):
    def test_old_values_stay_accepted(self):
        for record, old in (("bug", specs_cli.BUG_STATUSES), ("backlog", specs_cli.BACKLOG_STATUSES),
                            ("feature", specs_cli.FEATURE_STATUSES), ("document", specs_cli.DOCUMENT_STATUSES)):
            accepted = specs_cli.accepted_statuses(record)
            for value in old:
                self.assertIn(value, accepted)
                self.assertEqual(specs_cli.status_to_send(record, value), value)
            for value in specs_cli.SHARED_STATUSES[record]:
                self.assertIn(value, accepted)

    def test_twins(self):
        self.assertEqual(specs_cli.status_to_send("backlog", "new"), "idea")
        self.assertEqual(specs_cli.status_to_send("bug", "archived"), "closed")
        self.assertEqual(specs_cli.status_to_send("feature", "new"), "idea")
        self.assertEqual(specs_cli.status_to_send("document", "completed"), "approved")
        self.assertEqual(specs_cli.status_to_send("document", "ready_for_testing"), "ready")

    def test_only_values_without_a_twin_need_shared_statuses(self):
        self.assertTrue(specs_cli.needs_shared_statuses("bug", "blocked"))
        self.assertTrue(specs_cli.needs_shared_statuses("feature", "planned"))
        self.assertTrue(specs_cli.needs_shared_statuses("document", "archived"))
        self.assertFalse(specs_cli.needs_shared_statuses("backlog", "new"))
        self.assertFalse(specs_cli.needs_shared_statuses("bug", "completed"))

    def test_set_status_on_a_document_sends_the_old_twin(self):
        doc_id = "11111111-2222-3333-4444-555555555555"
        routes = {("PATCH", f"{SERVICE_URL}/api/documents/{doc_id}"): (200, "{}")}
        with _env(routes) as (out, _err, calls):
            specs_cli.set_status(doc_id, "completed")
        self.assertEqual(calls[0][2], {"status": "approved"})
        self.assertIn("→ completed", out.getvalue())

    def test_feature_status_without_a_twin_hints_at_a_newer_server(self):
        routes = {("PATCH", f"{SERVICE_URL}/api/features/lookup?id=proj%2F012-onboarding"):
                  (400, json.dumps({"error": "Invalid status"}))}
        with _env(routes) as (_out, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.set_status("proj/012-onboarding", "planned")
        self.assertEqual(calls[0][2], {"status": "planned"})
        self.assertIn("newer Signum", err.getvalue())

    def test_bug_list_filter_takes_a_shared_value(self):
        rows = [BUG_ROW, {**BUG_ROW, "id": "b2", "number": 2, "status": "open"}]
        routes = {("GET", "/projects/proj/bugs"): (200, json.dumps(rows))}
        with _env(routes) as (out, _err, _calls):
            specs_cli.list_bugs("proj", status_filter="ready_for_testing", as_json=True)
        listed = json.loads(out.getvalue())
        self.assertEqual([b["id"] for b in listed], ["b1"])


class ItemsCommandTest(unittest.TestCase):
    def test_lists_open_items_with_bug_numbers(self):
        routes = {("GET", "/projects/proj/items"): (200, json.dumps([ITEM_BUG, ITEM_IMPL, ITEM_DONE]))}
        with _env(routes) as (out, _err, _calls):
            specs_cli.list_items("proj")
        text = out.getvalue()
        self.assertIn("#74 (Bug #1) [bug] Ready for retest — Breadcrumb shows slug", text)
        self.assertIn("#75 [implementation] In progress — Item page", text)
        self.assertNotIn("#76", text)

    def test_all_shows_done_items(self):
        routes = {("GET", "/projects/proj/items"): (200, json.dumps([ITEM_DONE]))}
        with _env(routes) as (out, _err, _calls):
            specs_cli.list_items("proj", include_all=True)
        self.assertIn("#76 [activity] Completed", out.getvalue())

    def test_filters_go_to_the_server(self):
        routes = {("GET", "/projects/proj/items?kind=bug%2Cactivity&state=ready_for_retest"): (200, "[]")}
        with _env(routes) as (_out, _err, calls):
            specs_cli.list_items("proj", kinds=["bug", "activity"], state="ready_for_retest")
        self.assertEqual(len(calls), 1)

    def test_unknown_kind_is_refused_before_any_call(self):
        with _env({}) as (_out, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.list_items("proj", kinds=["epic"])
        self.assertIn("--kind must be one of", err.getvalue())
        self.assertEqual(calls, [])

    def test_older_server_needs_a_newer_one(self):
        routes = {("GET", "/projects/proj/items"): HTML_404}
        with _env(routes) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.list_items("proj")
        self.assertIn("newer Signum", err.getvalue())


class ItemCommandTest(unittest.TestCase):
    def test_shows_a_bug_with_its_bug_number(self):
        routes = {("GET", "/projects/proj/items/by-number/74"): (200, json.dumps(ITEM_BUG))}
        with _env(routes) as (out, _err, _calls):
            specs_cli.view_item("proj", "#74")
        text = out.getvalue()
        self.assertIn("#74 [bug] Breadcrumb shows slug", text)
        self.assertIn("bug:       #1", text)
        self.assertIn("state:     ready_for_testing (Ready for retest)", text)
        self.assertIn("/portal/proj/items/74", text)

    def test_bug_flag_reads_an_old_bug_number(self):
        routes = {("GET", "/projects/proj/items/by-number/1?legacy=bug"): (200, json.dumps(ITEM_BUG))}
        with _env(routes) as (out, _err, _calls):
            specs_cli.view_item("proj", "1", legacy_bug=True)
        self.assertIn("#74 [bug]", out.getvalue())

    def test_activity_shows_its_outcome(self):
        routes = {("GET", "/projects/proj/items/by-number/76"): (200, json.dumps(ITEM_DONE))}
        with _env(routes) as (out, _err, _calls):
            specs_cli.view_item("proj", "76")
        self.assertIn("Outcome:\nDone", out.getvalue())

    def test_missing_item(self):
        routes = {("GET", "/projects/proj/items/by-number/9"): (404, json.dumps({"error": "Item not found"}))}
        with _env(routes) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.view_item("proj", "9")
        self.assertIn("item #9 not found", err.getvalue())

    def test_older_server_needs_a_newer_one(self):
        routes = {("GET", "/projects/proj/items/by-number/74"): HTML_404}
        with _env(routes) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.view_item("proj", "74")
        self.assertIn("newer Signum", err.getvalue())


class ItemKindTest(unittest.TestCase):
    def test_changes_the_kind(self):
        routes = {("GET", "/projects/proj/items/by-number/74"): (200, json.dumps(ITEM_BUG)),
                  ("PATCH", "/items/b1"): (200, json.dumps({**ITEM_BUG, "kind": "implementation"}))}
        with _env(routes) as (out, _err, calls):
            specs_cli.set_item_kind("proj", "74", "implementation")
        self.assertEqual(calls[-1], ("PATCH", f"{API}/items/b1", {"kind": "implementation"}))
        self.assertIn("#74 (Bug #1) bug → implementation", out.getvalue())

    def test_reports_the_state_moving(self):
        routes = {("GET", "/projects/proj/items/by-number/74"): (200, json.dumps(ITEM_BUG)),
                  ("PATCH", "/items/b1"): (200, json.dumps({**ITEM_BUG, "kind": "activity", "state": "in_progress"}))}
        with _env(routes) as (out, _err, _calls):
            specs_cli.set_item_kind("proj", "74", "activity")
        self.assertIn("(state ready_for_testing → in_progress)", out.getvalue())

    def test_same_kind_is_a_no_op(self):
        routes = {("GET", "/projects/proj/items/by-number/74"): (200, json.dumps(ITEM_BUG))}
        with _env(routes) as (out, _err, calls):
            specs_cli.set_item_kind("proj", "74", "bug")
        self.assertIn("already bug", out.getvalue())
        self.assertEqual(len(calls), 1)

    def test_external_user_is_told_why(self):
        routes = {("GET", "/projects/proj/items/by-number/74"): (200, json.dumps(ITEM_BUG)),
                  ("PATCH", "/items/b1"): (403, json.dumps({"error": "kind_change_forbidden"}))}
        with _env(routes) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.set_item_kind("proj", "74", "implementation")
        self.assertIn("only internal users", err.getvalue())

    def test_unknown_kind(self):
        with _env({}) as (_out, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.set_item_kind("proj", "74", "epic")
        self.assertIn("kind must be one of", err.getvalue())
        self.assertEqual(calls, [])


class CliDispatchTest(unittest.TestCase):
    def _main(self, argv, target):
        with mock.patch.object(specs_cli.sys, "argv", ["specs-cli.py", *argv]), \
             mock.patch.object(specs_cli, target) as fn, \
             contextlib.redirect_stderr(io.StringIO()):
            specs_cli.main()
        return fn

    def test_items_flags(self):
        fn = self._main(["items", "--kind", "bug,activity", "proj", "--state", "new", "--all"], "list_items")
        fn.assert_called_once_with("proj", kinds=["bug", "activity"], state="new", source=None,
                                   include_all=True, as_json=False)

    def test_item_with_bug_flag(self):
        fn = self._main(["item", "proj", "#1", "--bug"], "view_item")
        fn.assert_called_once_with("proj", "#1", legacy_bug=True, as_json=False)

    def test_item_kind(self):
        fn = self._main(["item-kind", "proj", "74", "activity"], "set_item_kind")
        fn.assert_called_once_with("proj", "74", "activity", legacy_bug=False)

    def test_backlog_update_sends_new_as_idea(self):
        fn = self._main(["backlog-update", "proj", "#5", "--status", "new"], "update_backlog_item")
        self.assertEqual(fn.call_args[0][2]["status"], "idea")


if __name__ == "__main__":
    unittest.main()
