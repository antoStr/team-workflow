---
id: project-genome
title: Project Architectural Genome
type: genome
updated: "2026-11-20T10:45:46.338753+00:00"
---

# Project Architectural Genome

Assimilated from codebase AST/regex contracts, `70` git commits, and `3` active vaccines.

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
| `tests-isolate_home` | `tests/isolate_home.py` | 20 | 15 | 55 |
| `skills-team-scripts-tw` | `skills/team/scripts/tw.py` | 17 | 17 | 51 |
| `skills-team-scripts-cortex` | `skills/team/scripts/cortex.py` | 11 | 11 | 33 |
| `skills-team-scripts-doctor` | `skills/team/scripts/doctor.py` | 10 | 10 | 30 |
| `skills-team-scripts-library` | `skills/team/scripts/library.py` | 9 | 9 | 27 |
| `tests-test_opencode` | `tests/test_opencode.py` | 8 | 8 | 24 |
| `tests-test_cortex` | `tests/test_cortex.py` | 7 | 8 | 22 |
| `skills-team-scripts-talk` | `skills/team/scripts/talk.py` | 7 | 7 | 21 |

## Co-Change Coupling Rules
- `.claude-plugin/plugin.json` <-> `plugin.json` (20 co-changes, conf=0.87)
- `.claude-plugin/plugin.json` <-> `README.md` (18 co-changes, conf=0.72)
- `README.md` <-> `plugin.json` (16 co-changes, conf=0.64)
- `README.md` <-> `docs/CATALOG.md` (13 co-changes, conf=0.52)
- `.claude-plugin/plugin.json` <-> `docs/CATALOG.md` (12 co-changes, conf=0.52)
- `docs/CATALOG.md` <-> `plugin.json` (12 co-changes, conf=0.57)
- `docs/CATALOG.md` <-> `docs/memory/STATE.md` (8 co-changes, conf=0.53)
- `README.it.md` <-> `docs/CATALOG.it.md` (7 co-changes, conf=1.00)
- `README.it.md` <-> `docs/CATALOG.md` (7 co-changes, conf=0.47)
- `README.it.md` <-> `docs/memory/STATE.md` (7 co-changes, conf=0.58)

## Fragility Hotspots (Fix/Revert Density)
- `.claude-plugin/plugin.json` (16 fix/revert commits)
- `plugin.json` (14 fix/revert commits)
- `README.md` (11 fix/revert commits)
- `docs/memory/STATE.md` (11 fix/revert commits)
- `docs/CATALOG.md` (10 fix/revert commits)
- `README.it.md` (7 fix/revert commits)
- `docs/CATALOG.it.md` (7 fix/revert commits)
- `skills/team/SKILL.md` (6 fix/revert commits)
