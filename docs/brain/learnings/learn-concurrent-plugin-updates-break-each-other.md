---
id: learn-concurrent-plugin-updates-break-each-other
title: "Concurrent plugin updates break each other"
type: learning
category: bug
tags: ["#learning", "#bug"]
applies_to: ["*"]
confidence: 1
source: "manual"
created: "2026-11-20T12:06:35.059496+00:00"
---

# Learning: Concurrent plugin updates break each other

> [!WARNING] Anti-Pattern / What to Avoid
> **Trigger**: auto update at session start while the user runs tw.py update
> ```
> two update_plugin runs share ~/.team-workflow/*-update and the Claude marketplace clone
> ```

> [!TIP] Verified Solution / Required Pattern
> ```
> update_plugin.hold_lock: one run at a time, the second waits then rereads versions
> ```

## Connected Context
- Target Roles: All roles
- Target Modules: All modules
