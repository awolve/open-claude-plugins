"""Unit tests for the X-Signum-Client header: every call names this plugin and its version.

Run from the scripts dir:  python3 -m unittest discover -s tests
"""

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

MANIFEST = os.path.join(os.path.dirname(SCRIPTS_DIR), ".claude-plugin", "plugin.json")


def manifest():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


class _Response(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ClientHeaderTest(unittest.TestCase):
    def test_signum_client_is_name_and_version_from_the_manifest(self):
        m = manifest()
        self.assertEqual(specs_cli.signum_client(), f"{m['name']}/{m['version']}")

    def test_api_request_sends_the_header(self):
        sent = []

        def fake_urlopen(req, timeout=None):
            sent.append(req)
            return _Response(b"{}")

        with mock.patch.object(specs_cli.urllib.request, "urlopen", side_effect=fake_urlopen):
            status, _ = specs_cli.api_request("https://specs.example.com/api/x", headers={"Authorization": "Bearer t"})

        self.assertEqual(status, 200)
        headers = {k.lower(): v for k, v in sent[0].header_items()}
        self.assertEqual(headers["x-signum-client"], specs_cli.signum_client())
        self.assertEqual(headers["user-agent"], specs_cli.signum_client())
        self.assertEqual(headers["authorization"], "Bearer t")

    def test_the_callers_headers_are_not_changed(self):
        mine = {"Authorization": "Bearer t"}
        with mock.patch.object(specs_cli.urllib.request, "urlopen", return_value=_Response(b"{}")):
            specs_cli.api_request("https://specs.example.com/api/x", method="POST", headers=mine, data={"a": 1})
        self.assertEqual(mine, {"Authorization": "Bearer t"})

    def test_a_given_header_wins(self):
        self.assertEqual(specs_cli.with_client_header({"X-Signum-Client": "other/1"})["X-Signum-Client"], "other/1")

    def test_a_missing_manifest_still_sends_a_name(self):
        with mock.patch.object(specs_cli, "_plugin_name", return_value=""), \
             mock.patch.object(specs_cli, "_plugin_version", return_value="unknown"):
            self.assertEqual(specs_cli.signum_client(), "awolve-signum/unknown")


if __name__ == "__main__":
    unittest.main()
