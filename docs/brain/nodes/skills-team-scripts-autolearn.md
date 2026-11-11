---
id: skills-team-scripts-autolearn
title: autolearn.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/autolearn.py, autolearn.py]
upstream:
downstream:
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_autolearn_gate_smoke]]"
files: [skills/team/scripts/autolearn.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# autolearn.py

Autonomous Self-Improvement and Continuous Learning Engine for team-workflow.

Extracts anti-patterns, bug fixes, performance optimizations, and security lessons from:
1. Team Talk challenges and accepted fixes (builder ⚔️ breaker interactions).
2. Git fix/revert commits and test failure patterns.
3. Explicit agent/human recordings.

Saves learnings into docs/brain/learnings/ as Obsidian graph nodes, mirrors them into
docs/memory/LEARNINGS.md, and injects 'vaccines' (preventive constraints) into agent prompts.

## Contracts


### Functions
- `_slug(text)`
- `_ensure_dir(path)`
- `learnings_path(root)`
- `load_index(root)`
- `save_index(index_data, root)`
- `record_learning(root, title, trigger, anti_pattern, solution, applies_to, category, confidence, source)`
- `_mirror_to_memory(learnings, root)`
- `get_vaccines(root, file_path, role, limit)`
- `format_vaccine_prompt(vaccines)`
- `auto_learn_from_talk(root, topic)`
- `list_learnings(root)`

## Dependencies
### Upstream
- None
### Downstream
- [[skills-team-scripts-tw]]
- [[tests-test_autolearn_gate_smoke]]
