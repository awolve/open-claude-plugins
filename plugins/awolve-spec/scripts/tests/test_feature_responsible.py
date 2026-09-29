"""Unit tests for the feature responsible person in the CLI (Signum spec 048).

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

CFG = {
    "service_url": "https://specs.example.com",
    "projects": [{"id": "alpha", "path": "/tmp/none-alpha"}, {"id": "beta", "path": "/tmp/none-beta"}],
}
HEADERS = {"Authorization": "Bearer x"}


@contextlib.contextmanager
def _env():
    with mock.patch.object(specs_cli.config, "read_config", return_value=CFG), \
         mock.patch.object(specs_cli.auth, "get_headers", return_value=HEADERS):
        yield


def _run(fn, *a, **kw):
    """Call fn; return (exit code or None, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            fn(*a, **kw)
            code = None
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


def _main(argv):
    with mock.patch.object(specs_cli.sys, "argv", ["specs-cli.py", *argv]):
        return _run(specs_cli.main)


class ParseListFeaturesArgsTest(unittest.TestCase):
    def test_project_only_keeps_the_old_listing(self):
        self.assertEqual(specs_cli._parse_list_features_args(["alpha"]), ("alpha", None, False))

    def test_mine_without_a_project(self):
        self.assertEqual(specs_cli._parse_list_features_args(["--mine"]), (None, ("me", None), False))

    def test_responsible_takes_a_value(self):
        self.assertEqual(
            specs_cli._parse_list_features_args(["alpha", "--responsible", "a@x.com", "--all"]),
            ("alpha", ("email", "a@x.com"), True),
        )

    def test_flags_before_the_project_id(self):
        self.assertEqual(specs_cli._parse_list_features_args(["--unassigned", "beta"]), ("beta", ("unassigned", None), False))

    def test_the_three_filters_are_mutually_exclusive(self):
        for pair in (["--mine", "--unassigned"], ["--mine", "--responsible", "a@x.com"], ["--unassigned", "--responsible", "a@x.com"]):
            code, _, err = _run(specs_cli._parse_list_features_args, pair)
            self.assertEqual(code, 1, pair)
            self.assertIn("mutually exclusive", err)

    def test_responsible_without_a_value_is_refused(self):
        code, _, err = _run(specs_cli._parse_list_features_args, ["--responsible"])
        self.assertEqual(code, 1)
        self.assertIn("needs an email", err)
        code, _, _ = _run(specs_cli._parse_list_features_args, ["--responsible", "--all"])
        self.assertEqual(code, 1)

    def test_no_project_and_no_filter_is_a_usage_error(self):
        code, _, err = _run(specs_cli._parse_list_features_args, [])
        self.assertEqual(code, 1)
        self.assertIn("Usage", err)
        code, _, _ = _run(specs_cli._parse_list_features_args, ["--all"])
        self.assertEqual(code, 1)

    def test_unknown_flag_is_refused(self):
        code, _, err = _run(specs_cli._parse_list_features_args, ["alpha", "--mne"])
        self.assertEqual(code, 1)
        self.assertIn("unknown flag", err)


class ResponsibleErrorTest(unittest.TestCase):
    def _msg(self, code, who="a@x.com"):
        return specs_cli._responsible_error(json.dumps({"error": code}), who)

    def test_codes_are_translated(self):
        self.assertIn("sign in to Signum at least once", self._msg("assignee_not_found"))
        self.assertIn("'a@x.com'", self._msg("assignee_not_found"))
        self.assertIn("grant them access to this project first", self._msg("assignee_no_access"))
        self.assertIn("developer or admin role", self._msg("responsible_forbidden"))
        self.assertIn("--unassign", self._msg("invalid_responsible"))

    def test_other_errors_and_non_json_give_nothing(self):
        self.assertIsNone(self._msg("Feature not found"))
        self.assertIsNone(specs_cli._responsible_error("<html>", "a@x.com"))
        self.assertIsNone(specs_cli._responsible_error("[]", "a@x.com"))


class ResponsibleLabelTest(unittest.TestCase):
    def test_unset_is_a_dash(self):
        self.assertEqual(specs_cli._responsible_label({"responsibleId": None}), "-")
        self.assertEqual(specs_cli._responsible_label({}), "-")

    def test_email_is_shown(self):
        f = {"responsibleId": "u1", "responsibleEmail": "a@x.com", "responsibleName": "A",
             "responsibleActive": True, "responsibleHasAccess": True}
        self.assertEqual(specs_cli._responsible_label(f), "a@x.com")

    def test_inactive_and_no_access_are_marked(self):
        base = {"responsibleId": "u1", "responsibleEmail": "a@x.com"}
        self.assertEqual(specs_cli._responsible_label({**base, "responsibleActive": False}), "a@x.com (inactive)")
        self.assertEqual(specs_cli._responsible_label({**base, "responsibleHasAccess": False}), "a@x.com (no access)")

    def test_missing_flags_do_not_mark(self):
        # An older row without the flags must not read as inactive.
        self.assertEqual(specs_cli._responsible_label({"responsibleId": "u1", "responsibleEmail": "a@x.com"}), "a@x.com")


class FilterByResponsibleTest(unittest.TestCase):
    ROWS = [
        {"id": "p/1", "responsibleId": "u1", "responsibleEmail": "bjorn.allvin@example.com", "responsibleName": "Björn Allvin"},
        {"id": "p/2", "responsibleId": None},
        {"id": "p/3", "responsibleId": "u2", "responsibleEmail": "anna@example.com", "responsibleName": "Anna"},
    ]

    def test_unassigned(self):
        self.assertEqual([f["id"] for f in specs_cli._filter_by_responsible(self.ROWS, "unassigned")], ["p/2"])

    def test_email_is_case_insensitive(self):
        got = specs_cli._filter_by_responsible(self.ROWS, "email", "ANNA@example.com")
        self.assertEqual([f["id"] for f in got], ["p/3"])

    def test_name_fragment(self):
        got = specs_cli._filter_by_responsible(self.ROWS, "email", "björn")
        self.assertEqual([f["id"] for f in got], ["p/1"])


class FeatureItemsShapeTest(unittest.TestCase):
    def _items(self, body):
        with mock.patch.object(specs_cli, "api_request", return_value=(200, json.dumps(body))):
            return specs_cli._feature_items("https://s", HEADERS, "alpha")

    def test_old_bare_array(self):
        self.assertEqual(self._items([{"id": "alpha/001-x", "items": [{"n": 1}]}]), {"alpha/001-x": [{"n": 1}]})

    def test_new_object_with_viewer(self):
        body = {"features": [{"id": "alpha/001-x", "items": [{"n": 1}]}, {"id": "alpha/002-y"}],
                "viewer": {"canSetResponsible": True}}
        self.assertEqual(self._items(body), {"alpha/001-x": [{"n": 1}], "alpha/002-y": []})

    def test_unexpected_shapes_give_nothing(self):
        self.assertEqual(self._items({"viewer": {}}), {})
        self.assertEqual(self._items("nope"), {})


class SetResponsibleTest(unittest.TestCase):
    ROW = {"id": "alpha/001-x", "responsibleId": "u1", "responsibleEmail": "a@x.com",
           "responsibleActive": True, "responsibleHasAccess": True}

    def _call(self, argv, response=(200, None)):
        status, body = response
        if body is None:
            body = json.dumps(self.ROW)
        with _env(), mock.patch.object(specs_cli, "api_request", return_value=(status, body)) as req:
            code, out, err = _main(argv)
        return code, out, err, req

    def test_set_sends_the_email(self):
        code, out, _, req = self._call(["set-responsible", "alpha/001-x", "a@x.com"])
        self.assertIsNone(code)
        self.assertEqual(req.call_args.kwargs["data"], {"responsible": "a@x.com"})
        self.assertEqual(req.call_args.kwargs["method"], "PATCH")
        self.assertIn("/api/features/lookup?id=alpha%2F001-x", req.call_args.args[0])
        self.assertIn("responsible → a@x.com", out)

    def test_unassign_sends_an_explicit_null(self):
        code, out, _, req = self._call(["set-responsible", "alpha/001-x", "--unassign"],
                                       (200, json.dumps({**self.ROW, "responsibleId": None})))
        self.assertIsNone(code)
        self.assertIn("responsible", req.call_args.kwargs["data"])
        self.assertIsNone(req.call_args.kwargs["data"]["responsible"])
        self.assertIn("no responsible person", out)

    def test_email_and_unassign_together_is_a_usage_error(self):
        code, _, err, req = self._call(["set-responsible", "alpha/001-x", "a@x.com", "--unassign"])
        self.assertEqual(code, 1)
        self.assertIn("Usage", err)
        req.assert_not_called()

    def test_missing_email_is_a_usage_error(self):
        code, _, err, req = self._call(["set-responsible", "alpha/001-x"])
        self.assertEqual(code, 1)
        req.assert_not_called()

    def test_server_codes_are_translated_not_echoed(self):
        code, _, err, _ = self._call(["set-responsible", "alpha/001-x", "a@x.com"],
                                     (403, json.dumps({"error": "responsible_forbidden"})))
        self.assertEqual(code, 1)
        self.assertIn("developer or admin role", err)
        self.assertNotIn("responsible_forbidden", err)

    def test_an_old_service_that_ignores_the_field_is_caught(self):
        code, _, err, _ = self._call(["set-responsible", "alpha/001-x", "a@x.com"],
                                     (200, json.dumps({"id": "alpha/001-x", "status": "idea"})))
        self.assertEqual(code, 1)
        self.assertIn("does not support", err)


class CreateFeatureResponsibleTest(unittest.TestCase):
    def _call(self, argv, response):
        calls = []

        def fake(url, method="GET", headers=None, data=None):
            calls.append((url, method, data))
            if method == "POST":
                return response
            return 200, "{}"

        with _env(), mock.patch.object(specs_cli, "api_request", side_effect=fake), \
             mock.patch.object(specs_cli.os, "makedirs"):
            code, out, err = _main(argv)
        return code, out, err, calls

    def test_responsible_goes_in_the_post_body(self):
        row = {"id": "alpha/004-x", "responsibleId": "u1", "responsibleEmail": "a@x.com"}
        code, out, _, calls = self._call(["create-feature", "alpha", "004-x", "--responsible", "a@x.com"], (201, json.dumps(row)))
        self.assertIsNone(code)
        post = [c for c in calls if c[1] == "POST"][0]
        self.assertEqual(post[2]["responsible"], "a@x.com")
        self.assertIn("responsible: a@x.com", out)

    def test_without_the_flag_the_body_has_no_responsible_key(self):
        code, _, _, calls = self._call(["create-feature", "alpha", "004-x"], (201, json.dumps({"id": "alpha/004-x"})))
        self.assertIsNone(code)
        post = [c for c in calls if c[1] == "POST"][0]
        self.assertNotIn("responsible", post[2])

    def test_a_refused_responsible_is_translated(self):
        code, _, err, _ = self._call(["create-feature", "alpha", "004-x", "--responsible", "a@x.com"],
                                     (400, json.dumps({"error": "assignee_no_access"})))
        self.assertEqual(code, 1)
        self.assertIn("grant them access to this project first", err)

    def test_an_old_service_dropping_it_warns(self):
        code, _, err, _ = self._call(["create-feature", "alpha", "004-x", "--responsible", "a@x.com"],
                                     (201, json.dumps({"id": "alpha/004-x"})))
        self.assertIsNone(code)
        self.assertIn("ignored --responsible", err)

    def test_responsible_without_a_value_is_refused(self):
        code, _, err, calls = self._call(["create-feature", "alpha", "004-x", "--responsible"], (201, "{}"))
        self.assertEqual(code, 1)
        self.assertEqual(calls, [])

    def test_from_item_passes_it_through(self):
        with _env(), mock.patch.object(specs_cli, "create_feature_from_item") as from_item:
            code, _, _ = _main(["create-feature", "alpha", "--from-item", "7", "--responsible", "a@x.com"])
        self.assertIsNone(code)
        self.assertEqual(from_item.call_args.kwargs["responsible"], "a@x.com")


class ListFeaturesTest(unittest.TestCase):
    def _call(self, argv, routes):
        calls = []

        def fake(url, method="GET", headers=None, data=None):
            calls.append(url)
            for prefix, resp in routes.items():
                if prefix in url:
                    return resp
            return 404, "{}"

        with _env(), mock.patch.object(specs_cli, "api_request", side_effect=fake):
            code, out, err = _main(argv)
        return code, out, err, calls

    def test_across_projects_is_one_call_and_keeps_configured_projects(self):
        rows = [
            {"id": "alpha/001-a", "name": "001-a", "status": "in_progress", "projectId": "alpha", "projectName": "Alpha",
             "responsibleId": "u1", "responsibleEmail": "me@x.com"},
            {"id": "gamma/002-g", "name": "002-g", "status": "idea", "projectId": "gamma", "projectName": "Gamma",
             "responsibleId": "u1", "responsibleEmail": "me@x.com"},
        ]
        code, out, _, calls = self._call(["list-features", "--mine"], {"/api/portal/features?": (200, json.dumps({"features": rows}))})
        self.assertIsNone(code)
        self.assertEqual(len(calls), 1)
        self.assertIn("responsible=me", calls[0])
        self.assertNotIn("includeCompleted", calls[0])
        self.assertIn("001-a", out)
        self.assertNotIn("002-g", out)
        self.assertIn("1 more in projects not configured here", out)

    def test_all_asks_for_completed(self):
        _, _, _, calls = self._call(["list-features", "--unassigned", "--all"], {"/api/portal/features?": (200, json.dumps({"features": []}))})
        self.assertIn("responsible=unassigned", calls[0])
        self.assertIn("includeCompleted=1", calls[0])

    def test_across_with_an_email(self):
        _, _, _, calls = self._call(["list-features", "--responsible", "a@x.com"], {"/api/portal/features?": (200, json.dumps({"features": []}))})
        self.assertIn("responsible=a%40x.com", calls[0])

    def test_across_on_an_old_service_says_so(self):
        code, _, err, _ = self._call(["list-features", "--mine"], {})
        self.assertEqual(code, 1)
        self.assertIn("no cross-project feature list", err)

    def test_per_project_filter_is_client_side_and_hides_completed(self):
        rows = [
            {"id": "alpha/001-a", "name": "001-a", "status": "in_progress", "documentCount": 2,
             "responsibleId": "u1", "responsibleEmail": "anna@x.com", "responsibleName": "Anna"},
            {"id": "alpha/002-b", "name": "002-b", "status": "completed", "documentCount": 3,
             "responsibleId": "u1", "responsibleEmail": "anna@x.com", "responsibleName": "Anna"},
            {"id": "alpha/003-c", "name": "003-c", "status": "idea", "documentCount": 0, "responsibleId": None},
        ]
        routes = {"/api/features?project=alpha": (200, json.dumps(rows)),
                  "/api/portal/projects/alpha/features": (200, json.dumps({"features": [], "viewer": {}}))}
        code, out, _, _ = self._call(["list-features", "alpha", "--responsible", "anna"], routes)
        self.assertIsNone(code)
        self.assertIn("001-a", out)
        self.assertNotIn("002-b", out)
        self.assertNotIn("003-c", out)
        code, out, _, _ = self._call(["list-features", "alpha", "--responsible", "anna", "--all"], routes)
        self.assertIn("002-b", out)

    def test_unfiltered_listing_shows_the_responsible_column(self):
        rows = [
            {"id": "alpha/001-a", "name": "001-a", "status": "completed", "documentCount": 2,
             "responsibleId": "u1", "responsibleEmail": "anna@x.com", "responsibleActive": False},
            {"id": "alpha/003-c", "name": "003-c", "status": "idea", "documentCount": 0, "responsibleId": None},
        ]
        routes = {"/api/features?project=alpha": (200, json.dumps(rows)),
                  "/api/portal/projects/alpha/features": (200, json.dumps([]))}
        code, out, _, _ = self._call(["list-features", "alpha"], routes)
        self.assertIsNone(code)
        self.assertIn("anna@x.com (inactive)", out)
        self.assertIn("001-a", out)  # completed stays in the unfiltered list
        self.assertRegex(out, r"003-c.*  -")

    def test_per_project_mine_uses_the_service_and_keeps_that_project(self):
        rows = [
            {"id": "alpha/001-a", "name": "001-a", "status": "in_progress", "projectId": "alpha", "responsibleId": "u1", "responsibleEmail": "me@x.com"},
            {"id": "beta/001-b", "name": "001-b", "status": "in_progress", "projectId": "beta", "responsibleId": "u1", "responsibleEmail": "me@x.com"},
        ]
        routes = {"/api/portal/features?": (200, json.dumps({"features": rows})),
                  "/api/portal/projects/alpha/features": (200, "[]")}
        code, out, _, _ = self._call(["list-features", "alpha", "--mine"], routes)
        self.assertIsNone(code)
        self.assertIn("001-a", out)
        self.assertNotIn("001-b", out)

    def test_per_project_filter_on_an_old_service_says_so(self):
        rows = [{"id": "alpha/001-a", "name": "001-a", "status": "idea", "documentCount": 0}]
        code, _, err, _ = self._call(["list-features", "alpha", "--unassigned"], {"/api/features?project=alpha": (200, json.dumps(rows))})
        self.assertEqual(code, 1)
        self.assertIn("does not report who is responsible", err)


if __name__ == "__main__":
    unittest.main()
