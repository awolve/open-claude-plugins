"""Unit tests for backlog-add output: the created item's portal link.

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


class BacklogAddOutputTest(unittest.TestCase):
    def _run(self, response, **kwargs):
        out = io.StringIO()
        with mock.patch.object(specs_cli.config, "read_config", return_value={"service_url": SERVICE_URL}), \
             mock.patch.object(specs_cli.auth, "get_headers", return_value={"Authorization": "Bearer x"}), \
             mock.patch.object(specs_cli, "api_request", return_value=(201, json.dumps(response))) as api, \
             contextlib.redirect_stdout(out):
            specs_cli.create_backlog_item("my-project", "Improve onboarding", priority="high", **kwargs)
        return out.getvalue().splitlines(), api

    def test_prints_portal_link_by_number(self):
        lines, _ = self._run({"id": "b1f0c2d4-uuid", "number": 42, "title": "Improve onboarding", "priority": "high"})
        self.assertEqual(lines, [
            "Signum: created backlog item 'Improve onboarding' in 'my-project' (priority: high)",
            f"  portal: {SERVICE_URL}/portal/my-project/backlog/42",
        ])

    def test_epic_gets_the_same_link(self):
        lines, api = self._run({"id": "e-uuid", "number": 7, "title": "Improve onboarding", "priority": "high", "isEpic": True}, is_epic=True)
        self.assertEqual(lines, [
            "Signum: created epic 'Improve onboarding' in 'my-project' (priority: high)",
            f"  portal: {SERVICE_URL}/portal/my-project/backlog/7",
        ])
        self.assertTrue(api.call_args.kwargs["data"]["isEpic"])

    def test_no_number_means_no_link(self):
        lines, _ = self._run({"id": "b1f0c2d4-uuid", "title": "Improve onboarding", "priority": "high"})
        self.assertEqual(lines, [
            "Signum: created backlog item 'Improve onboarding' in 'my-project' (priority: high)",
        ])


if __name__ == "__main__":
    unittest.main()
