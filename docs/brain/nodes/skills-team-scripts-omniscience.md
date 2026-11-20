---
id: skills-team-scripts-omniscience
title: omniscience.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/omniscience.py, omniscience.py]
upstream:
  - "[[skills-team-scripts-roles]]"
downstream:
  - "[[skills-team-scripts-cortex]]"
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_cortex]]"
  - "[[tests-test_prose_budget]]"
files: [skills/team/scripts/omniscience.py]
status: active
last_updated: 2026-11-20T11:45:45
---

# omniscience.py

Omniscient & Neuro-Symbolic Cortex v3 Engines for team-workflow.

Addresses the 2025-2026 documented failure modes of coding agents:
1. Environment & Runtime Sensor: safe .env key drift, dependency drift, occupied ports, git conflicts.
2. Shadow Spec & Latent Intent Synthesizer: unwritten invariants + AST call-site signature contracts.
3. Anti-Tamper Test & Security Shield: detects test assertion deletions/skips, silent excepts, RLS/TLS weakening.
4. Pre-Flight AST Contract Diff Simulator: detects breaking signature/arity mutations before commit.
5. Loop Circuit-Breaker & Counterfactual Recovery: trips at >=2 repeated error fingerprints (MAST loops).
6. Darwin-Godel Role Auto-Mutation (TextGrad): evolves project-local .team-workflow/agents/<role>.md overrides.
7. Zero-Entropy Telemetry Protocol: high-density claim/diff/contract/proof inter-agent schema.

## Contracts


### Functions
- `_ensure_cortex_gitignore(root)`
- `_read_env_keys(path)`
- `_probe_local_ports(ports)`
- `_find_conflict_files(root)`
- `sense_environment(root)`
- `_extract_py_signatures(source)`
- `_extract_js_signatures(source)`
- `synthesize_shadow_spec(task_text, root, files, domains)`
- `_git_diff_text(root)`
- `audit_anti_tamper(root, diff_text)`
- `_compare_sources(before_src, after_src, file_label)`
- `check_ast_contracts(root, files, before_source, after_source, file_label)`
- `_normalize_error(error_text)`
- `record_attempt_and_check_circuit(root, command, error_text, reset)`
- `mutate_role_agent(root, role, lesson, trigger, anti_pattern, solution)`
- ... and 1 more functions

## Dependencies
### Upstream
- [[skills-team-scripts-roles]]
### Downstream
- [[skills-team-scripts-cortex]]
- [[skills-team-scripts-tw]]
- [[tests-test_cortex]]
- [[tests-test_prose_budget]]
