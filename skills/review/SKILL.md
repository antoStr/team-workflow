---
name: review
description: Independent review of the current changes - tests, code quality and security, with one verdict
argument-hint: "[commit range, PR number or files; default: uncommitted and unpushed changes]"
disable-model-invocation: true
---

Use the team-workflow skill to review: $ARGUMENTS
(With no argument: the uncommitted changes and the commits not pushed yet.)

1. Collect the diff and tell each reviewer exactly what it covers.
2. In parallel: `tester` (runs the checks, tests the behavior) and `code-reviewer` (quality);
   add `security-reviewer` when the diff touches security-sensitive code.
3. Merge their findings, drop duplicates, order them by severity.
4. Report the verdicts and the findings, then ask the user which findings to fix
   (AskUserQuestion, multiSelect). Change no code before the user answers.
