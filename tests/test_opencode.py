"""Offline tests for OpenCode support: agents, installer, plugin, workers, usage, add-ons,
and the options the session wizard offers."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import io
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
import opencode_cli  # noqa: E402
import roles  # noqa: E402
import run_worker  # noqa: E402
import settings  # noqa: E402
import usage  # noqa: E402

PYTHON_COMMAND = opencode_cli.python_command  # before the tests replace it

# what `opencode api GET /api/model` and `/api/provider` answer in OpenCode 2.x
API_MODELS = {"data": [
    {"id": "z-ai/glm-5.3", "providerID": "nano-gpt", "name": "GLM 5.3", "status": "active", "enabled": True,
     "variants": [{"id": "low"}, {"id": "high"}, {"id": "max"}]},
    {"id": "z-ai/glm-5.3-flash", "providerID": "nano-gpt", "name": "GLM 5.3 Flash", "enabled": True,
     "variants": [{"id": "low"}, {"id": "high"}]},
    {"id": "old-model", "providerID": "nano-gpt", "name": "Old", "enabled": False},
    {"id": "glm-5.3-flash-free", "providerID": "opencode", "name": "GLM-5.3-Flash Free", "variants": []}]}
API_PROVIDERS = {"data": [{"id": "nano-gpt", "name": "NanoGPT"}, {"id": "opencode", "name": "OpenCode"}]}


class OpenCodeTest(ScriptTest):
    def setUp(self):
        super().setUp()
        for patcher in (mock.patch.dict(os.environ, {"HOME": self.tmp, "USERPROFILE": self.tmp}),
                        # no real OpenCode: the tests say which version and Python there is
                        mock.patch.object(opencode_cli, "binary", return_value=None),
                        mock.patch.object(opencode_cli, "python_command", return_value="python3")):
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
        self.assertIn("permission:\n  edit: deny\n  bash: deny\n  webfetch: deny\n  websearch: deny", text)
        text = open(self.conf("agents", "product-manager.md")).read()
        self.assertIn("  webfetch: allow\n  websearch: allow", text)
        meta, _ = roles.parse(open(self.conf("agents", "tester.md")).read())
        self.assertEqual(meta["model"], "anthropic/claude-sonnet-5")
        self.assertNotIn("variant", meta)  # medium: no variant
        with self.assertRaises(ValueError):
            settings.parse_value("models.opencode.tester", "sonnet")

    def test_installer_for_opencode_2_writes_a_command_folder_and_the_agents_md_block(self):
        mine = self.conf("commands", "deploy.md")
        os.makedirs(os.path.dirname(mine))
        open(mine, "w").write("my command\n")
        open(self.conf("commands", "team-workflow"), "w").close()  # left by 0.7 on Windows
        os.makedirs(self.conf("plugins"))
        open(self.conf("plugins", "team-workflow.js"), "w").write("// 1.x plugin\n")
        open(self.conf("AGENTS.md"), "w").write("# My rules\n\n- be brief\n")
        with mock.patch.object(opencode_cli, "python_command", return_value="python"):
            result = install_opencode.install(version=(2, 1, 2))
        self.assertTrue(result["v2"])
        self.assertEqual(sorted(os.listdir(self.conf("commands"))), ["deploy.md", "team-workflow"])
        commands = sorted(os.listdir(self.conf("commands", "team-workflow")))
        self.assertIn("call-team.md", commands)
        self.assertEqual(result["commands"], len(commands))
        scripts = install_opencode.posix(self.conf("skills", "team-workflow", "scripts"))
        body = open(self.conf("commands", "team-workflow", "usage-costs.md")).read()
        self.assertIn(f"{scripts}/dashboard.py", body)
        self.assertNotIn("python3 ", body)  # the Python that runs here
        settings_cmd = open(self.conf("commands", "team-workflow", "settings.md")).read()
        self.assertIn(f'!`python "{scripts}/tw.py" settings $ARGUMENTS`', settings_cmd)
        self.assertFalse(os.path.exists(self.conf("plugins", "team-workflow.js")))  # 2.x cannot load it
        rules = open(self.conf("AGENTS.md")).read()
        self.assertTrue(rules.startswith("# My rules\n\n- be brief\n"))
        self.assertIn(f'`python "{scripts}/session_start.py" --text`', rules)
        self.assertIn("subagent tool", rules)
        skill = open(self.conf("skills", "team-workflow", "SKILL.md")).read()
        self.assertNotIn("python3 <skill>", skill)
        self.assertEqual(install_opencode.installed_source(), install_opencode.REPO)
        self.assertEqual(len(result["agents"]), 20)
        install_opencode.install(version=(2, 1, 2))  # again: one block, nothing stale
        self.assertEqual(open(self.conf("AGENTS.md")).read().count(install_opencode.BEGIN), 1)
        install_opencode.uninstall()
        self.assertEqual(os.listdir(self.conf("commands")), ["deploy.md"])
        self.assertEqual(open(self.conf("AGENTS.md")).read(), "# My rules\n\n- be brief\n")
        self.assertEqual(os.listdir(self.conf("agents")), [])

    @unittest.skipIf(os.name == "nt", "a colon is not allowed in a Windows file name")
    def test_installer_removes_the_old_colon_commands(self):
        os.makedirs(self.conf("commands"))
        old = self.conf("commands", "team-workflow:settings.md")
        open(old, "w").write(f"---\n---\n{install_opencode.MARK}\n")
        result = install_opencode.install(version=(2, 1, 2))
        self.assertFalse(os.path.exists(old))
        self.assertIn("team-workflow:settings.md", result["stale_commands_removed"])

    def test_installer_for_opencode_1_writes_the_plugin(self):
        result = install_opencode.install(version=(1, 14, 0))
        self.assertFalse(result["v2"])
        js = open(self.conf("plugins", "team-workflow.js")).read()
        self.assertIn(install_opencode.posix(self.conf("skills", "team-workflow", "scripts")), js)
        self.assertIn(json.dumps(sys.executable), js)
        self.assertNotIn("__SCRIPTS__", js)
        self.assertNotIn("__PYTHON__", js)
        self.assertIn("team-workflow[:/]", js)
        self.assertFalse(os.path.exists(self.conf("AGENTS.md")))
        self.assertIn("call-team.md", os.listdir(self.conf("commands", "team-workflow")))
        install_opencode.uninstall()
        self.assertFalse(os.path.exists(self.conf("plugins", "team-workflow.js")))

    def test_worker_command_and_usage_from_events(self):
        with mock.patch.object(opencode_cli, "version", return_value=(2, 1, 2)):
            cmd = run_worker.build_command("opencode", "openai/gpt-6", "high", "brief", False)
        self.assertEqual(cmd[1:8], ["run", "--format", "json", "-m", "openai/gpt-6#high", "--agent", "plan"])
        self.assertNotIn("--variant", cmd)
        with mock.patch.object(opencode_cli, "version", return_value=(1, 14, 0)):
            cmd = run_worker.build_command("opencode", "openai/gpt-6", "high", "brief", False)
        self.assertEqual(cmd[4:7], ["-m", "openai/gpt-6", "--variant"])
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
        db.close()
        rows = {(r["agent"], r["session"]): r for r in usage.opencode_runs(self.root)}
        self.assertEqual(set(rows), {("main", "s1"), ("tester", "s1")})
        self.assertEqual((rows[("tester", "s1")]["input"], rows[("tester", "s1")]["output"]), (20, 2))
        self.assertAlmostEqual(usage.cost_usd(rows[("main", "s1")], "anthropic/claude-sonnet-5",
                                              usage.load_pricing()), 10 * 2e-6 + 2 * 10e-6 + 2 * 2e-7)

    def opencode2_db(self):
        """OpenCode 2.x's store: session_v2 and session_message, the model as an object."""
        path = usage.opencode_db()
        os.makedirs(os.path.dirname(path))
        db = sqlite3.connect(path)
        db.execute("create table session_v2 (id text, parent_id text, directory text, model text)")
        db.execute("create table session_message (session_id text, type text, time_created int, data text)")
        glm = {"id": "z-ai/glm-5.3", "providerID": "nano-gpt"}
        db.executemany("insert into session_v2 values (?, ?, ?, ?)", [
            ("s1", None, self.root.replace(os.sep, "/"), json.dumps(glm)),
            ("s2", "s1", self.root, json.dumps(dict(glm, variant="high"))),
            ("s3", None, "/elsewhere", json.dumps({"id": "glm-5.3-flash-free", "providerID": "opencode"}))])
        msg = lambda agent, n: json.dumps({"agent": agent, "model": glm, "cost": 0.25,
                                           "tokens": {"input": n, "output": 1, "reasoning": 1, "cache": {"read": 2}}})
        db.executemany("insert into session_message values (?, ?, ?, ?)", [
            ("s1", "assistant", 1_790_000_000_000, msg("build", 10)),
            ("s2", "assistant", 1_790_000_000_500, msg("tester", 20)),
            ("s1", "user", 1_790_000_000_900, json.dumps({"text": "hi"}))])
        db.commit()
        db.close()

    def test_usage_and_recent_models_from_the_opencode_2_store(self):
        self.opencode2_db()
        rows = {(r["agent"], r["session"]): r for r in usage.opencode_runs(self.root)}
        self.assertEqual(set(rows), {("main", "s1"), ("tester", "s1")})
        self.assertEqual(rows[("tester", "s1")]["model"], "nano-gpt/z-ai/glm-5.3")
        self.assertEqual((rows[("tester", "s1")]["input"], rows[("tester", "s1")]["output"]), (20, 2))
        self.assertEqual(opencode_cli.recent(), [("nano-gpt/z-ai/glm-5.3", 2), ("opencode/glm-5.3-flash-free", 1)])

    def test_catalog_lists_every_provider_with_names_and_variants(self):
        answers = {("api", "GET", "/api/model"): json.dumps(API_MODELS),
                   ("api", "GET", "/api/provider"): json.dumps(API_PROVIDERS)}
        with mock.patch.object(opencode_cli, "version", return_value=(2, 1, 2)), \
                mock.patch.object(opencode_cli, "run", side_effect=lambda *a, **k: answers.get(a, "")):
            models = opencode_cli.catalog()
        self.assertEqual([m["id"] for m in models],
                         ["nano-gpt/z-ai/glm-5.3", "nano-gpt/z-ai/glm-5.3-flash", "opencode/glm-5.3-flash-free"])
        self.assertEqual(models[0]["variants"], ["low", "high", "max"])
        self.assertEqual(opencode_cli.providers(models),
                         {"nano-gpt": {"name": "NanoGPT", "models": 2}, "opencode": {"name": "OpenCode", "models": 1}})
        self.assertEqual([m["name"] for m in opencode_cli.search(models, "nano-gpt", "glm 5.3")],
                         ["GLM 5.3", "GLM 5.3 Flash"])
        self.assertEqual([m["id"] for m in opencode_cli.search(models, text="FLASH free")],
                         ["opencode/glm-5.3-flash-free"])
        with mock.patch.object(opencode_cli, "version", return_value=(1, 14, 0)), \
                mock.patch.object(opencode_cli, "run", return_value="anthropic/claude-sonnet-5\nopenai/gpt-6\n"):
            old = opencode_cli.catalog()  # 1.x: ids only
        self.assertEqual([(m["provider"], m["name"]) for m in old],
                         [("anthropic", "claude-sonnet-5"), ("openai", "gpt-6")])

    def test_wizard_options_show_providers_and_the_models_used_most(self):
        import tw
        self.opencode2_db()
        answers = {("api", "GET", "/api/model"): json.dumps(API_MODELS),
                   ("api", "GET", "/api/provider"): json.dumps(API_PROVIDERS), ("--version",): "opencode v2.1.2"}
        with mock.patch.object(opencode_cli, "binary", return_value="opencode"), \
                mock.patch.object(opencode_cli, "version", return_value=(2, 1, 2)), \
                mock.patch.object(opencode_cli, "run", side_effect=lambda *a, **k: answers.get(a, "")):
            native = tw.app_options("opencode", self.root)["native"]
            with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
                tw.main(["models", "--provider", "nano-gpt", "--search", "glm 5.3"])
        self.assertEqual(native["providers"]["nano-gpt"], {"name": "NanoGPT", "models": 2})
        self.assertEqual(native["recent"][0], {"id": "nano-gpt/z-ai/glm-5.3", "name": "GLM 5.3",
                                               "variants": ["low", "high", "max"]})
        self.assertEqual(native["models"][:2], ["inherit", "nano-gpt/z-ai/glm-5.3"])
        self.assertIn("--search", native["find"])
        self.assertIn("matching 'glm 5.3': 2", out.getvalue())
        self.assertIn("variants: low, high, max", out.getvalue())

    def test_python_command_skips_a_python3_that_does_not_run(self):
        runs = {"python3": 9009, "python": 0}  # 9009: the Microsoft Store placeholder
        with mock.patch.object(opencode_cli.shutil, "which", side_effect=lambda n: n if n in runs else None), \
                mock.patch.object(opencode_cli.subprocess, "run",
                                  side_effect=lambda cmd, **k: mock.Mock(returncode=runs[cmd[0]])):
            self.assertEqual(PYTHON_COMMAND.__wrapped__(), "python")  # uncached

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
        self.assertIn("session effort", data["roles"]["architect"]["runs"])
        claude = tw.app_options("claude", self.root)
        self.assertIn("no effort", tw.runs_as("claude", dict(type="custom", model="haiku", effort="high"),
                                              claude["native"]))
        self.assertIn("worker", tw.runs_as("agy", dict(type="worker", model="x", effort="low"), {}))
        with mock.patch.object(tw.shutil, "which", return_value=None), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            tw.main(["options", "--app", "all"])
        for heading in ("== Claude Code", "== agy", "== OpenCode", "When you can change"):
            self.assertIn(heading, out.getvalue())
        self.assertIn("thorough", data["presets"])
        self.assertIn("general", tw.app_options("opencode")["types"])
        self.init_memory()
        out = self.run_script("session_start.py", hook={"cwd": self.root, "session_id": "w"},
                              env={"TEAM_WORKFLOW_APP": "opencode"})
        context = json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("session setup is on", context)
        self.assertIn("tw.py options --app opencode", context)
        self.assertIn("subagent tool, agent = the role", context)
        self.assertIn("/team-workflow/<name>", context)
        # OpenCode 2.x: the model runs it from the AGENTS.md block and reads plain text
        out = self.run_script("session_start.py", "--text", cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("docs/memory/INDEX.md", out.stdout)
        self.assertIn("subagent tool", out.stdout)
        self.assertNotIn("hookSpecificOutput", out.stdout)


if __name__ == "__main__":
    unittest.main()
