---
name: audit
description: Security audit of the AI agent setup - Claude Code and agy settings, permissions, hooks, MCP servers, agents, skills and instruction files - for secrets, risky permissions, download-and-run hooks, unpinned servers and prompt injection (no tokens in Claude Code; in agy run `!team-workflow audit`)
argument-hint: "[--strict] [--json]"
disable-model-invocation: true
---

In Claude Code a hook answers this command without the model; you only see it when that hook
did not run. Then run `python3 <team-workflow skill folder>/scripts/tw.py audit $ARGUMENTS`
from the repository root and show its output. If the user asks for fixes, propose them one by
one and change configuration only after they agree; never print a secret, and tell the user
to rotate any secret the audit found.
