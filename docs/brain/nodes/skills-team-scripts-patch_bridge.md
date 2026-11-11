---
id: skills-team-scripts-patch_bridge
title: patch_bridge.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/patch_bridge.py, patch_bridge.py]
upstream:
downstream:
  - "[[tests-test_v230_features]]"
files: [skills/team/scripts/patch_bridge.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# patch_bridge.py

Patch-Bridge: Atomic Unified Diff & Subagent Patch Patcher.

Allows subagents or CI pipelines to generate unified diff patches (unified diff,
git diff, or markdown ```diff blocks) that can be applied atomically across
repositories without requiring raw multi-file edit permissions.

## Contracts


### Functions
- `extract_diff_from_text(text)`
- `parse_unified_diff(diff_text)`
- `apply_file_hunks(original_lines, hunks)`
- `apply_patch(diff_content, root, dry_run)`

## Dependencies
### Upstream
- None
### Downstream
- [[tests-test_v230_features]]
