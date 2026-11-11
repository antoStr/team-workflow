---
id: skills-team-scripts-visual_check
title: visual_check.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/visual_check.py, visual_check.py]
upstream:
downstream:
  - "[[tests-test_v230_features]]"
files: [skills/team/scripts/visual_check.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# visual_check.py

Automated Responsive & Visual Layout Auditor.

Audits web templates for responsive layout integrity:
 1. Viewport meta tag presence
 2. Horizontal overflow risks (fixed pixel widths > 320px without max-width)
 3. CSS Breakpoints coverage (mobile, tablet, desktop)
 4. Touch target sizes and tap friendliness
 5. Heading hierarchy (single <h1> per view)
 6. Motion safety (@media (prefers-reduced-motion))

## Contracts


### Functions
- `audit_html_files(root)`
- `audit_css_files(root)`
- `run_visual_check(root)`

## Dependencies
### Upstream
- None
### Downstream
- [[tests-test_v230_features]]
