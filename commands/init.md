---
description: Set up the shared project memory (docs/memory) in this repository and fill it from the code
argument-hint: "[notes about the project]"
---

Use the team-workflow skill to set up the project memory of this repository.

1. If `docs/memory/INDEX.md` already exists, say so, run memcheck and stop.
2. Run `python3 <team-workflow skill folder>/scripts/init_memory.py --root <repository root>`.
3. Fill the memory from the real code, facts only:
   - `STATE.md`: version and the file that holds it, CI, known limits.
   - `PLAYBOOKS.md`: run the detected commands to confirm them; add the release steps.
   - `MAP.md`: every module or package in one line, grouped by area.
   - One card per area in `areas/`, from `areas/_TEMPLATE.md`: key files, contracts, tests,
     known traps.
   - `ACCESS.md`: what each folder holds and what must never be touched.
   In a large repository, split the reading of the areas between `doc-keeper` agents and
   check what they write.
4. Run memcheck and fix what it reports.
5. Report what was created, which commands you confirmed and what the user should check.

Notes from the user: $ARGUMENTS
