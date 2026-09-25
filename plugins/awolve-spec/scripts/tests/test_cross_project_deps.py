"""Unit tests for dependencies across projects in the CLI.

Run from the scripts dir:  python3 -m unittest discover -s tests
"""

import importlib.util
import os
import unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("specs_cli", os.path.join(SCRIPTS_DIR, "specs-cli.py"))
specs_cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(specs_cli)


class SplitCrossRefTest(unittest.TestCase):
    def test_other_project(self):
        self.assertEqual(specs_cli._split_cross_ref("web", "api#12"), ("api", "#12"))
        self.assertEqual(specs_cli._split_cross_ref("web", "Data-Platform#7"), ("data-platform", "#7"))

    def test_home_forms_stay_home(self):
        self.assertEqual(specs_cli._split_cross_ref("web", "#12"), ("web", "#12"))
        self.assertEqual(specs_cli._split_cross_ref("web", "12"), ("web", "12"))
        uuid = "3f2a1b4c-0000-4000-8000-000000000000"
        self.assertEqual(specs_cli._split_cross_ref("web", uuid), ("web", uuid))


class DepLabelTest(unittest.TestCase):
    def test_home_item(self):
        d = {"restricted": False, "projectId": "web", "number": 41, "title": "Import rounding"}
        self.assertEqual(specs_cli._dep_label(d, "web"), "#41 Import rounding")

    def test_item_elsewhere(self):
        d = {"restricted": False, "projectId": "api", "number": 12, "title": "Expose tiers"}
        self.assertEqual(specs_cli._dep_label(d, "web"), "api#12 Expose tiers")
        self.assertEqual(specs_cli._dep_ref(d, "web"), "api#12")

    def test_item_you_cannot_read(self):
        d = {"restricted": True, "projectId": "api", "projectName": "API", "status": "planned"}
        self.assertEqual(specs_cli._dep_label(d, "web"), "(an item in API)")

    def test_old_service_response_without_project(self):
        # A service from before cross-project links sends no projectId.
        d = {"id": "x", "number": 9, "title": "Old shape", "status": "planned"}
        self.assertEqual(specs_cli._dep_label(d, "web"), "#9 Old shape")


if __name__ == "__main__":
    unittest.main()
