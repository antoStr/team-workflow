---
name: pm-control
description: Project cost and progress control - cost types and estimating, budget, contingency and management reserves, cost baseline, S-curve and cash flow, progress measurement rules, earned value management (PV, EV, AC, CV, SV, CPI, SPI, EAC, ETC, VAC, TCPI) with interpretation and forecasts, status reporting and change impact. Includes scripts/evm.py, a tested calculator. Use when building a budget, measuring progress, writing a status report with figures or forecasting a project's final cost.
origin: team-workflow
---

# Cost, progress and earned value

## Costs and estimates

- **Direct** costs belong to the project (team time, materials, subcontracts); **indirect**
  costs are shared (offices, overheads) and allocated by a rule.
- **Fixed** costs do not change with volume; **variable** costs do.
- Estimating methods: analogous (top-down, rough), parametric (unit rate x quantity),
  bottom-up (from work packages, most accurate), three-point. State the accuracy range: a rough
  order of magnitude early (for example -25%/+75%), a definitive estimate later (for example
  -5%/+10%).

## Budget and reserves

```text
work package estimates
+ contingency reserve      (for identified risks: known-unknowns; managed by the PM)
= cost baseline            (time-phased: the S-curve used for earned value)
+ management reserve       (for unidentified risks: unknown-unknowns; released by the sponsor)
= project budget
```

The **S-curve** is the cumulative planned cost over time. **Cash flow** compares payments out
with receipts in (milestone payments, invoices): a profitable project can still run out of
cash. Project margin = revenue - total cost.

## Measuring progress

Agree one rule per work package before the first report and keep it:

| Rule | Earned when | Fits |
|---|---|---|
| 0/100 | only when finished | short work packages (one period) |
| 50/50 (or 20/80) | part at start, the rest at finish | work packages of two or three periods |
| Weighted milestones | each milestone earns its share | long work packages with clear steps |
| Physical % / units | measured quantity done / total | repetitive work (metres, items) |
| Level of effort | as time passes | support work without a deliverable |

Never use "percent of budget spent" as progress: it confuses cost with work done.

## Earned value management (EVM)

All values cumulative, at the same cut-off date ("time now"), in the same currency.

| Term | Meaning |
|---|---|
| BAC | budget at completion: the total cost baseline |
| PV | planned value: budget of the work scheduled up to time now |
| EV | earned value: budget of the work actually done up to time now |
| AC | actual cost of the work done up to time now |
| CV = EV - AC | cost variance: negative = over budget |
| SV = EV - PV | schedule variance, in money: negative = behind schedule |
| CPI = EV / AC | value earned per unit spent: < 1 over budget |
| SPI = EV / PV | rate of progress compared with plan: < 1 behind schedule |
| ETC | estimate to complete: cost of the remaining work |
| EAC = AC + ETC | estimate at completion: the expected total cost |
| VAC = BAC - EAC | variance at completion: negative = expected overrun |
| TCPI | cost efficiency needed on the remaining work to hit a target |

**Forecasts**, pick by the cause of the variance:

| EAC formula | Assumes | Use when |
|---|---|---|
| AC + (BAC - EV) | the variance was a one-off; the rest goes at budget rate | an isolated event caused it |
| BAC / CPI = AC + (BAC - EV) / CPI | current cost efficiency continues | the variance is structural (typical) |
| AC + (BAC - EV) / (CPI x SPI) | cost and schedule pressure both continue | a fixed end date forces recovery spending |
| AC + new bottom-up ETC | the original plan is no longer valid | the forecasts above are not credible |

TCPI = (BAC - EV) / (BAC - AC) to finish on budget, or (BAC - EV) / (EAC - AC) to finish on
the new EAC. A TCPI well above the current CPI (more than about 10%) is rarely achieved:
report the EAC instead of promising the BAC.

Run the calculator rather than computing by hand:

```bash
python3 scripts/evm.py --bac 120000 --pv 48000 --ev 42000 --ac 50000
python3 scripts/evm.py --bac 120000 progress.csv    # columns: period, pv, ev, ac (cumulative)
```

**Reading the numbers**

- CPI and SPI both below 1: over budget and late; find the work packages driving it.
- SPI below 1 with CPI above 1: underspending because work is late, not because it is efficient.
- SV is in money and tends to zero at the end even for a late project (EV reaches PV = BAC);
  check the critical path for the real delay.
- Early in a project (under about 15-20% complete) the indices are unstable; after that the
  cumulative CPI rarely improves much.

## Status report

1. Headline: on track / at risk / off track, and why, in one line.
2. Progress since last report and next period's plan.
3. Figures: % complete, CPI, SPI, EAC with the formula used, milestone forecast versus baseline.
4. Top risks and issues with owners and dates.
5. Decisions needed, from whom, by when.

## Change impact analysis

For every change request: scope affected (WBS elements), schedule impact (re-run the
network), cost and reserve impact, quality and risk impact, options (accept, defer, reject,
alternative), recommendation. The baselines change only after approval.

Related entries: `pm-lifecycle` (baselines, change control), `pm-schedule` (time),
`pm-risk` (contingency sizing).
