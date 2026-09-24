---
name: feature
description: Build a feature with the team - plan, choose the agents, implement, verify, review, report
argument-hint: "<what to build>"
disable-model-invocation: true
---

Use the team-workflow skill to build this feature: $ARGUMENTS

1. Read the memory and the cards of the areas involved.
2. Size the task. If it is structural, start with `architect` and let the user choose an
   option before any code is written.
3. Propose the team with AskUserQuestion, recommended roles first.
4. Split the work into items (owner, files, acceptance tests) and dispatch them.
5. `tester` verifies, then `code-reviewer` reviews; add `security-reviewer` when the change
   touches security-sensitive code.
6. Update the memory and give the end-of-task report.
