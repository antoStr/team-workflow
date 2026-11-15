---
name: pm-risk
description: Project risk management for threats and opportunities - identification (risk breakdown structure, assumptions analysis, SWOT, checklists, lessons learned), writing risks as cause-event-effect, qualitative probability-impact scoring and heat maps, response strategies (avoid, transfer, mitigate, accept; exploit, share, enhance, accept), owners, triggers, contingency reserves, preventive vs corrective actions, issue logs and risk reviews, with a register template. Use when identifying or reviewing project risks or writing a risk register.
origin: team-workflow
---

# Project risk management

## Concepts

- A **risk** is an uncertain event or condition that, if it occurs, affects at least one
  objective. **Negative** risks are threats; **positive** risks are opportunities.
- An **issue** has already happened: log it in the issue log and act; then ask which risks
  are related.
- **Risk appetite / tolerance**: how much uncertainty the sponsor accepts; it sets the
  threshold above which a risk needs a response.
- **Preventive action**: lowers the probability or the impact before the event.
  **Corrective action**: brings performance back in line after a deviation.
  **Contingency plan**: what to do if the risk occurs, prepared in advance, started by a trigger.

## Process

1. **Plan**: scales, thresholds, roles, review frequency, register format.
2. **Identify**: whole team plus stakeholders. Sources: assumptions and constraints (what if
   each is false?), WBS and schedule (long, new or parallel work, single suppliers), lessons
   learned, checklists by category, SWOT (strengths, weaknesses, opportunities, threats).
3. **Analyze**: probability and impact, level, ranking; quantitative analysis (Monte Carlo on
   the schedule, expected monetary value) only when the stakes justify it.
4. **Plan responses**: strategy, actions, owner, trigger, budget.
5. **Implement and monitor**: run the actions, watch triggers, review the register on a
   schedule, close the risks that passed, add new ones.

**Risk breakdown structure** (example categories): technical (requirements, technology,
complexity, quality), external (suppliers, regulation, market, weather), organizational
(resources, funding, priorities), project management (estimates, planning, communication).

## Write a risk precisely

"Because of **<cause>**, **<event>** may occur, which would lead to **<effect on objective>**."

Bad: "Supplier risk." Good: "Because the only certified supplier is at full capacity, delivery
of the switches may slip by four weeks, which would delay go-live and the first invoice."

## Qualitative analysis

Use one agreed scale for every risk, for example 1-5:

| Score | Probability | Impact on time | Impact on cost |
|---|---|---|---|
| 1 | < 10% | < 1 week | < 1% of budget |
| 3 | 30-50% | 2-4 weeks | 5-10% |
| 5 | > 70% | > 2 months | > 20% |

**Level** = probability x impact (1-25). A heat map places the risks on the grid:

```text
Impact ->   1    2    3    4    5
P 5        M    H    H    VH   VH
P 4        M    M    H    H    VH
P 3        L    M    M    H    H
P 2        L    L    M    M    H
P 1        L    L    L    M    M
```

Rank by level, but look separately at low-probability, high-impact risks: they rarely top the
list and can end a project.

## Response strategies

| Threats | Opportunities | What it means |
|---|---|---|
| Avoid | Exploit | change the plan so the event cannot happen / make sure it happens |
| Transfer | Share | give it to a party better placed to handle it (insurance, contract) / partner to capture it |
| Mitigate | Enhance | lower / raise the probability or the impact |
| Accept (active or passive) | Accept | keep it; active means a contingency reserve or plan |
| Escalate | Escalate | outside the project's authority: hand it to the program or the sponsor |

Every response has an **owner** (one person), **actions with dates**, a **trigger**, and the
**residual risk** (what remains after the response) and **secondary risks** (new risks the
response creates). Transfer moves the consequence, not always the risk itself, and costs a
premium.

## Contingency

Size the contingency reserve from the accepted risks, for example by expected monetary value
(probability x impact in money, summed for threats and subtracted for opportunities) or by
schedule simulation. Keep it visible and separate from the estimates.

## Register (template)

```markdown
| ID | Category | Cause - event - effect | P | I | Level | Strategy | Actions (date) | Owner | Trigger | Status | Reviewed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | External | Because ..., ... may ..., leading to ... | 3 | 4 | 12 | Mitigate | Second supplier qualified (2026-03-15) | M. Rossi | PO not confirmed by 03-01 | Open | 2026-02-10 |
```

## Reviews

At every status cycle: new risks, changed scores, actions done, triggers fired, risks closed.
At phase gates and at closure: which risks occurred, which responses worked, what goes into the
lessons learned.

Related entries: `pm-lifecycle`, `pm-control` (reserves), `pm-schedule` (buffers, three-point
estimates).
