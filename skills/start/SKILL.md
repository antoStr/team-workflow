---
name: start
description: Start team-workflow - session setup (where choices are saved, preset, roles, model and effort per role, skills, add-ons, team talk), then choose what to do - new feature, fix a bug, review, call a team, release, docs, memory, usage
argument-hint: "[task description]"
disable-model-invocation: true
---

Use the team-workflow skill. Run its session setup first (`WIZARD.md`, "Session setup"): show
`tw.py options --app <claude|agy|opencode>` for the app you run in, then ask with the question tool
where the choices go, the preset, the roles, model and effort for every chosen role, the
skills and add-ons, and team talk, then the session recap.

Then, if the user gave a task: $ARGUMENTS
size it and continue as the team-workflow skill says (section 2).

With no task, ask with the question tool what to do now, one option per workflow, recommended
first: new feature, fix a bug, review changes, call a team, release, write docs, set up or
update the memory, usage and costs. Then run that workflow.
