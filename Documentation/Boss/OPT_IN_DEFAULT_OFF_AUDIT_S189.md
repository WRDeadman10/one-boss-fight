# Experimental profile opt-in default-off audit (S189)

Static comparison of the editable profile defaults (`RPGBossFrameworkProfile.h`) with authored/runtime profile validation (`RPGBossFrameworkProfile.cpp`), the S156–S160 opt-in inventory, and the release proof gate in S188. The complete field/default inventory remains in `REF_PROFILE.md`; the grouped gate/reset/telemetry inventory is `PROFILE_OPT_IN_AUDIT_R156_160.md`.

## Default and group-gate review

- **Disabled scalar defaults:** selector tie band, cone hysteresis, neutral strafe, guard chip, parry recovery, parry posture, phase threshold, arena radius, center bias, LOS search, punish margin/reach, reaction delay range, fatigue grace/floor, and all five bleed fields default to zero. Their validation either keeps zero disabled or requires a bounded, coherent F5 configuration when activated. `PhaseTwoId` is empty, combo graph/root are empty, and optional stagger/phase clips are null by default.
- **Boolean defaults:** `bRangeBandPartition`, `ParryFairTelegraph`, `bAggroEnabled`, `bPhaseSupersedesStagger`, `bArenaLeash`, `bArenaCenterAuthored`, and `bParryGradeScale` default false. `bDamageEnabled` is a fixture identity contract (false in F3, true in F4/F5), not an optional gameplay feature switch.
- **Grouped disabled defaults:** posture and bleed groups are all-zero/off; flask reaction min/max are both zero/off; reposition max and turn rate are both zero and must agree; dodge history depth is zero/off; anti-cheese ranges are zero/off; arena behavior is off when radius is zero. Companion defaults such as dodge threshold/speed, anti-cheese streak, and center-bias start fraction remain inert while their owning gate is off.
- **Nonzero companion defaults:** `ParryFairMinScale=0.4` and the aggro thresholds/rates/window have valid baseline values, but their booleans are false. Validation checks the parameters' domains and only exposes the corresponding behavior when the F5-gated boolean is enabled.

## Discovered lane-gate mismatch and fix

`bRangeBandPartition` was documented as an F5-lane option in `RPGBossFrameworkProfile.h`, but `ValidateProfile` had no corresponding `!bF5` refusal. The enabled property changes resolved-card band validation (`RPGBossFrameworkProfile.cpp:195`), so it could be set on F3/F4 profiles despite the documented lane. Added a fail-closed `Framework.Profile.Domain` refusal in `ValidateProfile` and regression assertions in `RPGFrameworkRuntimeTests.cpp`: default F3 remains valid; enabled partition is refused in F3 and F4; enabled partition is accepted for a valid F5 profile. Updated the range-band how-to and the prior S156–S160 audit note.

The other opt-in guards reviewed match their authored lane/group requirements in source. This is not approval to enable any option for release: S188's owner decision, executed tests, matched live control, and packaged evidence requirements still apply. The new C++ regression assertions were not run by Codex; Lead must build and run the framework suite before accepting the code change. No live/profile asset was changed.
