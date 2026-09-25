"""Offline tests for the version parsing in update_plugin.py."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "skills", "team-workflow", "scripts"))
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


if __name__ == "__main__":
    unittest.main()
