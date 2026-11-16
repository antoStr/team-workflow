---
id: learn-use-safe-rmtree-for-temp-git-clones-on-windows
title: "Use safe_rmtree for temp git clones on Windows"
type: learning
category: bug
tags: ["#learning", "#bug"]
applies_to: ["backend-dev", "skills/team/scripts/update_plugin.py"]
confidence: 1
source: "manual"
created: "2026-11-16T01:08:25.509754+00:00"
---

# Learning: Use safe_rmtree for temp git clones on Windows

> [!WARNING] Anti-Pattern / What to Avoid
> **Trigger**: update_plugin.py failed updating opencode and codex on Windows because git clone left read-only pack files
> ```
> Calling shutil.rmtree(..., ignore_errors=True) on directories that contain .git objects
> ```

> [!TIP] Verified Solution / Required Pattern
> ```
> Use safe_rmtree which clears read-only flags before unlinking on Windows
> ```

## Connected Context
- Target Roles: `backend-dev`
- Target Modules: `skills/team/scripts/update_plugin.py`
