# BL-26..30: guard tests, batch 6 (Desperation, Difficulty, Enrage)

Assigned by X-2172 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 6 of 20. The scope follows the lead's gap list.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source, and each file has positive and boundary-valid controls.

## BL-29: re-verification (by hand)

| Header | Guard (line) | Gap tested | Existing tests, not repeated |
|---|---|---|---|
| `RPGBossDesperationRules.h` | `:10-11` | `HealthFraction<0` or `>1`, `StartFraction<=0`, and `MaxMultiplier<1` give 1; `MaxMultiplier==3` is accepted | `…Desperation.Rules`, full-threshold mutation |
| `RPGBossDifficultyRules.h` | `:12-14` `IsValid`; `:18` neutral `FScales()` | non-positive minima, reversed ranges, over-bound maxima, and each non-finite field give the neutral scales; exact maxima 3/2/2 and equal endpoints are valid | `…Difficulty.Rules`, equal-endpoints mutation, endpoint-adjacent, invalid inputs |
| `RPGBossEnrageRules.h` | `:16-17` `IsValid` | `MaxDamageScale<1` and `MaxSpeedScale<1` fail closed (scales 1, progress 0); exact bounds 3 and 2 are accepted | `…Enrage.Rules`, ramp endpoint-adjacent, non-finite and repeat |

## BL-26..28: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-26 | `Source/OneBossFight/Tests/RPGBossDesperationGuardTests.cpp` | `OneBossFight.Framework.Desperation.Guards` | **Controls:** 1.5 at 0 health, 1.25 half-way, 1 above the start. **Invalid → 1** (checked at 0 health): health -0.1 and 1.1; start 0 and -0.1; max multiplier 0.9. A max of exactly 3 gives 3. |
| BL-27 | `.../RPGBossDifficultyGuardTests.cpp` | `OneBossFight.Framework.Difficulty.Guards` | **Control:** the default at 0.5 is non-neutral (damage 1.025, speed 1.05). **Invalid → `!IsValid` and neutral {1, 1, 1}:** each minimum 0 and negative; each Max below its Min; `DamageMax` 3.01; `SpeedMax` 2.01; `TelegraphMax` 2.01; each of the 6 fields NaN, +Inf or -Inf. **Valid:** maxima of exactly 3/2/2, with `Evaluate(1)` returning them to within 1e-12, and equal endpoints. |
| BL-28 | `.../RPGBossEnrageGuardTests.cpp` | `OneBossFight.Framework.Enrage.Guards` | **Controls:** the default at 60 s gives damage 1.25 and speed 1.125. A damage max of 0.99 is invalid: damage 1, speed 1 and progress 0 at 120 s. A speed max of 0.99 is invalid the same way. A damage max of exactly 3 reaches 3 at 120 s; a speed max of exactly 2 reaches 2. |

## BL-30: status

- **Names:** the new names are unique; the existing tests are named `.Rules`, mutation, adjacent, and non-finite/repeat.
- **Precision:** the Difficulty upper-bound check uses a 1e-12 tolerance, because `Lerp` at 1 may be one ulp off.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
