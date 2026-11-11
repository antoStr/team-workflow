---
id: skills-team-scripts-gate
title: gate.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/gate.py, gate.py]
upstream:
downstream:
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_autolearn_gate_smoke]]"
files: [skills/team/scripts/gate.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# gate.py

Adversarial Gating Protocol (Builder ⚔️ Breaker) for team-workflow.

Enforces strict verification where code written by a Builder role (e.g. backend-dev)
must survive attack attempts by an adversarial Breaker role (e.g. pentester, tester,
or performance-engineer) before it can pass the gate into main/production.

When a flaw is proven via PoC, the gate BLOCKS until fixed, and the lesson is
automatically fed into autolearn.py so the team never repeats the mistake.

## Contracts


### Functions
- `_ensure_dir(path)`
- `_slug(text)`
- `gates_path(root)`
- `_validate_gate_id(gate_id)`
- `load_gate(gate_id, root)`
- `save_gate(gate, root)`
- `create_gate(root, target, builder, breaker, topic, hypothesis)`
- `block_gate(root, gate_id, poc, challenger)`
- `pass_gate(root, gate_id, evidence, verifier)`
- `list_gates(root, topic)`
- `active_blocking_gates(root, topic)`

## Dependencies
### Upstream
- None
### Downstream
- [[skills-team-scripts-tw]]
- [[tests-test_autolearn_gate_smoke]]
