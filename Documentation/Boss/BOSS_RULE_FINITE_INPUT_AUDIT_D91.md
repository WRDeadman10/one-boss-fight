# Boss pure-rule finite-number audit (D91)

Date: 2026-11-03. Static source/test review of the 56 `*Rules.h` headers under `Source/OneBossFight`. No build or test was run and no source was changed.

## Findings that need explicit boundaries

| Rule | Source behavior | Existing evidence / gap |
|---|---|---|
| `RPGFlaskHudRules::DecideFill` | `RPGFlaskHudRules.h:18–27` accepts arbitrary nonnegative `int32` counts, then evaluates `Count * 3 > Maximum * 2` in signed `int32`; multiplication may overflow/trigger UB and invert the two-thirds comparison. For example `Count=357920370`, `Maximum=1073761110` is mathematically below two-thirds, but wrapped 32-bit arithmetic compares as above. | `RPGFlaskHudTests.cpp:11–17` covers ordinary values only; no upper-domain/overflow case. Either widen before multiplication or define a small valid-count domain and reject above it.
| `RPGBossLeashRules::IsOutsideArena` | `RPGBossLeashRules.h:9–12` checks only `RadiusCm > 0`; it does not reject nonfinite radius or vector components. A NaN distance compares false to the radius and is classified as inside; positive-infinite radius also silently makes every finite position inside. | D82's edge test `RPGBossQueueDEdgeTests.cpp:54–56` covers equality and adjacent finite distances, not NaN/infinity. The bool API has no distinct invalid-input result; decide whether malformed geometry should fail closed as outside or use an explicit result enum.
| `RPGBossYawProbe::YawAt` | `RPGBossYawProbeRules.h:11–14` rejects nonfinite inputs but does not validate the computed result; finite extreme center/amplitude can overflow `CenterDeg + AmplitudeDeg * Sin(Phase)`. | `RPGBossYawProbeTests.cpp:48–49` covers zero period and NaN input, and normal finite signal bounds; no extreme finite output case. This is a test/probe helper rather than the runtime turn authority.
| `RPGBossStrafe::HoldSeconds` / `NextPosition` | `RPGBossStrafeRules.h:10–34,37–47` checks inputs and intermediate arc/angle, but not final position; `HoldSeconds` allows arbitrary finite endpoints, so `MaxSeconds-MinSeconds` can overflow for extreme finite bounds. | `RPGBossStrafeTests.cpp:37–45,51–56` covers NaN/infinity input, invalid direction/radius, typical holds, and reversed ranges; no extreme finite result check. `DirectionAt` rejects nonpositive hold bounds, but direct `HoldSeconds` does not.
| `RPGBossTrack::RingFront` / `GroundedZ` | `RPGBossTrackRules.h:89,113` are raw arithmetic with no finite input or output check. `RingTouches` immediately rejects nonfinite front values (`:90–95`), so that downstream path fails closed; `GroundedZ` is passed directly to `SetActorLocationAndRotation` by `RPGFrameworkMoveExecutor.cpp:390`, with no local result guard. | `RPGFrameworkRuntimeTests.cpp:606,640` tests only ordinary finite examples. No nonfinite or extreme finite tests for either helper.

## Broader scan

The 56-header scan found direct `FMath::IsFinite`/`ContainsNaN` usage in 43 headers. The 13 without those tokens are: `RPGFlaskHudRules.h`, `RPGBuildSelectRules.h`, `RPGBossGuardRules.h`, `RPGBossComboAbortRules.h`, `RPGBossCloseClipSwapRules.h`, `RPGBossBakeFreshnessRules.h`, `RPGBuildRules.h`, `RPGBossStuckRecoveryRules.h`, `RPGBossPunishLimiterRules.h`, `RPGBossPresentationRules.h`, `RPGBossPatternDetectRules.h`, `RPGBossParryFeedbackRules.h`, and `RPGBossLeashRules.h`. Most take only enum/name/bool/integer inputs; the flask count arithmetic and leash geometry are the finite/overflow-relevant exceptions. A finite-check token elsewhere in a header does not prove that every numeric function or computed output is guarded.

Several other numeric helpers explicitly check their intermediates or bound inputs, including bleed state reset, stuck accumulator overflow reset, ring-contact input rejection, and the strafe arc/angle checks. This is a targeted source audit, not an exhaustive proof that all finite input combinations yield finite outputs. Existing tests do not currently cover the gaps above; no test pass is claimed.

## C-757 source disposition (2026-11-03)

Lead ordered two findings closed with minimal fail-safe code and edge cases: `RPGBossLeashRules.h:11-15` now treats nonfinite position/center/radius as outside, with NaN/infinity witnesses added at `RPGBossQueueDEdgeTests.cpp:59-64`; `RPGFlaskHudRules.h:28` widens both products to `int64`, with the large-maximum regression at `RPGFlaskHudTests.cpp:18`. These additions were not run by Codex.

## C-771 source disposition (2026-11-03; build pending)

The four remaining finite-output cases now fail closed: `RPGBossYawProbe::YawAt` returns neutral yaw when its computed result is nonfinite; `RPGBossStrafe::HoldSeconds` returns its finite minimum when the endpoint range or result overflows; `RPGBossTrack::RingFront` returns a negative invalid-radius sentinel on nonfinite/overflowing output, and `RingTouches` rejects negative fronts; `GroundedZ` returns finite `FloorZ` (or zero when the floor itself is nonfinite) if inputs or the sum are nonfinite. Ordinary finite valid values use the same arithmetic. E46-E50 now assert these fallbacks. No C++ build/test run by Codex; awaiting Lead validation.
