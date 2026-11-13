# Queue BE Batch 4 — one-run navigation diagnosis checklist

Date: 2026-11-10  
Status: source and checklist READY; live navigation route still requires Claude's map run.

## One-run checklist

Capture the following in one fresh Development PIE run on the selected framework route. Keep the map, build ID, route, and actor identities in one run summary.

1. **World/navigation witness:** record the map and route, boss/player actor names and unique IDs, encounter ID, generation, controller and possessed pawn. Record whether `UNavigationSystemV1` and a `RecastNavMesh` actor are present.
2. **Projection:** record the requested goal, projected goal, projection delta in centimeters, profile band min/max, acceptance radius, and whether the destination is inside the authored arena. Projection failure must terminate the run as a failure.
3. **Path request:** record request ID, request result code, full-path/partial-path state, route and generation. A missing request/result field is a failed diagnostic, not an inferred success.
4. **Terminal completion:** capture exactly one `nav_terminal` line with result code and numeric code value, raw flags, actor terminal location, projected goal, and remaining 2D distance in centimeters. Success must arrive inside the acceptance radius; Blocked, OffPath, Aborted, Invalid, or timeout must remain distinguishable.
5. **Reconciliation:** compare the request and terminal lines by request ID, route and generation. Confirm the actor ID is unchanged, read the final actor location and target distance, and record the boss outcome. Do not use per-frame logging as a substitute for terminal evidence.
6. **Repeatability/safety:** run the same route once more only after the first result is saved; confirm one terminal line per owned request, no stale callback is attributed to the new generation, PIE ends cleanly, and no assets are saved.

The checklist's one-run acceptance fields are diagnostic guidance. Codex did not start PIE or claim a Recast projection, full path, movement success, or map acceptance in Batch 4.

## Source changes and tests

The controller now stores and reports terminal path-following code/flags, route, generation, request, actor/goal positions and remaining distance. An id-free Development getter makes the current summary available to the Lead's live driver; that driver logs it and fails closed for an empty or still-pending result. The explicitly skipped in-band test walk reports `TEST_WALK_SKIPPED` instead of masquerading as a path result.

Native formatting cases cover Success, Invalid, Blocked and Aborted. The offline contract checks controller telemetry, driver fail-closed behavior, and this checklist.

## Validation

- `test_be_x16_x20_navigation_diagnostics_contract.py`: 3/3 passed.
- `py_compile` for the live driver and contract: passed.
- `test_check_shipping_guards.py`: 4/4 passed.
- C-1155 Development build exit 0; DD27j-pinned full suite 509/509 started / passed, 0 failed, complete. `OneBossFight.Framework.Runtime.NavigationDiagnosticFormatting` passed. No assets; both locks released.
- Receipt: `Docs/BossCombatReview/Execution/Codex/BE_X16_X20_NAVIGATION_DIAGNOSTICS/Run_20261110_180400/`.
