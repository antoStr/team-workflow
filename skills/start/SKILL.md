---
name: start
description: Start team-workflow - session setup (preset, roles, model and effort per role), then choose what to do - new feature, fix a bug, review, call a team, release, docs, memory, usage
argument-hint: "[task description]"
disable-model-invocation: true
---

Use the team-workflow skill. Run its session setup first (`WIZARD.md`, "Session setup"): show
`tw.py options --app <claude|agy|opencode>` for the app you run in, then ask preset, roles, and
model and effort for every chosen role with the question tool, then the session board.

Then, if the user gave a task: $ARGUMENTS
size it and continue as the team-workflow skill says (section 2).

With no task, ask with the question tool what to do now, one option per workflow, recommended
first: new feature, fix a bug, review changes, call a team, release, write docs, set up or
update the memory, usage and costs. Then run that workflow.
