---
id: project-genome
title: Project Architectural Genome
type: genome
updated: "2026-11-20T12:07:00.270965+00:00"
---

# Project Architectural Genome

Assimilated from codebase AST/regex contracts, `72` git commits, and `4` active vaccines.

## Stack & Verification Commands
- Languages: Python
- Frameworks: none
- Test Suites: pytest
- Commands: `pytest`

## Architectural Hubs (Centrality)
| Module | File | In | Out | Centrality |
|---|---|---:|---:|---:|
| `skills-team-scripts-roles` | `skills/team/scripts/roles.py` | 21 | 21 | 63 |
| `skills-team-scripts-settings` | `skills/team/scripts/settings.py` | 19 | 19 | 57 |
| `tests-isolate_home` | `tests/isolate_home.py` | 21 | 15 | 57 |
| `skills-team-scripts-tw` | `skills/team/scripts/tw.py` | 17 | 17 | 51 |
| `skills-team-scripts-cortex` | `skills/team/scripts/cortex.py` | 12 | 12 | 36 |
| `skills-team-scripts-doctor` | `skills/team/scripts/doctor.py` | 10 | 10 | 30 |
| `skills-team-scripts-library` | `skills/team/scripts/library.py` | 9 | 9 | 27 |
| `tests-test_opencode` | `tests/test_opencode.py` | 8 | 8 | 24 |
| `tests-test_cortex` | `tests/test_cortex.py` | 7 | 8 | 22 |
| `skills-team-scripts-talk` | `skills/team/scripts/talk.py` | 7 | 7 | 21 |

## Co-Change Coupling Rules
- `.claude-plugin/plugin.json` <-> `plugin.json` (21 co-changes, conf=0.88)
- `.claude-plugin/plugin.json` <-> `README.md` (19 co-changes, conf=0.73)
- `README.md` <-> `plugin.json` (17 co-changes, conf=0.65)
- `README.md` <-> `docs/CATALOG.md` (14 co-changes, conf=0.54)
- `.claude-plugin/plugin.json` <-> `docs/CATALOG.md` (13 co-changes, conf=0.54)
- `docs/CATALOG.md` <-> `plugin.json` (13 co-changes, conf=0.59)
- `docs/CATALOG.md` <-> `docs/memory/STATE.md` (9 co-changes, conf=0.56)
- `README.it.md` <-> `docs/CATALOG.it.md` (8 co-changes, conf=1.00)
- `README.it.md` <-> `docs/CATALOG.md` (8 co-changes, conf=0.50)
- `README.it.md` <-> `docs/memory/STATE.md` (8 co-changes, conf=0.61)

## Fragility Hotspots (Fix/Revert Density)
- `.claude-plugin/plugin.json` (18 fix/revert commits)
- `plugin.json` (16 fix/revert commits)
- `README.md` (13 fix/revert commits)
- `docs/memory/STATE.md` (13 fix/revert commits)
- `docs/CATALOG.md` (12 fix/revert commits)
- `README.it.md` (9 fix/revert commits)
- `docs/CATALOG.it.md` (9 fix/revert commits)
- `skills/team/SKILL.md` (7 fix/revert commits)
