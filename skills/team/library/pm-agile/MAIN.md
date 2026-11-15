---
name: pm-agile
description: Agile project delivery - choosing between predictive, iterative, incremental, agile and hybrid lifecycles, the Agile Manifesto values, Scrum (accountabilities, events, artifacts, Definition of Done), Kanban (visual board, WIP limits, flow metrics, Little's law), Lean waste, XP practices, user stories (INVEST) and splitting, relative estimation, velocity and forecasting, burndown and burnup charts, MVP slicing, refactoring and technical debt. Use when choosing or running an agile approach, building a backlog or planning sprints and releases.
origin: team-workflow
---

# Agile delivery

## Choosing the lifecycle

| Signal | Predictive | Agile |
|---|---|---|
| Requirements | known and stable | emerging, likely to change |
| Customer feedback | at the end is enough | needed often |
| Cost of change late | very high (construction, hardware) | low (software, content) |
| Value | only when everything is done | from early increments |
| Contract / regulation | fixed scope required | allows evolving scope |

Most real projects are **hybrid**: predictive where things are fixed (contracts,
infrastructure, compliance), agile where they are learned. Choose per part, not per company.

## Values

The Agile Manifesto (2001) values individuals and interactions over processes and tools,
working software over comprehensive documentation, customer collaboration over contract
negotiation, and responding to change over following a plan; the items on the right still have
value. Its twelve principles stress early and continuous delivery, welcoming change, short
cycles, daily collaboration with the business, motivated and trusted people, face-to-face
conversation, working output as the measure of progress, sustainable pace, technical
excellence, simplicity (maximizing the work not done), self-organizing teams and regular
reflection. Mindset comes before tools: a board and stand-ups do not make a team agile.

## Scrum (Scrum Guide 2020)

**Accountabilities**
- **Product Owner**: maximizes the value of the product; owns and orders the Product Backlog.
- **Scrum Master**: makes Scrum work; removes impediments; coaches the team and the organization.
- **Developers**: create the increment; own the Sprint Backlog and the quality (Definition of
  Done). One team, typically ten people or fewer, with all the skills needed.

**Events** (all timeboxed; the sprint is one month or less)
- **Sprint**: the container; a usable increment every sprint.
- **Sprint Planning**: why (Sprint Goal), what (items selected), how (plan).
- **Daily Scrum**: 15 minutes for the Developers to inspect progress toward the Sprint Goal and
  adapt the plan.
- **Sprint Review**: inspect the increment with stakeholders and adapt the Product Backlog.
- **Sprint Retrospective**: inspect how the team worked and pick improvements.

**Artifacts and their commitments**
- Product Backlog -> **Product Goal**.
- Sprint Backlog -> **Sprint Goal**.
- Increment -> **Definition of Done**: the quality bar every increment meets; work that does
  not meet it is not done and is not shown as done.

Pillars: transparency, inspection, adaptation. **Backlog refinement** (splitting, clarifying,
estimating) is continuous, not an event. A Definition of Ready is optional and must not become
a gate that blocks collaboration.

## Kanban and Lean

- Visualize the workflow on a board (columns for each state), **limit work in progress** per
  column, make policies explicit (when an item may move), manage flow, improve continuously.
- Pull, not push: a column takes new work only when it has capacity.
- **Flow metrics**: lead time (request to done), cycle time (started to done), throughput
  (items done per period), WIP. **Little's law**: average cycle time = average WIP / average
  throughput: lowering WIP shortens cycle time.
- **Lean** removes waste: partially done work, extra features, relearning, handoffs, delays,
  task switching, defects. It comes from the Toyota Production System, as does the kanban card.
- Scrum and Kanban combine well (Scrum with a Kanban board and WIP limits).

## Other practices

- **XP**: pair programming, test-driven development, continuous integration, small releases,
  collective code ownership, refactoring, simple design, sustainable pace.
- Scaled and adjacent methods (DSDM, Crystal, FDD, SAFe, LeSS): use their ideas when one team
  is not enough; do not adopt a framework bigger than the problem.

## User stories

"As a **<user>**, I want **<capability>** so that **<benefit>**", with acceptance criteria
(Given / When / Then). Good stories are **INVEST**: independent, negotiable, valuable,
estimable, small, testable. Split large stories (epics) by workflow step, business rule,
data variation, interface, happy path first then exceptions; never split by technical layer
only (a "database story" delivers no value alone).

## Estimating and forecasting

- **Relative estimation** in story points (often a Fibonacci-like scale) by the people doing
  the work, for example with Planning Poker; or count items when they are similar in size.
- **Velocity**: points (or items) done per sprint; use the average of the last three to five
  sprints, as a range. Never compare velocity between teams or use it as a target.
- **Release forecast**: remaining backlog / velocity range = number of sprints as a range.
- **Burndown**: work remaining over time (sprint or release). **Burnup**: work done and total
  scope over time; it shows scope changes that a burndown hides.

## MVP and increments

The **minimum viable product** is the smallest thing that tests the riskiest assumption with
real users; it is a learning tool, not a low-quality product. Slice end to end, so every
increment is usable.

## Refactoring and technical debt

**Technical debt** is the future cost of shortcuts taken now (missing tests, duplicated code,
outdated dependencies, quick fixes). Like money debt it accrues interest: each change gets
slower and riskier. Make it visible (backlog items, a debt register), pay it continuously
(refactoring as part of the Definition of Done, a share of each sprint), and avoid creating it
unknowingly (code review, automated tests, CI). **Refactoring** changes the structure without
changing behavior, in small steps protected by tests.

## Signs of "agile in name only"

Sprints without a usable increment; a Product Owner without authority; stand-ups as status
reports to a manager; velocity used as a performance target; retrospectives without changes;
fixed scope, fixed date and fixed cost all at once.

Related entries: `story-lifecycle` (file-based epics and sprints), `pm-lifecycle` (hybrid
governance), `pm-stakeholders` (team and communication).
