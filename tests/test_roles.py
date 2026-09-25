"""Offline tests for the modular roles: packs, overrides and the native files of both apps."""
import os
import sys
import tempfile
import unittest
from unittest import mock

from test_scripts import SCRIPTS

sys.path.insert(0, SCRIPTS)
import roles  # noqa: E402
import settings  # noqa: E402


class RolesTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = tmp.name
        patcher = mock.patch.dict(os.environ, {"HOME": self.home})
        patcher.start()
        self.addCleanup(patcher.stop)

    def native(self, app, role):
        path = os.path.join(roles.native_dir(app), role + ".md")
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return roles.parse(f.read())

    def test_claude_agents_carry_model_and_only_a_valid_effort(self):
        roles.sync("claude")
        meta, body = self.native("claude", "architect")
        self.assertEqual((meta["model"], meta["effort"]), ("opus", "high"))
        self.assertEqual(meta["tools"], '["Read", "Grep", "Glob"]')
        self.assertIn(roles.MARK, body)
        meta, _ = self.native("claude", "doc-keeper")
        self.assertEqual(meta["model"], "haiku")
        self.assertNotIn("effort", meta)  # haiku has no effort

    def test_settings_switch_type_model_and_packs(self):
        settings.save("models.claude.tester", "fable")
        settings.save("effort.tester", "xhigh")
        settings.save("type.agy.tester", "research")
        settings.save("enabled.data-analyst", False)
        for app in roles.APPS:
            roles.sync(app)
        self.assertEqual(self.native("claude", "tester")[0]["effort"], "xhigh")
        self.assertIsNone(self.native("agy", "tester"))  # a built-in type: no custom file
        self.assertIsNone(self.native("claude", "data-analyst"))
        settings.save("packs.core", False)
        self.assertEqual(len(roles.sync("claude")["removed"]), 19)

    def test_user_roles_override_and_extend(self):
        path = roles.new_role("tester")  # override starts from the plugin's text
        with open(path, "a", encoding="utf-8") as f:
            f.write("\nAlways run the slow suite too.\n")
        roles.new_role("api-designer")
        catalog = roles.catalog()
        self.assertEqual((catalog["tester"]["origin"], catalog["tester"]["pack"]), ("user", "core"))
        self.assertEqual(catalog["api-designer"]["pack"], "custom")
        roles.sync("claude")
        self.assertIn("slow suite", self.native("claude", "tester")[1])
        self.assertIsNotNone(self.native("claude", "api-designer"))
        with self.assertRaises(ValueError):
            roles.new_role("Bad Name")

    def test_foreign_files_are_left_alone_and_stale_ones_removed(self):
        dest = roles.native_dir("claude")
        os.makedirs(dest)
        with open(os.path.join(dest, "tester.md"), "w") as f:
            f.write("---\nname: tester\n---\nmine\n")
        with open(os.path.join(dest, "gone.md"), "w") as f:
            f.write(f"---\nname: gone\n---\n{roles.MARK}\n")
        result = roles.sync("claude")
        self.assertIn("tester", result["skipped"])
        self.assertIn("gone", result["removed"])
        with open(os.path.join(dest, "tester.md")) as f:
            self.assertIn("mine", f.read())

    def test_language_packs_expand_detect_and_switch_on(self):
        catalog = roles.catalog()
        langs = roles.languages()
        self.assertGreaterEqual(len(langs), 10)
        for slug in langs:
            for kind in ("reviewer", "build-fixer"):
                meta, body = roles.parse(roles.read(catalog[f"{slug}-{kind}"]))
                self.assertNotRegex(meta["description"] + body,
                                    r"\{(language|files|focus|triggers|checklist|build|tools)\}")
                self.assertTrue(roles.sections(body).get("Tools"), slug)
        meta, body = roles.load("go-reviewer")
        self.assertIn("Go changes", meta["description"])
        self.assertIn("errors.Is/As", body)
        repo = os.path.join(self.home, "repo")
        os.makedirs(os.path.join(repo, "web"))
        open(os.path.join(repo, "go.mod"), "w").close()
        open(os.path.join(repo, "web", "package.json"), "w").close()
        self.assertEqual(roles.detect(repo), ["go", "typescript"])
        self.assertIsNone(roles.sync("claude") and self.native("claude", "go-reviewer"))
        settings.save("packs.go", True)
        roles.sync("claude")
        self.assertIsNotNone(self.native("claude", "go-build-fixer"))


if __name__ == "__main__":
    unittest.main()
