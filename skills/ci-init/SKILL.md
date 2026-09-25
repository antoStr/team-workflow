---
name: ci-init
description: Add a GitHub Actions workflow that checks the project memory and audits the agent configuration on every pull request and push (no tokens in Claude Code; in agy run `!team-workflow ci-init`)
disable-model-invocation: true
---

In Claude Code a hook answers this command without the model; you only see it when that hook
did not run. Then run `python3 <team-workflow skill folder>/scripts/tw.py ci-init` from the
repository root, show its output, and offer to add the project's build and test commands from
`docs/memory/PLAYBOOKS.md` to the workflow.
