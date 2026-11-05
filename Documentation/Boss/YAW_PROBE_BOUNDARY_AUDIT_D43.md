# Boss yaw probe boundary audit (Queue D43)

Scope: inspect yaw probe extrema, period endpoints, signed-angle range, and wraparound tests. Static review only; no test/build/Editor run.

## Rule and consumer semantics

- `RPGBossYawProbe::YawAt` returns `CenterDeg + AmplitudeDeg * sin(2π * SampleIndex / Period)`; it rejects nonfinite center/amplitude or nonpositive period by returning 0, but does not clamp, normalize, or validate the computed result (`Source/OneBossFight/Player/RPGBossYawProbeRules.h:7-17`). Negative sample indices are permitted by the formula.
- Actor source starts with `FindDeltaAngleDegrees` (canonical signed shortest yaw), then a positive non-Shipping CVar replaces it with `YawAt` and logs the raw result (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:424,430-436`). The selector consumes this as `SignedYawDegrees`; it does not re-normalize the synthetic value at the hook.
- For current 45° center / 5° amplitude, all probe values remain `[40°,50°]`, so no wrap is involved (`Docs/BossCombatReview/Execution/Codex/Proofs/YAW_PROBE_NO_HYSTERESIS_EXPECTED.md`). With a large positive dev-hook amplitude, output can exceed the canonical `[-180°,180°]` signed-yaw range; this is a probe-domain limit, not a production actor-yaw path.

## Existing tests and gaps

- `OneBossFight.Framework.BossYawProbe.Rules` tests 240 samples, periodicity, determinism, random centers `[-180,180]`, amplitudes `[0,60]`, periods `[1,240]`, negative and exact period indices, and zero/nonfinite input refusal (`Source/OneBossFight/Tests/RPGBossYawProbeTests.cpp:8-50`). The generated raw bounds are checked, not normalized angular bounds.
- Missing named endpoint cases: exact `Center=±180`, exact peak/trough `SampleIndex=Period/4` and `3*Period/4` under even period, period 1/2 wrap behavior in the downstream selector, and outputs immediately either side of ±180. No test asserts whether the hook should normalize or intentionally expose out-of-range synthetic yaw.
- Existing yaw probe expected sheets intentionally use a small 5° amplitude and check cone-boundary samples; the A/B audit notes retained logs only cover samples 0 and 1, insufficient for a full crossing. These are cone-boundary checks, not angular wrap tests.

Disposition: current intended small-amplitude cone probe is bounded and deterministic. Add explicit wrap/endpoint coverage or document the hook as valid only when `Center ± Amplitude` stays in signed range; do not infer a production yaw defect or claim ±180 wrap proof from the randomized pure test.
