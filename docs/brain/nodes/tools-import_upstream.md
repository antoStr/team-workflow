---
id: tools-import_upstream
title: import_upstream.py
layer: tools
tags: [code, py]
aliases: [tools/import_upstream.py, import_upstream.py]
upstream:
downstream:
files: [tools/import_upstream.py]
status: active
last_updated: 2026-11-08T16:54:25
---

# import_upstream.py

Import the upstream agent collection (Everything Claude Code, MIT license, see
library/NOTICE.md) into team-workflow:

    python3 tools/import_upstream.py <path to the upstream checkout>

- Upstream agents that team-workflow has no role for become roles in
  skills/team-workflow/roles/<pack>/<role>.md. Their model is dropped (the settings choose it)
  and so is their prompt-defense block (every role gets roles/_shared/untrusted-input.md).
  The agents team-workflow already covers (COVERED) are imported too, as alternative versions:
  alt-<name> in the alt pack (off by default).
- Upstream skills, commands and rules become the library, skills/team-workflow/library/<id>/,
  each with MAIN.md instead of SKILL.md, so no app loads hundreds of skills by itself, and
  library/index.json; `tw.py library` searches them and installs the chosen ones as skills.
  Entries that only serve the upstream project itself (its installer, its repository, its
  scripts) are left out: everything in the library works on its own.
- Role text names neither the upstream project nor its paths: `skills/<id>/SKILL.md` becomes
  the library entry.

Rerun it after an upstream update: the library is rebuilt and the imported roles are rewritten;
a role file without the `source: "imported` line is never overwritten. An upstream agent that
is in neither IMPORT nor COVERED stops the import, so every new agent gets a decision.

## Contracts


### Functions
- `read(path)`
- `write(path, text)`
- `front(text)`
- `neutral(text, ids)`
- `neutral_main(path, ids)`
- `drop_defense(body)`
- `import_agents(ecc)`
- `digest(folder)`
- `one_line(text)`
- `entry(eid, kind, pack, description, folder)`
- `skill_packs(ecc)`
- `extra_skills(ecc)`
- `command_files(ecc)`
- `import_library(ecc)`
- `main(argv)`

## Dependencies
### Upstream
- None
### Downstream
- None
