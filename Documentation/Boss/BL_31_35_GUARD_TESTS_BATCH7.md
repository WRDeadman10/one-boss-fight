# BL-31..35: guard tests, batch 7 (Fatigue, Feint, GapCloser)

Assigned by X-2174 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 7 of 20. The scope follows the lead's gap list.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source, and each file has positive controls.

## BL-34: re-verification (by hand)

| Header | Guard (line) | Gap tested | Existing tests, not repeated |
|---|---|---|---|
| `RPGBossFatigueRules.h` | `:11-12` | `GraceWhiffs<0`; `ReductionPerWhiff` <0, >1 or non-finite; `MinRateScale` >1 or non-finite → -1 | `…Fatigue.Rules`, exact rule boundaries, maximum whiff count, runtime profile |
| `RPGBossFeintRules.h` | `:10-11` | a negative reaction, negative Fast, negative `MinChance`; `MaxChance<MinChance` or `>1`; `Slow==Fast` → 0 | `…Feint.Rules`, max-chance boundary mutation |
| `RPGBossGapCloserRules.h` | `:10` | a negative `RangeCm` or `EnterRangeCm` → false | `…GapCloser.Rules`, exit and enter adjacent cases, collapsed band |

## BL-31..33: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-31 | `Source/OneBossFight/Tests/RPGBossFatigueGuardTests.cpp` | `OneBossFight.Framework.Fatigue.Guards` | **Control:** `RateScale(4)` = 0.9. **Each of these gives -1:** `GraceWhiffs` -1; `ReductionPerWhiff` -0.01, 1.01, NaN or +Inf; `MinRateScale` 1.01, NaN or -Inf. |
| BL-32 | `.../RPGBossFeintGuardTests.cpp` | `OneBossFight.Framework.Feint.Guards` | **Controls:** `Chance(.15)` = 0.45; `Chance(.375)` > 0.05. **Each of these gives 0:** a reaction of -0.1; Fast -0.1; `MinChance` -0.05; max 0.2 with min 0.3; `MaxChance` 1.01; Slow equal to Fast (0.3). |
| BL-33 | `.../RPGBossGapCloserGuardTests.cpp` | `OneBossFight.Framework.GapCloser.Guards` | **Controls:** a fresh gate at 800 closes; an active gate at 400 keeps closing. **Each gives false:** a negative range (fresh or active); a negative enter range (fresh or active). |

**Observability note for BL-33:** a negative `RangeCm` gives false with or without its guard. A negative range can never exceed a non-negative threshold, so this guard is an equivalent mutant and its tests document behavior rather than discriminate. The negative `EnterRangeCm` case **does** discriminate: without the guard, `(true, 400, -1, 500)` would return true.

## BL-35: status

- **Names:** the new names are unique; the existing tests are named `.Rules`, mutation and adjacent.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
