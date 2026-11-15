---
name: pm-lifecycle
description: Project management end to end, following ISO 21502 and common IPMA/PMI practice - what makes work a project, project vs program vs portfolio, organization structures and the project manager's authority, the five process groups (initiating, planning, implementing, controlling, closing), lifecycles and phase gates, the project charter, baselines, change control, quality management, closure and lessons learned. Use when starting, planning, steering or closing a project, or when writing a charter or a project plan.
origin: team-workflow
---

# Project lifecycle and process groups

## What a project is

A **project** is a temporary, unique set of coordinated activities, with a start and an end,
undertaken to reach objectives within constraints of scope, time, cost, quality and resources.
Its key traits:

- **Temporary**: it ends when objectives are met, or when it is stopped.
- **Unique**: the output, the context or the team differ from anything done before, so it
  carries uncertainty (risk).
- **Progressively elaborated**: detail grows as the work advances; plans are refined, not
  written once.
- **Constrained**: scope, time and cost pull against each other (the "triple constraint"), with
  quality and risk in the middle. Changing one moves the others.

**Operations** are repetitive and ongoing; a project changes something and then hands it to
operations.

## Project, program, portfolio

| Level | What it is | Managed for |
|---|---|---|
| Project | temporary work with a defined output | delivering the output on scope, time, cost |
| Program | related projects managed together | benefits that single projects cannot deliver alone |
| Portfolio | projects, programs and operations of an organization | the right mix of work for the strategy |

A **PMO** (project or program management office) sets standards, supports and sometimes directs
projects. **Governance** defines who authorizes, funds, decides and accepts: the sponsor owns
the business case; the steering committee decides on escalations; the project manager runs the
project within delegated authority.

## Organization structures and authority

| Structure | Project manager's authority | Typical risk |
|---|---|---|
| Functional | low, often part-time coordinator | priorities of the function win |
| Weak matrix | low | resources pulled back by line managers |
| Balanced matrix | shared with line managers | two bosses, negotiation over resources |
| Strong matrix | high, full-time PM | line managers feel bypassed |
| Projectized | full; team reports to the PM | duplicated resources, team without a home at the end |

Write the authority explicitly in the charter: budget, staffing, decisions, escalation.

## The five process groups

These are not phases: they repeat inside every phase.

1. **Initiating** — define the objectives and justify the project; appoint the project manager;
   write and approve the **charter**; identify stakeholders.
2. **Planning** — scope and WBS, schedule, budget, resources and responsibilities, risks,
   quality, communication, procurement. Integrate them into the **project plan** and approve
   the **baselines** (scope, schedule, cost).
3. **Implementing** — do the work, lead and develop the team, manage stakeholders and
   suppliers, assure quality, distribute information.
4. **Controlling** — measure progress against the baselines, analyze variances, forecast,
   decide corrective and preventive actions, run **change control**, control risks, quality and
   contracts. It runs in parallel with implementing for the whole project.
5. **Closing** — confirm acceptance, close the contracts and the accounts, release resources,
   collect **lessons learned**, archive.

Planning, implementing and controlling form a cycle (Plan-Do-Check-Act): control results feed
re-planning. Rolling-wave planning details the next period and keeps later work at a higher
level.

## Lifecycles and phases

- **Predictive (waterfall)**: scope fixed early, phases in sequence; fits stable requirements,
  contracts on a fixed scope, regulated work.
- **Iterative**: the solution is refined in repeated cycles; scope is learned along the way.
- **Incremental**: the output is delivered in usable pieces, each adding capability.
- **Agile**: iterative and incremental with short timeboxes and continuous customer feedback
  (see `pm-agile`).
- **Hybrid**: predictive for stable parts (infrastructure, contracts) and agile for uncertain ones.

Each **phase** ends with a **gate**: a review of deliverables and of the business case, and a
decision to continue, change course or stop. Effort and cost are low at the start, peak during
execution and fall at closure; the ability to change at low cost is highest at the start.

The **project lifecycle** (start to handover) sits inside the **product lifecycle** (idea to
retirement).

## Project charter (template)

```markdown
# Project charter: <name>
- Sponsor: <name, role>          Project manager: <name> - authority: <budget, staff, decisions>
- Purpose and business justification: <why now, which benefit, link to strategy>
- Objectives (SMART): <measurable outcomes with target dates>
- Scope: in <...>; out <...>
- Main deliverables and acceptance criteria: <...>
- Milestones: <name - target date>
- Budget (order of magnitude) and funding: <...>
- Key stakeholders: <...>
- Main risks, assumptions and constraints: <...>
- Success criteria and who judges them: <...>
- Approval: <sponsor, date>
```

## Success criteria

Agree them at the start, with whoever will judge them: delivered scope and quality, time,
cost, stakeholder satisfaction, realized benefits (often measured after closure). A project can
be on time and on budget and still fail its purpose; record both project success (the output)
and product success (the benefits).

## Baselines and change control

- A **baseline** is the approved version of scope (scope statement, WBS, WBS dictionary),
  schedule and cost. Progress is measured against it.
- **Configuration management** identifies the items under control (documents, deliverables,
  versions) and records their status.
- **Change control**: every change request is logged, its impact on scope, time, cost, quality
  and risk is analyzed, a person or board with the authority decides, the baselines and plans
  are updated, and the change is communicated. Without approval, nothing changes.

## Quality

- Plan which standards apply and how they will be met; assure that the processes are followed;
  control the deliverables against the acceptance criteria.
- Principles: the customer defines quality; prevention costs less than inspection; continuous
  improvement through PDCA; decisions on data.
- Quality (meeting requirements) is not grade (category or level of features).

## Closure and lessons learned

1. Formal acceptance of each deliverable, in writing.
2. Contract closure: deliverables verified, claims settled, payments made, documents archived.
3. Administrative closure: accounts closed, resources released, documents archived.
4. Lessons learned: what worked, what did not, what to repeat or avoid, with the evidence; store
   them where the next project starts (in a repository: `docs/memory/LEARNINGS.md`).
5. Hand over to operations, with the support arrangements.

## Maturity

Maturity models (for example P3M3, OPM3, CMMI-based) describe how consistently an organization
manages projects, from ad hoc to optimized. Use them to choose what to improve next, not as a
score to chase.

## Further reading

ISO 21500 (concepts) and ISO 21502 (guidance on project management); the PMI PMBOK Guide; the
IPMA Individual Competence Baseline. Related entries: `pm-scope-wbs`, `pm-schedule`,
`pm-control`, `pm-risk`, `pm-stakeholders`, `pm-procurement`, `pm-agile`.
