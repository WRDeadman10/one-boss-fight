# AJ-C01–C05 — C-998 override hotfix source audit

Date: 2026-11-07. This is static source/test review only. It does not replace Lead's native build or PIE result.

## AJ-C01 — override lifetime and restoration

`URPGDodgeTiming::EndPlay` calls the full restore path (`RPGDodgeTiming.cpp:40–46`). `TickEldenRingInput` services override state before returning for an inactive input context (`:420–427`). A successful override stores montage/kind/deadline (`:634–637`); while playback is active, it restores the ability arrays but retains semantic metadata (`:688–695`). When playback ends, or an override never starts before its deadline, the full restore clears metadata (`:697–699`). No static path was found that leaves the temporary ability arrays substituted after interruption or component teardown.

## AJ-C02 — classification timing and identity

Call sites label the temporary slots explicitly: AirLight → `JumpLight` (`RPGDodgeTiming.cpp:470–482`), AirHeavy → `JumpHeavy` (`:489–515`), GuardCounter → `Strong` (`:528–532`). `GetActiveMontageOverrideKind` resolves by object identity (`:534–537`; helper `RPGAttackKind.h:38–42`). SwingTracker checks this before consulting restored ability arrays (`RPGSwingTracker.cpp:177–199`). Hit intake captures the kind from the exact current montage during `BuildRecord` at event time (`RPGHitIntake.cpp:362–401`, `:511`), then uses that captured value after its next-tick finalization deferral (`:522`, `:575–587`).

## AJ-C03 — AttackData mapping

`RPGAttackDataNameForKind` maps jump-light to the default asset, jump-heavy and ground strong to the strong asset, charged to charged, and knockdown to knockdown (`RPGAttackKind.h:44–57`). The hit record changes to the canonical asset when the pack's delayed HitData differs (`RPGHitIntake.cpp:579–590`) and marks the provenance `MontageOverride`. The path format matches the existing four pack data asset names in `Scripts/Editor/pie_hit_intake.py:14–18` and `g3_dump_attack_data.py:7`. Static source review cannot prove `StaticLoadObject` succeeds for the packaged object path; Lead runtime logging must confirm AirHeavy reports `StrongMeleeAttackData`.

## AJ-C04 — table and health flow

For `SwordCombatStyle`, the JumpHeavy row has posture 38 and receives the table's 0.39 health multiplier (`RPGWeaponAttackTable.cpp:42–66`). Hit intake applies the selected row multiplier to the existing scaler (`RPGHitIntake.cpp:608–619`, `:642–646`). Thus the C-998 expected -22.4 HP must be checked in the Lead probe; it is not asserted by source review. For a native-health boss, the row is passed through `ApplyPlayerAttackHit` (`RPGHitIntake.cpp:632–636`), so the route's own health semantics remain distinct from the pack boss path.

## AJ-C05 — test and evidence limits

`OneBossFight.Hit.Classify` now covers matching override identity for AirLight/AirHeavy/GuardCounter, mismatch refusal, and canonical AttackData mapping (`RPGAutomationTests.cpp:420–439`). These are pure helper cases; they do not instantiate the component or exercise array restoration, playback, delayed HitData, or an actual asset load. Codex did not run native tests or a build. TEST_PLAN records Lead's next steps as build/run of the native suite followed by both-route `P_C992_AIRHITS` confirmation; owner review of the new strips remains separate.

## Disposition

No additional source defect was established by this static audit. Remaining validation is Lead-owned: native compile/test, AirHeavy `StrongMeleeAttackData`/`JumpHeavy`/posture 38 readback, expected health-row delta on both routes, and retention of raw logs. No asset, build, PIE, package, or level edit was made.

## Additional C++ compile-shape checklist

A second source-only pass applied the Queue V C-871 checklist to the changed files. Declarations and definitions match for the changed override, classifier, and BuildRecord APIs; all call sites were found, and the legacy `ActiveGuardCounterMontage` field has no remaining references. The added `RPGAttackKind.h` include precedes each generated header; changed control-flow files have balanced preprocessor directives (DodgeTiming 0/0; SwingTracker 4/4; HitIntake 3/3; automation tests 4/4). The new paths add no lambdas, and the reflected header keeps its generated include last. Scoped `git diff --check` is clean. These checks do not establish UE compilation or runtime asset loading; Lead's build/native/PIE checks remain pending.
