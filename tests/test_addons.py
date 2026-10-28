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

    def test_frontend_bundle_copies_skills_from_their_folder_also_into_claude(self):
        for name, folder in (("impeccable", ".agents/skills/impeccable"), ("solar-icons", "skills/solar-icons")):
            clone = addons.clone_dir(name)
            self.write(os.path.join(clone, *folder.split("/"), "SKILL.md"), f"---\nname: {name}\n---\n")
            os.makedirs(os.path.join(clone, ".git"), exist_ok=True)
        with mock.patch.object(addons, "run", return_value=(True, "")):
            ok, log = addons.copy_skills("impeccable", addons.CATALOG["impeccable"])  # .agents/skills
        self.assertTrue(ok, log)
        self.assertEqual(addons.agy_skill_dirs("impeccable"), ["impeccable"])
        present = lambda app: app == "claude"  # noqa: E731
        with mock.patch.object(addons, "run", return_value=(True, "")), \
                mock.patch.object(addons, "present", present):
            ok, log = addons.apply("add", "solar-icons", ("claude",))
            self.assertTrue(ok, log)  # no marketplace: copied as skills, no `claude plugin`
            self.assertNotIn("claude plugin", log)
            self.assertEqual(addons.claude_version(addons.CATALOG["solar-icons"], "solar-icons"), "skills")
            ok, log = addons.apply("remove", "solar-icons", ("claude",))
        self.assertFalse(os.path.exists(os.path.join(addons.claude_skills_dir(), "solar-icons")))
        with mock.patch.object(addons, "apply", wraps=addons.apply) as spy, \
                mock.patch.object(addons, "present", return_value=False):
            ok, log = addons.apply("add", "frontend")
        self.assertEqual([c.args[1] for c in spy.call_args_list[1:]], list(addons.BUNDLES["frontend"]))
        self.assertEqual(set(addons.BUNDLES["frontend"]) - set(addons.chosen()), set())


class McpTest(unittest.TestCase):
    setUp, write = AddonsTest.setUp, AddonsTest.write  # same throwaway home, without its tests

    def test_mcp_servers_are_written_per_app_and_foreign_ones_left_alone(self):
        entry = addons.CATALOG["serena"]
        ok, log = addons.mcp_apply("opencode", "add", "serena", entry)
        self.assertTrue(ok, log)
        with open(addons.opencode_config_path(), encoding="utf-8") as f:
            server = json.load(f)["mcp"]["serena"]
        self.assertEqual((server["type"], server["command"][0]), ("local", "uvx"))
        self.assertNotIn("claude-code", server["command"])  # Claude-only arguments stay out
        addons.mcp_apply("agy", "add", "serena", entry)
        self.assertEqual(addons.mcp_servers("agy")["serena"]["command"], "uvx")
        self.assertEqual(addons.agy_version("serena", entry), "mcp")
        with mock.patch.object(addons, "run", return_value=(True, "")) as run:
            addons.mcp_apply("claude", "add", "serena", entry)
        self.assertIn("claude-code", run.call_args.args)
        self.write(".config/opencode/opencode.json", json.dumps({"mcp": {"playwright": {"mine": 1}}}))
        ok, log = addons.mcp_apply("opencode", "add", "playwright", addons.CATALOG["playwright"])
        self.assertIn("left as it is", log)
        self.assertEqual(addons.mcp_servers("opencode")["playwright"], {"mine": 1})
        addons.mcp_apply("agy", "remove", "serena", entry)
        self.assertNotIn("serena", addons.mcp_servers("agy"))

    def test_bundles_name_only_catalog_entries(self):
        for names in addons.BUNDLES.values():
            self.assertFalse(set(names) - set(addons.CATALOG))
        self.assertFalse(set(addons.BUNDLES) & set(addons.CATALOG))


if __name__ == "__main__":
    unittest.main()
