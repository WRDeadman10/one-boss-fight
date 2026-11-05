# Gap-closer timing-to-motion audit (Queue D34)

Scope: compare the maintained gap-closer rule to authored timing and framework warp/motion consumers. Static source/doc review only; no test/build/Editor/runtime activity.

## Range decision versus movement timeline

- `RPGBossGapCloser::ShouldClose` accepts the current-closing flag, range, enter range, and exit range. It rejects invalid/reversed inputs, then returns `Range > ExitRange` when starting and `Range > EnterRange` while already closing (`Source/OneBossFight/Player/RPGBossGapCloserRules.h:8-14`). There are no seconds, speed, animation, montage, warp, or movement commands in this rule.
- The project reference calls this gate “unwired by design” and says a caller owns chase state and action start/stop (`Documentation/Boss/RULES_REFERENCE_116_GAP_CLOSER.md:3-15`). The tests establish only this pure boolean/range behavior (`Source/OneBossFight/Tests/RPGBossGapCloserRulesTests.cpp:6-18`; strict exit equality separately in `RPGBossGapCloserExitBoundaryMutationTests.cpp:10-16`).
- A distinct framework card can carry `WarpStartSeconds`, `WarpEndSeconds`, distance/angle budgets, authored hold, commit, active-start, and recovery timing (`Source/OneBossFight/Player/RPGBossMoveCard.h`; playback and timeline consumption in `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:140-173,422-477,486-500`). The executor uses `RPGBossApproach::StepCm` for an optional smoothstep warp and has a peak-speed helper (`Source/OneBossFight/Player/RPGBossApproachRules.h:5-27`). This generic card-motion path is described as a gap-closer warp, but source does not connect the separate `ShouldClose` selector rule to the executor or identify a specific card assignment.
- `Move_Sevarog_BandGap_MOV001` is a named framework proof card visible by path; its name alone does not establish that it is the authored gap-closer action or prove its runtime motion assignment. Without asset readback, its warp times, budgets, sequence, and slot remain UNKNOWN.

## Timeline and claim boundary

The source supports a generic card timeline (commit/hold/active/recovery plus optional warp interval) and smoothstep movement math, but not a named gap-closer action timeline. The separate range/hysteresis rule is not connected to the generic executor in maintained source. Actual card assignment and authored times, selected sequence, root-motion behavior, movement speed/curve, start/stop caller, and landing position remain UNKNOWN pending asset/reflection/runtime evidence. No runtime mismatch or active integration claim is made.
