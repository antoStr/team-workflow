---
id: tests-test_pm
title: test_pm.py
layer: tests
tags: [code, py]
aliases: [tests/test_pm.py, test_pm.py]
upstream:
downstream:
files: [tests/test_pm.py]
status: active
last_updated: 2026-11-19T11:00:10
---

# test_pm.py

The project-management calculators shipped in the library: critical path and earned value.

## Contracts

### Classes
- `CriticalPathTest` (methods: test_finish_to_start_network, test_free_float_differs_from_total_float, test_relation_types_and_lags, test_three_point_estimates_and_probability, test_bad_networks_are_refused, test_cli_prints_table_and_gantt)
- `EarnedValueTest` (methods: test_metrics_and_forecasts, test_zero_actuals_give_no_index_instead_of_crashing, test_overspent_budget_has_no_tcpi, test_invalid_input, test_cli_series)

### Functions
- `load(entry, name)`
- `network()`

## Dependencies
### Upstream
- None
### Downstream
- None
