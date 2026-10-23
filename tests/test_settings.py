"""Offline tests for the settings, the no-model commands and the agy subagent files."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import glob
import json
import os
import re
import sys
import tempfile
import unittest
from unittest import mock

from test_scripts import SCRIPTS, ScriptTest

sys.path.insert(0, SCRIPTS)
import install_agy  # noqa: E402
import prompt_command  # noqa: E402
import settings  # noqa: E402

REPO = os.path.normpath(os.path.join(SCRIPTS, "..", "..", ".."))


class SettingsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home, self.root = os.path.join(tmp.name, "home"), os.path.join(tmp.name, "repo")
        os.makedirs(self.root)
        patcher = mock.patch.dict(os.environ, {"HOME": self.home, "USERPROFILE": self.home})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_project_overrides_user_overrides_defaults(self):
        settings.save("wizard", "full")
        settings.save("models.agy.tester", "flash")
        settings.save("wizard", "off", self.root)
        data = settings.load(self.root)
        self.assertEqual(data["wizard"], "off")
        self.assertEqual(settings.load()["wizard"], "full")
        self.assertEqual(settings.role_value(data, "models", "tester", "agy"), "flash")
        self.assertEqual(settings.role_value(data, "models", "backend-dev", "agy"), "inherit")
        self.assertEqual(settings.role_value(data, "effort", "architect"), "high")
        settings.save("wizard", None, self.root)  # reset
        self.assertEqual(settings.load(self.root)["wizard"], "full")
        self.assertIn('wizard="full"', settings.summary(settings.load()))

    def test_values_are_typed_and_checked(self):
        self.assertIs(settings.parse_value("stop_check", "off"), False)
        self.assertEqual(settings.parse_value("max_agents", "6"), 6)
        self.assertEqual(settings.parse_value("models.claude.tester", "opus"), "opus")
        self.assertEqual(settings.parse_value("effort.tester", "max"), "max")
        for key, value in (("wizard", "sometimes"), ("models.agy.tester", "sonnet"),
                           ("effort.tester", "huge"), ("colour", "red"), ("models", "x"),
                           ("stop_check", "maybe")):
            with self.assertRaises(ValueError, msg=key):
                settings.parse_value(key, value)


class NoModelCommandTest(ScriptTest):
    def test_only_our_commands_are_intercepted(self):
        self.assertEqual(prompt_command.tw_args("/team-workflow:settings set wizard full"),
                         ["settings", "set", "wizard", "full"])
        self.assertEqual(prompt_command.tw_args("  /team-workflow:update-plugin check"),
                         ["update", "check"])
        for prompt in ("/team-workflow:setup-memory", "/team-workflow:settingsx",
                       "please /team-workflow:settings", "", None):
            self.assertIsNone(prompt_command.tw_args(prompt), prompt)

    def test_hook_answers_and_blocks_the_prompt(self):
        out = self.run_script("prompt_command.py", hook={
            "prompt": "/team-workflow:settings set wizard full", "cwd": self.root})
        answer = json.loads(out.stdout)
        self.assertEqual(answer["decision"], "block")
        self.assertIn("wizard", answer["reason"])
        with open(os.path.join(self.tmp, ".team-workflow", "settings.json")) as f:
            self.assertEqual(json.load(f)["wizard"], "full")
        passed = self.run_script("prompt_command.py", hook={"prompt": "fix the bug", "cwd": self.root})
        self.assertEqual(passed.stdout.strip(), "")

    def test_stop_check_setting_turns_the_reminder_off(self):
        self.init_memory()
        self.git("add", "-A")
        self.git("commit", "-qm", "memory")
        hook = {"cwd": self.root, "session_id": "s-off"}
        self.run_script("session_start.py", hook=hook)
        self.write("src/app.py", "print(1)\n")
        self.run_script("tw.py", "settings", "set", "stop_check", "false")
        self.assertEqual(self.run_script("stop_check.py", hook=hook).stdout.strip(), "")

    def test_session_context_carries_the_settings(self):
        self.init_memory()
        self.run_script("tw.py", "settings", "set", "wizard", "full")
        out = self.run_script("session_start.py", hook={"cwd": self.root, "session_id": "s-set"})
        context = json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn('team-workflow settings: wizard="full"', context)


class FirstSessionTest(ScriptTest):
    def test_first_session_writes_agents_and_asks_for_a_restart(self):
        self.init_memory()
        hook = {"cwd": self.root, "session_id": "first"}
        first = json.loads(self.run_script("session_start.py", hook=hook).stdout)
        self.assertIn("restart Claude Code", first["systemMessage"])
        self.assertIn("general-purpose", first["hookSpecificOutput"]["additionalContext"])
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, ".claude", "agents", "tester.md")))
        second = json.loads(self.run_script("session_start.py", hook=dict(hook, session_id="second")).stdout)
        self.assertNotIn("systemMessage", second)


class AgySubagentTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"HOME": tmp.name, "USERPROFILE": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_every_role_becomes_a_valid_agy_agent(self):
        with tempfile.TemporaryDirectory() as dest:
            config = settings._merge(settings.DEFAULTS, {"models": {"agy": {"tester": "flash"}}})
            roles = install_agy.sync_agents(dest, config=config)
            self.assertEqual(len(roles), len(glob.glob(os.path.join(REPO, "skills", "team-workflow", "roles", "core", "*.md"))))
            for path in glob.glob(os.path.join(dest, "*.md")):
                with open(path, encoding="utf-8") as f:
                    head = f.read().split("---\n")[1]
                meta = dict(line.split(": ", 1) for line in head.splitlines())
                self.assertEqual(meta["name"], os.path.basename(path)[:-3])
                json.loads(meta["description"])  # quoted: agy drops a bare description with ": "
                self.assertIn(meta["model"], ("inherit", "flash", "pro"))
            with open(os.path.join(dest, "tester.md")) as f:
                self.assertIn("\nmodel: flash\n", f.read())
            with open(os.path.join(dest, "architect.md")) as f:
                text = f.read()
            self.assertIn('tools: ["view_file", "grep_search", "find_by_name", "list_dir"]', text)
            self.assertIn("\nmodel: inherit\n", text)  # the session model: pro is older
            self.assertEqual(install_agy.sync_agents(dest, config=config), [])  # already current

    def test_leaves_a_foreign_agent_alone(self):
        with tempfile.TemporaryDirectory() as dest:
            with open(os.path.join(dest, "tester.md"), "w") as f:
                f.write("---\nname: tester\ndescription: \"mine\"\n---\nMy own tester.\n")
            self.assertNotIn("tester", install_agy.sync_agents(dest))
            with open(os.path.join(dest, "tester.md")) as f:
                self.assertIn("My own tester.", f.read())


class RepositoryTest(unittest.TestCase):
    def read(self, rel):
        with open(os.path.join(REPO, rel), encoding="utf-8") as f:
            return f.read()

    def test_versions_match(self):
        claude = json.loads(self.read(".claude-plugin/plugin.json"))["version"]
        agy = json.loads(self.read("plugin.json"))["version"]
        self.assertEqual(claude, agy)

    def test_every_named_command_exists_with_its_name(self):
        text = self.read("README.md") + self.read("skills/team-workflow/SKILL.md")
        for name in set(re.findall(r"/team-workflow:([a-z-]+)", text)):
            path = os.path.join(REPO, "skills", name, "SKILL.md")
            self.assertTrue(os.path.isfile(path), f"/team-workflow:{name} has no skill")
        for path in glob.glob(os.path.join(REPO, "skills", "*", "SKILL.md")):
            with open(path, encoding="utf-8") as f:
                self.assertIn(f"\nname: {os.path.basename(os.path.dirname(path))}\n", f.read())


if __name__ == "__main__":
    unittest.main()
