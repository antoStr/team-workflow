---
id: skills-team-scripts-cortex
title: cortex.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/cortex.py, cortex.py]
upstream:
  - "[[skills-team-scripts-autolearn]]"
  - "[[skills-team-scripts-brain]]"
  - "[[skills-team-scripts-library]]"
  - "[[skills-team-scripts-omniscience]]"
  - "[[skills-team-scripts-roles]]"
  - "[[skills-team-scripts-scan]]"
  - "[[skills-team-scripts-settings]]"
  - "[[skills-team-scripts-talk]]"
downstream:
  - "[[skills-team-scripts-questions]]"
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_cortex]]"
files: [skills/team/scripts/cortex.py]
status: active
last_updated: 2026-11-20T11:45:45
---

# cortex.py

Neural Cortex Router, Project Genome Assimilation & Meta-Skill Evolution Engine.

Evolves team-workflow beyond prompt-based multi-agent orchestration into a
resource-aware neural routing & self-evolving system:
1. Sensory Layer: perceives available resources (hardware thermal/RAM headroom,
   app models/efforts, roles, library + learned skills, Brain graph, vaccines)
   and required task resources (14-domain activation, Brain blast radius, risk,
   complexity, verification gates).
2. Hidden/Output Layer: propagates excitatory & inhibitory synaptic activations
   across specialist roles, allocates optimal models/efforts, binds library &
   learned skills, and selects execution topology.
3. Project Knowledge Assimilation: extracts Brain architectural hubs, git
   co-change coupling clusters, fragility hotspots, and verification commands
   into .team-workflow/project_knowledge.json and docs/brain/PROJECT_GENOME.md.
4. Hebbian Plasticity & Meta-Skill Evolution: learns from task outcomes via
   synaptic weight updates and synthesizes reusable SKILL.md modules (including
   `team-meta-cortex`) in .team-workflow/skills/.

## Contracts


### Functions
- `_clamp(val, lo, hi)`
- `_slug(text)`
- `_tokenize(text)`
- `_cortex_dir(root)`
- `_weights_path(root)`
- `_global_weights_path()`
- `_knowledge_path(root)`
- `_read_json(path, default)`
- `_ensure_cortex_gitignore(cortex_dir)`
- `_write_json(path, data)`
- `_empty_weights()`
- `load_weights(root)`
- `_parse_frontmatter(text)`
- `load_learned_skills(root)`
- `_hardware_profile(config)`
- ... and 23 more functions

## Dependencies
### Upstream
- [[skills-team-scripts-autolearn]]
- [[skills-team-scripts-brain]]
- [[skills-team-scripts-library]]
- [[skills-team-scripts-omniscience]]
- [[skills-team-scripts-roles]]
- [[skills-team-scripts-scan]]
- [[skills-team-scripts-settings]]
- [[skills-team-scripts-talk]]
### Downstream
- [[skills-team-scripts-questions]]
- [[skills-team-scripts-tw]]
- [[tests-test_cortex]]
