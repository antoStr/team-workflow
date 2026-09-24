---
description: Assemble a team (product, frontend, backend, fullstack, data, marketing, quality, release, maintenance, docs, architecture) for a task
argument-hint: "<team> <task>"
---

Use the team-workflow skill. Read `TEAMS.md` in the skill's folder, then assemble a team for:
$ARGUMENTS

1. Take the team from the first word. If it is missing or unknown, show the teams in
   `TEAMS.md` and ask which one (AskUserQuestion).
2. Run the assignment wizard (`WIZARD.md`): the roles this task needs ("Who builds?", "Who
   checks?"), then for each agent what it works on, how, model and effort with the estimated
   cost, then the board to confirm.
3. Launch as agreed (native or worker); run independent work in parallel and dependent work in
   order.
4. Collect the results, check them against the evidence, apply the definition of done,
   update the memory and give the end-of-task report.
