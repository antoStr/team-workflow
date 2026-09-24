---
description: Fix a bug the safe way - reproduce it as a failing test first, then fix, verify and report
argument-hint: "<bug description or issue link>"
---

Use the team-workflow skill to fix this bug: $ARGUMENTS

1. `tester` reproduces the bug as a failing regression test (verdict `REPRODUCED`). If it
   cannot, report what was tried and ask the user for details.
2. `backend-dev` or `frontend-dev` fixes the root cause until the test passes, touching only
   the files you assign.
3. `tester` verifies the fix and the callers that could regress; add `security-reviewer` when
   the bug is security-related.
4. Record the lesson under "Known traps" in the area card, update `STATE.md` and give the
   end-of-task report.

For a trivial bug you may do the steps yourself, but the failing test still comes first.
