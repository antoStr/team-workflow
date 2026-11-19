---
id: skills-team-scripts-questions
title: questions.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/questions.py, questions.py]
upstream:
  - "[[skills-team-scripts-cortex]]"
  - "[[skills-team-scripts-library]]"
  - "[[skills-team-scripts-roles]]"
downstream:
  - "[[skills-team-scripts-tw]]"
files: [skills/team/scripts/questions.py]
status: active
last_updated: 2026-11-19T11:50:06
---

# questions.py

The session setup questions, ready for the app's question tool (`tw.py questions`).

The model used to pick which roles and skills to offer and dropped most of them; agy and
Claude Code also asked different things. These calls are the same in every app: every enabled
role, the library skills for the task, model and effort for every chosen role. Claude Code's
AskUserQuestion takes 2-4 options per question and 4 questions per call, so long lists are
split; the tool's free-text "Other" takes any role or library id not shown.

## Contracts


### Functions
- `chunks(items, size)`
- `calls(questions)`
- `short(text, size)`
- `role_text(role, root)`
- `setup_calls(data, task_words, config, root)`
- `model_options(data, current)`
- `effort_options(data, model, current)`
- `model_calls(data, chosen)`

## Dependencies
### Upstream
- [[skills-team-scripts-cortex]]
- [[skills-team-scripts-library]]
- [[skills-team-scripts-roles]]
### Downstream
- [[skills-team-scripts-tw]]
