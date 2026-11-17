import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import json
import os
import unittest

from test_scripts import ScriptTest


def user(text, **extra):
    return {"type": "user", "message": {"role": "user", "content": text}, **extra}


def tool(name, **inp):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}}


class SetupGateTest(ScriptTest):
    """The PreToolUse hook holds team roles until `tw.py options` and AskUserQuestion ran."""

    def gate(self, transcript, role="code-reviewer", env=None):
        path = os.path.join(self.tmp, "t.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(e) + "\n" for e in transcript)
        hook = {"cwd": self.root, "session_id": "s1", "transcript_path": path, "tool_name": "Agent",
                "tool_input": {"subagent_type": role, "prompt": "review"}}
        out = self.run_script("setup_gate.py", hook=hook, env=env)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"] if out.stdout.strip() else None

    def test_denies_team_role_after_scan_only(self):
        skill = user([{"type": "text", "text": 'Skip it only when the user says "defaults" or "skip setup"'}],
                     isMeta=True)  # the skill body names the opt-out words: not the user's
        t = [user("/team:team usa 2 agenti sonnet e fai una codereview"), skill,
             tool("Bash", command='"py" "C:/x/tw.py" scan')]
        self.assertEqual(self.gate(t), "deny")

    def test_allows_after_options_and_question(self):
        t = [user("/team review"), tool("Bash", command='"py" "C:/x/tw.py" options --app claude'),
             tool("AskUserQuestion", questions=[])]
        self.assertIsNone(self.gate(t))

    def test_question_before_options_is_not_enough(self):
        t = [user("/team review"), tool("AskUserQuestion", questions=[]),
             tool("Bash", command="python tw.py options --app claude")]
        self.assertEqual(self.gate(t), "deny")

    def test_user_opt_out_and_builtin_agents_pass(self):
        self.assertIsNone(self.gate([user("/team review, skip setup")]))
        self.assertIsNone(self.gate([user("/team review")], role="Explore"))
        self.assertIsNone(self.gate([user("/team review")], env={"TEAM_WORKFLOW_SETUP_GATE": "0"}))

    def test_session_wizard_off(self):
        with open(os.path.join(self.tmp, ".team-workflow", "settings.json"), "w") as f:
            json.dump({"update_check": False, "session_wizard": False}, f)
        self.assertIsNone(self.gate([user("/team review")]))


if __name__ == "__main__":
    unittest.main()
