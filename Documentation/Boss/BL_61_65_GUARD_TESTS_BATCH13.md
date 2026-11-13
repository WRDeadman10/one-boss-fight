# BL-61..65: guard tests, batch 13 (StaminaPressure, Strafe NextPosition / HoldSeconds / DirectionAt, StuckRecovery)

Assigned by X-2190 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 13 of 20.

**Four new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source.

## BL-64/65: re-verification, scope corrections and observability (by hand)

| Header | Gap tested | Existing coverage, not repeated | Equivalent or unreachable guards |
|---|---|---|---|
| `RPGBossStaminaPressureRules.h:10-11` | threshold <0 or >1; max pressure <0; NaN or Inf inputs; exact boundaries (threshold 1, max 3, max 0) | fraction <0 and max pressure >3 (`…StaminaPressure.Rules`) | **threshold == 0**: `(0-f)/0 = -Inf` clamps to 0. **fraction > 1**: the ramp is negative and clamps to 0. Both are documented. |
| `RPGBossStrafeRules.h:11-30` `NextPosition` | NaN or Inf Target; -Inf `Boss.Y`; a negative speed; a NaN, Inf or negative delta; `Dir` ±2; arc overflow (`1e200*1e200`) | `RPGBossStrafeTests.cpp:39-44`: NaN `Boss.X`, +Inf speed, radius 0.5, `Dir` 0, zero speed or delta | **The Angle-overflow guard (`:26-27`) is unreachable:** `Radius >= 1`, so `|Angle| <= ArcLength`, which is already finite. Documented, not tested. |
| `:33-46` `HoldSeconds` | a non-finite min gives 0; a non-finite max with a finite min gives the min; an in-range deterministic control | **the reversed range is already asserted** (`RPGBossStrafeTests.cpp:55`), so X-2190's reversed-range item is skipped; the finite-range overflow witness | — |
| `:49-67` `DirectionAt` | NaN, negative or Inf elapsed; MinHold 0; a negative MaxHold; NaN MinHold and NaN MaxHold → 1, tested on a seed whose initial direction is **-1** so the asserts discriminate; segment behavior: segment 0 is the initial direction, mid segment 1 is flipped, after two holds it is back | the first-boundary mutation and the `StrafeTests:56-58` boundary | — |
| `RPGBossStuckRecoveryRules.h:10` | `MaxAttempts` 0 or -1 refuses | negative Attempts, cap reached, cap >8, blocked or used | **Both are equivalent:** `Attempts>=0 && Attempts<MaxAttempts` already requires `MaxAttempts > 0`. Documented. |

## BL-61..65: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-61 | `Source/OneBossFight/Tests/RPGBossStaminaPressureGuardTests.cpp` | `OneBossFight.Framework.StaminaPressure.Guards` | **Controls:** 1 and 0.5. **Exact:** threshold 1 gives 1; max 3 gives 3; max 0 gives 0. **Discriminating → 0:** threshold -0.1 or 1.5; max -0.1; NaN stamina; +Inf threshold; NaN max. **Equivalent → 0:** threshold 0; stamina 1.1. |
| BL-62 | `.../RPGBossStrafeNextPositionGuardTests.cpp` | `OneBossFight.Framework.Strafe.NextPositionGuards` | **Control:** a valid step moves the boss and keeps radius 300. **Returns the unchanged Boss:** NaN Target.X, +Inf Target.Y, -Inf Boss.Y (checked component by component, because `Equals` cannot compare infinities), speed -200, delta NaN, +Inf or negative, `Dir` 2 or -2, and arc overflow. |
| BL-63/64 | `.../RPGBossStrafeHoldDirectionGuardTests.cpp` | `OneBossFight.Framework.Strafe.HoldDirectionGuards` | **`HoldSeconds`:** in range and deterministic (control); a NaN or -Inf min gives 0; a NaN or +Inf max gives the min of 0.4. **`DirectionAt`:** for a seed found with initial direction -1, invalid elapsed, MinHold, and MaxHold (including NaN MaxHold) return 1; the segment checks are -1, then 1, then -1. Elapsed times stay below about 2 s, so the bounded source loop runs only a few iterations. |
| BL-65 | `.../RPGBossStuckRecoveryGuardTests.cpp` | `OneBossFight.Framework.StuckRecovery.Guards` | **Control:** (blocked, unused, 0, 3) recovers. `MaxAttempts` 0 or -1 refuses (equivalent, documented). |

## Status

- **Names:** the new names are unique; the existing tests are named `.Rules`, mutation, the overflow witness and the runtime strafe profile.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
