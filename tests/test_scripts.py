"""Offline tests for the team-workflow scripts:  python3 -m unittest discover -s tests"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "skills", "team-workflow", "scripts")


class ScriptTest(unittest.TestCase):
    """A throwaway git repository, plus a private temp dir for the hooks' snapshots."""

    def setUp(self):
        base = tempfile.TemporaryDirectory()
        self.addCleanup(base.cleanup)
        self.root = os.path.join(base.name, "repo")
        self.tmp = os.path.join(base.name, "tmp")
        os.makedirs(self.root)
        os.makedirs(self.tmp)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "test")
        self.git("config", "commit.gpgsign", "false")
        os.makedirs(os.path.join(self.tmp, ".team-workflow"))  # HOME of the scripts: no network
        with open(os.path.join(self.tmp, ".team-workflow", "settings.json"), "w") as f:
            json.dump({"update_check": False}, f)

    def git(self, *args):
        subprocess.run(["git", "-C", self.root, *args], check=True, capture_output=True)

    def run_script(self, name, *args, hook=None, env=None, cwd=None):
        e = dict(os.environ, TMPDIR=self.tmp, TEMP=self.tmp, TMP=self.tmp, HOME=self.tmp,
                 **(env or {}))
        e.pop("CLAUDE_PROJECT_DIR", None)
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, name), *args],
                              input=json.dumps(hook) if hook is not None else "",
                              capture_output=True, text=True, env=e, timeout=60, cwd=cwd)

    def write(self, rel, text, mtime=None):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        if mtime is not None:
            os.utime(path, (mtime, mtime))

    def read(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8") as f:
            return f.read()

    def init_memory(self):
        out = self.run_script("init_memory.py", "--root", self.root)
        self.assertEqual(out.returncode, 0, out.stderr)


class InitMemoryTest(ScriptTest):
    def test_creates_memory_commands_and_pointers_once(self):
        self.write("go.mod", "module example.com/demo\n")
        self.write("GEMINI.md", "# Gemini rules\n")
        self.init_memory()
        for name in ("INDEX.md", "STATE.md", "MAP.md", "DECISIONS.md", "PLAYBOOKS.md",
                     "ACCESS.md", "areas/_TEMPLATE.md"):
            self.assertTrue(os.path.isfile(os.path.join(self.root, "docs", "memory", name)), name)
        self.assertIn("go test ./...", self.read("docs/memory/PLAYBOOKS.md"))
        self.assertIn("docs/memory/INDEX.md", self.read("GEMINI.md"))
        self.assertFalse(os.path.exists(os.path.join(self.root, "CLAUDE.md")))

        self.write("docs/memory/STATE.md", "# mine\n")
        self.init_memory()
        self.assertEqual(self.read("docs/memory/STATE.md"), "# mine\n")
        self.assertEqual(self.read("AGENTS.md").count("team-workflow:start"), 1)


class MemcheckTest(ScriptTest):
    def memcheck(self, *args):
        return self.run_script("memcheck.py", "--root", self.root, *args)

    def test_fresh_memory_passes_strict(self):
        self.init_memory()
        out = self.memcheck("--strict")
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_limits_secrets_and_missing_paths(self):
        self.init_memory()
        self.write("docs/memory/STATE.md", "x\n" * 51)
        out = self.memcheck()
        self.assertEqual(out.returncode, 1)
        self.assertIn("limit 50", out.stdout)

        self.write("docs/memory/STATE.md", "key AKIA" + "Q" * 16 + "\n")
        self.assertIn("AWS access key", self.memcheck().stdout)

        self.write("internal/pkg/pkg_test.go", "package pkg\n")
        self.git("add", "internal")
        self.write("docs/memory/STATE.md",
                   "see `src/missing.py`, `docs/memory/INDEX.md` and `pkg/pkg_test.go`\n")
        out = self.memcheck()
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("`src/missing.py` not found", out.stdout)
        self.assertNotIn("INDEX.md` not found", out.stdout)
        self.assertNotIn("pkg_test.go` not found", out.stdout)  # path relative to internal/
        self.assertEqual(self.memcheck("--strict").returncode, 1)


class SessionStartTest(ScriptTest):
    def context(self, cwd, session):
        out = self.run_script("session_start.py", hook={"cwd": cwd, "session_id": session})
        return json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"] if out.stdout else None

    def test_silent_outside_git(self):
        self.assertIsNone(self.context(self.tmp, "outside"))

    def test_hint_without_memory(self):
        self.assertIn("no docs/memory", self.context(self.root, "nomem"))

    def test_injects_index_and_state(self):
        self.init_memory()
        self.write("docs/memory/STATE.md", "# Current state\nVersion: **9.9.9**\n")
        ctx = self.context(self.root, "mem")
        self.assertIn("--- docs/memory/INDEX.md ---", ctx)
        self.assertIn("9.9.9", ctx)


class StopCheckTest(ScriptTest):
    def setUp(self):
        super().setUp()
        self.init_memory()
        self.git("add", "-A")
        self.git("commit", "-qm", "memory")
        self.hook = {"cwd": self.root, "session_id": "stop"}
        self.run_script("session_start.py", hook=self.hook)

    def stop(self, extra=None, env=None):
        out = self.run_script("stop_check.py", hook=dict(self.hook, **(extra or {})), env=env)
        return json.loads(out.stdout)["decision"] if out.stdout.strip() else None

    def test_nothing_changed(self):
        self.assertIsNone(self.stop())

    def test_code_change_without_state_update_blocks(self):
        self.write("src/app.py", "print(1)\n")
        self.assertEqual(self.stop(), "block")

    def test_never_twice_and_opt_out(self):
        self.write("src/app.py", "print(1)\n")
        self.assertIsNone(self.stop({"stop_hook_active": True}))
        self.assertIsNone(self.stop(env={"TEAM_WORKFLOW_STOP_CHECK": "0"}))

    def test_state_must_be_newer_than_the_latest_change(self):
        now = time.time()
        self.write("src/app.py", "print(1)\n", mtime=now - 60)
        self.write("docs/memory/STATE.md", "# Current state\nupdated\n", mtime=now)
        self.assertIsNone(self.stop())
        self.write("src/app.py", "print(2)\n", mtime=now + 60)
        self.assertEqual(self.stop(), "block")

    def test_commit_without_state_update_blocks(self):
        self.write("src/app.py", "print(1)\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "code")
        self.assertEqual(self.stop(), "block")

    def test_silent_without_memory(self):
        self.git("rm", "-rq", "docs")
        self.git("commit", "-qm", "no memory")
        self.write("src/app.py", "print(1)\n")
        self.assertIsNone(self.stop())


if __name__ == "__main__":
    unittest.main()
