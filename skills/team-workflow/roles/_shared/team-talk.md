## Team talk

When your assignment names a team channel (a topic and the `tw.py talk` command), you work with
the other agents of the task through it, not alone:

- Post what others need as soon as you have it: a `finding` or a `note`, with evidence
  (`file:line`, the command and its output). `--to <role>` for one agent, nothing for everyone.
- Read the channel (`talk read <topic> --for <your role>`) before you start, at each milestone
  and before your final answer; to wait for a reply, add `--wait 120`.
- Answer every `question` and `challenge` addressed to you: a `fix` with the evidence, or an
  `answer` that disputes it with evidence. Never ignore one.
- Challenge any claim you doubt, including another agent's "it works": rerun its command or
  read its diff first, then post a `challenge` naming the claim and what you saw.
- Close a challenge you opened with a `verdict` (`--re <id>`, "accepted" or "rejected" and
  why) only after you checked the fix yourself.
- Disagree openly when the evidence says so; agreeing to end the discussion is a failure.
  Keep messages short: facts, evidence, the next step.
