---
id: skills-team-scripts-talk
title: talk.py
layer: skills
tags: [code, py]
aliases: [skills/team/scripts/talk.py, talk.py]
upstream:
  - "[[skills-team-scripts-settings]]"
downstream:
  - "[[skills-team-scripts-tw]]"
  - "[[tests-test_brain]]"
  - "[[tests-test_setup_library_talk]]"
  - "[[tests-test_v230_features]]"
files: [skills/team/scripts/talk.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# talk.py

Team talk: one channel per task where everybody working on it talks together: the
orchestrator, every agent, and anyone who joins later (another agent, the user). They debug
together, challenge each other's claims and verify each other's work (TALK.md).

A topic is one JSON line per message in <git common dir>/team-workflow/talk/<topic>.jsonl: the
common dir is shared by every worktree of the repository, so agents in separate worktrees see
the same channel, and it is never committed. Outside a repository: ~/.team-workflow/talk/.

Message: {"id", "time", "from", "to" (a role, or null for everyone), "kind", "re" (the id it
answers), "text"}. A question stays open until a reply with re=its id; a challenge stays open
until a verdict with re=its id. `open_threads` is the orchestrator's gate before "done".
<topic>.seen.json keeps, per role, the last message it read: `read --for ROLE` shows only what
is new for that role, so agents never track ids nor reread the history. A `join` message says
who takes part and what they own; a newcomer reads the whole history first.

## Contracts

### Classes
- `_Lock` (methods: __init__, __enter__, __exit__)
- `Unread` (methods: __init__)

### Functions
- `channel_dir(cwd)`
- `path(topic, cwd)`
- `read(topic, cwd)`
- `post(topic, sender, text, kind, to, re_id, cwd)`
- `for_role(msgs, role, since)`
- `_cursors_path(topic, cwd)`
- `seen(topic, role, cwd)`
- `mark_seen(topic, role, last, cwd)`
- `unread(topic, role, since, cwd)`
- `wait(topic, role, since, timeout, poll, cwd)`
- `open_threads(msgs)`
- `unread_by_role(topic, cwd)`
- `members(msgs)`
- `topics(cwd)`
- `clear(topic, cwd)`
- ... and 3 more functions

## Dependencies
### Upstream
- [[skills-team-scripts-settings]]
### Downstream
- [[skills-team-scripts-tw]]
- [[tests-test_brain]]
- [[tests-test_setup_library_talk]]
- [[tests-test_v230_features]]
