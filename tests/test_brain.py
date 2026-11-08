"""Unit tests for the Brain (Obsidian vault) engine and Talk Digest."""
import isolate_home  # noqa: F401
import json
import os
import shutil
import tempfile
import unittest

from test_scripts import SCRIPTS, ScriptTest
import sys
sys.path.insert(0, SCRIPTS)
import brain
import settings
import talk


class BrainTest(ScriptTest):
    def setUp(self):
        super().setUp()
        self.vault = os.path.join(self.tmp, "docs", "brain")

    def test_init_vault_creates_obsidian_structure(self):
        res = brain.init_vault(vault_dir="docs/brain", root=self.tmp)
        self.assertEqual(res["status"], "created")
        self.assertTrue(os.path.isfile(os.path.join(self.vault, "INDEX.md")))
        self.assertTrue(os.path.isfile(os.path.join(self.vault, ".obsidian", "graph.json")))
        self.assertTrue(os.path.isfile(os.path.join(self.vault, ".obsidian", "app.json")))
        self.assertTrue(os.path.isdir(os.path.join(self.vault, "nodes")))

    def test_map_and_query_and_check(self):
        # Create dummy python files
        src_dir = os.path.join(self.tmp, "src")
        os.makedirs(src_dir, exist_ok=True)
        auth_file = os.path.join(src_dir, "auth.py")
        with open(auth_file, "w", encoding="utf-8") as f:
            f.write('''"""Authentication service."""
from src import store

class Authenticator:
    def login(self, user, pwd):
        return True
''')
        store_file = os.path.join(src_dir, "store.py")
        with open(store_file, "w", encoding="utf-8") as f:
            f.write('''"""Data store."""
class Store:
    def get(self, k):
        return None
''')
        # 1. Map repository
        map_res = brain.map_repo(root=self.tmp, vault_dir="docs/brain")
        self.assertGreaterEqual(map_res["nodes_written"], 2)

        # 2. Check vault integrity
        chk = brain.check_vault(vault_dir="docs/brain", root=self.tmp)
        self.assertTrue(chk["ok"], f"Check failed: {chk['findings']}")

        # 3. Query context (BFS 1-hop)
        out = brain.query_context("auth", vault_dir="docs/brain", root=self.tmp, hops=1)
        self.assertIn("@node src-auth", out)
        self.assertIn("Authenticator", out)
        self.assertIn("[[src-store]]", out)

    def test_talk_compact_preserves_open_threads(self):
        topic = "test-compact"
        talk.clear(topic, cwd=self.tmp)

        def safe_post(*args, **kwargs):
            try:
                return talk.post(*args, **kwargs)
            except talk.Unread:
                return talk.post(*args, **kwargs)

        # Post a question and answer (closed)
        q1 = safe_post(topic, "orchestrator", "Question 1", kind="question", cwd=self.tmp)
        safe_post(topic, "tester", "Answer 1", kind="answer", re_id=q1["id"], cwd=self.tmp)

        # Post a challenge without verdict (OPEN)
        q2 = safe_post(topic, "orchestrator", "Challenge open", kind="challenge", cwd=self.tmp)

        # Post notes to fill up
        for i in range(20):
            safe_post(topic, "orchestrator", f"Progress note {i}", kind="note", cwd=self.tmp)

        msgs_before = talk.read(topic, cwd=self.tmp)
        self.assertGreaterEqual(len(msgs_before), 23)

        # Compact topic
        digest = talk.compact_topic(topic, threshold=10, cwd=self.tmp, force=True)
        self.assertIsNotNone(digest)
        self.assertEqual(digest["kind"], "digest")

        msgs_after = talk.read(topic, cwd=self.tmp)
        self.assertLess(len(msgs_after), len(msgs_before))

        # Check open challenge is preserved!
        open_after = talk.open_threads(msgs_after)
        self.assertTrue(any(m["id"] == q2["id"] for m in open_after), "Open thread was lost in digest!")

        # Check archive file exists
        archive_file = talk.path(topic, self.tmp)[:-len(".jsonl")] + ".archive.jsonl"
        self.assertTrue(os.path.isfile(archive_file))


if __name__ == "__main__":
    unittest.main()
