"""Offline tests for 0.9: activation (auto or manual), the ECC library and team talk."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import json
import os
import sys
import tempfile
import time
import unittest
from unittest import mock

from test_scripts import SCRIPTS, ScriptTest

sys.path.insert(0, SCRIPTS)
import library  # noqa: E402
import roles  # noqa: E402
import settings  # noqa: E402
import talk  # noqa: E402


class ActivationTest(ScriptTest):
    def context(self):
        out = self.run_script("session_start.py", hook={"cwd": self.root, "session_id": "act"})
        return json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]

    def test_manual_replaces_the_memory_with_one_line_and_stops_the_stop_check(self):
        self.init_memory()
        self.git("add", "-A")
        self.git("commit", "-qm", "memory")
        self.assertIn("--- docs/memory/INDEX.md ---", self.context())
        self.assertIn("team talk is on", self.context())
        with open(os.path.join(self.root, ".team-workflow.json"), "w") as f:
            json.dump({"activation": "manual"}, f)
        ctx = self.context()
        self.assertIn("manual activation", ctx)
        self.assertNotIn("docs/memory/INDEX.md ---", ctx)
        self.write("src/app.py", "print(1)\n")
        out = self.run_script("stop_check.py", hook={"cwd": self.root, "session_id": "act"})
        self.assertEqual(out.stdout.strip(), "")

    def test_setup_shows_every_group_and_where_values_come_from(self):
        with open(os.path.join(self.root, ".team-workflow.json"), "w") as f:
            json.dump({"activation": "manual"}, f)
        out = self.run_script("tw.py", "setup", cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stderr)
        for text in ("Activation", '"manual"     project', "talk_rounds", "Library", "Roles:"):
            self.assertIn(text, out.stdout)


class LibraryTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict(os.environ, {"HOME": tmp.name, "USERPROFILE": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_index_is_complete_and_every_entry_has_its_main_file(self):
        found = library.entries()
        kinds = {e["kind"] for e in found.values()}
        self.assertEqual(kinds, {"skill", "command", "rule"})
        self.assertGreater(len(found), 400)
        for e in found.values():
            self.assertTrue(os.path.isfile(library.main_file(e["id"])), e["id"])
            self.assertIn(e["pack"], library.index()["packs"])
        self.assertFalse(set(found) & set(library.index()["packs"]))

    def test_search_ranks_the_matching_entries_first(self):
        ids = [e["id"] for e in library.search(["python", "testing"])]
        self.assertIn("python-testing", ids[:3])
        self.assertEqual(library.search(["zzzz-nothing"]), [])

    def test_enable_installs_skills_with_requirements_and_disable_removes_only_ours(self):
        config = settings.load()
        settings.parse_value("library.packs.security", "true")  # a valid key
        config["library"] = {"packs": {"default": False}, "skills": {"rules-python": True}}
        dest = library.native_dir("claude")
        foreign = os.path.join(dest, "council")
        os.makedirs(foreign)
        config["library"]["skills"]["council"] = True
        r = library.sync("claude", config=config)
        self.assertEqual(sorted(r["written"]), ["rules-common", "rules-python"])
        self.assertEqual(r["skipped"], ["council"])
        with open(os.path.join(dest, "rules-python", "SKILL.md"), encoding="utf-8") as f:
            self.assertIn("name: rules-python", f.read())
        self.assertFalse(os.path.exists(os.path.join(dest, "rules-python", "MAIN.md")))
        self.assertEqual(library.sync("claude", config=config)["written"], [])  # unchanged: no copy
        config["library"]["skills"] = {}
        r = library.sync("claude", config=config)
        self.assertEqual(sorted(r["removed"]), ["rules-common", "rules-python"])
        self.assertTrue(os.path.isdir(foreign))

    def test_a_pack_turns_its_entries_on_and_a_single_entry_can_override_it(self):
        config = {"library": {"packs": {"default": False, "rules": True}, "skills": {"rules-go": False}}}
        on = library.wanted(config)
        self.assertIn("rules-python", on)
        self.assertNotIn("rules-go", on)
        self.assertNotIn("council", on)


class ImportedRolesTest(unittest.TestCase):
    def test_imported_roles_are_ours_and_carry_the_shared_blocks(self):
        catalog = roles.catalog()
        imported = [r for r, i in catalog.items() if "path" in i and 'source: "ECC' in roles.read(i)]
        self.assertGreaterEqual(len(imported), 30)
        meta, body = roles.load("react-reviewer")
        self.assertNotIn("Prompt Defense Baseline", body)
        self.assertNotIn("model", meta)
        self.assertIn("## Team talk", body)
        self.assertIn("## Untrusted content", body)
        self.assertIn("## Review discipline", body)
        self.assertEqual(catalog["react-reviewer"]["pack"], "frameworks")


class ReadmeCatalogTest(unittest.TestCase):
    def test_readme_lists_every_agent_and_library_entry_of_this_version(self):
        tools = os.path.join(SCRIPTS, "..", "..", "..", "tools")
        sys.path.insert(0, tools)
        import readme_catalog
        try:
            readme_catalog.main(["--check"])
        except SystemExit as e:
            self.fail(str(e))


class TalkTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.cwd = tmp.name  # not a repository: the channel lives in the (isolated) home
        patcher = mock.patch.dict(os.environ, {"HOME": tmp.name, "USERPROFILE": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_challenge_stays_open_until_the_challenger_gives_a_verdict(self):
        talk.post("t", "tester", "pytest red on auth", "challenge", to="backend-dev", cwd=self.cwd)
        self.assertEqual(len(talk.open_threads(talk.read("t", self.cwd))), 1)
        talk.post("t", "backend-dev", "fixed auth.py:40, 12 passed", "fix", re_id=1, cwd=self.cwd)
        self.assertEqual(len(talk.open_threads(talk.read("t", self.cwd))), 1)
        talk.post("t", "tester", "accepted: reran, 12 passed", "verdict", re_id=1, cwd=self.cwd)
        self.assertEqual(talk.open_threads(talk.read("t", self.cwd)), [])

    def test_messages_for_a_role_and_validation(self):
        talk.post("t", "a", "to everyone", cwd=self.cwd)
        talk.post("t", "a", "to b", to="b", cwd=self.cwd)
        talk.post("t", "a", "to c", to="c", cwd=self.cwd)
        self.assertEqual([m["text"] for m in talk.for_role(talk.read("t", self.cwd), "b")],
                         ["to everyone", "to b"])
        self.assertEqual(talk.for_role(talk.read("t", self.cwd), "b", since=2), [])
        with self.assertRaises(ValueError):
            talk.post("t", "a", "no re", "answer", cwd=self.cwd)
        with self.assertRaises(ValueError):
            talk.post("t", "a", "unknown id", "answer", re_id=99, cwd=self.cwd)
        with self.assertRaises(ValueError):
            talk.post("Bad Topic", "a", "x", cwd=self.cwd)

    def test_wait_returns_on_timeout_without_messages(self):
        start = time.time()
        self.assertEqual(talk.wait("quiet", "b", timeout=0.3, poll=0.1, cwd=self.cwd), [])
        self.assertLess(time.time() - start, 3)

    def test_worktrees_share_the_repository_channel(self):
        import subprocess
        repo = os.path.join(self.cwd, "repo")
        os.makedirs(repo)
        run = lambda *a, cwd=repo: subprocess.run(["git", *a], cwd=cwd, capture_output=True, check=True)  # noqa: E731
        run("init", "-q")
        run("-c", "user.email=t@e", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
        run("worktree", "add", "-q", os.path.join(self.cwd, "wt"))
        talk.post("shared", "a", "from main", cwd=repo)
        self.assertEqual([m["text"] for m in talk.read("shared", os.path.join(self.cwd, "wt"))], ["from main"])


if __name__ == "__main__":
    unittest.main()
