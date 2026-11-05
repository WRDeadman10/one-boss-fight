# Queue E proposal: 200 bounded tasks

Proposed by Codex, 2026-11-03, following Claude C-768. Queue D exhausted (X-967). This proposal has 120 concrete test tasks, 40 decision audits, and 40 owner-scoped opt-in protocols. No behavior changes are authorized. Tests are authored only; Claude builds once after each five-task C++ batch. Label any Source-touching task Source changed. Use std::numeric_limits for infinity/NaN and cite exact engine header lines for engine APIs. No commit, push, asset mutation, Unreal run, or build by Codex.

## E1-E120: concrete tests (24 batches of five)

Each task extends the named test file or creates it if absent. Acceptance is the stated assertion; audit IDs identify the source gap. Offline fixture tasks are Python tests.

### E1-E5: selector/start parity
1. **E1 [D5-D7]** Source/OneBossFight/Tests/RPGBossSelectorStartParityTests.cpp: add one test asserting same eligible snapshot. Acceptance: the assertion runs under the existing suite registration and fails if that contract is violated.
2. **E2 [D5-D7]** Source/OneBossFight/Tests/RPGBossSelectorStartParityTests.cpp: add one test asserting cone boundary equality. Acceptance: the assertion runs under the existing suite registration and fails if that contract is violated.
3. **E3 [D5-D7]** Source/OneBossFight/Tests/RPGBossSelectorStartParityTests.cpp: add one test asserting adjacent cone values. Acceptance: the assertion runs under the existing suite registration and fails if that contract is violated.
4. **E4 [D5-D7]** Source/OneBossFight/Tests/RPGBossSelectorStartParityTests.cpp: add one test asserting zero/one candidate determinism. Acceptance: the assertion runs under the existing suite registration and fails if that contract is violated.
5. **E5 [D5-D7]** Source/OneBossFight/Tests/RPGBossSelectorStartParityTests.cpp: add one test asserting fixed-seed tie repeatability. Acceptance: the assertion runs under the existing suite registration and fails if that contract is violated.

### E6-E10: parry timing and cost gaps
6. **E6 [D17]** Source/OneBossFight/Tests/RPGBossParryBoundaryUpgradeTests.cpp: assert the representable values immediately before and after the 40% grade boundary classify Perfect and Good. Acceptance: both neighboring grades are asserted using std::nextafter.
7. **E7 [D17]** Source/OneBossFight/Tests/RPGBossParryBoundaryUpgradeTests.cpp: assert the representable values immediately before and after the 80% grade boundary classify Good and Late. Acceptance: both neighboring grades are asserted using std::nextafter.
8. **E8 [D17]** Source/OneBossFight/Tests/RPGBossParryBoundaryUpgradeTests.cpp: pass the last valid representable offset to both IsOpen and Grade. Acceptance: it is open and grades Late, while the exact close is closed and None.
9. **E9 [D18]** Source/OneBossFight/Tests/RPGBossParryBoundaryUpgradeTests.cpp: assert an accepted press at ReadyAt advances ReadyAt by max(window,cooldown). Acceptance: exact resulting ReadyAt is asserted.
10. **E10 [D19]** Source/OneBossFight/Tests/RPGBossParryBoundaryUpgradeTests.cpp: assert CanPress rejects positive and negative infinity in both stamina and cost. Acceptance: all four invalid-input combinations return false.

### E11-E15: poise/stagger/aggro/difficulty audited gaps
11. **E11 [D94]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert exact poise ramp endpoint equals BasePerSecond*MaxScale. Acceptance: exact endpoint assertion is present.
12. **E12 [D94]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert zero delay and zero elapsed return base rate, and MaxScale 1 remains flat at ramp endpoint. Acceptance: both cases are explicit.
13. **E13 [D95]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert stagger scale endpoints 0 and 3 and invalid negative/NaN/infinite overrides return neutral. Acceptance: each endpoint and invalid class has an assertion.
14. **E14 [D96]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert exact close-entry and close-exit range thresholds preserve the source strict-comparison semantics. Acceptance: equality and immediate neighbors are asserted.
15. **E15 [D97]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert difficulty values adjacent to 0 and 1 remain valid and interpolate within configured endpoints. Acceptance: std::nextafter samples at both ends are checked.

### E16-E20: enrage/limiter/retreat/gap-closer audited gaps
16. **E16 [D98]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert exact ramp endpoint and adjacent elapsed samples. Acceptance: std::nextafter neighbors are bounded and the endpoint reaches the configured cap.
17. **E17 [D98]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert NaN and ±infinity elapsed time fail to baseline and repeated identical calls are deterministic.
18. **E18 [D100]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert maximum allowed budget 100, rejected 101, and MAX_int32 corrupt use count refuse without increment.
19. **E19 [D102]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert retreat range neighbors and configurable threat-threshold just-below/equality behavior.
20. **E20 [D103]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert nextafter neighbors around both active-enter and new-action exit boundaries, including accepted equal thresholds.

### E21-E25: poise/stagger/aggro/difficulty residual gaps
21. **E21 [D94]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert nextafter samples around delay+ramp endpoint remain ordered and capped.
22. **E22 [D95]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert negative and MAX_int32 unknown phases return neutral scale with explicit overrides.
23. **E23 [D96]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert far-entry and far-exit equality plus adjacent representable ranges.
24. **E24 [D96]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert dodge-rate neighbors around enter/exit thresholds and invalid config preserves current band.
25. **E25 [D97]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert invalid negative/>1/infinite difficulty and equal speed/telegraph endpoints.

### E26-E30: fatigue/dodge/cue/defense audited gaps
26. **E26 [D99]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert exact grace+1, floor-reaching fatigue count, zero reduction, and floor 1 behavior.
27. **E27 [D101]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert MAX_int32 recent hits with HitsToStart=0 does not overflow and clamps to MaxChance.
28. **E28 [D104]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert cue jitter changes for at least one alternate seed and one alternate cue index while staying in safe band.
29. **E29 [D104]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert zero-jitter and out-of-safe-interval bases clamp exactly to both safe endpoints.
30. **E30 [D100]** Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp: assert defense cooldown at 3 seconds and its immediate representable neighbors.

### E31-E35: combo/selector/model audited gaps
31. **E31 [D124]** Source/OneBossFight/Tests/RPGBossComboTests.cpp: assert MaxDepth refusal precedes unknown-root refusal when both faults are present.
32. **E32 [D125]** Source/OneBossFight/Tests/RPGBossComboTests.cpp: assert malformed unreachable orphan nodes are still structurally validated.
33. **E33 [D127]** Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp: assert positive subnormal weight can underflow to a zero score while remaining eligible; record the audited edge without changing production behavior.
34. **E34 [D130]** Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp: assert reset twice reproduces a fresh selector's first seeded tie result after history has advanced.
35. **E35 [D131]** Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp: assert an actually open hit window is cleared by normal finish, with positive pre-finish and zero post-finish counts.

### E36-E40: D13 executor lifecycle harness, no watchdog
36. **E36 [D13]** Source/OneBossFight/Tests/RPGBossExecutorHarnessTests.cpp: assert equal-generation rearm refusal preserves the active card identity.
37. **E37 [D13]** same file: assert older-generation rearm reports MoveModel.Generation and preserves the accepted callback token.
38. **E38 [D13]** same file: assert strictly newer-generation rearm clears ActiveCard and leaves executor idle.
39. **E39 [D13]** same file: assert repeated abort leaves no active card and remains idle.
40. **E40 [D13]** same file: assert a stale callback token is rejected while the current active card/token remain accepted. No watchdog assertion.

### E41-E45: move-model refusal and open-window cleanup
41. **E41 [D126]** Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp: assert invalid card refusal precedes simultaneous invalid target.
42. **E42 [D126]** same file: after a completed move, assert vertical-limit refusal precedes stale-frame refusal.
43. **E43 [D131]** same file: open an active hit window, abort, and assert window count returns to zero.
44. **E44 [D131]** same file: open an active hit window, force backward-clock refusal, and assert cleanup returns model to idle with zero windows.
45. **E45 [D131]** Source/OneBossFight/Tests/RPGBossEncounterLoopTests.cpp: after generation reset from an open window, assert open-window count is zero.

### E46-E50: D91 extreme finite-output fail-closed regressions
46. **E46 [D91]** `Source/OneBossFight/Tests/RPGBossFiniteRuleOverflowWitnessTests.cpp`: finite max center/amplitude inputs to YawAt return the neutral yaw fallback.
47. **E47 [D91]** same file: finite extreme HoldSeconds bounds return the finite minimum fallback when their range subtraction overflows.
48. **E48 [D91]** same file: finite max RingFront inputs return the invalid-radius sentinel and RingTouches rejects it.
49. **E49 [D91]** same file: finite max FloorZ and CapsuleHalfHeight return finite FloorZ fallback when GroundedZ addition overflows.
50. **E50 [D91]** same file: opposite-sign extreme yaw inputs return the neutral yaw fallback. Ordinary finite inputs retain their prior arithmetic path.

### E51-E55: D13 executor harness recovery invariants, no watchdog
51. **E51 [D13]** Source/OneBossFight/Tests/RPGBossExecutorHarnessTests.cpp: assert equal-generation rearm leaves the live executor non-idle.
52. **E52 [D13]** same file: assert older-generation rearm leaves the live executor non-idle and current token accepted.
53. **E53 [D13]** same file: assert same-generation recovery after abort leaves executor idle with no active card.
54. **E54 [D13]** same file: assert retry after recovery starts a new monotonically increasing instance token.
55. **E55 [D13]** same file: assert new-generation rearm leaves no active card and invalidates previous generation token. No watchdog assertion.

### E56-E60: damage-scaler and bleed finite-input gaps
56. **E56 [D92]** Source/OneBossFight/Tests/RPGBossDamageBleedFiniteInputTests.cpp: assert nonfinite OnLoss time/amount returns zero and enqueues no loss.
57. **E57 [D92]** same file: assert nonfinite OnHit multiplier is normalized to 1 and claims a matching pending loss without adjustment.
58. **E58 [D92]** same file: assert Apply returns unchanged finite health for nonfinite adjustment and preserves nonfinite Health input.
59. **E59 [D93]** same file: assert FLT_MAX buildup plus finite input procs once, resets buildup, and increments proc count safely.
60. **E60 [D93]** same file: assert an externally supplied state threshold above configured ThresholdMax persists as current behavior.

### E61-E65: offline evidence tools
61. **E61 [D84]** `Scripts/Tools/test_queue_e_driver_fixtures.py`: assert the generated automation-ID index contains rows and no duplicate IDs, and that the source inventory tool recognizes both supported registration macro forms. Acceptance: fixture checks the maintained index/source contract without invoking Unreal.
62. **E62 [D85]** same file: assert the packaged benchmark wrapper has a bounded timeout, waits only to that deadline, and terminates its owned PID tree on expiry. Acceptance: source fixture fails if any timeout/cleanup contract is removed.
63. **E63 [D86]** same file: assert the experiment runner encloses benchmark execution in `finally` cleanup for its owned GPU sampler. Acceptance: source fixture pins cleanup structure without starting processes.
64. **E64 [D87]** same file: assert the editor bridge runner exits nonzero when a task is not completed or an encounter probe reports failure/incomplete output. Acceptance: fixture pins failure propagation without contacting the bridge.
65. **E65 [D88]** same file: assert evidence collection uses stop-on-error, checks copied run folders, and rejects absent/empty archives. Acceptance: source fixture pins fail-closed behavior without copying or archiving files.

### E66-E70: offline audit tools
66. **E66 [D89]** `Scripts/Tools/test_queue_e_audit_fixtures.py`: assert each D89 inventory CSV path exists, is unique, and that the known parse exception remains represented. Acceptance: fixture detects stale/malformed inventory without importing Editor scripts.
67. **E67 [D90]** same file: assert all three inventoried editor dry-run controls remain explicitly default-off. Acceptance: fixture checks source constants and gate presence; it does not execute or change them.
68. **E68 [D91]** same file: pin closed finite-input gaps (nonfinite leash geometry, widened flask arithmetic, and fail-closed extreme yaw) alongside remaining finite-rule witness cases. Acceptance: evidence distinguishes fixed cases from remaining witnesses.
69. **E69 [D92]** same file: pin reciprocal damage-scaler boundary coverage separately from nonfinite-input fixtures. Acceptance: both source contracts remain represented in their focused tests.
70. **E70 [D93]** same file: pin MAX_int32 proc-counter saturation and the separate extreme finite buildup test against ordinary property-test coverage. Acceptance: each risk has identifiable regression evidence.

### E71-E75: re-do executing C++ tests (original source-grep fixtures not accepted; C-772)
71. **E71 [D15]** `Source/OneBossFight/Tests/RPGBossSelectorRouteLifecycleTests.cpp`, `FBossSelectorImmediateRouteFreshSnapshot`: execute immediate authored-card start with the current combo snapshot, record selector memory from that snapshot clock, finish, and assert the next normal selection sees cooldown.
72. **E72 [D15]** same file, `FBossSelectorDelayedRouteFreshSnapshot`: execute pre-pause near-card lifecycle, reject stale-range pending far card, accept it with fresh wake snapshot, record wake clock, then assert cooldown on the next selection.
73. **E73 [D5-D6]** same file, `FBossSelectorGenerationResetClearsMemory`: execute reset into a newer generation with a lower clock and prove the former cooldown no longer blocks the first move.
74. **E74 [D7]** same file, `FBossSelectorZeroTieSeedIsValid`: execute zero-seed/tie-band initialization and selection; assert the choice corresponds to an eligible candidate.
75. **E75 [D15]** same file, `FBossSelectorRouteClockRegressionRefused`: execute a route clock regression and assert the named stale-decision refusal and no chosen card.

### E76-E80: re-do executing C++ boundary tests (C-772)
76. **E76 [D99]** `Source/OneBossFight/Tests/RPGBossQueueEBoundaryTests.cpp`, `FBossFatigueMaximumWhiffCount`: execute `RateScale(MAX_int32)` and assert finite output clamped to the configured floor.
77. **E77 [D100]** same file, `FBossPunishLimiterMaximumCounterFailsClosed`: execute `CanUse`/`RecordUse` on a corrupted `MAX_int32` use count; assert refusal and unchanged state.
78. **E78 [D101]** same file, `FBossReactiveDodgeNegativeHitCountFailsClosed`: execute the helper with `MIN_int32` recent hits and assert zero chance/no dodge.
79. **E79 [D102]** same file, `FBossRetreatNonfiniteThresholdsFailClosed`: execute NaN range and infinite threat/threshold cases; assert fail-closed false.
80. **E80 [D103-D104]** same file, `FBossGapAndCueNonfiniteInputsFailClosed`: execute infinite gap thresholds and nonfinite cue inputs; assert the documented fail-closed outcomes.

### E81-E85: re-do and covered-case replacements (C-772)
81. **E81 [D105]** Covered by `FBossMoveSelectorInit` (zero weight rejects with `Selector.Domain`) and `FBossMoveSelectorSubnormalScore` (positive subnormal remains eligible with zero score). Replacement: `FBossLeashLargeFiniteCoordinate` in `RPGBossQueueDEdgeTests.cpp` executes a large finite displacement and asserts outside-arena behavior.
82. **E82 [D106]** Covered by `FBossMoveSelectorPolicy` and `FBossMoveSelectorBoundedTie` (input-order tie and seeded repeatability). Replacement: `FRPGFlaskHudFillTest` executes `MAX_int32` count/max arithmetic and asserts full fill without overflow.
83. **E83 [D107]** Covered by `FBossMoveSelectorRepeatedResetTieReplay` (two resets reproduce fresh first tie choice). Replacement: `FBossYawProbeRules` executes positive-infinity center/amplitude inputs and asserts neutral fallback.
84. **E84 [D108]** Covered by `FBossMoveModelCrossing`, `FBossMoveModelAbort`, `FBossMoveModelGeneration`, and `FBossMoveModelBackwardClockWindowCleanup`, which directly assert open-window cleanup for finish, abort, generation reset, and backward-clock refusal. Replacement: `FBossAggroRules` executes NaN range/infinite dodge-rate inputs and asserts current-band preservation.
85. **E85 [D110]** Covered by `FBossEncounterPureLoopRestart` for selector/model restart only; actor-level terminal restart remains outside that test's evidence. Replacement: `FBossEnrageRules` executes invalid infinite/out-of-bound maxima and asserts baseline fallback.

### E86-E90: re-do and covered-case replacements (C-772)
86. **E86 [D110]** Not reachable in a transient world; existing live PIE lifecycle evidence: BUILD-80 regression across F3-F8 and three clean restart runs, plus BUILD-81 lethal-hit/death/new-generation restart. Neither is a direct completed-state restart matrix assertion. Replacement: use a pure rule/property gap in a later batch; no state setter or pack-target transient test.
87. **E87 [D110]** Not reachable in a transient world; BUILD-81 witnesses lethal-hit death and a clean generation-2 restart; BUILD-80 records three clean restart runs. This is live lifecycle evidence, not direct transient eligibility assertions. Replacement: pure rule/property gap in a later batch.
88. **E88 [D110]** Not reachable in a transient world; existing BUILD-80/81 live PIE lifecycle evidence does not directly prove the Failed guard. Replacement: pure rule/property gap in a later batch; retain `FBossRestartFailedTerminalIdempotence` as the transient terminal-path test.
89. **E89 [D110]** `RPGBossEncounterRestartMatrixTests.cpp`, `FBossRestartFailedTerminalIdempotence`: execute public `Fail` twice on a transient boss; assert Failed persists, generation is unchanged, and restart refusal returns the named state token. Expected error is declared once.
90. **E90 [D110]** Not reachable in a transient world; live lifecycle references are BUILD-80/81, but neither is cited as direct executor-counter reset evidence. Replacement: pure rule/property gap in a later batch; no counter setter or pack-target transient test.

### E91-E95: D38 turn-latch exact boundaries (replacements for duplicate route tests)
91. **E91 [D38]** `RPGBossTurnLatchBoundaryTests.cpp`, `FBossTurnLatchExactThreshold`: execute the exact 150-degree back-axis threshold and assert the previous turn direction remains latched without a flip.
92. **E92 [D38]** same file, `FBossTurnLatchBelowThresholdReleases`: execute just below 150 degrees and assert the latch releases and counts the reversal.
93. **E93 [D38]** same file, `FBossTurnLatchAboveThresholdRetains`: execute just above 150 degrees and assert the previous direction remains latched.
94. **E94 [D38]** same file, `FBossTurnLatchZeroAndWrap`: execute zero yaw and both ±180 wrap crossings; assert zero clears active direction and wrap follows the shortest path.
95. **E95 [D38]** same file, `FBossTurnLatchRefusalPreservesState`: execute committed, zero-speed, negative-time, and nonfinite-time refusals; assert yaw and all latch memory fields remain unchanged.

### E96-E100: D40 strict arena leash radius boundaries
96. **E96 [D40]** `RPGBossArenaLeashBoundaryTests.cpp`, `FBossArenaLeashInsideRadius`: execute 249 cm planar distance against radius 250 and assert inside.
97. **E97 [D40]** same file, `FBossArenaLeashExactRadius`: execute equality at 250 cm and assert strict comparison keeps it inside.
98. **E98 [D40]** same file, `FBossArenaLeashOneCentimeterOutside`: execute 251 cm and assert outside.
99. **E99 [D40]** same file, `FBossArenaLeashUsesPlanarDistance`: execute large vertical separation at exact planar radius and assert Z does not affect classification.
100. **E100 [D40]** same file, `FBossArenaLeashInvalidAndDisabledRadius`: execute nonfinite position fail-closed and zero-radius disabled behavior. These are helper behavior tests; actor-level leash transitions remain unproved.

### E101-E105: covered scaler case and adjacent rule gaps
101. **E101 [D92]** Covered by `FDamageScalerLowerWindowBoundaryTest`, `FDamageScalerWindowBoundaryMutationTest`, and `FDamageScalerReciprocalBoundaryTest`; these execute inclusive boundaries and adjacent representable instants in both event orders. Replacement: `FBossRetreatAdjacentRangeAndThreat` in `RPGBossQueueEAdjacentBoundaryTests.cpp` executes adjacent range and configurable threat-threshold edges from D102.
102. **E102 [D93]** same file, `FBossBleedExactThresholdCrossing`: execute one-ULP-below buildup (Added) and exact threshold buildup (Proc), checking state/count.
103. **E103 [D96]** same file, `FBossAggroRangeAdjacentBoundaries`: execute exact and adjacent close/far entry/exit range boundaries.
104. **E104 [D103]** same file, `FBossGapCloserExitAdjacentRepresentable`: execute one representable instant below, at, and above the strict exit boundary.
105. **E105 [D103]** same file, `FBossGapCloserEnterAdjacentAndCollapsedBand`: execute adjacent active-enter values and equal-threshold behavior. Gap-closer remains a pure unwired helper.

### E106-E110: selector order, aggro refusal, executor-counter gap
106. **E106 [D105]** Covered by `FBossMoveSelectorInit` (zero-weight candidate rejects with `Selector.Domain`). Replacement: `FBossMoveSelectorSeededTieOrderPermutation` in `RPGBossMoveSelectorTests.cpp` executes the D106 same-seed tie-index behavior under candidate permutation and asserts identity follows input order.
107. **E107 [D106]** `RPGBossMoveSelectorTests.cpp`, `FBossMoveSelectorZeroBandPermutation`: execute exact ties with zero tie band under two candidate orders; assert the first input candidate wins.
108. **E108 [D107]** Covered by `FBossMoveSelectorRepeatedResetTieReplay`, which resets twice and compares the next selection to a fresh selector's first seeded choice. Replacement: `FBossAggroInvalidConfigPreservesState` in `RPGBossQueueEPolicyBoundaryTests.cpp` executes malformed threshold order and asserts the current band is preserved (D96).
109. **E109 [D108]** Covered by `FBossMoveModelOpenWindowFinishCleanup`, `FBossMoveModelOpenWindowAbortCleanup`, `FBossMoveModelGeneration`, and `FBossMoveModelBackwardClockWindowCleanup`. Replacement: `FBossAggroBehaviorOverrideAtBoundaries` in `RPGBossQueueEPolicyBoundaryTests.cpp` executes hugging/kiting precedence at exact close/far exit boundaries (D96).
110. **E110 [D109]** Not reachable in the current transient harness: direct framework executor accepted/guarded/parried counter ordering requires authored montage playback and the real weapon-window sweep; the public executor API has no hit injection and no counter setters are allowed. Minimal follow-up: a real proof-map test that drives a card montage/contact and reads the existing counter accessors. Pure resolver behavior remains covered by `FRPGDamageDecideTest` and related resolver tests; that is not executor-counter evidence.

### E111-E115: D40 actor-level target-fault boundary matrix
111. **E111 [D110]** Not reachable in a transient world; live PIE arena leash transition is witnessed by BUILD-121 / MOV-005 (outside -> abort -> center -> resume -> clean completion). Replacement: pure rule/property gap in a later batch.
112. **E112 [D110]** Not reachable in a transient world; BUILD-121 / MOV-005 is the live actor-level leash proof, with its documented F5-only scope. Replacement: pure rule/property gap in a later batch.
113. **E113 [D110]** Not reachable in a transient world; BUILD-121 / MOV-005 witnesses the actor leash transition, not the actor TargetFault exact/adjacent matrix. Replacement: pure rule/property gap in a later batch.
114. **E114 [D110]** Duplicate Fail idempotence remains covered by `FBossRestartFailedTerminalIdempotence`; actor leash proof is BUILD-121 / MOV-005. Replacement: pure rule/property gap in a later batch.
115. **E115 [D110]** Not reachable in a transient world; BUILD-121 / MOV-005 is live leash evidence but does not prove the planar actor TargetFault boundary. Replacement: pure rule/property gap in a later batch.
The transient actor-level route and its initializer were removed after BUILD-196 showed Framework.Boss.TargetHealth failures. The earlier BUILD-196 CookCoverage exemptions for the removed files/assets are no longer needed.

### E116-E120: executor callback recovery and stale model paths
116. **E116 [D13]** Existing `FBossMoveModelGeneration` / `FBossExecutorLifecycleHarness` cover old-generation token rejection. Replacement: `FBossMoveModelStaleObservedAfterRestart` in `RPGBossMoveModelTests.cpp` executes stale observed-local callback refusal after a newer-generation attack has started.
117. **E117 [D13]** Existing `FBossExecutorLifecycleHarness` proves an aborted token is rejected after retry. Replacement: `FBossMoveModelStaleAbortAfterRestart` executes stale abort refusal after a newer-generation attack starts, with empty events and live current token.
118. **E118 [D13]** Existing `FBossExecutorLifecycleHarness` covers successful same-generation recovery once. Replacement: add an assertion that recovery before any abort is refused and leaves idle state unchanged.
119. **E119 [D13]** `FBossExecutorLifecycleHarness` asserts repeated recovery is refused after the abort marker was consumed and leaves idle/no-card state unchanged.
120. **E120 [D109]** Not reachable in transient automation: framework executor outcome counters require a real authored window contact through montage/sweep, and no hit-injection or counter-setter hook is allowed. Minimal follow-up: run a proof-map montage/contact and assert `AcceptedHits`, `GuardedHits`, and `ParriedHits` against resolver outcomes. Pure resolver outcomes are covered by `FRPGDamageDecideTest`, not executor counters.

### E121-E125: combo mutation properties
121. **E121 [D124-D131]** `RPGBossComboTests.cpp`, `FBossComboNodePermutationMutation`: reverse the validated DAG's node storage order and assert validity and root longest-path are unchanged; this avoids duplicating existing self/two-node cycle examples.
122. **E122 [D124-D131]** same file, `FBossComboEdgeMutationReachability`: remove the root's sole edge to the deep branch and assert `LongestPath` changes 3 -> 1 while the graph remains valid.
123. **E123 [D124-D131]** same file, `FBossComboPairedInvalidPrecedence`: pair an unknown edge target with a later NaN edge-domain field and assert the validator reports the earlier `Combo.UnknownNode` token.
124. **E124 [D124-D131]** `RPGBossMoveSelectorTests.cpp`, `FBossMoveSelectorExtremeFiniteScore`: use maximum legal weight and four pattern multipliers and assert selection and stored score remain finite.
125. **E125 [D124-D131]** same file, `FBossMoveSelectorZeroScoreOutsideTieTier`: keep a positive candidate and an eligible subnormal candidate whose score underflows to zero; assert the zero-score candidate is excluded from the positive top tie tier.

## E126-E165: decision-needed audits (40)

Each task records one unresolved decision, current evidence, authority, and bounded recommendation in a dedicated Documentation/Boss artifact. If no decision is missing, record none with references; do not invent policy.
126. **E126 [D91]** Audit whether the project needs a decision on integer extremes public contract; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E126_DECISION_AUDIT.md.
127. **E127 [D93]** Audit whether the project needs a decision on bleed saturation reachability; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E127_DECISION_AUDIT.md.
128. **E128 [D94]** Audit whether the project needs a decision on poise regen integration status; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E128_DECISION_AUDIT.md.
129. **E129 [D95]** Audit whether the project needs a decision on unknown phase policy; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E129_DECISION_AUDIT.md.
130. **E130 [D96]** Audit whether the project needs a decision on aggro band production eligibility; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E130_DECISION_AUDIT.md.
131. **E131 [D97]** Audit whether the project needs a decision on difficulty configuration ownership; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E131_DECISION_AUDIT.md.
132. **E132 [D98]** Audit whether the project needs a decision on enrage ramp reset ownership; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E132_DECISION_AUDIT.md.
133. **E133 [D99]** Audit whether the project needs a decision on fatigue inclusion in Gate 4; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E133_DECISION_AUDIT.md.
134. **E134 [D100]** Audit whether the project needs a decision on punish limiter design approval; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E134_DECISION_AUDIT.md.
135. **E135 [D101]** Audit whether the project needs a decision on reactive dodge attempt budget; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E135_DECISION_AUDIT.md.
136. **E136 [D102]** Audit whether the project needs a decision on retreat vertical gate need; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E136_DECISION_AUDIT.md.
137. **E137 [D103]** Audit whether the project needs a decision on gap closer live proof gate; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E137_DECISION_AUDIT.md.
138. **E138 [D104]** Audit whether the project needs a decision on cue jitter distribution requirement; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E138_DECISION_AUDIT.md.
139. **E139 [D105]** Audit whether the project needs a decision on zero-weight refusal token stability; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E139_DECISION_AUDIT.md.
140. **E140 [D106]** Audit whether the project needs a decision on tie-order compatibility promise; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E140_DECISION_AUDIT.md.
141. **E141 [D107]** Audit whether the project needs a decision on selector reset immutable config rule; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E141_DECISION_AUDIT.md.
142. **E142 [D108]** Audit whether the project needs a decision on window count observability; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E142_DECISION_AUDIT.md.
143. **E143 [D109]** Audit whether the project needs a decision on hit counter external contract; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E143_DECISION_AUDIT.md.
144. **E144 [D110]** Audit whether the project needs a decision on actor restart proof bar; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E144_DECISION_AUDIT.md.
145. **E145 [D13]** Audit whether the project needs a decision on transient-world harness sufficiency; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E145_DECISION_AUDIT.md.
146. **E146 [D3/D14]** Audit whether the project needs a decision on fresh snapshot route contract; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E146_DECISION_AUDIT.md.
147. **E147 [D6]** Audit whether the project needs a decision on selector memory lifetime; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E147_DECISION_AUDIT.md.
148. **E148 [D7]** Audit whether the project needs a decision on cross-platform seed guarantee; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E148_DECISION_AUDIT.md.
149. **E149 [D5]** Audit whether the project needs a decision on cooldown clock regression policy; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E149_DECISION_AUDIT.md.
150. **E150 [D4]** Audit whether the project needs a decision on fallback token compatibility; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E150_DECISION_AUDIT.md.
151. **E151 [D6/D15]** Audit whether the project needs a decision on repeat penalty decay rule; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E151_DECISION_AUDIT.md.
152. **E152 [D40]** Audit whether the project needs a decision on leash overflow designer policy; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E152_DECISION_AUDIT.md.
153. **E153 [D91]** Audit whether the project needs a decision on flask threshold rounding contract; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E153_DECISION_AUDIT.md.
154. **E154 [D43]** Audit whether the project needs a decision on yaw probe profile authorship; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E154_DECISION_AUDIT.md.
155. **E155 [D36/D37]** Audit whether the project needs a decision on strafe interruption reset policy; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E155_DECISION_AUDIT.md.
156. **E156 [D48/E187]** Audit whether the project needs a decision on ring-front sector authorship; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E156_DECISION_AUDIT.md.
157. **E157 [D91]** Audit whether the project needs a decision on grounded height missing sample; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E157_DECISION_AUDIT.md.
158. **E158 [D96]** Audit whether the project needs a decision on aggro hysteresis ownership; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E158_DECISION_AUDIT.md.
159. **E159 [D97]** Audit whether the project needs a decision on difficulty endpoint customization; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E159_DECISION_AUDIT.md.
160. **E160 [D45]** Audit whether the project needs a decision on invalid elapsed handling; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E160_DECISION_AUDIT.md.
161. **E161 [D102]** Audit whether the project needs a decision on retreat equality semantics; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E161_DECISION_AUDIT.md.
162. **E162 [D102]** Audit whether the project needs a decision on threat equality semantics; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E162_DECISION_AUDIT.md.
163. **E163 [D92]** Audit whether the project needs a decision on damage scaler nonfinite policy; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E163_DECISION_AUDIT.md.
164. **E164 [D124-D125]** Audit whether the project needs a decision on combo unreachable node policy; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E164_DECISION_AUDIT.md.
165. **E165 [D126-D131]** Audit whether the project needs a decision on stable refusal and cleanup contract; acceptance: cite the audit and current implementation, identify the decision owner, and record decision-needed or none in Documentation/Boss/E165_DECISION_AUDIT.md.

## E166-E200: owner-scoped opt-in protocols (35)

Protocol only. Every artifact requires owner scope before implementation and specifies default-off behavior, invariants, paired evidence, and rollback. No task changes behavior, assets, or defaults.
166. **E166** Owner-scoped protocol for optional per-profile difficulty curve; acceptance: `Documentation/Boss/E166_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
167. **E167** Owner-scoped protocol for optional fatigue profile; acceptance: `Documentation/Boss/E167_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
168. **E168** Owner-scoped protocol for optional punish limiter profile; acceptance: `Documentation/Boss/E168_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
169. **E169** Owner-scoped protocol for optional reactive dodge attempt budget; acceptance: `Documentation/Boss/E169_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
170. **E170** Owner-scoped protocol for optional retreat vertical gate; acceptance: `Documentation/Boss/E170_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
171. **E171** Owner-scoped protocol for optional gap-closer persistence tuning; acceptance: `Documentation/Boss/E171_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
172. **E172** Owner-scoped protocol for optional cue jitter profile; acceptance: `Documentation/Boss/E172_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
173. **E173** Owner-scoped protocol for optional selector repeat penalty; acceptance: `Documentation/Boss/E173_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
174. **E174** Owner-scoped protocol for optional selector tie policy; acceptance: `Documentation/Boss/E174_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
175. **E175** Owner-scoped protocol for optional combo graph editor validation; acceptance: `Documentation/Boss/E175_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
176. **E176** Owner-scoped protocol for optional combo reachability visualization; acceptance: `Documentation/Boss/E176_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
177. **E177** Owner-scoped protocol for optional executor window telemetry; acceptance: `Documentation/Boss/E177_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
178. **E178** Owner-scoped protocol for optional encounter restart diagnostics; acceptance: `Documentation/Boss/E178_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
179. **E179** Owner-scoped protocol for optional poise regeneration prototype; acceptance: `Documentation/Boss/E179_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
180. **E180** Owner-scoped protocol for optional stagger resistance profile; acceptance: `Documentation/Boss/E180_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
181. **E181** Owner-scoped protocol for optional aggro band profile; acceptance: `Documentation/Boss/E181_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
182. **E182** Owner-scoped protocol for optional enrage ramp profile; acceptance: `Documentation/Boss/E182_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
183. **E183** Owner-scoped protocol for optional leash visualization; acceptance: `Documentation/Boss/E183_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
184. **E184** Owner-scoped protocol for optional flask threshold profile; acceptance: `Documentation/Boss/E184_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
185. **E185** Owner-scoped protocol for optional yaw probe tuning; acceptance: `Documentation/Boss/E185_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
186. **E186** Owner-scoped protocol for optional strafe interruption policy; acceptance: `Documentation/Boss/E186_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
187. **E187** Owner-scoped protocol for optional ring-front sector profile; acceptance: `Documentation/Boss/E187_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
188. **E188** Owner-scoped protocol for optional grounded-height tolerance; acceptance: `Documentation/Boss/E188_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
189. **E189** Owner-scoped protocol for optional combo fallback telemetry; acceptance: `Documentation/Boss/E189_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
190. **E190** Owner-scoped protocol for optional snapshot freshness trace; acceptance: `Documentation/Boss/E190_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
191. **E191** Owner-scoped protocol for optional cooldown clock diagnostic; acceptance: `Documentation/Boss/E191_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
192. **E192** Owner-scoped protocol for optional selector score saturation; acceptance: `Documentation/Boss/E192_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
193. **E193** Owner-scoped protocol for optional bleed counter telemetry; acceptance: `Documentation/Boss/E193_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
194. **E194** Owner-scoped protocol for optional damage scaler diagnostics; acceptance: `Documentation/Boss/E194_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
195. **E195** Owner-scoped protocol for optional D13 harness extension; acceptance: `Documentation/Boss/E195_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
196. **E196** Owner-scoped protocol for optional terminal transition trace; acceptance: `Documentation/Boss/E196_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
197. **E197** Owner-scoped protocol for optional window cleanup visualization; acceptance: `Documentation/Boss/E197_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
198. **E198** Owner-scoped protocol for optional combo cycle policy; acceptance: `Documentation/Boss/E198_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
199. **E199** Owner-scoped protocol for optional boundary table fixture generator; acceptance: `Documentation/Boss/E199_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
200. **E200** Owner-scoped protocol for optional offline audit report index; acceptance: `Documentation/Boss/E200_OPT_IN_PROTOCOL.md` defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
201. **E201** Owner-scoped protocol for optional bridge timeout dashboard; acceptance: artifact defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
202. **E202** Owner-scoped protocol for optional evidence-copy integrity summary; acceptance: artifact defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
203. **E203** Owner-scoped protocol for optional test ID alias report; acceptance: artifact defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
204. **E204** Owner-scoped protocol for optional editor dry-run inventory view; acceptance: artifact defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.
205. **E205** Owner-scoped protocol for optional packaged diagnostics follow-up; acceptance: artifact defines owner decision, disabled default, gameplay invariants, paired proof, and rollback without implementing or changing the feature.

Counts: 125 tests (E1-E125), 40 decision audits (E126-E165), 35 opt-in protocols (E166-E200): 200 core tasks. E201-E205 are supplemental backlog items outside that 200-task count.
