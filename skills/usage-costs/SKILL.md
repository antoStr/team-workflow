---
name: usage-costs
description: Token and cost dashboard of this repository - by agent, model and session, with memory health
argument-hint: "[days | latest]"
disable-model-invocation: true
---

Use the team-workflow skill to show the usage dashboard: $ARGUMENTS

1. Run `python3 <team-workflow skill folder>/scripts/dashboard.py --root <repository root> --html`
   with `--days <n>` when the user gave a number, or `--session latest` for "latest".
2. Summarize in the user's language: total cost at API prices, tokens, cache share, the agents
   and models that cost most, memory health; say where the HTML page is and offer to open it.
3. Point out anything worth acting on (an agent on a pricier model than its work needs, low
   cache use, memory warnings), as a proposal only.
