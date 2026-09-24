---
name: ship
description: Release verified work - run the pipeline, prepare version, commit, tag and notes, publish after approval
argument-hint: "[version or notes]"
disable-model-invocation: true
---

Use the team-workflow skill to release: $ARGUMENTS

1. The changes need the tester's `APPROVED` verdict; without it, run `/team-workflow:review`
   first.
2. `release-manager` runs the pipeline from `PLAYBOOKS.md` and prepares version, commit, tag
   and notes.
3. Show the user what will be pushed and published, and ask for approval (AskUserQuestion).
4. Only after the approval: `release-manager` publishes and checks CI.
5. Update `STATE.md` (version, latest changes) and give the end-of-task report.
