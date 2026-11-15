---
name: pm-schedule
description: Project scheduling - activities and dependencies (FS, SS, FF, SF, lags and leads), duration estimating (analogous, parametric, three-point/PERT), network diagrams, the critical path method with forward and backward pass, total and free float, Gantt charts and milestones, resource leveling and smoothing, schedule compression (crashing, fast tracking) and critical chain buffers. Includes scripts/cpm.py, a tested calculator. Use when building, checking or recovering a project schedule.
origin: team-workflow
---

# Scheduling: networks, critical path and compression

## Activities and dependencies

Activities come from the WBS work packages and are named with verbs. Each has a duration, a
unit (working days unless stated) and predecessors.

| Relation | Meaning | Example |
|---|---|---|
| FS finish-to-start (default) | B starts after A finishes | paint after plastering |
| SS start-to-start | B starts after A starts | lay cable once trenching has started |
| FF finish-to-finish | B finishes after A finishes | testing ends after coding ends |
| SF start-to-finish | B finishes after A starts | old shift ends once the new shift starts |

A **lag** delays the successor (concrete curing: FS+3); a **lead** (negative lag) lets it start
earlier (FS-2). Dependencies are **mandatory** (physical, contractual), **discretionary** (best
practice, can be changed to compress), or **external** (outside the project's control).

Network diagrams: the **precedence diagram** (activity on node, AON) supports all four
relations and is the standard; activity on arrow (AOA) needs dummy activities and FS only.

## Estimating durations

- **Analogous**: from similar past activities; fast, rough.
- **Parametric**: quantity x productivity rate (200 m of cable / 50 m per day = 4 days).
- **Three-point (PERT, beta)**: te = (O + 4M + P) / 6, standard deviation (P - O) / 6. The sum
  of variances along the critical path gives the uncertainty of the end date.
- **Bottom-up**: estimate detailed pieces and add up.
- Estimate **effort** first, then the **duration** from the resources available. State the
  assumptions and add contingency where risk is identified, visibly, not hidden in every task.

## Critical path method (CPM)

1. **Forward pass**: ES (early start) = the latest of the constraints from the predecessors;
   EF = ES + duration. The largest EF is the project duration.
2. **Backward pass**: LF (late finish) = the earliest of the constraints from the successors
   (the project end for the last activities); LS = LF - duration.
3. **Total float** = LS - ES = LF - EF: how much an activity can slip without delaying the
   project end.
4. **Free float** = how much it can slip without delaying the early start of any successor;
   always less than or equal to total float.
5. **Critical path**: the chain of activities with zero total float (negative when a date
   constraint is already missed). It is the longest path and sets the project duration. There
   can be more than one; near-critical paths (small float) deserve the same attention.

Do not compute by hand. Write the activities to a CSV and run the calculator:

```text
id,name,duration,predecessors
A,Requirements,5,
B,Design,8,A
C,Procurement,12,A
D,Build,15,B;C:SS+4
E,Test,6,D
M,Go-live,0,E
```

```bash
python3 scripts/cpm.py plan.csv --gantt --start 2026-02-02
python3 scripts/cpm.py plan.csv --target 45        # with optimistic,most_likely,pessimistic columns
python3 scripts/cpm.py plan.csv --json
```

It prints ES, EF, LS, LF, total and free float, the critical path and a Mermaid Gantt; with
three-point columns, the standard deviation and the probability of meeting `--target`. It uses
calendar units: map them to working days and holidays when you turn them into dates.

## Gantt charts and milestones

A Gantt shows activities as bars on a time axis: easy to read, weak at showing dependencies
and float, so keep the network as the source. **Milestones** have zero duration and mark
events (approval, delivery, gate). Show the baseline next to the current forecast.

## Resources

- Build the **resource histogram** from the schedule (people or equipment per period).
- **Resource smoothing**: move activities within their free or total float so peaks fall; the
  end date does not change.
- **Resource leveling**: resolve over-allocation even when it moves the end date; the critical
  path can change.
- Plan with the real availability (calendars, part-time, holidays), not with 100% of everyone.

## Compressing the schedule

- **Fast tracking**: run in parallel activities planned in sequence (change FS to SS or add a
  lead). Costs little money, adds risk and rework. Works only on critical activities with
  discretionary dependencies.
- **Crashing**: add resources (overtime, more people, faster equipment) to critical
  activities. For each candidate compute cost per unit of time saved = (crash cost - normal
  cost) / (normal duration - crash duration); shorten the cheapest first, one step at a time,
  and re-check the critical path after each step (another path may become critical).
- Compressing non-critical activities does not shorten the project.

## Critical chain (CCPM)

Critical chain extends CPM by taking **resource** availability into account.

1. Schedule with aggressive estimates (about 50% confidence), removing the safety margin hidden
   in each task.
2. The **critical chain** is the longest chain of dependent activities considering both logic
   and resource constraints.
3. Put part of the removed safety into a **project buffer** at the end of the chain, **feeding
   buffers** where non-critical chains join it, and **resource buffers** (alerts before a
   critical resource is needed).
4. Control the project by **buffer consumption** compared with chain progress (green, yellow,
   red), not by individual task dates.

Compared with CPM: it protects the end date against student syndrome and Parkinson's law and
accounts for resources; it needs a team that accepts aggressive estimates and no multitasking.

## Checks before you publish a schedule

- Every activity has at least one predecessor and one successor, except the start and end.
- No loops; no hard date constraints unless the contract imposes them.
- Floats are plausible; a very large float often means a missing dependency.
- The critical path is explainable in one sentence.
- Durations have a source; three-point when the uncertainty is real.

Related entries: `pm-scope-wbs` (where activities come from), `pm-control` (progress and
earned value), `pm-risk` (schedule risks and buffers).
