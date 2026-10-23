"""Offline tests for the add-on manager (no network, no real apps)."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

from test_scripts import SCRIPTS

sys.path.insert(0, SCRIPTS)
import addons  # noqa: E402
import settings  # noqa: E402


class AddonsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = tmp.name
        patcher = mock.patch.dict(os.environ, {"HOME": self.home, "USERPROFILE": self.home})
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, rel, text):
        path = os.path.join(self.home, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_resolves_catalog_names_and_marketplace_ids(self):
        name, entry = addons.resolve("ponytail")
        self.assertEqual((name, entry["agy"]), ("ponytail", "plugin"))
        name, entry = addons.resolve("code-review@claude-plugins-official")
        self.assertEqual((name, entry["marketplace"], entry["agy"]),
                         ("code-review", "claude-plugins-official", "plugin@marketplace"))
        with self.assertRaises(ValueError):
            addons.resolve("not a spec!")

    def test_claude_adds_an_unknown_marketplace_then_installs(self):
        entry = addons.CATALOG["caveman"]
        self.assertEqual(addons.claude_steps("add", entry), [
            ("claude", "plugin", "marketplace", "add", "JuliusBrussee/caveman"),
            ("claude", "plugin", "install", "caveman@caveman")])
        self.write(".claude/plugins/known_marketplaces.json", json.dumps({"caveman": {}}))
        self.assertEqual(addons.claude_steps("update", entry)[0],
                         ("claude", "plugin", "marketplace", "update", "caveman"))
        self.assertEqual(addons.claude_steps("remove", entry),
                         [("claude", "plugin", "uninstall", "caveman@caveman")])
        self.write(".claude/plugins/installed_plugins.json",
                   json.dumps({"plugins": {"caveman@caveman": [{"version": "3.1.0"}]}}))
        self.assertEqual(addons.claude_version(entry), "3.1.0")

    def test_agy_skills_are_copied_marked_and_only_ours_removed(self):
        clone = addons.clone_dir("caveman")
        for skill in ("caveman", "caveman-commit", "taken"):
            self.write(os.path.join(clone, "skills", skill, "SKILL.md"), f"---\nname: {skill}\n---\n")
        os.makedirs(os.path.join(clone, ".git"))
        self.write(os.path.join(clone, "skills", "notes.md"), "not a skill folder")
        foreign = self.write(".gemini/config/skills/taken/SKILL.md", "someone else's")
        with mock.patch.object(addons, "run", return_value=(True, "")):
            ok, log = addons.copy_skills("caveman", addons.CATALOG["caveman"])
        self.assertTrue(ok, log)
        self.assertEqual(addons.agy_skill_dirs("caveman"), ["caveman", "caveman-commit"])
        self.assertIn("skipped, not ours: taken", log)
        addons.agy_apply("remove", "caveman", addons.CATALOG["caveman"], None)
        self.assertEqual(addons.agy_skill_dirs("caveman"), [])
        self.assertTrue(os.path.isfile(foreign))

    def test_chosen_addons_are_saved_and_removed(self):
        with mock.patch.object(addons.shutil, "which", return_value=None):
            addons.apply("add", "ponytail")
            self.assertIn("ponytail", addons.chosen())
            self.assertIn("addons=ponytail", settings.summary(settings.load()))
            addons.apply("remove", "ponytail")
        self.assertNotIn("ponytail", addons.chosen())


if __name__ == "__main__":
    unittest.main()
