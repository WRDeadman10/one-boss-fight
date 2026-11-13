# Queue BF Batch 2 — navigation and autonomous driver resilience

Date: 2026-11-11. Offline/source audit only; no Editor, PIE, build, or asset operation.

## Task dispositions

| ID | Disposition | Evidence |
|---|---|---|
| BF-X06 | Complete — source audit | Missing selector result, terminal outcome, time cap, missing PIE world/player, and callback exception all produce explicit status and route through `finish`. |
| BF-X07 | Complete | Added executable offline tests for time-cap default/fallback/clamps, missing selection, terminal/time-cap completion, callback unregister, End PIE, and idempotent finish. |
| BF-X08 | Complete | The driver now refuses navigation summaries whose route/generation do not match the selected profile and test generation, and refuses a controller that does not possess the spawned boss. The summary has no stable actor ID, so the live checklist joins the separate spawn-name and possession witnesses. |
| BF-X09 | Complete — source audit | `OnMoveCompleted` accepts only the current owned request, invalidates it before `WalkArrived`/`Fail`, and emits one terminal line per accepted callback; non-owned/duplicate callbacks return. `StopOwnedWalk` invalidates before `StopMovement`. No per-frame navigation logging was found. |
| BF-X10 | Complete | Added a Lead checklist with route/actor/generation, Recast, projection, request, terminal result and cleanup fields kept distinct. |

## Source findings

- `Scripts/Editor/pie_sevarog_framework_live.py`: autonomous duration defaults to 45 seconds, malformed input falls back to 45, and valid values clamp to 5–90 seconds. A missing selected card logs `NoSelectionOrStart`; success/failure outcomes and time cap each log an explicit result. The driver caps PIE-world wait at 60 seconds and player wait at 30 seconds. Tick exceptions log traceback and terminate.
- `finish()` is idempotent (`STATE["done"]`), unregisters the Slate tick handle, clears the handle and requests End PIE. If unregister or End PIE raises, it catches the exception; End PIE request failure is logged.
- `RPGFrameworkBossController::OnMoveCompleted` filters invalid or non-owned request IDs, captures route/generation/request/result/flags and final geometry, invalidates the request, then dispatches arrival/failure. `StopOwnedWalk` invalidates before calling `StopMovement`, protecting against synchronous callbacks.
- Navigation text exposes route, generation, request, result code/flags and actor/goal positions, not a stable actor ID. `validate_navigation_identity` now fails closed unless route matches `FixtureLabel` and generation matches the test initializer's generation 1. The driver also refuses when controller possession does not resolve to the spawned boss (`controller_pawn_match` must be `1`). `SPAWN PASS actor=...` remains the human-readable actor witness; the Lead checklist joins it to possession in the same run.
- The live driver refuses missing/empty/PENDING navigation summary. For the deliberately skipped in-band walk, the summary is `TEST_WALK_SKIPPED` with route/generation, not a movement success.

## Verification

- `python Scripts/Tools/test_bf_x06_x10_navigation_driver_contract.py`: 6/6 passed, including route/generation match, mismatch and malformed-summary cases. Tests execute actual Python helper functions in isolation with a fake Unreal boundary; no Editor is imported or launched.
- No engine build/full native suite was run: this batch adds only an offline Python contract and documentation.
- No route, movement, Recast projection, saved asset, or PIE acceptance is claimed. No commit or push.

## Lead navigation acceptance checklist

1. Record build/map/route, selected definition, boss/player names and unique IDs, encounter/generation, controller and possessed pawn in one run.
2. Record Recast/NavSystem presence separately from projection request, requested/projected goal, projection delta and acceptance radius.
3. Record each path request ID/result/full-path status/route/generation; reconcile it to exactly one terminal result with code/value/flags/terminal position/goal/remaining distance.
4. Join `NAV_RESULT`, `SPAWN PASS actor=...`, and `controller_pawn_match`; actor identity must remain unchanged across request and terminal lines. A skipped walk is not a path pass.
5. On repeat, confirm one terminal line per owned request, no old request attributed to a newer generation, bounded failure/timeout, clean End PIE and no saves.

See also `Documentation/Boss/BE_X16_X20_NAVIGATION_DIAGNOSIS.md` for the original Lead map-run fields.
