---
id: learn-avoid-bare-word-nothing-in-library-descriptions
title: "Avoid bare word nothing in library descriptions"
type: learning
category: bug
tags: ["#learning", "#bug"]
applies_to: ["tools/import_strix.py", "library"]
confidence: 1
source: manual
created: "2026-11-08T14:58:22.036533+00:00"
---

# Learning: Avoid bare word nothing in library descriptions

> [!WARNING] Anti-Pattern / What to Avoid
> **Trigger**: test_setup_library_talk negative test zzzz-nothing split into zzzz and nothing
> ```
> Using bare word nothing in skill description
> ```

> [!TIP] Verified Solution / Required Pattern
> ```
> Use domain-specific phrases like no immunity or zero guarantee
> ```

## Connected Context
- Target Roles: library
- Target Modules: tools/import_strix.py
