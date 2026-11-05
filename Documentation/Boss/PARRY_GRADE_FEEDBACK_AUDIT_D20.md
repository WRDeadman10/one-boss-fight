# Parry grade-to-feedback audit (Queue D D20, 2026-11-03)

## Grade contract

`RPGParryGrade::Grade(offset, window)` fails closed to `None` for non-finite inputs, negative offset, nonpositive window, and `offset >= window`. For a valid offset, Perfect is `<40%`, Good is `>=40% and <80%`, and Late is `>=80% and <100%` (`Player/RPGParryGradeRules.h`). At the current proposed `.25 s` window, exact `.10 s` is Good, exact `.20 s` is Late, and exact `.25 s` has no grade. `RPGParryGradeTests.cpp` tests the exact thresholds, representative values on the lower side, close edge, invalid values, a monotonic sweep, and scales. D17 separately records missing `nextafter` checks immediately around `.10` and `.20`.

## Grade consumers and outputs

| Consumer/output | Mapping | Coverage and limit |
|---|---|---|
| Player's last-grade string / boss overlay | `LastGradeName` maps Perfect/Good/Late and defaults to None (`RPGPlayerParry.cpp:122–129`); `RPGBossOverlay::Format` prints `Grade=<string>` when parry data is present. | `RPGFrameworkRuntimeTests.cpp:832–833` asserts `Grade=Perfect`; no explicit formatter case for None/unknown text. Last grade is set on an actual resolver-parried contact (`RPGPlayerParry.cpp:138–144`). |
| Parry telemetry | `RecordParriedContact` maps enum to `Perfect|Good|Late|None` and emits `[FrameworkProof] parry_grade grade=... scale=...` (`RPGFrameworkMoveExecutor.cpp:34–45`). | BUILD-154 validator allows None; BUILD-154 live proof saw Perfect only. Good/Late are pure-rule-tested, not live-witnessed (`TEST_PLAN.md:513`). |
| Boss posture reaction | `PostureScale`: Perfect 1.0, Good .6, Late .3, None/unknown 0. Profile bool `bParryGradeScale` gates this scaling; default false preserves scale 1 (`RPGBossFrameworkProfile.h:116`). | `RPGParryGradeTests.cpp` asserts scales and monotonicity. `RecordParriedContact` applies it only through boss `NoteParried`; false setting is intentionally unscaled. |
| Optional post-parry recovery | `RPGBossRecoveryWindow::Seconds` maps grade to fractions .65/.45/.25, clamped to [.05,1.5] by default; unknown grade returns -1. `ScaledSeconds` returns 0 when feature scale is zero, otherwise validates and delegates (`RPGBossRecoveryWindowRules.h`). | `RPGBossParryRecoveryWiringTests.cpp` covers off, Perfect, Good composition, None, and NaN scale. These are pure tests; no claim of a grade-specific live result. |
| Hit-stop helper | `RPGBossHitStop::Seconds` maps Perfect/Good/Late to configured durations and None/unknown to zero; header explicitly says “Unwired by design.” | `RPGBossHitStopRulesTests.cpp` checks ordering, None=0, and config rejection. No runtime feedback claim. |
| Animation/audio/UI cue | No grade-specific parry animation or sound is wired in the reviewed sources; overlay text is the observed UI representation. | `PARRY_HOWTO.md` documents the no-animation/sound limit. Do not infer a full presentation response from grade telemetry. |

## Findings

The numerical mapping is consistent across the tested pure rule and current consumers: lower offset grade produces the strongest posture scale and the longest configured recovery; None never produces a grade-specific posture scale, recovery rejects it when enabled, and the unwired hit-stop helper returns zero. When posture-grade scaling is disabled, the executor deliberately uses scale 1.0 for any parried contact; this is the feature's default-off behavior, not an accidental grade mapping. No code mismatch found.

Follow-up is bounded: add the adjacent representable threshold cases already specified in D17; assert overlay `None` fallback; keep Good/Late live-witness gaps explicit if those grades are used as balance claims. No feature activation or product-value change proposed.

## Verification boundary

Static source, test, and retained-evidence inspection only. Tests/evidence were read, not rerun. No code, test, build, or Editor changes/execution.
