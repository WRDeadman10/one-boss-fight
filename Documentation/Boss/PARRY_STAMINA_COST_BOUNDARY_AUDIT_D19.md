# Parry stamina cost and refusal audit (Queue D D19, 2026-11-03)

## Source contract

`URPGPlayerParry::Press` rejects a pending cost operation, non-finite/negative cost, unreadable stamina, or stamina below cost. A positive cost is written before the cooldown/window rule runs; if cooldown refuses, `FinishStaminaCost` restores the pre-press value, retrying failed writes. A successful parry marks the pending charge; when the window closes, the component returns half the paid cost, capped at the readable maximum when available. A whiff keeps the full cost. With `StaminaCost == 0`, the component skips attribute reads/writes and still attempts the window; this is the default (`RPGPlayerParry.cpp:65–109,137–181`; `RPGPlayerParry.h:25–34`).

The pure `RPGParryCost` rules accept exact equality (`Stamina >= Cost`), reject insufficient/negative/non-finite inputs, charge the full cost on whiff and half net cost on parry, and cap `ParryRefund` at maximum stamina (`Player/RPGParryCostRules.h`).

## Coverage matrix

| Case | Source outcome | Existing test/evidence | Boundary |
|---|---|---|---|
| Enough / exact-cost stamina | `CanPress` accepts `Stamina >= Cost`; exact equality allowed. | `OneBossFight.Framework.ParryCost.Rules`, `RPGParryCostTests.cpp:12–14`. | Pure equality is covered. |
| Insufficient stamina | Refuses before opening a window; no stamina write or `RPGParry::Press`. | Same test checks 3.99 < 4.0. `BUILD-176` live evidence does not exercise insufficient stamina (`TEST_PLAN.md:639`). | Pure branch covered; component/live no-mutation result is not witnessed. |
| Negative/non-finite cost or stamina | `CanPress` refuses invalid resource values; component separately rejects non-finite/negative `StaminaCost` before charging. | Cost tests cover negative/NaN; helper also checks all operands finite. | Positive infinity is not explicitly asserted in this file; component invalid `StaminaCost` branch lacks a wrapper test. |
| No-cost default | `StaminaCost == 0` bypasses attribute read/write and opens via window/cooldown rule. | `RPGPlayerParry.h:31–34`, source; `PARRY_HOWTO.md` documents zero as default. | No explicit component test proving open with absent stamina attribute and zero cost. |
| Whiff vs successful parry | Paid press subtracts full cost; successful parry adds half back on window close. | Pure helper tests cover 10-4=6 whiff and net 8 for parry (`RPGParryCostTests.cpp:21–24`). BUILD-176 live: cost 20, whiff 100→80, Perfect parry 80→70 (`TEST_PLAN.md:639`). | Successful/whiff aggregate behavior is evidenced; live insufficient path is not. |
| Maximum cap | Refund helper caps at Max; component applies this when maximum attribute can be read. | `RPGParryCostTests.cpp:27–30`; component `RPGPlayerParry.cpp:159–170`. | If max is unreadable, component falls back to adding half cost without a cap; live/reflected attribute-read behavior determines whether this can exceed actual max. |
| Cooldown refusal after charge | Component first charges, then on failed `RPGParry::Press` schedules exact rollback; retry state blocks another press until settled. | `RPGParryTests.cpp` covers pure cooldown refusal and unchanged timing state; source path at `RPGPlayerParry.cpp:101–106`. | No component fixture injects a failing rollback write or verifies stamina restoration/readback. |

## Findings and bounded follow-up

No mismatch was found in the pure exact-cost, insufficient, full-whiff, half-refund, or cap rules. The primary evidence gap is the component-level insufficient-stamina refusal: the pure predicate is tested, but the no-open/no-mutation live branch remains explicitly unexercised by BUILD-176. Add an isolated component fixture or Lead-owned PIE case for below-cost refusal, exact-cost accepted press, default-zero cost with unreadable stamina, and cooldown refusal with restored stamina; setup/readback failures must fail or mark the run inconclusive, never pass. Consider a separate test for the documented fallback when maximum stamina cannot be read; do not claim capped refund in that condition.

Lead disposition C-744: the uncapped fallback when maximum stamina cannot be read is tracked as low, unverified KI-176. The source branch exists; reachability with the project player's attribute component is not established.

## Verification boundary

Static source/test/log review only. Existing tests and BUILD-176 report were inspected, not rerun. No code, test, build, or Editor changes/execution.
