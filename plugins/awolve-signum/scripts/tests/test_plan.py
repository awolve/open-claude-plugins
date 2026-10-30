"""Unit tests for phases and milestones (at Awolve: Signum spec 052): the
`phase`, `phase-*`, `milestones` and `milestone-*` commands, and
`backlog-update --milestone/--unmilestone`.

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
HTML_404 = (404, "<!DOCTYPE html><html><body>404</body></html>")

PILOT = {"id": "p1", "name": "Pilot", "startDate": "2026-10-27", "endDate": "2026-11-13", "color": None, "state": "in_progress"}
WAVE = {"id": "p2", "name": "Wave 1", "startDate": "2026-11-01", "endDate": None, "color": "pink", "state": "planned"}
FIXES = {"id": "m1", "kind": "deadline", "name": "Pilot fixes", "date": "2026-11-13", "progress": {"done": 1, "total": 5}, "state": "in_progress", "overdue": False}
GOLIVE = {"id": "m2", "kind": "date", "name": "Go-live", "date": "2026-11-20", "progress": None, "state": "planned", "overdue": False}
LATE = {"id": "m3", "kind": "deadline", "name": "Security review", "date": "2026-10-24", "progress": {"done": 0, "total": 1}, "state": "planned", "overdue": True}


def _router(routes):
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


def _ok(body, status=200):
    return (status, json.dumps(body))


class PhaseTest(unittest.TestCase):
    def test_current_phases_are_listed_with_dates(self):
        with _env({("GET", "/projects/proj/phase"): _ok({"phase": PILOT, "phases": [PILOT, WAVE]})}) as (out, _, _c):
            specs_cli.show_phase("proj")
        self.assertIn("current phases in 'proj': Pilot (2026-10-27 – 2026-11-13), Wave 1 (2026-11-01 – open-ended)", out.getvalue())

    def test_no_current_phase(self):
        with _env({("GET", "/projects/proj/phase"): _ok({"phase": None, "phases": []})}) as (out, _, _c):
            specs_cli.show_phase("proj")
        self.assertIn("no current phase", out.getvalue())

    def test_all_marks_the_current_ones_and_shows_a_colour(self):
        with _env({("GET", "/projects/proj/phase"): _ok({"phase": PILOT, "phases": [PILOT]}),
                   ("GET", "/projects/proj/phases"): _ok([PILOT, WAVE])}) as (out, _, _c):
            specs_cli.show_phase("proj", show_all=True)
        lines = out.getvalue().splitlines()
        self.assertTrue(any(l.strip().startswith("* Pilot") for l in lines))
        self.assertTrue(any("Wave 1" in l and "[pink]" in l and "*" not in l for l in lines))

    def test_older_service_says_it_has_no_phases(self):
        with _env({("GET", "/projects/proj/phase"): HTML_404}) as (_, err, _c):
            with self.assertRaises(SystemExit):
                specs_cli.show_phase("proj")
        self.assertIn("no phases or milestones yet", err.getvalue())

    def test_add_sends_name_dates_and_colour(self):
        with _env({("POST", "/projects/proj/phases"): _ok({"phase": WAVE}, 201)}) as (out, _, calls):
            specs_cli.add_phase("proj", "Wave 1", "2026-11-01", None, "pink")
        self.assertEqual(calls[0][2], {"name": "Wave 1", "startDate": "2026-11-01", "endDate": None, "color": "pink"})
        self.assertIn("added phase 'Wave 1' (2026-11-01 – open-ended)", out.getvalue())

    def test_add_checks_the_colour_and_date_before_calling(self):
        with _env({}) as (_, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.add_phase("proj", "X", "2026-11-01", None, "mauve")
            with self.assertRaises(SystemExit):
                specs_cli.add_phase("proj", "X", "1 Nov", None, None)
        self.assertEqual(calls, [])
        self.assertIn("--color must be one of", err.getvalue())

    def test_update_finds_by_name_in_any_case_and_patches_only_what_was_given(self):
        with _env({("GET", "/projects/proj/phases"): _ok([PILOT, WAVE]),
                   ("PATCH", "/phases/p2"): _ok({"phase": {**WAVE, "endDate": "2026-12-20", "color": None}})}) as (out, _, calls):
            specs_cli.update_phase("proj", "wave 1", {"endDate": "2026-12-20", "color": None})
        self.assertEqual(calls[1][2], {"endDate": "2026-12-20", "color": None})
        self.assertIn("2026-11-01 – 2026-12-20", out.getvalue())

    def test_two_phases_with_one_name_ask_for_the_id(self):
        twin = {**PILOT, "id": "p9", "startDate": "2027-03-01"}
        with _env({("GET", "/projects/proj/phases"): _ok([PILOT, twin])}) as (_, err, _c):
            with self.assertRaises(SystemExit):
                specs_cli.delete_phase("proj", "Pilot")
        self.assertIn("2 phases are called 'Pilot'", err.getvalue())
        self.assertIn("p9", err.getvalue())

    def test_a_refusal_is_explained(self):
        with _env({("GET", "/projects/proj/phases"): _ok([PILOT]),
                   ("PATCH", "/phases/p1"): (403, json.dumps({"error": "timing_forbidden"}))}) as (_, err, _c):
            with self.assertRaises(SystemExit):
                specs_cli.update_phase("proj", "Pilot", {"name": "Pilot 2"})
        self.assertIn("only internal users can change phases and milestones", err.getvalue())


class MilestoneTest(unittest.TestCase):
    def test_list_shows_progress_dates_and_overdue(self):
        with _env({("GET", "/projects/proj/milestones"): _ok([LATE, FIXES, GOLIVE])}) as (out, _, _c):
            specs_cli.list_milestones("proj")
        text = out.getvalue()
        self.assertIn("Security review", text)
        self.assertIn("overdue", text)
        self.assertIn("1/5 done", text)
        self.assertIn("upcoming", text)

    def test_create_checks_the_kind(self):
        with _env({}) as (_, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.create_milestone("proj", "X", "2026-12-01", "gate")
        self.assertEqual(calls, [])
        self.assertIn("--kind must be deadline or date", err.getvalue())

    def test_add_items_by_number_and_reports_moves(self):
        with _env({("GET", "/projects/proj/milestones"): _ok([FIXES]),
                   ("POST", "/milestones/m1/items"): _ok({"added": 2, "moved": 1, "unchanged": 1})}) as (out, _, calls):
            specs_cli.add_to_milestone("proj", "Pilot fixes", items="#12, 15")
        self.assertEqual(calls[1][2], {"itemIds": [12, 15]})
        self.assertIn("added 2 item(s) to 'Pilot fixes' (1 moved from another deadline); 1 already in it", out.getvalue())

    def test_add_an_epic_sends_only_the_epic(self):
        with _env({("GET", "/projects/proj/milestones"): _ok([FIXES]),
                   ("POST", "/milestones/m1/items"): _ok({"added": 3, "moved": 0, "unchanged": 0})}) as (_, _e, calls):
            specs_cli.add_to_milestone("proj", "m1", epic="E3")
        self.assertEqual(calls[1][2], {"epicId": "E3"})

    def test_add_needs_exactly_one_source(self):
        with _env({}) as (_, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.add_to_milestone("proj", "m1", items="1", epic="E3")
        self.assertEqual(calls, [])

    def test_delete_says_how_many_items_went_back_to_unplanned(self):
        with _env({("GET", "/projects/proj/milestones"): _ok([FIXES]),
                   ("DELETE", "/milestones/m1"): _ok({"deleted": True, "unplanned": 5})}) as (out, _, _c):
            specs_cli.delete_milestone("proj", "Pilot fixes")
        self.assertIn("5 item(s) back to Unplanned", out.getvalue())


class BacklogMilestoneFlagTest(unittest.TestCase):
    def test_milestone_flag_takes_a_name_and_refuses_a_date(self):
        with _env({("GET", "/projects/proj/milestones"): _ok([FIXES, GOLIVE])}) as (_, err, _c):
            self.assertEqual(specs_cli._resolve_milestone_for_item("proj", "pilot FIXES"), "m1")
            with self.assertRaises(SystemExit):
                specs_cli._resolve_milestone_for_item("proj", "Go-live")
        self.assertIn("is a date; only a deadline holds items", err.getvalue())


if __name__ == "__main__":
    unittest.main()
