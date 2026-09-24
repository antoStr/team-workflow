"""Offline tests for run_worker.py with fake claude and agy CLIs."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "skills", "team-workflow", "scripts", "run_worker.py")

FAKE = """#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
shown = ("-p=<prompt>" if a.startswith("-p=") else a for a in args)
flags = " ".join(a for a in shown if len(a) < 100)
if {agy}:
    print(json.dumps({{"conversation_id": "c1", "status": "SUCCESS", "response": flags,
        "num_turns": 2, "usage": {{"input_tokens": 1000, "output_tokens": 20, "thinking_tokens": 5,
        "cache_read_tokens": 400}}}}))
else:
    print(json.dumps({{"type": "result", "is_error": False, "result": flags,
        "session_id": "s1", "num_turns": 3, "total_cost_usd": 0.5,
        "modelUsage": {{"claude-sonnet-5": {{}}}},
        "usage": {{"input_tokens": 10, "cache_read_input_tokens": 9000, "output_tokens": 50,
                  "cache_creation": {{"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 300}}}}}}))
"""


class WorkerTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home, self.root = tmp.name, os.path.join(tmp.name, "repo")
        os.makedirs(self.root)
        self.bins = {}
        for name, agy in (("claude", False), ("agy", True)):
            path = os.path.join(tmp.name, "fake-" + name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(FAKE.format(agy=agy))
            os.chmod(path, 0o755)
            self.bins[name] = path

    def run_worker(self, harness, *extra):
        env = dict(os.environ, HOME=self.home, TEAM_WORKFLOW_CLAUDE_BIN=self.bins["claude"],
                   TEAM_WORKFLOW_AGY_BIN=self.bins["agy"])
        out = subprocess.run([sys.executable, SCRIPT, "--harness", harness, "--role", "tester",
                              "--root", self.root, "--task", "check the parser", *extra],
                             capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        ledger = os.path.join(self.home, ".team-workflow", "ledger")
        with open(os.path.join(ledger, os.listdir(ledger)[0]), encoding="utf-8") as f:
            return out.stdout, json.loads(f.read().splitlines()[-1])

    def test_claude_worker_is_read_only_by_default_and_recorded(self):
        stdout, rec = self.run_worker("claude", "--model", "sonnet", "--effort", "xhigh")
        self.assertIn("--permission-mode plan", stdout)
        self.assertIn("--effort xhigh", stdout)
        self.assertEqual((rec["harness"], rec["model"], rec["cost_usd"]), ("claude-cli", "claude-sonnet-5", 0.5))
        self.assertEqual((rec["usage"]["cache_read"], rec["usage"]["cache_write_1h"]), (9000, 300))

    def test_agy_worker_with_edits_counts_thinking_as_output(self):
        stdout, rec = self.run_worker("agy", "--model", "gemini-3.8-flash-high", "--allow-edits")
        self.assertIn("--mode accept-edits", stdout)
        self.assertIn("-p=", stdout)
        self.assertEqual((rec["harness"], rec["usage"]["output"], rec["usage"]["cache_read"]), ("agy", 25, 400))
        self.assertIsNone(rec["cost_usd"])  # Gemini models have no price in the table


if __name__ == "__main__":
    unittest.main()
