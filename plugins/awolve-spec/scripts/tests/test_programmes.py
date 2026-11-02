"""Unit tests for programmes (at Awolve: Signum spec 055): `programmes`,
`programme`, `project-kind`, `programme-add`, `programme-remove`,
`milestone-link` and `milestone-unlink`.

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
CFG = {"service_url": SERVICE_URL, "projects": [{"id": "prog", "path": "./specs"}]}
API = f"{SERVICE_URL}/api"

PROG_DEADLINE = {"id": "pm1", "kind": "deadline", "name": "Pilot in production", "date": "2027-02-28",
                 "progress": {"done": 9, "total": 31}, "state": "in_progress", "overdue": False, "linkCount": 2,
                 "linkedOverdue": [{"projectId": "ga", "projectName": "GA", "milestoneId": "g1"}],
                 "linkedLate": [{"projectId": "mv", "projectName": "Medvind", "milestoneId": "v1", "date": "2027-03-12", "days": 12}]}
EMPTY_DEADLINE = {"id": "pm2", "kind": "deadline", "name": "Phase 3 sign-off", "date": "2027-06-30",
                  "progress": {"done": 0, "total": 0}, "state": "new", "overdue": False, "linkCount": 0, "linkedOverdue": [], "linkedLate": []}
MEMBER_LATE = {"id": "v1", "kind": "deadline", "name": "M2 pilot", "date": "2027-03-12", "progress": {"done": 0, "total": 15}, "state": "planned", "overdue": False}
MEMBER_DATE = {"id": "v2", "kind": "date", "name": "Demo", "date": "2027-01-10", "progress": None, "state": "planned", "overdue": False}


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


class ProgrammesTest(unittest.TestCase):
    def test_list_shows_member_counts(self):
        rows = [{"id": "prog", "name": "Platform", "clientName": "Acme", "kind": "programme", "memberCount": 2}]
        with _env({("GET", "/portal/projects?kind=programme"): _ok(rows)}) as (out, _, _c):
            specs_cli.list_programmes()
        self.assertIn("1 programme(s)", out.getvalue())
        self.assertIn("Platform  (Acme) — 2 members", out.getvalue())

    def test_show_programme_has_progress_links_and_members(self):
        plan = {"kind": "programme", "today": "2026-11-02", "currentPhases": [{"name": "Phase 1"}],
                "milestones": [PROG_DEADLINE, EMPTY_DEADLINE], "links": [],
                "members": [
                    {"project": {"id": "ga", "name": "GA"}, "plan": {"currentPhases": [{"name": "Build"}], "milestones": [{**MEMBER_LATE, "id": "g1", "name": "Akutt", "date": "2026-10-01", "overdue": True}]}},
                    {"project": {"id": "mv", "name": "Medvind"}, "plan": None, "error": "load_failed"},
                ]}
        with _env({("GET", "/portal/projects/prog/plan?members=1"): _ok(plan)}) as (out, _, _c):
            specs_cli.show_programme("prog")
        text = out.getvalue()
        self.assertIn("now: Phase 1", text)
        self.assertIn("9/31 done  · 2 linked", text)
        self.assertIn("Phase 3 sign-off                 not broken down yet", text)
        self.assertIn("! GA: a linked deadline is overdue", text)
        self.assertIn("! Medvind: a linked deadline is 12 day(s) later (2027-03-12)", text)
        self.assertIn("GA                                   now: Build; 1 overdue", text)
        self.assertIn("Medvind                              could not load its plan", text)

    def test_show_on_a_normal_project_says_so(self):
        with _env({("GET", "/portal/projects/prog/plan?members=1"): _ok({"milestones": []})}) as (_, err, _c):
            with self.assertRaises(SystemExit):
                specs_cli.show_programme("prog")
        self.assertIn("is a project, not a programme", err.getvalue())

    def test_project_kind_patches_the_admin_route(self):
        with _env({("PATCH", "/projects/prog"): _ok({"id": "prog", "kind": "programme"})}) as (out, _, calls):
            specs_cli.set_project_kind("prog", "programme")
        self.assertEqual(calls[0][2], {"kind": "programme"})
        self.assertIn("'prog' is now a programme", out.getvalue())

    def test_project_kind_refusal_is_explained(self):
        refused = (409, json.dumps({"error": "programme_has_members", "count": 2}))
        with _env({("PATCH", "/projects/prog"): refused}) as (_, err, _c):
            with self.assertRaises(SystemExit):
                specs_cli.set_project_kind("prog", "project")
        self.assertIn("still has members", err.getvalue())

    def test_project_kind_checks_the_value_first(self):
        with _env({}) as (_, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.set_project_kind("prog", "program")
        self.assertEqual(calls, [])
        self.assertIn("project or programme", err.getvalue())

    def test_add_member_and_twice(self):
        with _env({("POST", "/portal/projects/prog/members"): _ok({"added": True, "members": [{"id": "ga"}, {"id": "mv"}]}, 201)}) as (out, _, calls):
            specs_cli.add_programme_member("prog", "mv")
        self.assertEqual(calls[0][2], {"projectId": "mv"})
        self.assertIn("added 'mv' to programme 'prog'", out.getvalue())
        with _env({("POST", "/portal/projects/prog/members"): _ok({"added": False, "members": [{"id": "mv"}]})}) as (out, _, _c):
            specs_cli.add_programme_member("prog", "mv")
        self.assertIn("already a member", out.getvalue())

    def test_add_a_programme_is_refused(self):
        refused = (409, json.dumps({"error": "member_is_programme"}))
        with _env({("POST", "/portal/projects/prog/members"): refused}) as (_, err, _c):
            with self.assertRaises(SystemExit):
                specs_cli.add_programme_member("prog", "other-prog")
        self.assertIn("can't be a member", err.getvalue())

    def test_remove_without_yes_only_counts(self):
        with _env({("DELETE", "/portal/projects/prog/members/mv?dryRun=1"): _ok({"removed": False, "linksRemoved": 2, "dryRun": True})}) as (out, _, calls):
            specs_cli.remove_programme_member("prog", "mv")
        self.assertEqual(len(calls), 1)
        self.assertIn("also removes 2 link(s)", out.getvalue())
        self.assertIn("--yes", out.getvalue())

    def test_remove_with_yes(self):
        with _env({("DELETE", "/portal/projects/prog/members/mv"): _ok({"removed": True, "linksRemoved": 2, "dryRun": False})}) as (out, _, _c):
            specs_cli.remove_programme_member("prog", "mv", confirmed=True)
        self.assertIn("removed 'mv' from 'prog'; 2 deadline link(s) removed", out.getvalue())

    def test_link_by_names_and_flag_a_later_member_date(self):
        routes = {
            ("GET", "/portal/projects/prog/milestones"): _ok([PROG_DEADLINE, EMPTY_DEADLINE]),
            ("GET", "/portal/projects/mv/milestones"): _ok([MEMBER_LATE, MEMBER_DATE]),
            ("POST", "/portal/milestones/pm1/links"): _ok({"linked": True, "link": {}}, 201),
        }
        with _env(routes) as (out, _, calls):
            specs_cli.link_milestones("prog", "pilot in production", "mv:M2 pilot")
        self.assertEqual(calls[-1][2], {"milestoneId": "v1"})
        self.assertIn("is now delivered by mv 'M2 pilot'", out.getvalue())
        self.assertIn("neither date was changed", out.getvalue())

    def test_unlink(self):
        routes = {
            ("GET", "/portal/projects/prog/milestones"): _ok([PROG_DEADLINE]),
            ("GET", "/portal/projects/mv/milestones"): _ok([MEMBER_LATE]),
            ("DELETE", "/portal/milestones/pm1/links/v1"): _ok({"unlinked": True}),
        }
        with _env(routes) as (out, _, _c):
            specs_cli.link_milestones("prog", "pm1", "mv:v1", unlink=True)
        self.assertIn("'Pilot in production' unlinked mv 'M2 pilot'", out.getvalue())

    def test_member_deadline_needs_project_and_milestone(self):
        with _env({}) as (_, err, calls):
            with self.assertRaises(SystemExit):
                specs_cli.link_milestones("prog", "pm1", "M2 pilot")
        self.assertEqual(calls, [])
        self.assertIn("<project-id>:<milestone-name-or-id>", err.getvalue())

    def test_link_refusal_is_explained(self):
        routes = {
            ("GET", "/portal/projects/prog/milestones"): _ok([PROG_DEADLINE]),
            ("GET", "/portal/projects/mv/milestones"): _ok([MEMBER_LATE]),
            ("POST", "/portal/milestones/pm1/links"): (409, json.dumps({"error": "not_a_member_deadline"})),
        }
        with _env(routes) as (_, err, _c):
            with self.assertRaises(SystemExit):
                specs_cli.link_milestones("prog", "pm1", "mv:v1")
        self.assertIn("not in one of the programme's member projects", err.getvalue())


if __name__ == "__main__":
    unittest.main()
