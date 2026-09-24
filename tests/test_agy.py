"""Offline tests for agy support: hook payloads in agy's format and the agy plugin builder."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

from test_scripts import SCRIPTS, ScriptTest


class AgyHooksTest(ScriptTest):
    def setUp(self):
        super().setUp()
        self.init_memory()
        self.git("add", "-A")
        self.git("commit", "-qm", "memory")
        self.payload = {"conversationId": "agy-1", "workspacePaths": [self.root], "modelName": "auto"}

    def test_pre_invocation_saves_snapshot_without_injecting(self):
        out = self.run_script("session_start.py", hook=dict(self.payload, invocationNum=1))
        self.assertEqual(json.loads(out.stdout), {})
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "team-workflow-agy-1.json")))

    def test_stop_continues_once_when_state_is_behind(self):
        self.run_script("session_start.py", hook=self.payload)
        self.write("src/app.py", "print(1)\n", mtime=time.time() + 60)
        first = self.run_script("stop_check.py", hook=dict(self.payload, executionNum=0))  # agy starts at 0
        self.assertEqual(json.loads(first.stdout)["decision"], "continue")
        again = self.run_script("stop_check.py", hook=dict(self.payload, executionNum=1))
        self.assertEqual(again.stdout.strip(), "")
        same_state = self.run_script("stop_check.py", hook=dict(self.payload, executionNum=0))
        self.assertEqual(same_state.stdout.strip(), "")  # never asks twice for the same files

    @unittest.skipUnless(os.path.isdir("/proc/self"), "needs Linux /proc")
    def test_finds_the_repository_through_agy_process_without_workspace_paths(self):
        # agy runs the hook from its plugin folder with empty workspacePaths (print mode);
        # the repository is the working folder of the agy process, the hook's parent.
        plugin_dir = os.path.join(self.tmp, "plugin")
        os.makedirs(plugin_dir)
        payload = json.dumps({"conversationId": "agy-proc", "workspacePaths": []})
        hook = os.path.join(SCRIPTS, "session_start.py")
        launcher = (f"import subprocess, sys; subprocess.run([sys.executable, {hook!r}], "
                    f"cwd={plugin_dir!r}, input={payload!r}, text=True)")
        subprocess.run([sys.executable, "-c", launcher], cwd=self.root, capture_output=True,
                       env=dict(os.environ, TMPDIR=self.tmp), timeout=60)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "team-workflow-agy-proc.json")))


class AgyPluginTest(unittest.TestCase):
    def build(self, dest):
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, "install_agy.py"), "--dest", dest],
                              capture_output=True, text=True, env=dict(os.environ, PATH="/nonexistent"))

    def test_builds_plugin_with_skills_roles_rules_and_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = os.path.join(tmp, "team-workflow")
            out = self.build(dest)
            self.assertEqual(out.returncode, 0, out.stderr)
            with open(os.path.join(dest, "plugin.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f)["name"], "team-workflow")
            with open(os.path.join(dest, "hooks.json"), encoding="utf-8") as f:
                self.assertEqual(sorted(json.load(f)["team-workflow"]), ["PreInvocation", "Stop"])
            self.assertTrue(os.path.isfile(os.path.join(dest, "rules", "AGENTS.md")))
            self.assertTrue(os.path.isfile(os.path.join(dest, "agents", "tester.md")))
            skills = os.path.join(dest, "skills")
            self.assertIn("team-workflow", os.listdir(skills))
            for name in ("init", "team", "wrap-up"):  # agy loads only skills/<name>/SKILL.md
                with open(os.path.join(skills, name, "SKILL.md"), encoding="utf-8") as f:
                    self.assertIn(f"name: {name}\n", f.read())
            self.assertEqual(self.build(dest).returncode, 0)  # rebuilding replaces its own output

    def test_never_replaces_a_foreign_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "mine"))
            out = self.build(os.path.join(tmp, "mine"))
            self.assertNotEqual(out.returncode, 0)
            self.assertTrue(os.path.isdir(os.path.join(tmp, "mine")))


if __name__ == "__main__":
    unittest.main()
