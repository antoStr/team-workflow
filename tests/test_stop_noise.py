"""Stop hook without noise: no false "update STATE.md" after a pull, the cortex and the brain once per
set of changes, no brain node rewritten only for its date."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import json
import os
import sys
import time
import unittest

from test_scripts import SCRIPTS, ScriptTest

sys.path.insert(0, SCRIPTS)
import brain  # noqa: E402
import cortex  # noqa: E402


class StopNoiseTest(ScriptTest):
    def setUp(self):
        super().setUp()
        self.init_memory()
        self.git("add", "-A")
        self.git("commit", "-qm", "memory")
        self.hook = {"cwd": self.root, "session_id": "noise"}
        self.run_script("session_start.py", hook=self.hook)

    def stop(self):
        out = self.run_script("stop_check.py", hook=self.hook)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)["decision"] if out.stdout.strip() else None

    def test_state_in_the_same_commit_as_the_code_passes_whatever_the_mtimes(self):
        self.write("src/app.py", "print(1)\n")
        self.write("docs/memory/STATE.md", self.read("docs/memory/STATE.md") + "\n- app added\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "app")
        later = time.time() + 100  # a pull wrote the code after STATE.md
        os.utime(os.path.join(self.root, "src", "app.py"), (later, later))
        self.assertIsNone(self.stop())

    def test_code_committed_after_state_still_asks(self):
        self.write("docs/memory/STATE.md", self.read("docs/memory/STATE.md") + "\n- planned\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "state")
        time.sleep(1.1)  # commit times have 1 s resolution
        self.write("src/app.py", "print(1)\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "app")
        self.assertEqual(self.stop(), "block")

    def test_cortex_records_one_pass_per_set_of_changes(self):
        self.write("src/app.py", "print(1)\n")
        self.stop()
        self.stop()  # next turn, same files
        with open(cortex._weights_path(self.root), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["stats"]["passes"], 1)

    def test_genome_not_rewritten_for_its_date_only(self):
        os.makedirs(os.path.join(self.root, "docs", "brain"), exist_ok=True)
        cortex.assimilate_project_knowledge(self.root, write_genome_md=True)
        path = os.path.join(self.root, "docs", "brain", "PROJECT_GENOME.md")
        before = os.path.getmtime(path)
        time.sleep(0.05)
        cortex.assimilate_project_knowledge(self.root, write_genome_md=True)
        self.assertEqual(os.path.getmtime(path), before)

    def test_brain_node_not_rewritten_for_its_date_only(self):
        self.write("src/app.py", '"""App."""\n')
        self.assertEqual(brain.map_repo(root=self.root)["nodes_written"], 1)
        self.assertEqual(brain.map_repo(root=self.root)["nodes_written"], 0)
        self.write("src/app.py", '"""App, changed."""\n')
        self.assertEqual(brain.map_repo(root=self.root)["nodes_written"], 1)


if __name__ == "__main__":
    unittest.main()
