#!/usr/bin/env python3
"""Tests for autolearn, adversarial gate, and smoke live execution verification."""
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.normpath(os.path.join(HERE, "..", "skills", "team", "scripts"))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import autolearn
import gate
import smoke


class AutoLearnTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_record_and_get_vaccines(self):
        item = autolearn.record_learning(
            root=self.tmp,
            title="Avoid unchecked game canvas render",
            trigger="Canvas 2D context crashed on null element",
            anti_pattern="canvas.getContext('2d') without checking if canvas exists",
            solution="if (!canvas) return; const ctx = canvas.getContext('2d');",
            applies_to=["frontend-dev", "game.js"],
            category="bug"
        )
        self.assertTrue(item["id"].startswith("learn-"))
        self.assertEqual(item["category"], "bug")

        # Test vaccine matching role
        vac_role = autolearn.get_vaccines(root=self.tmp, role="frontend-dev")
        self.assertEqual(len(vac_role), 1)
        self.assertIn("Avoid unchecked game canvas render", vac_role[0]["title"])

        # Test vaccine matching file
        vac_file = autolearn.get_vaccines(root=self.tmp, file_path="src/game.js")
        self.assertEqual(len(vac_file), 1)

        # Test vaccine not matching unrelated
        vac_none = autolearn.get_vaccines(root=self.tmp, role="devops-engineer", file_path="deploy.yml")
        self.assertEqual(len(vac_none), 0)

        # Test prompt formatting
        prompt = autolearn.format_vaccine_prompt(vac_role)
        self.assertIn("TEAM AUTO-LEARN VACCINES", prompt)
        self.assertIn("Avoid unchecked game canvas render", prompt)


class AdversarialGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_gate_lifecycle_and_autolearn_feed(self):
        # 1. Create gate
        g = gate.create_gate(
            root=self.tmp,
            target="game/player.py",
            builder="game-dev",
            breaker="tester",
            hypothesis="Player velocity may exceed max speed on diagonal input"
        )
        self.assertEqual(g["status"], "PENDING_BREAKER")

        # 2. Block gate with PoC
        g_blocked = gate.block_gate(
            root=self.tmp,
            gate_id=g["id"],
            poc="Diagonal movement vector (1, 1) has magnitude 1.414, breaking speed limit"
        )
        self.assertEqual(g_blocked["status"], "BLOCKED")
        self.assertEqual(g_blocked["blocks_count"], 1)

        # 3. Pass gate with verified fix
        g_passed = gate.pass_gate(
            root=self.tmp,
            gate_id=g["id"],
            evidence="Normalized movement vector: velocity = velocity.normalized() * speed"
        )
        self.assertEqual(g_passed["status"], "PASSED")

        # 4. Verify that resolution automatically fed autolearn
        learnings = autolearn.list_learnings(root=self.tmp)
        self.assertEqual(len(learnings), 1)
        self.assertIn("gate:gate-game-player-py", learnings[0]["source"])


class SmokeExecutionTest(unittest.TestCase):
    def test_clean_exit_command(self):
        res = smoke.run_smoke("python -c \"print('Hello Smoke')\"", timeout=3.0)
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "CLEAN_EXIT")
        self.assertEqual(res["exit_code"], 0)

    def test_crashed_command_detected(self):
        res = smoke.run_smoke("python -c \"raise SystemExit(2)\"", timeout=3.0)
        self.assertFalse(res["ok"])
        self.assertEqual(res["status"], "CRASHED")
        self.assertEqual(res["exit_code"], 2)

    @unittest.skipUnless(shutil.which("wsl"), "needs WSL")
    def test_wsl_smoke_execution(self):
        res = smoke.run_smoke("echo 'Hello WSL'", timeout=10.0, wsl=True)
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "CLEAN_EXIT")
        self.assertEqual(res["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
