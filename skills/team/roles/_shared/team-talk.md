## Team talk

When your assignment names a team channel (a topic and the `tw.py talk` command), you work in a
group conversation with the orchestrator, the other agents and anyone who joins later, the
user included. You do not work alone:

- First join: `talk join <topic> --as <your role> "what you own"`. It shows you the whole
  conversation so far: read it before you start.
- Post what others need as soon as you have it: a `finding` or a `note`, with evidence
  (`file:line`, the command and its output). `--to <role>` for one, nothing for everyone;
  `--to orchestrator` for a scope question or a decision.
- Read with `talk read <topic> --for <your role>` at each milestone and before your final
  answer: you see only what is new. To ask and wait for the reply in one call:
  `talk post ... --wait 90`; to wait without posting: `talk read ... --wait 90`. A post is
  refused while messages for you are unread: it shows them, take them into account, post again.
- Answer every `question` and `challenge` addressed to you: a `fix` with the evidence, or an
  `answer` that disputes it with evidence. Never ignore one. Post a `fix` only after you ran
  the check it cites, with the result in the same message, never "see next post".
- Challenge any claim you doubt, including another agent's "it works": rerun its command or
  read its diff first, then post a `challenge` naming the claim and what you saw.
- Close a challenge you opened with a `verdict` (`--re <id>`, "accepted" or "rejected" and
  why) only after you checked the fix yourself.
- A `decision` from the orchestrator or the user applies to everyone; your scope and files
  change only with a new assignment.
- Disagree openly when the evidence says so; agreeing to end the discussion is a failure.
  Keep messages short: facts, evidence, the next step.
