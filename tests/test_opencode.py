"""Offline tests for OpenCode support: agents, installer, plugin, workers, usage, add-ons,
and the options the session wizard offers."""
import json
import os
import sqlite3
import sys
import unittest
from unittest import mock

from test_scripts import SCRIPTS, ScriptTest

sys.path.insert(0, SCRIPTS)
import addons  # noqa: E402
import install_opencode  # noqa: E402
import roles  # noqa: E402
import run_worker  # noqa: E402
import settings  # noqa: E402
import usage  # noqa: E402


class OpenCodeTest(ScriptTest):
    def setUp(self):
        super().setUp()
        patcher = mock.patch.dict(os.environ, {"HOME": self.tmp})
        patcher.start()
        self.addCleanup(patcher.stop)

    def conf(self, *parts):
        return os.path.join(self.tmp, ".config", "opencode", *parts)

    def test_roles_become_opencode_subagents(self):
        settings.save("models.opencode.tester", "anthropic/claude-sonnet-5")
        roles.sync("opencode")
        meta, body = roles.parse(open(self.conf("agents", "architect.md")).read())
        self.assertEqual((meta["mode"], meta["variant"], meta["color"]), ("subagent", "high", "#3E63DD"))
        self.assertNotIn("model", meta)  # inherit: the calling agent's model
        text = open(self.conf("agents", "architect.md")).read()
        self.assertIn("permission:\n  edit: deny\n  bash: deny\n  webfetch: deny", text)
        meta, _ = roles.parse(open(self.conf("agents", "tester.md")).read())
        self.assertEqual(meta["model"], "anthropic/claude-sonnet-5")
        self.assertNotIn("variant", meta)  # medium: no variant
        with self.assertRaises(ValueError):
            settings.parse_value("models.opencode.tester", "sonnet")

    def test_installer_writes_commands_plugin_agents_and_uninstalls_only_ours(self):
        mine = self.conf("commands", "deploy.md")
        os.makedirs(os.path.dirname(mine))
        open(mine, "w").write("my command\n")
        result = install_opencode.install()
        commands = sorted(os.listdir(self.conf("commands")))
        self.assertIn("team-workflow:call-team.md", commands)
        self.assertEqual(result["commands"], len(commands) - 1)
        body = open(self.conf("commands", "team-workflow:usage-costs.md")).read()
        self.assertIn(self.conf("skills", "team-workflow", "scripts", "dashboard.py"), body)
        js = open(self.conf("plugins", "team-workflow.js")).read()
        self.assertIn(self.conf("skills", "team-workflow", "scripts"), js)
        self.assertNotIn("__SCRIPTS__", js)
        self.assertTrue(os.path.isfile(self.conf("skills", "team-workflow", "SKILL.md")))
        self.assertEqual(install_opencode.installed_source(), install_opencode.REPO)
        self.assertEqual(len(result["agents"]), 20)
        install_opencode.uninstall()
        self.assertEqual(os.listdir(self.conf("commands")), ["deploy.md"])
        self.assertFalse(os.path.exists(self.conf("plugins", "team-workflow.js")))
        self.assertEqual(os.listdir(self.conf("agents")), [])

    def test_worker_command_and_usage_from_events(self):
        cmd = run_worker.build_command("opencode", "openai/gpt-6", "high", "brief", False)
        self.assertEqual(cmd[1:9], ["run", "--format", "json", "-m", "openai/gpt-6", "--agent", "plan",
                                    "--variant"])
        self.assertNotIn("--auto", cmd)
        self.assertIn("--auto", run_worker.build_command("opencode", "m/x", "", "b", True))
        events = run_worker.opencode_events("\n".join(json.dumps(e) for e in [
            {"type": "step_start", "sessionID": "ses_1"},
            {"type": "text", "part": {"text": "done"}},
            {"type": "step_finish", "part": {"cost": 0.01, "tokens": {"input": 10, "output": 5, "reasoning": 2,
                                                                      "cache": {"read": 100, "write": 20}}}},
            {"type": "step_finish", "part": {"tokens": {"input": 1, "output": 1, "reasoning": 0, "cache": {}}}}]))
        usage_, text, session, cost, ok, _ = run_worker.normalize("opencode", events)
        self.assertEqual((usage_["input"], usage_["output"], usage_["cache_read"], usage_["calls"]), (11, 8, 100, 2))
        self.assertEqual((text, session, cost, ok), ("done", "ses_1", 0.01, True))

    def test_usage_reads_the_opencode_store_for_this_repository(self):
        path = usage.opencode_db()
        os.makedirs(os.path.dirname(path))
        db = sqlite3.connect(path)
        db.execute("create table session (id text, parent_id text, directory text)")
        db.execute("create table message (session_id text, time_created int, data text)")
        db.executemany("insert into session values (?, ?, ?)", [
            ("s1", None, self.root), ("s2", "s1", self.root), ("s3", None, "/elsewhere")])
        msg = lambda agent, n: json.dumps({"role": "assistant", "agent": agent, "providerID": "anthropic",
                                           "modelID": "claude-sonnet-5", "cost": 0.5,
                                           "tokens": {"input": n, "output": 1, "reasoning": 1, "cache": {"read": 2}}})
        db.executemany("insert into message values (?, ?, ?)", [
            ("s1", 1_790_000_000_000, msg("build", 10)), ("s2", 1_790_000_000_500, msg("tester", 20)),
            ("s3", 1_790_000_000_000, msg("build", 99)), ("s1", 1_790_000_000_900, json.dumps({"role": "user"}))])
        db.commit()
        rows = {(r["agent"], r["session"]): r for r in usage.opencode_runs(self.root)}
        self.assertEqual(set(rows), {("main", "s1"), ("tester", "s1")})
        self.assertEqual((rows[("tester", "s1")]["input"], rows[("tester", "s1")]["output"]), (20, 2))
        self.assertAlmostEqual(usage.cost_usd(rows[("main", "s1")], "anthropic/claude-sonnet-5",
                                              usage.load_pricing()), 10 * 2e-6 + 2 * 10e-6 + 2 * 2e-7)

    def test_addons_list_a_plugin_file_in_opencode_json(self):
        clone = addons.clone_dir("ponytail")
        os.makedirs(os.path.join(clone, ".git"))
        os.makedirs(os.path.join(clone, ".opencode", "plugins"))
        open(os.path.join(clone, ".opencode", "plugins", "ponytail.mjs"), "w").write("export {}")
        os.makedirs(self.conf())
        json.dump({"$schema": "x", "model": "a/b"}, open(self.conf("opencode.json"), "w"))
        with mock.patch.object(addons, "run", return_value=(True, "")):
            ok, log = addons.opencode_apply("add", "ponytail", addons.CATALOG["ponytail"], None)
        self.assertTrue(ok, log)
        data = json.load(open(self.conf("opencode.json")))
        self.assertEqual(data["model"], "a/b")
        self.assertEqual(data["plugin"], [os.path.join(clone, ".opencode", "plugins", "ponytail.mjs")])
        self.assertEqual(addons.opencode_version("ponytail", addons.CATALOG["ponytail"]), "plugin")
        addons.opencode_apply("remove", "ponytail", addons.CATALOG["ponytail"], None)
        self.assertEqual(json.load(open(self.conf("opencode.json")))["plugin"], [])

    def test_session_wizard_options_and_context(self):
        import tw
        with mock.patch.object(tw.shutil, "which", return_value=None):
            data = tw.app_options("agy", self.root)
        self.assertEqual(data["native"]["models"], ["inherit", "flash", "pro"])
        self.assertEqual(data["roles"]["architect"]["model"], "inherit")
        self.assertIn("thorough", data["presets"])
        self.assertIn("general", tw.app_options("opencode")["types"])
        self.init_memory()
        out = self.run_script("session_start.py", hook={"cwd": self.root, "session_id": "w"},
                              env={"TEAM_WORKFLOW_APP": "opencode"})
        context = json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("session setup is on", context)
        self.assertIn("tw.py options --app opencode", context)
        self.assertIn("task tool", context)


if __name__ == "__main__":
    unittest.main()
