---
id: skills-team-scripts-components_cli
title: components_cli.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/components_cli.py, components_cli.py]
upstream:
downstream:
  - "[[tests-test_v230_features]]"
files: [skills/team/scripts/components_cli.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# components_cli.py

Component Scaffolding CLI for Frontend-Components.

Provides direct scaffolding (`tw.py component add <name>`) for modern UI components:
 - cmdk (Command Palette ⌘K / Ctrl+K)
 - sonner (Stacked modern toast notifications)
 - number-flow (Smooth animated numeric rolling counters)
 - vaul (Mobile gesture bottom-sheet drawer)
 - spotlight (Card hover spotlight glow)
 - marquee (Continuous hardware-accelerated partner marquee)
 - dot-grid (Clean editorial background dot grid)

## Contracts


### Functions
- `list_components()`
- `add_component(name, dest_dir, root)`

## Dependencies
### Upstream
- None
### Downstream
- [[tests-test_v230_features]]
