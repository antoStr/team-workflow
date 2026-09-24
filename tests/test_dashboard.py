"""Offline tests for dashboard.py on a fake Claude Code history and worker ledger."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "skills", "team-workflow", "scripts"))
import dashboard  # noqa: E402
import usage  # noqa: E402
from test_usage import PRICING, Fixture, assistant  # noqa: E402


class DashboardTest(Fixture):
    def test_totals_groups_and_safe_html(self):
        self.jsonl(os.path.join(self.pdir, "s1.jsonl"), [
            assistant("m1", "text", i=10, r=1_000_000, o=1000, w=100_000),
            assistant("m1", "tool_use", i=10, r=1_000_000, o=1000, w=100_000)])
        self.add_subagent("agent-a", "team-workflow:tester<x>", r=500_000, o=500)
        os.makedirs(os.path.dirname(usage.ledger_path(self.root, self.home)))
        with open(usage.ledger_path(self.root, self.home), "w", encoding="utf-8") as f:
            f.write(json.dumps({"ts": 1, "harness": "agy", "role": "backend-dev", "model": "gemini-3.8-flash-high",
                                "usage": {"input": 20_000, "output": 100, "calls": 2}}) + "\n")
        d = dashboard.build(self.root, home=self.home, pricing=PRICING)
        self.assertEqual(d["total"]["calls"], 4)  # 1 main message, 1 subagent message, 2 worker turns
        self.assertEqual([name for name, _ in d["by_agent"]][0], "main")
        self.assertEqual(d["total"]["unpriced"], 20_100)  # the Gemini worker has no price
        self.assertGreater(d["total"]["cost"], 0)
        page = dashboard.render_html(d, dashboard.T["en"])
        self.assertIn("team-workflow:tester&lt;x&gt;", page)  # agent names are escaped
        self.assertNotIn("<script", page)
        self.assertIn("backend-dev", dashboard.render_text(d, dashboard.T["it"]))

    def test_empty_history(self):
        d = dashboard.build(self.root, home=self.home, pricing=PRICING)
        self.assertEqual(d["total"]["tokens"], 0)
        self.assertIn("No usage", dashboard.render_text(d, dashboard.T["en"]))


if __name__ == "__main__":
    unittest.main()
