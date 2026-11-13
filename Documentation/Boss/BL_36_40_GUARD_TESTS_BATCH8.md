# BL-36..40: guard tests, batch 8 (Guard, Leash, MusicIntensity)

Assigned by X-2177 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 8 of 20. The scope follows the lead's list, and Leash is limited to the one confirmed gap.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source, and each file has positive controls.

## BL-39: re-verification (by hand)

| Header | Guard (line) | Gap tested | Existing tests, not repeated |
|---|---|---|---|
| `RPGBossGuardRules.h` | `:30-35` `IsProofParryPulse`; `:24-27` `CardOutcome` | NaN/Inf `SinceFirstAttack`; phase clamp at ±`FLT_MAX`; a huge negative phase gives a negative clock → false; exact edges (0.1 excluded, 0.5 wraps); negative counts treated as 0 | `…Guard.Rules` (Classify, Name, normal pulse); BlockChip's Classify use |
| `RPGBossLeashRules.h` | `:17` `RadiusCm > 0. && …` | **only** a negative finite radius → false (the leash is disabled) | invalid radius and zero (disabled) radius, inside, exact radius, outside by 1 cm, planar distance, large coordinates |
| `RPGBossMusicIntensityRules.h` | `:10` | health NaN/Inf/<0/>1 → 0; boost NaN/<0 → 0; boost exactly 0 and 1 accepted; phase ≤ 0 → 0 | `…MusicIntensity.Rules` |

## BL-36..38: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-36 | `Source/OneBossFight/Tests/RPGBossGuardGuardTests.cpp` | `OneBossFight.Framework.Guard.Guards` | **Control:** 0.05 s is a pulse. NaN and +Inf elapsed time give false. A phase of `1e300` behaves the same as `+FLT_MAX` (clamp). Phases of `-1e300` and `-FLT_MAX` give a negative clock → false. A clock of exactly 0.1 is false; exactly 0.5 is true (wrap), including 0.25 + phase 0.25. **CardOutcome:** control (1, 1, 1) = Parried; (-1, -1, -1) = Whiff; (1, -5, -5) = Hit; (0, 1, -3) = Guarded. |
| BL-37 | `.../RPGBossLeashGuardTests.cpp` | `OneBossFight.Framework.Leash.Guards` | **Control:** radius 100 puts a point 1000 cm away outside. Radius -100 gives false. |
| BL-38 | `.../RPGBossMusicIntensityGuardTests.cpp` | `OneBossFight.Framework.MusicIntensity.Guards` | **Controls:** 0.5 in phase 1, 0.75 in phase 2. Health NaN, +Inf, -0.1 or 1.1 gives 0. A NaN or -0.1 boost gives 0. A boost of 0 gives 0.5 and a boost of 1 gives 1 (clamped). Phase 0 or -1 gives 0. |

## BL-40: status

- **Names:** the new names are unique; the existing tests are `…Guard.Rules`, the `FBossArenaLeash*` set and `…MusicIntensity.Rules`.
- **Portability:** the `bool` equivalence check uses `TestTrue(a==b)`.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
