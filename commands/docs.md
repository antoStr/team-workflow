---
description: Write or refresh documentation for people from the project memory - architecture, onboarding, changelog, README - with every fact checked against the code
argument-hint: "[architecture | onboarding | changelog | readme | all]"
---

Use the team-workflow skill to write documentation from the project memory: $ARGUMENTS

1. Read `docs/memory` (INDEX, STATE, MAP, the area cards, DECISIONS, PLAYBOOKS, ACCESS). If it
   is missing, offer `/team-workflow:init` first; if it looks outdated, have `doc-keeper` fix it
   before writing anything from it.
2. Agree what to write, where and in which language (AskUserQuestion; numbered options in agy):
   architecture overview (for example `docs/ARCHITECTURE.md`), onboarding or contributing guide,
   changelog from `STATE.md` and `git log`, README sections. Existing files are updated, not
   replaced.
3. Run the assignment wizard for `technical-writer`.
4. Every fact comes from the memory and is checked against the code; every command shown is run
   first. Nothing in the documentation may contradict the memory: if they disagree, the code
   decides and the memory is corrected too.
5. Report the files written, what each covers, and the facts that could not be verified.
