# BL-56..60: guard tests, batch 12 (RepeatPenalty, Retreat, BossRules)

Assigned by X-2188 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 12 of 20.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source, and each file has positive controls.

## BL-59: re-verification (by hand)

| Header | Guard (line) | Gap tested | Existing tests, not repeated |
|---|---|---|---|
| `RPGBossRepeatPenaltyRules.h` | `:10` | `RepeatCount` 101 → 0; negative or NaN `BaseWeight`; negative or NaN `PerRepeatScale` | `…RepeatPenalty.Rules` |
| `RPGBossRetreatRules.h` | `:10-12` | NaN `RangeCm`, a negative `CloseRangeCm`, and `ThreatThreshold` <0 or >1 → false | `…Retreat.Rules`, close-boundary mutation, adjacent range/threat, adjacent thresholds, non-finite thresholds (negative Range, Threat>1, NaN CloseRange, Inf Threat/Threshold) |
| `RPGBossRules.h` | `:76-79` `ResolveTransition`; `:30-56` `Name` | non-finite Health, Max or Fraction, and Fraction <0 or >1 → NotReady; negative health → Dead; every `Name` string plus the `?` fallback for both enums | `…Codex.BossRulesEdges`, Tier2 BossRules (priority and threshold) |

## Observability correction (Retreat)

X-2188 described the negative `CloseRangeCm` case and the out-of-range thresholds as equivalent mutants. **Hand-checked against `:10-12`:**

| Case | Equivalent? | Why |
|---|---|---|
| a negative `CloseRangeCm` | **yes** | `RangeCm >= 0` (guarded) is never below a negative close range, so the result is false anyway |
| `ThreatThreshold > 1` | **yes** | `Threat01 <= 1` (guarded) never reaches it |
| NaN `RangeCm` | **yes** (also equivalent) | `NaN < Close` is false |
| **`ThreatThreshold < 0`** | **no, it discriminates** | without the guard, `(50, 100, .3, -.1)` gives `50<100 && .3>=-.1`, which is **true**; only the guard refuses it |

The tests label each case accordingly.

## BL-56..58: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-56 | `Source/OneBossFight/Tests/RPGBossRepeatPenaltyGuardTests.cpp` | `OneBossFight.Framework.RepeatPenalty.Guards` | **Controls:** 0 repeats give 10; 2 repeats give 4.9; 100 repeats are accepted (> 0). Count 101, base -10, base NaN, scale -0.1 and scale NaN each give 0. |
| BL-57 | `.../RPGBossRetreatGuardTests.cpp` | `OneBossFight.Framework.Retreat.Guards` | **Control:** (50, 100, 0.6) retreats. A -0.1 threshold is refused (**discriminates**). NaN range, close range -1 and threshold 1.1 are refused (**equivalent**, documented). |
| BL-58 | `.../RPGBossRulesGuardTests.cpp` | `OneBossFight.Framework.BossRules.Guards` | **Controls:** 50/100 at 0.5 → Start; 80/100 → AboveThreshold. NaN health, +Inf max, NaN fraction, fraction -0.1 and 1.1 → NotReady; health -1 → Dead. The exact `Name` text for all 6 `EBreakResult` and all 7 `ETransitionResult` values, and `?` for `static_cast<…>(200)` of each. |

## BL-60: status

- **Names:** the new names are unique; the existing tests are named `.Rules`, mutation, adjacent, `Codex.BossRulesEdges` and Tier2.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
