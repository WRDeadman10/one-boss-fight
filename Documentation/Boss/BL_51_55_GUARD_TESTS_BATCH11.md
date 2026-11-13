# BL-51..55: guard tests, batch 11 (Punish, ReactiveDodge, RecoveryWindow)

Assigned by X-2186 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 11 of 20. The scope follows the lead's list, without duplicating the named existing coverage.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source, and each file has positive controls.

## BL-54: re-verification (by hand)

| Header | Guard (line) | Gap tested | Existing coverage, not repeated |
|---|---|---|---|
| `RPGBossPunishRules.h` | `:14-17` cone escape; `:22-24` `IsValid`; `:27-31` `TravelSeconds` | NaN or negative cone, and exactly 180 (excluded) all force the check; 179.9 bypasses it. `IsValid` rejects NaN or zero startups, a negative run speed and a negative reach; reach 0 is valid. A negative run speed gives the max double | `…Punish.Rules` arithmetic, `…Punish.Sweep`, `…Punish.PackMontages` |
| `RPGBossReactiveDodgeRules.h` | `:11-12` `IsValid`; `:22` roll range | `HitsToStart` -1 or 101; Base above Max; Base and PerHit negative or NaN; a negative roll; a roll of 1 | `…ReactiveDodge.Rules`, the maximum-hit boundary, negative hit count; NaN roll; MaxChance above 1 |
| `RPGBossRecoveryWindowRules.h` | `:14-18` `IsValid`; `:37` Scale range; `:38` zero scale | Scale -0.1 or 3.01 → -1; Scale 3 accepted; Late below 0; Perfect above 1; `MinSeconds` 0 or negative; a zero scale returns 0 even with an invalid recovery | `…RecoveryWindow.Rules`: NaN scale, the normal zero scale, non-finite or non-positive recovery, inverted fractions and range |

## BL-51..53: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-51 | `Source/OneBossFight/Tests/RPGBossPunishGuardTests.cpp` | `OneBossFight.Framework.Punish.Guards` | **Control:** a 90° tracking channel bypasses the check. A NaN, -1 or exactly 180° cone requires the check; 179.9° bypasses it. **`IsValid`:** valid control; NaN Light or Heavy, 0 Light or Heavy, run speed -1 and reach -1 are invalid; reach 0 is valid. **`TravelSeconds`:** control 1 s; a run speed of -1 gives `TNumericLimits<double>::Max()`. |
| BL-52 | `.../RPGBossReactiveDodgeGuardTests.cpp` | `OneBossFight.Framework.ReactiveDodge.Guards` | **Controls:** 3 hits give 0.25; 200 hits give 0.65. **Invalid config → `!IsValid` and chance 0:** `HitsToStart` -1; `HitsToStart` 101, tested at 200 hits so the guard discriminates; Base 0.7 (above Max 0.65); Base -0.01 or NaN; PerHit -0.01 or NaN. **Roll:** control 0.1 dodges; -0.1 is refused (and would be below the chance); 1.0 is refused. |
| BL-53 | `.../RPGBossRecoveryWindowGuardTests.cpp` | `OneBossFight.Framework.RecoveryWindow.Guards` | **Control:** scale 1 gives 0.65. Scale -0.1 or 3.01 gives -1; scale 3 gives 1.5 (1.95 clamped to the max). **Config (isolated):** Late -0.01, Perfect 1.01, `MinSeconds` 0 or -0.1 are invalid and `Seconds` gives -1 (control: the default is valid). **Zero scale:** returns 0 with a -5 or NaN recovery; control: scale 1 with -5 gives -1. |

**Observability note:** the ReactiveDodge `Roll>=1` guard is an **equivalent mutant**. `Chance` never exceeds 1, so a roll of 1 or more can never be below it; the assert documents the behavior. The negative-roll guard does discriminate.

## BL-55: status

- **Names:** the new names are unique; the existing tests are named `.Rules`, `.Sweep`, `.PackMontages`, the HealPunish binding tests and the QueueE boundary tests.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
