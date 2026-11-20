"""Learnings with a check: enforced on every edit, at Stop and in CI, not sent as prose."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import json
import os
import unittest

from test_scripts import ScriptTest


class ChecksTest(ScriptTest):
    def tw(self, *args):
        return self.run_script("tw.py", *args, cwd=self.root)

    def record(self, pattern=r"setTimeout\(", glob="*.ts"):
        return self.tw("learn", "record", "--title", "No timer hacks", "--anti-pattern", "setTimeout to wait",
                       "--solution", "await the event", "--applies-to", "frontend-dev",
                       "--check-pattern", pattern, "--check-glob", glob)

    def hook(self, rel, env=None):
        out = self.run_script("check_hook.py", env=env, hook={
            "cwd": self.root, "tool_name": "Edit", "tool_input": {"file_path": rel}})
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout) if out.stdout.strip() else None

    def test_edit_hook_blocks_a_match_with_file_and_line(self):
        self.assertEqual(self.record().returncode, 0)
        self.write("src/a.ts", "const x = 1;\nsetTimeout(go, 0);\n")
        self.write("src/b.ts", "await ready;\n")
        self.write("src/c.py", "setTimeout(go)\n")  # outside the glob
        verdict = self.hook("src/a.ts")
        self.assertEqual(verdict["decision"], "block")
        self.assertIn("src/a.ts:2: No timer hacks: await the event", verdict["reason"])
        self.assertIsNone(self.hook("src/b.ts"))
        self.assertIsNone(self.hook("src/c.py"))
        self.assertIsNone(self.hook("src/a.ts", env={"TEAM_WORKFLOW_CHECKS": "0"}))
        self.assertIsNone(self.hook("../outside.ts"))

    def test_cli_check_exit_code_and_no_prose_vaccine(self):
        self.record()
        self.write("src/a.ts", "setTimeout(go, 0);\n")
        self.git("add", "-A")
        out = self.tw("learn", "check")
        self.assertEqual(out.returncode, 1)
        self.assertIn("src/a.ts:1", out.stdout)
        self.assertEqual(self.tw("learn", "check", "src/missing.ts").returncode, 0)
        vaccines = json.loads(self.tw("learn", "vaccine", "--role", "frontend-dev", "--json").stdout)
        self.assertEqual(vaccines, [])  # enforced by the check, so not repeated as prose

    def test_the_learning_text_itself_does_not_fail(self):
        self.tw("learn", "record", "--title", "No timer", "--anti-pattern", "calling setTimeout( to wait",
                "--solution", "await", "--check-pattern", r"setTimeout\(")  # glob * covers the learning files
        self.git("add", "-A")
        out = self.tw("learn", "check")
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIsNone(self.hook("docs/memory/LEARNINGS.md"))

    def test_absolute_paths_and_big_or_binary_files(self):
        self.record()
        self.write("src/a.ts", "setTimeout(go, 0);\n")
        self.assertEqual(self.hook(os.path.join(self.root, "src", "a.ts"))["decision"], "block")
        self.write("src/big.ts", "setTimeout(go);\n" + "x" * 1_100_000)
        self.assertIsNone(self.hook("src/big.ts"))
        with open(os.path.join(self.root, "src", "bin.ts"), "wb") as f:
            f.write(b"\0setTimeout(go)")
        self.assertIsNone(self.hook("src/bin.ts"))

    def test_invalid_pattern_is_refused(self):
        out = self.record(pattern="(unclosed")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("Invalid check pattern", out.stderr)

    def test_stop_blocks_on_a_changed_file_that_fails_a_check(self):
        self.init_memory()
        self.record()
        self.git("add", "-A")
        self.git("commit", "-qm", "memory")
        hook = {"cwd": self.root, "session_id": "checks"}
        self.run_script("session_start.py", hook=hook)
        self.write("src/a.ts", "setTimeout(go, 0);\n")
        out = json.loads(self.run_script("stop_check.py", hook=hook).stdout)
        self.assertEqual(out["decision"], "block")
        self.assertIn("fail recorded checks", out["reason"])
        again = self.run_script("stop_check.py", hook=hook).stdout  # same failure, next turn
        self.assertNotIn("fail recorded checks", again)  # asked once, not on every turn


if __name__ == "__main__":
    unittest.main()
