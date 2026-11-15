"""Offline tests for the version parsing in update_plugin.py."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "skills", "team", "scripts"))
import update_plugin  # noqa: E402


class UpdateTest(unittest.TestCase):
    def test_latest_tag_compares_numbers_not_text(self):
        out = "a\trefs/tags/v0.9.0\nb\trefs/tags/v0.10.0\nc\trefs/tags/v0.4.0-rc1\nd\trefs/tags/other\n"
        self.assertEqual(update_plugin.latest_tag(out), "0.10.0")
        self.assertIsNone(update_plugin.latest_tag(""))

    def test_claude_version_from_plugin_list(self):
        out = "  ❯ other@x\n    Version: 9.9.9\n  ❯ team-workflow@team-workflow\n    Version: 0.3.1\n"
        self.assertEqual(update_plugin.claude_version(out), "0.3.1")
        self.assertIsNone(update_plugin.claude_version("  ❯ other@x\n    Version: 1.0.0\n"))

    def test_update_targets_the_installed_plugin_id(self):
        legacy = "  ❯ team-workflow@team-workflow\n    Version: 2.3.0\n"
        current = "  ❯ team@team\n    Version: 2.4.0\n"
        self.assertEqual(update_plugin.claude_ids(legacy), ("team-workflow", "team-workflow@team-workflow"))
        self.assertEqual(update_plugin.claude_ids(current), ("team", "team@team"))
        self.assertEqual(update_plugin.claude_ids(legacy + current), ("team", "team@team"))
        self.assertEqual(update_plugin.claude_ids(""), ("team", "team@team"))  # not installed yet


if __name__ == "__main__":
    unittest.main()
