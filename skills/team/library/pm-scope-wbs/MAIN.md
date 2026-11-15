---
name: pm-scope-wbs
description: Project scope and work breakdown - requirements to scope statement, deliverables and acceptance criteria, building a WBS (100% rule, decomposition by product, by phase or by process, work packages, coding), the WBS dictionary, the OBS and the responsibility assignment matrix (RAM/RACI). Use when the scope of a project must be defined, a WBS built or checked, or responsibilities assigned.
origin: team-workflow
---

# Scope, WBS and responsibilities

## From requirements to scope

1. **Collect requirements** from stakeholders: what the output must do and which conditions it
   must meet (business, user, functional, non-functional, regulatory, transition).
2. **Scope statement**: description of the output, deliverables, acceptance criteria,
   exclusions (what is explicitly out), constraints and assumptions.
3. **Deliverables**: every unique, verifiable product, result or capability the project must
   produce, including the management ones (plans, reports) when the client expects them.
4. **Acceptance criteria**: measurable conditions for each deliverable, and who accepts it.

Scope creep is uncontrolled growth of scope without matching time, cost and approval. The cure
is a written scope, exclusions included, and change control.

## Work breakdown structure (WBS)

A WBS is a hierarchical decomposition of the **total** work of the project into deliverables
and smaller, manageable pieces. It describes **what**, not when or who.

**Rules**
- **100% rule**: each level contains all the work of its parent and nothing more; the WBS
  contains all the work of the project, project management included.
- Elements are **nouns** (deliverables or results), not verbs; activities come later.
- Children of one parent do not overlap.
- Decompose until a **work package** can be estimated, assigned to one owner, scheduled and
  controlled. A common guide: between about one and ten working days of effort, or no more than
  one reporting period.
- Not all branches need the same depth; detail the near work more (rolling wave).
- Number every element (1, 1.1, 1.1.2...) and keep the codes stable: costs, schedule and
  reports reference them.

**Decomposition logics** (choose one per level, do not mix on the same level)

| Logic | Second level made of | Fits |
|---|---|---|
| By product | the components of the output | engineering, construction, software modules |
| By phase / lifecycle | design, build, test, deploy... | predictive projects with clear phases |
| By process / function | the disciplines doing the work | organizational or service projects |
| By location | sites, regions | rollouts across sites |

**Formats**: tree (organization-chart style) for overview, indented outline for working and
version control:

```text
1 Office relocation
  1.1 Project management
  1.2 New site
    1.2.1 Lease contract
    1.2.2 Fit-out
  1.3 IT
    1.3.1 Network
    1.3.2 Workstations
  1.4 Move
  1.5 Handover and closure
```

**Common mistakes**: activities instead of deliverables; missing project management, testing,
training, documentation or handover; one branch per department instead of per output; too
deep (micromanagement) or too shallow (not estimable).

## WBS dictionary

One entry per work package: code, name, description of the work, deliverable, acceptance
criteria, owner, estimated effort and cost, assumptions, dependencies, resources. The WBS, its
dictionary and the scope statement form the **scope baseline**.

## Work packages to activities

Each work package becomes one or more **activities** (verbs: "pull cables", "configure
switches") with durations and dependencies: that is the schedule's job (`pm-schedule`).

## OBS and responsibility matrices

- **OBS (organizational breakdown structure)**: the project organization as a hierarchy of
  units and people.
- **RAM (responsibility assignment matrix)**: WBS elements (rows) crossed with OBS units or
  people (columns), so every work package has an owner.
- **RACI** is a RAM with four codes:
  - **R**esponsible: does the work (one or more);
  - **A**ccountable: answers for the result, approves; **exactly one** per row;
  - **C**onsulted: gives input before (two-way);
  - **I**nformed: told after (one-way).

```markdown
| Work package | PM | Architect | Dev team | Client |
|---|---|---|---|---|
| 1.2.1 Requirements | A | C | R | C |
| 1.3.1 Build | I | C | R/A | I |
| 1.5 Acceptance | R | I | C | A |
```

Checks: no row without an A or with two A; no row without an R; a column full of A means a
bottleneck; a column without any letter means someone is not needed or forgotten.

## Related entries

`pm-lifecycle` (charter, baselines, change control), `pm-schedule` (activities and dates),
`pm-control` (costs per work package).
