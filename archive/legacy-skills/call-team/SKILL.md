---
name: call-team
description: Call a team of agents for a task you describe - pick several roles (product, frontend, backend, fullstack, data, marketing, quality, release, maintenance, docs, architecture, or any mix), agree model and effort, launch
argument-hint: "[team] <task description>"
disable-model-invocation: true
---

Use the team-workflow skill. Read `TEAMS.md` in the skill's folder, then assemble a team for:
$ARGUMENTS

1. If the first word names a team in `TEAMS.md`, start from that team's roles. Otherwise the
   whole argument is the task: pick the roles it needs from all the agents in `TEAMS.md`, across
   teams. With no task at all, ask the user to describe it first.
2. Run the assignment wizard (`WIZARD.md`): the user picks several roles at once (multi-select),
   then for each agent what it works on, how, model and effort with the estimated cost, then
   the board to confirm.
3. Launch as agreed (native or worker); run independent work in parallel and dependent work in
   order.
4. Collect the results, check them against the evidence, apply the definition of done,
   update the memory and give the end-of-task report.
