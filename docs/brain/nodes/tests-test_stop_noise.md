---
id: tests-test_stop_noise
title: test_stop_noise.py
layer: tests
tags: [code, py]
aliases: [tests/test_stop_noise.py, test_stop_noise.py]
upstream:
  - "[[skills-team-scripts-brain]]"
  - "[[skills-team-scripts-cortex]]"
  - "[[tests-isolate_home]]"
downstream:
files: [tests/test_stop_noise.py]
status: active
last_updated: 2026-11-20T12:09:10
---

# test_stop_noise.py

Stop hook without noise: no false "update STATE.md" after a pull, the cortex and the brain once per
set of changes, no brain node rewritten only for its date.

## Contracts

### Classes
- `StopNoiseTest` (methods: setUp, stop, test_state_in_the_same_commit_as_the_code_passes_whatever_the_mtimes, test_code_committed_after_state_still_asks, test_cortex_records_one_pass_per_set_of_changes, test_genome_not_rewritten_for_its_date_only, test_brain_node_not_rewritten_for_its_date_only)

## Dependencies
### Upstream
- [[skills-team-scripts-brain]]
- [[skills-team-scripts-cortex]]
- [[tests-isolate_home]]
### Downstream
- None
