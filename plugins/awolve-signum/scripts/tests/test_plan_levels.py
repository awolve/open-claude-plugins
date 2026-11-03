"""Unit tests for planning at any level (at Awolve: Signum spec 056):
`milestone-add --epic / --feature` plan the epic or feature itself,
`--epic-items / --feature-items` keep adding the open items, and
`milestones` names the level its progress counts.

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
CFG = {"service_url": SERVICE_URL, "projects": [{"id": "demo", "path": "./specs"}]}
API = f"{SERVICE_URL}/api"
MILESTONES = ("GET", "/portal/projects/demo/milestones")
ITEMS = ("POST", "/portal/milestones/m1/items")
PILOT = {"id": "m1", "kind": "deadline", "name": "Pilot", "date": "2027-01-31",
         "progress": {"done": 1, "total": 3, "level": "features"}, "state": "in_progress", "overdue": False}


def _ok(body, status=200):
    return (status, json.dumps(body))


@contextlib.contextmanager
def _env(routes):
    calls = []

    def fake(url, method="GET", headers=None, data=None):
        calls.append((method, url, data))
        key = (method, url[len(API):])
        if key in routes:
            return routes[key]
        raise AssertionError(f"unexpected request {method} {url}")

    out, err = io.StringIO(), io.StringIO()
    with mock.patch.object(specs_cli.config, "read_config", return_value=CFG), \
         mock.patch.object(specs_cli.auth, "get_headers", return_value={"Authorization": "Bearer x"}), \
         mock.patch.object(specs_cli, "api_request", side_effect=fake), \
         contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        yield out, err, calls


class MilestoneAdd(unittest.TestCase):
    def test_feature_plans_the_feature_itself(self):
        routes = {MILESTONES: _ok([PILOT]), ITEMS: _ok({"added": 1, "moved": 0, "unchanged": 0, "following": 7})}
        with _env(routes) as (out, _err, calls):
            specs_cli.add_to_milestone("demo", "Pilot", feature="016-sales-report")
        self.assertEqual(calls[-1][2], {"featureIds": ["016-sales-report"]})
        self.assertIn("planned feature '016-sales-report' into 'Pilot' (its 7 items follow it)", out.getvalue())

    def test_epic_plans_the_epic_itself(self):
        routes = {MILESTONES: _ok([PILOT]), ITEMS: _ok({"added": 1, "moved": 1, "unchanged": 0, "following": 0})}
        with _env(routes) as (out, _err, calls):
            specs_cli.add_to_milestone("demo", "Pilot", epic="E3")
        self.assertEqual(calls[-1][2], {"epicIds": ["E3"]})
        self.assertIn("planned epic E3 into 'Pilot' (moved from another deadline)", out.getvalue())

    def test_already_planned(self):
        routes = {MILESTONES: _ok([PILOT]), ITEMS: _ok({"added": 0, "moved": 0, "unchanged": 1, "following": 2})}
        with _env(routes) as (out, _err, _calls):
            specs_cli.add_to_milestone("demo", "Pilot", epic="E3")
        self.assertIn("epic E3 is already planned into 'Pilot'", out.getvalue())

    def test_epic_items_keeps_the_old_behaviour(self):
        routes = {MILESTONES: _ok([PILOT]), ITEMS: _ok({"added": 4, "moved": 1, "unchanged": 0})}
        with _env(routes) as (out, _err, calls):
            specs_cli.add_to_milestone("demo", "Pilot", epic_items="E3")
        self.assertEqual(calls[-1][2], {"epicId": "E3"})
        self.assertIn("added 4 item(s) to 'Pilot' (1 moved from another deadline)", out.getvalue())

    def test_feature_items_sends_feature_id(self):
        routes = {MILESTONES: _ok([PILOT]), ITEMS: _ok({"added": 2, "moved": 0, "unchanged": 0})}
        with _env(routes) as (_out, _err, calls):
            specs_cli.add_to_milestone("demo", "Pilot", feature_items="016-sales-report")
        self.assertEqual(calls[-1][2], {"featureId": "016-sales-report"})

    def test_older_service_says_to_use_the_items_flag(self):
        routes = {MILESTONES: _ok([PILOT]), ITEMS: _ok({"error": "one_of_required"}, 400)}
        with _env(routes) as (_out, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.add_to_milestone("demo", "Pilot", feature="016-sales-report")
        self.assertIn("use --feature-items", err.getvalue())
        self.assertEqual(sum(1 for c in calls if c[0] == "POST"), 1)

    def test_a_refusal_is_reported_once(self):
        routes = {MILESTONES: _ok([PILOT]), ITEMS: _ok({"error": "feature_not_found"}, 404)}
        with _env(routes) as (_out, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.add_to_milestone("demo", "Pilot", feature="nope")
        self.assertIn("feature_not_found", err.getvalue())
        self.assertEqual(sum(1 for c in calls if c[0] == "POST"), 1)

    def test_exactly_one_flag(self):
        with _env({}) as (_out, err, _calls):
            with self.assertRaises(SystemExit):
                specs_cli.add_to_milestone("demo", "Pilot", epic="E3", items="4")
        self.assertIn("exactly one of", err.getvalue())


class MilestonesLevel(unittest.TestCase):
    def test_progress_names_its_level(self):
        rows = [PILOT,
                {**PILOT, "id": "m2", "name": "Beta", "progress": {"done": 2, "total": 5, "level": "items"}},
                {**PILOT, "id": "m3", "name": "Wave", "progress": {"done": 4, "total": 9, "level": "mixed"}},
                {**PILOT, "id": "m4", "name": "Later", "progress": {"done": 0, "total": 0, "level": "items"}},
                {**PILOT, "id": "m5", "name": "Old", "progress": {"done": 1, "total": 2}}]
        with _env({MILESTONES: _ok(rows)}) as (out, _err, _calls):
            specs_cli.list_milestones("demo")
        text = out.getvalue()
        self.assertIn("1/3 features done", text)
        self.assertIn("2/5 items done", text)
        self.assertIn("4/9 pieces of work done", text)
        self.assertIn("nothing planned yet", text)
        self.assertIn("1/2 done", text)  # an older service sends no level


if __name__ == "__main__":
    unittest.main()
