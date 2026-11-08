---
name: profile
description: Apply a team-workflow preset - budget, fast, balanced, thorough, security or research - that changes wizard, team size, models, effort and packs at once (no tokens in Claude Code; in agy run `!team-workflow profile`)
argument-hint: "[budget | fast | balanced | thorough | security | research] [--project]"
disable-model-invocation: true
---

In Claude Code a hook answers this command without the model; you only see it when that hook
did not run. Then run `python3 <team-workflow skill folder>/scripts/tw.py profile $ARGUMENTS`
from the repository root and show its output as it is.
