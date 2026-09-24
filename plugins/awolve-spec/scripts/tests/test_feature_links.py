"""Unit tests for item → feature links in the CLI.

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


class SlugifyTitleTest(unittest.TestCase):
    def test_nordic_letters_are_transliterated_not_dropped(self):
        # The case an older slugifier turned into `beskrivningsf-lt-f-r-sektioner`.
        self.assertEqual(specs_cli._slugify_title("Beskrivningsfält för sektioner"), "beskrivningsfalt-for-sektioner")

    def test_o_slash_and_ae_survive(self):
        # Neither is an accented form of anything, so a plain accent-strip drops them.
        self.assertEqual(specs_cli._slugify_title("Kvinnor på Æbleø — søknad"), "kvinnor-pa-aebleo-soknad")

    def test_other_accents_are_stripped(self):
        self.assertEqual(specs_cli._slugify_title("Café résumé"), "cafe-resume")

    def test_punctuation_collapses_to_single_hyphens(self):
        self.assertEqual(specs_cli._slugify_title("Feature ↔ Item Links"), "feature-item-links")

    def test_long_titles_are_cut_at_a_word_boundary(self):
        slug = specs_cli._slugify_title("one two three four five six seven eight nine ten eleven twelve")
        self.assertLessEqual(len(slug), 50)
        self.assertFalse(slug.endswith("-"))
        self.assertTrue(all(w in "one two three four five six seven eight nine ten eleven twelve".split() for w in slug.split("-")))

    def test_a_title_with_no_letters_gives_nothing(self):
        self.assertEqual(specs_cli._slugify_title("!!!"), "")


class FeatureRefTest(unittest.TestCase):
    def test_unlinked_item_renders_nothing(self):
        self.assertIsNone(specs_cli._feature_ref({"featureId": None}))
        self.assertIsNone(specs_cli._feature_line({}))

    def test_same_project_shows_only_the_number(self):
        item = {"featureId": "signum/046-links", "featureNumber": 46, "projectId": "signum"}
        self.assertEqual(specs_cli._feature_ref(item), "#46")

    def test_other_project_is_named(self):
        item = {"featureId": "web-app/036-thing", "featureNumber": 36, "projectId": "api-service"}
        self.assertEqual(specs_cli._feature_ref(item), "web-app #36")

    def test_falls_back_to_the_name_without_a_number(self):
        # Older services return only featureId on list rows.
        self.assertEqual(specs_cli._feature_ref({"featureId": "signum/046-links"}), "046-links")

    def test_view_line_labels_the_status_as_the_features(self):
        item = {"featureId": "signum/046-links", "featureNumber": 46, "featureTitle": "Links",
                "featureStatus": "in_progress", "projectId": "signum", "status": "idea"}
        self.assertEqual(specs_cli._feature_line(item), "#46 Links [in_progress]")


class StageSummaryTest(unittest.TestCase):
    def test_no_items_is_nothing(self):
        self.assertIsNone(specs_cli._stage_summary([]))

    def test_items_without_stages_are_a_bare_count(self):
        self.assertEqual(specs_cli._stage_summary([{}, {}]), "2 items")

    def test_singular(self):
        self.assertEqual(specs_cli._stage_summary([{"deployedStage": "staging"}]), "1 item · 1 staging")

    def test_ordered_by_count_then_name(self):
        items = [{"deployedStage": s} for s in ("preview", "staging", "staging", "production")]
        self.assertEqual(specs_cli._stage_summary(items), "4 items · 2 staging, 1 preview, 1 production")


class CheckFeatureTookTest(unittest.TestCase):
    def _run(self, body, requested):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            try:
                specs_cli._check_feature_took(json.dumps(body), requested)
                return None, err.getvalue()
            except SystemExit as e:
                return e.code, err.getvalue()

    def test_a_bare_name_matches_the_stored_project_qualified_id(self):
        code, _ = self._run({"featureId": "signum/046-links"}, "046-links")
        self.assertIsNone(code)

    def test_a_qualified_name_matches_exactly(self):
        code, _ = self._run({"featureId": "web-app/036-thing"}, "web-app/036-thing")
        self.assertIsNone(code)

    def test_clearing_expects_null(self):
        code, _ = self._run({"featureId": None}, None)
        self.assertIsNone(code)

    def test_an_old_service_that_drops_the_field_is_caught(self):
        # 200 OK, but the value never landed — the silent drop this guards against.
        code, err = self._run({"featureId": None, "title": "x"}, "046-links")
        self.assertEqual(code, 1)
        self.assertIn("does not support item→feature links", err)

    def test_a_clear_that_did_not_take_is_caught(self):
        code, _ = self._run({"featureId": "signum/046-links"}, None)
        self.assertEqual(code, 1)


class FromItemRefusalsTest(unittest.TestCase):
    def _run(self, item):
        err = io.StringIO()
        with mock.patch.object(specs_cli.config, "read_config", return_value={"service_url": "https://specs.example.com", "projects": [{"id": "p", "path": "/tmp/none"}]}), \
             mock.patch.object(specs_cli.auth, "get_headers", return_value={"Authorization": "Bearer x"}), \
             mock.patch.object(specs_cli, "_resolve_backlog_id", return_value=("uuid", item)), \
             mock.patch.object(specs_cli, "create_feature") as create, \
             contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit):
                specs_cli.create_feature_from_item("p", "7")
        return err.getvalue(), create

    def test_an_epic_is_refused_before_anything_is_created(self):
        err, create = self._run({"number": 7, "isEpic": True, "title": "Big theme"})
        self.assertIn("is an epic", err)
        create.assert_not_called()

    def test_an_already_linked_item_is_refused_and_told_how_to_move_it(self):
        err, create = self._run({"number": 7, "featureId": "p/003-other", "title": "x"})
        self.assertIn("already delivers p/003-other", err)
        self.assertIn("--feature", err)
        create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
