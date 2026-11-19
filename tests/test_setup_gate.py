import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import glob
import json
import os
import unittest

from test_scripts import ScriptTest


def user(text, **extra):
    return {"type": "user", "message": {"role": "user", "content": text}, **extra}


def tool(name, **inp):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}}


class SetupGateTest(ScriptTest):
    """The PreToolUse hook holds team roles until the whole session setup ran."""

    def gate(self, transcript, role="code-reviewer", env=None, ask=None):
        path = os.path.join(self.tmp, "t.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(e) + "\n" for e in transcript)
        hook = {"cwd": self.root, "session_id": "s1", "transcript_path": path, "tool_name": "Agent",
                "tool_input": {"subagent_type": role, "prompt": "review"}}
        if ask is not None:  # the hook on AskUserQuestion instead
            hook.update(tool_name="AskUserQuestion",
                        tool_input={"questions": [{"header": h, "question": "?", "options": []} for h in ask]})
        out = self.run_script("setup_gate.py", hook=hook, env=env)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"] if out.stdout.strip() else None

    def test_denies_team_role_after_scan_only(self):
        skill = user([{"type": "text", "text": 'Skip it only when the user says "defaults" or "skip setup"'}],
                     isMeta=True)  # the skill body names the opt-out words: not the user's
        t = [user("/team:team usa 2 agenti sonnet e fai una codereview"), skill,
             tool("Bash", command='"py" "C:/x/tw.py" scan')]
        self.assertEqual(self.gate(t), "deny")

    def setup(self):
        ask = lambda *hs: tool("AskUserQuestion", questions=[{"header": h, "question": q} for h, q in hs])
        return [user("/team review"), tool("Bash", command='"py" "C:/x/tw.py" options --app claude'),
                tool("Bash", command='"py" "C:/x/tw.py" questions --app claude --task review'),
                ask(("Scope", "Where?"), ("Preset", "Which?"), ("Roles 1/2", "Roles?"), ("Roles 2/2", "Roles?")),
                ask(("Skills 1/1", "Skills?"), ("Team talk", "Talk?")),
                tool("Bash", command='"py" "C:/x/tw.py" questions --app claude --roles tester'),
                ask(("tester", "Model for tester?"), ("tester", "Effort for tester?"))]

    def test_allows_after_the_whole_setup(self):
        t = self.setup()
        self.assertIsNone(self.gate(t, role="tester"))
        self.assertEqual(self.gate(t, role="code-reviewer"), "deny")  # no model question for it
        self.assertEqual(self.gate(t[:6], role="tester"), "deny")  # groups asked, model and effort not yet
        self.assertEqual(self.gate(t[:3] + t[4:], role="tester"), "deny")  # skills never asked

    def test_translated_text_counts_by_header(self):
        t = self.setup()
        for q in t[3]["message"]["content"][0]["input"]["questions"] + t[6]["message"]["content"][0]["input"]["questions"]:
            q["question"] = "Domanda tradotta?"
        self.assertIsNone(self.gate(t, role="tester"))

    def test_made_up_question_does_not_count(self):
        t = self.setup()
        t[3] = tool("AskUserQuestion", questions=[{"header": "Confirm", "question": "Start?"}])
        self.assertEqual(self.gate(t, role="tester"), "deny")
        t = self.setup()
        t[3]["message"]["content"][0]["input"]["questions"].pop()  # "Roles 2/2" never asked
        self.assertEqual(self.gate(t, role="tester"), "deny")

    def test_a_retry_asks_only_the_gaps(self):
        t = self.setup()
        t[3]["message"]["content"][0]["input"]["questions"].pop()  # "Roles 2/2" skipped
        self.assertEqual(self.gate(t, role="tester"), "deny")
        t.append(tool("AskUserQuestion", questions=[{"header": "Roles 2/2", "question": "Roles?"}]))
        self.assertIsNone(self.gate(t, role="tester"))

    def test_question_check_during_the_setup(self):
        t = self.setup()[:3]  # `questions` ran, nothing asked yet
        self.assertEqual(self.gate(t, ask=["Ruoli"]), "deny")  # made up
        self.assertEqual(self.gate(t, ask=["tester", "tester"]), "deny")  # model before the groups
        self.assertIsNone(self.gate(t, ask=["Scope", "Preset", "Roles 1/2", "Roles 2/2"]))
        self.assertIsNone(self.gate(self.setup()[:1], ask=["Anything"]))  # no setup running
        self.assertIsNone(self.gate(self.setup()[:5], ask=["Whatever"]))  # setup groups done

    def test_user_opt_out_and_builtin_agents_pass(self):
        self.assertIsNone(self.gate([user("/team review, skip setup")]))
        self.assertIsNone(self.gate([user("/team review")], role="Explore"))
        self.assertIsNone(self.gate([user("/team review")], env={"TEAM_WORKFLOW_SETUP_GATE": "0"}))

    def printed_setup(self, task="review"):
        """`tw.py questions --task` as the model runs it: the transcript entry, the printed headers and
        the state file the gate reads them from."""
        out = self.run_script("tw.py", "questions", "--app", "claude", "--task", task, cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stderr)
        printed = [q["header"] for c in json.loads(out.stdout)["calls"] for q in c["questions"]]
        state = glob.glob(os.path.join(self.tmp, ".team-workflow", "setup", "*.json"))
        self.assertEqual(len(state), 1)
        run = tool("Bash", command=f'"py" "C:/x/tw.py" questions --app claude --task {task}')
        run["timestamp"] = "2000-01-01T00:00:00.000Z"  # before the state file was written
        return run, printed, state[0]

    def test_gate_follows_the_headers_questions_printed(self):
        run, printed, _ = self.printed_setup()
        groups = [h for h in printed if h in ("Scope", "Preset") or h.startswith(("Roles ", "Skills "))]
        ask = lambda hs: tool("AskUserQuestion", questions=[{"header": h, "question": "?"} for h in hs])
        base = [user("/team review"), tool("Bash", command='"py" "C:/x/tw.py" options --app claude'), run]
        model = ask(["tester", "tester"])
        self.assertIsNone(self.gate(base + [ask(groups), model], role="tester"))
        self.assertEqual(self.gate(base + [ask(groups[:-1]), model], role="tester"), "deny")

    def test_no_skills_question_when_none_was_printed(self):
        run, _, state = self.printed_setup()
        with open(state, "w", encoding="utf-8") as f:  # under 2 skills found: no "Skills" group printed
            json.dump({"time": 4102444800, "headers": ["Scope", "Preset", "Roles 1/1", "Team talk"]}, f)
        ask = tool("AskUserQuestion", questions=[{"header": h, "question": "?"} for h in
                                                 ("Scope", "Preset", "Roles 1/1", "Team talk", "tester")])
        t = [user("/team review"), tool("Bash", command='"py" "C:/x/tw.py" options --app claude'), run, ask]
        self.assertIsNone(self.gate(t, role="tester"))

    def test_defaults_inside_a_request_keeps_the_setup(self):
        self.assertEqual(self.gate([user("/team reset the parser to its defaults")]), "deny")
        self.assertIsNone(self.gate([user("/team review"), user("defaults")]))
        self.assertIsNone(self.gate([user("/team review"), user("ok, use defaults.")]))

    def test_malformed_transcript_lines_still_deny(self):
        t = [1, "text", {"type": "assistant", "message": "text"},
             {"type": "assistant", "message": {"content": "text"}},
             tool("AskUserQuestion", questions=["Scope", None]), user("/team review")]
        self.assertEqual(self.gate(t), "deny")

    def test_session_wizard_off(self):
        with open(os.path.join(self.tmp, ".team-workflow", "settings.json"), "w") as f:
            json.dump({"update_check": False, "session_wizard": False}, f)
        self.assertIsNone(self.gate([user("/team review")]))


class QuestionsTest(ScriptTest):
    """`tw.py questions`: every enabled role, AskUserQuestion's limits, model and effort per role."""

    def questions(self, *args):
        out = self.run_script("tw.py", "questions", "--app", "claude", *args, cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)

    def test_every_enabled_role_is_offered_within_the_tool_limits(self):
        data = self.questions("--task", "review", "python")
        offered = [o["label"] for c in data["calls"] if c["step"] == "roles" for q in c["questions"]
                   for o in q["options"]]
        enabled = json.loads(self.run_script("tw.py", "options", "--app", "claude", "--json", cwd=self.root).stdout)["roles"]
        self.assertEqual(sorted(offered), sorted(enabled))
        self.assertTrue(any(c["step"] == "skills" for c in data["calls"]))
        for c in data["calls"]:
            self.assertLessEqual(len(c["questions"]), 4)
            for q in c["questions"]:
                self.assertTrue(2 <= len(q["options"]) <= 4, q)
                self.assertLessEqual(len(q["header"]), 12, q)

    def test_model_and_effort_for_every_chosen_role(self):
        data = self.questions("--roles", "tester,code-reviewer,nope")
        self.assertEqual(data["unknown_roles"], ["nope"])
        asked = [q["question"] for c in data["calls"] for q in c["questions"]]
        for role in ("tester", "code-reviewer"):
            self.assertIn(f"Model for {role}?", asked)
            self.assertTrue(any(a.startswith(f"Effort for {role}?") for a in asked))


if __name__ == "__main__":
    unittest.main()
