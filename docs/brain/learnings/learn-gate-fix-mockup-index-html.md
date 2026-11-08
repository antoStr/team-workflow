---
id: learn-gate-fix-mockup-index-html
title: "Gate Fix: mockup/index.html"
type: learning
category: bug
tags: ["#learning", "#bug"]
applies_to: ["frontend-dev", "mockup/index.html"]
confidence: 1
source: gate:gate-mockup-index-html-9919
created: "2026-11-08T14:58:55.222250+00:00"
---

# Learning: Gate Fix: mockup/index.html

> [!WARNING] Anti-Pattern / What to Avoid
> **Trigger**: Breaker pentester blocked gate with PoC: Hash fragment #alert(1) unescaped in innerHTML
> ```
> Hash fragment #alert(1) unescaped in innerHTML
> ```

> [!TIP] Verified Solution / Required Pattern
> ```
> Replaced innerHTML with textContent and validated encodeURIComponent sanitization.
> ```

## Connected Context
- Target Roles: frontend-dev
- Target Modules: mockup/index.html
