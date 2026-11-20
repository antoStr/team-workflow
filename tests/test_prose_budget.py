"""Prose budget: the always-loaded instructions may not grow unnoticed. Agents skip long rules; a lesson
that must hold belongs in a check (`tw.py learn record --check-pattern`), not in more prose. Raise a
ceiling only on purpose, after trimming elsewhere."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import glob
import os
import sys
import tempfile
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "skills", "team", "scripts"))

import omniscience  # noqa: E402

BUDGET = {  # words, a little above the size at v2.5.2
    "skills/team/SKILL.md": 1750,
    "skills/team/WIZARD.md": 2800,
    "rules/AGENTS.md": 775,
    "skills/team/roles/_shared/*.md": 1250,
}


def words(pattern):
    total = 0
    for path in glob.glob(os.path.join(ROOT, pattern)):
        with open(path, encoding="utf-8") as f:
            total += len(f.read().split())
    return total


class ProseBudgetTest(unittest.TestCase):
    def test_always_loaded_prose_stays_within_budget(self):
        for pattern, ceiling in BUDGET.items():
            self.assertLessEqual(words(pattern), ceiling, f"{pattern}: trim it or turn a rule into a check")

    def test_role_mutations_are_capped(self):
        with tempfile.TemporaryDirectory() as root:
            for i in range(omniscience.MAX_MUTATIONS + 5):
                out = omniscience.mutate_role_agent(root=root, role="backend-dev", lesson=f"lesson {i}")
                if i == 0:  # a section the user added below the mutations survives
                    with open(out["path"], "a", encoding="utf-8") as f:
                        f.write("\n## Notes\nkeep me\n")
            self.assertEqual(out["mutations_count"], omniscience.MAX_MUTATIONS)
            with open(out["path"], encoding="utf-8") as f:
                text = f.read()
            self.assertIn(f"lesson {omniscience.MAX_MUTATIONS + 4}", text)
            self.assertNotIn("**lesson 0**", text)
            self.assertIn("## Notes\nkeep me", text)


if __name__ == "__main__":
    unittest.main()
