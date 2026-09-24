"""Offline tests for usage.py and estimate.py:  python3 -m unittest discover -s tests"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "skills", "team-workflow", "scripts"))
import estimate  # noqa: E402
import usage  # noqa: E402

PRICING = {"aliases": {"sonnet": "claude-sonnet-5"},
           "models": {"claude-sonnet-5": {"input": 2, "output": 10}}}


def assistant(msg_id, block, model="claude-sonnet-5", sidechain=False, **u):
    usage_ = {"input_tokens": u.get("i", 0), "cache_read_input_tokens": u.get("r", 0),
              "output_tokens": u.get("o", 0), "cache_creation_input_tokens": u.get("w", 0),
              "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": u.get("w", 0)}}
    return {"type": "assistant", "requestId": "req-" + msg_id, "isSidechain": sidechain,
            "timestamp": "2026-09-24T10:00:00Z",
            "message": {"id": msg_id, "model": model, "usage": usage_, "content": [{"type": block}]}}


class Fixture(unittest.TestCase):
    """A fake HOME with the Claude Code project folder of a throwaway repository."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = tmp.name
        self.root = os.path.join(tmp.name, "repo")
        os.makedirs(self.root)
        self.pdir = usage.claude_project_dir(self.root, self.home)
        os.makedirs(os.path.join(self.pdir, "s1", "subagents"))

    def jsonl(self, path, records):
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(json.dumps(r) for r in records) + "\n")

    def add_subagent(self, name, agent_type, **u):
        base = os.path.join(self.pdir, "s1", "subagents", name)
        self.jsonl(base + ".jsonl", [assistant("m-" + name, "text", sidechain=True, **u)])
        with open(base + ".meta.json", "w", encoding="utf-8") as f:
            json.dump({"agentType": agent_type, "description": "d"}, f)


class UsageTest(Fixture):
    def test_message_blocks_counted_once_and_labelled(self):
        # three content blocks of one API message repeat its usage: it must count once
        self.jsonl(os.path.join(self.pdir, "s1.jsonl"), [
            assistant("m1", "thinking", i=10, r=1000, o=50, w=200),
            assistant("m1", "text", i=10, r=1000, o=50, w=200),
            assistant("m1", "tool_use", i=10, r=1000, o=50, w=200),
            assistant("m2", "text", i=5, r=2000, o=20, w=0)])
        self.add_subagent("agent-a", "team-workflow:tester", r=500, o=5)
        rows = usage.all_runs(self.root, home=self.home)
        main = [r for r in rows if r["agent"] == "main"][0]
        self.assertEqual((main["calls"], main["cache_read"], main["output"]), (2, 3000, 70))
        self.assertEqual(main["cache_write_1h"], 200)
        self.assertEqual([r["agent"] for r in rows if r["agent"] != "main"], ["team-workflow:tester"])

    def test_cost_and_ledger(self):
        u = {"input": 1_000_000, "cache_write_1h": 1_000_000, "cache_read": 1_000_000, "output": 1_000_000}
        self.assertAlmostEqual(usage.cost_usd(u, "sonnet", PRICING), 2 + 4 + 0.2 + 10)
        self.assertIsNone(usage.cost_usd(u, "gemini-3.8-flash-high", PRICING))
        self.assertEqual(usage.cost_usd(u, "claude-sonnet-5-20260101", PRICING), usage.cost_usd(u, "sonnet", PRICING))
        os.makedirs(os.path.dirname(usage.ledger_path(self.root, self.home)))
        with open(usage.ledger_path(self.root, self.home), "w", encoding="utf-8") as f:
            f.write(json.dumps({"ts": 1, "harness": "agy", "role": "tester", "model": "gemini-3.8-flash-high",
                                "usage": {"input": 12000, "output": 10, "calls": 1}}) + "\n")
        rows = usage.all_runs(self.root, home=self.home)
        self.assertEqual([(r["harness"], r["agent"], r["input"]) for r in rows], [("agy", "tester", 12000)])


class EstimateTest(Fixture):
    def test_profile_scales_with_effort_and_files(self):
        high = estimate.profile_usage("small", "high")
        low = estimate.profile_usage("small", "low")
        self.assertEqual(high["calls"], 10)
        self.assertLess(low["cache_read"], high["cache_read"])
        self.assertGreater(estimate.profile_usage("small", "high", 10_000)["cache_read"], high["cache_read"])

    def test_history_calibrates_and_unknown_model_has_no_price(self):
        self.jsonl(os.path.join(self.pdir, "s1.jsonl"), [assistant("m1", "text", r=10)])
        self.add_subagent("agent-a", "team-workflow:tester", r=100_000, o=100)
        self.add_subagent("agent-b", "team-workflow:tester", r=300_000, o=300)
        rows = estimate.estimate("tester", "large", "max", ["sonnet", "gemini-3.8-flash-high"],
                                 root=self.root, home=self.home, pricing=PRICING)
        self.assertEqual(rows[0]["source"], "median of 2 past runs")
        self.assertEqual(rows[0]["usage"]["cache_read"], 200_000)
        self.assertIsNotNone(rows[0]["cost"])
        self.assertIsNone(rows[1]["cost"])


if __name__ == "__main__":
    unittest.main()
