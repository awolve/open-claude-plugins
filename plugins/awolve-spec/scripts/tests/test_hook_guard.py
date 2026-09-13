"""Unit tests for the hook guard: the older plugin name stands down when the newer one is enabled.

Run from the scripts dir:  python3 -m unittest discover -s tests
"""

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

KEY = "awolve-signum@awolve-open-claude-plugins"


class HookGuardTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="guard-home-")
        self.project = tempfile.mkdtemp(prefix="guard-proj-")
        self._prev_home = os.environ.get("HOME")
        os.environ["HOME"] = self.home

    def tearDown(self):
        if self._prev_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = self._prev_home
        shutil.rmtree(self.home, ignore_errors=True)
        shutil.rmtree(self.project, ignore_errors=True)

    def _write(self, base, name, plugins):
        d = os.path.join(base, ".claude")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            json.dump({"enabledPlugins": plugins}, f)

    def test_nothing_configured_means_not_enabled(self):
        self.assertFalse(specs_cli._plugin_enabled(KEY, self.project))

    def test_user_scope_enables(self):
        self._write(self.home, "settings.json", {KEY: True})
        self.assertTrue(specs_cli._plugin_enabled(KEY, self.project))

    def test_project_local_overrides_user(self):
        self._write(self.home, "settings.json", {KEY: True})
        self._write(self.project, "settings.local.json", {KEY: False})
        self.assertFalse(specs_cli._plugin_enabled(KEY, self.project))

    def test_project_enables_when_user_does_not(self):
        self._write(self.project, "settings.json", {KEY: True})
        self.assertTrue(specs_cli._plugin_enabled(KEY, self.project))

    def test_broken_settings_file_is_ignored(self):
        d = os.path.join(self.home, ".claude")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "settings.json"), "w", encoding="utf-8") as f:
            f.write("{not json")
        self.assertFalse(specs_cli._plugin_enabled(KEY, self.project))

    def test_older_name_stands_down_when_newer_enabled(self):
        self._write(self.home, "settings.json", {KEY: True})
        self.assertTrue(specs_cli._hooks_belong_to_successor(self.project, plugin_name="awolve-spec"))

    def test_older_name_runs_when_newer_not_enabled(self):
        self.assertFalse(specs_cli._hooks_belong_to_successor(self.project, plugin_name="awolve-spec"))

    def test_newer_name_always_runs(self):
        self._write(self.home, "settings.json", {KEY: True})
        self.assertFalse(specs_cli._hooks_belong_to_successor(self.project, plugin_name="awolve-signum"))


if __name__ == "__main__":
    unittest.main()
