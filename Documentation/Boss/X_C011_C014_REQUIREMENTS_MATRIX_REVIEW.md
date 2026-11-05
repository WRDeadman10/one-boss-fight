# Queue X X-C011-X-C014 — requirements matrix registration review

Date: 2026-11-06. Static source/validator review only; no Antigravity-owned file changed and no Unreal/build/native automation was run.

## X-C011 / X-C013 — exact test-name registration cross-check

The V-A054 report describes each `PrimaryAutomationTest` as the authoritative native automation test. I scanned `Source/OneBossFight/Tests/**/*.cpp` for literal second arguments to `IMPLEMENT_*AUTOMATION_TEST`, including `TEXT("...")` forms (478 unique registered path literals). Compared all 82 CSV rows by exact test-path string and declared `SourceFile`.

Result: **5/82 exact path-and-file matches; 77/82 CSV `PrimaryAutomationTest` strings do not appear as registered paths anywhere in the scanned C++ test sources; 0 rows point to a different source file for an otherwise exact path.** This identifies stale/unsupported automation identifiers in the matrix, not proof that the underlying requirement has no conceptual test coverage. The required evidence is the registration literal, and the reported names cannot currently identify those tests. The test inventory itself reports 478 registrations, corroborating the scan's scope.

| Requirement | Matrix `PrimaryAutomationTest` | Declared source file | Static result |
|---|---|---|---|
| BOSS-AWR-001 | `OneBossFight.Binding.Activation.InjectedFaults` | `Source/OneBossFight/Tests/RPGBossActivationTests.cpp` | Exact registration in stated file |
| BOSS-AWR-002 | `OneBossFight.Binding.Activation.Success` | `Source/OneBossFight/Tests/RPGBossActivationTests.cpp` | Exact registration in stated file |
| BOSS-AWR-003 | `OneBossFight.Binding.MoveModel.CandidateDistance` | `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-AWR-004 | `OneBossFight.Binding.MoveModel.AimHysteresis` | `Source/OneBossFight/Tests/RPGBossAimHysteresisTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-AWR-005 | `OneBossFight.Binding.MoveModel.VerticalSeparation` | `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-AWR-006 | `OneBossFight.Binding.AggroRules.PlayerActivity` | `Source/OneBossFight/Tests/RPGBossAggroRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-AWR-007 | `OneBossFight.Binding.LosLeash.OcclusionSearch` | `Source/OneBossFight/Tests/RPGBossLosLeashDeadlineTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-AWR-008 | `OneBossFight.Binding.PatternDetect.SoftAdaptation` | `Source/OneBossFight/Tests/RPGBossPatternDetectRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-001 | `OneBossFight.Binding.MoveModel.DecisionGates` | `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-002 | `OneBossFight.Binding.MoveModel.HardFilterPrecedence` | `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-003 | `OneBossFight.Binding.MoveCard.MissingAssetRejection` | `Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-004 | `OneBossFight.Binding.MoveSelector.UtilityScoring` | `Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-005 | `OneBossFight.Binding.MoveSelector.BoundedRandomness` | `Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-006 | `OneBossFight.Binding.MoveSelector.CooldownSemantics` | `Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-007 | `OneBossFight.Binding.RepeatPenalty.AntiLoop` | `Source/OneBossFight/Tests/RPGBossRepeatPenaltyRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-008 | `OneBossFight.Binding.MoveSelector.NoCandidateFallback` | `Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-009 | `OneBossFight.Framework.Runtime.ReactionLatency` | `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-SEL-010 | `OneBossFight.Framework.Runtime.DecisionTraceAudit` | `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-EXE-001 | `OneBossFight.Binding.MoveModel.PriorityHierarchy` | `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-EXE-002 | `OneBossFight.Binding.MoveModel.InstanceBeforeMontage` | `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-EXE-003 | `OneBossFight.Binding.MoveModel.StartRollback` | `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-EXE-004 | `OneBossFight.Binding.MoveModel.StaleEventRejection` | `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-EXE-005 | `OneBossFight.Framework.Executor.PriorityResolution` | `Source/OneBossFight/Tests/RPGBossExecutorHarnessTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-EXE-006 | `OneBossFight.Boss.Abort.IdempotentCleanup` | `Source/OneBossFight/Tests/RPGBossAbortTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-EXE-007 | `OneBossFight.Framework.Runtime.ExecutorWatchdogRule` | `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp` | Exact registration in stated file |
| BOSS-EXE-008 | `OneBossFight.Framework.Executor.StatefulLifecycleHarness` | `Source/OneBossFight/Tests/RPGBossExecutorHarnessTests.cpp` | Exact registration in stated file |
| BOSS-COM-001 | `OneBossFight.Binding.Combo.AuthoredGraph` | `Source/OneBossFight/Tests/RPGBossComboTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-COM-002 | `OneBossFight.Binding.Combo.GateAfterDamage` | `Source/OneBossFight/Tests/RPGBossComboTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-COM-003 | `OneBossFight.Binding.Combo.FreshBranchContext` | `Source/OneBossFight/Tests/RPGBossComboTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-COM-004 | `OneBossFight.Binding.Combo.HitConfirmPolicy` | `Source/OneBossFight/Tests/RPGBossComboPropertyTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-COM-005 | `OneBossFight.Binding.Combo.SingleUseGate` | `Source/OneBossFight/Tests/RPGBossComboTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-COM-006 | `OneBossFight.Boss.ComboAbort.FinitePressure` | `Source/OneBossFight/Tests/RPGBossComboAbortRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-COM-007 | `OneBossFight.Binding.ComboFallback.DefaultRecovery` | `Source/OneBossFight/Tests/RPGBossComboFallbackTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-ANM-001 | `OneBossFight.Binding.MoveCard.MontageTimelineAuthority` | `Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-ANM-002 | `OneBossFight.Boss.TelegraphScale.Phases` | `Source/OneBossFight/Tests/RPGBossTelegraphScaleRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-ANM-003 | `OneBossFight.Binding.MoveCardHold.BoundedHolds` | `Source/OneBossFight/Tests/RPGBossMoveCardHoldEndBoundaryTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-ANM-004 | `OneBossFight.Binding.TurnRateRamp.StagedRotationCap` | `Source/OneBossFight/Tests/RPGBossTurnRateRampTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-ANM-005 | `OneBossFight.Binding.CloseClipSwap.ExclusiveMotionAuthority` | `Source/OneBossFight/Tests/RPGBossCloseClipSwapTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-ANM-006 | `OneBossFight.Boss.WarpCurve.BoundedMotionWarping` | `Source/OneBossFight/Tests/RPGBossWarpCurveRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-ANM-007 | `OneBossFight.Binding.MoveCard.NotifyEndIndependence` | `Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-ANM-008 | `OneBossFight.Binding.MoveCard.HandoffTransitions` | `Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-001 | `OneBossFight.Binding.BakedSample.GeometryFidelity` | `Source/OneBossFight/Tests/RPGBossBakeFreshnessRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-002 | `OneBossFight.Binding.BakedSample.SweptTemporalSampling` | `Source/OneBossFight/Tests/RPGBossBakedSampleEndpointMutationTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-003 | `OneBossFight.Binding.BakedSample.BladeInteriorSamples` | `Source/OneBossFight/Tests/RPGBossBakedSampleLastEndpointBoundaryTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-004 | `OneBossFight.Binding.BakedSample.AdaptiveSubsteps` | `Source/OneBossFight/Tests/RPGBossBakeFreshnessRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-005 | `OneBossFight.Binding.DamageScaler.QueryFiltering` | `Source/OneBossFight/Tests/RPGDamageScalerLowerWindowBoundaryTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-006 | `OneBossFight.Framework.Runtime.LogicalVictimDedupe` | `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-007 | `OneBossFight.Binding.DamageScaler.ExplicitHitPolicy` | `Source/OneBossFight/Tests/RPGDamageScalerWindowBoundaryMutationTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-008 | `OneBossFight.Framework.Parry.CentralDefenseOrder` | `Source/OneBossFight/Tests/RPGParryTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-009 | `OneBossFight.Framework.Parry.IframeCompleteness` | `Source/OneBossFight/Tests/RPGParryTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-010 | `OneBossFight.Binding.BlockChip.DirectSplashPrecedence` | `Source/OneBossFight/Tests/RPGBossBlockChipRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-011 | `OneBossFight.Binding.Shockwave.SweptAnnulus` | `Source/OneBossFight/Tests/RPGBossShockwaveAdaptersTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-HIT-012 | `OneBossFight.Binding.HitStop.GrabFailSafe` | `Source/OneBossFight/Tests/RPGBossHitStopRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-MOV-001 | `OneBossFight.Binding.Approach.RangeBandPolicy` | `Source/OneBossFight/Tests/RPGBossApproachTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-MOV-002 | `OneBossFight.Binding.Strafe.CombatPositioning` | `Source/OneBossFight/Tests/RPGBossStrafeTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-MOV-003 | `OneBossFight.Binding.StrafeResume.MovementCommitment` | `Source/OneBossFight/Tests/RPGBossStrafeResumeRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-MOV-004 | `OneBossFight.Binding.ArenaEdge.WallSafeAttacks` | `Source/OneBossFight/Tests/RPGBossArenaEdgeRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-MOV-005 | `OneBossFight.Binding.ArenaLeash.ArenaValidResponses` | `Source/OneBossFight/Tests/RPGBossArenaLeashBoundaryTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-MOV-006 | `OneBossFight.Binding.Retreat.ArenaAttackFit` | `Source/OneBossFight/Tests/RPGBossRetreatRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PAC-001 | `OneBossFight.Binding.MoveCard.ExplicitAttackSegments` | `Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PAC-002 | `OneBossFight.Boss.Fatigue.PressureVariation` | `Source/OneBossFight/Tests/RPGBossFatigueRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PAC-003 | `OneBossFight.Binding.RecoveryWindow.GuaranteedOpenings` | `Source/OneBossFight/Tests/RPGBossRecoveryWindowRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PAC-004 | `OneBossFight.Binding.Cue.ConditionalOpeningCues` | `Source/OneBossFight/Tests/RPGBossCueTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PAC-005 | `OneBossFight.Binding.PunishLimiter.PunishMarginCalculation` | `Source/OneBossFight/Tests/RPGBossPunishLimiterRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PAC-006 | `OneBossFight.Binding.Punish.NeutralPurposeful` | `Source/OneBossFight/Tests/RPGBossPunishTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-DEF-001 | `OneBossFight.Binding.DamageBleed.SeparateMeters` | `Source/OneBossFight/Tests/RPGBossDamageBleedFiniteInputTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-DEF-002 | `OneBossFight.Boss.PoiseRegen.PostureRegeneration` | `Source/OneBossFight/Tests/RPGBossPoiseRegenRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-DEF-003 | `OneBossFight.Binding.StaggerPolicy.SingleStanceBreak` | `Source/OneBossFight/Tests/RPGBossStaggerPolicyAdaptersTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-DEF-004 | `OneBossFight.Boss.StaggerResist.WindowedHyperarmor` | `Source/OneBossFight/Tests/RPGBossStaggerResistRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-DEF-005 | `OneBossFight.Binding.Defense.FairBossDefense` | `Source/OneBossFight/Tests/RPGBossDefenseTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PHS-001 | `OneBossFight.Binding.PhaseFlow.ThresholdTransition` | `Source/OneBossFight/Tests/RPGBossPhaseFlowAdaptersTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PHS-002 | `OneBossFight.Binding.Phase.SafeTransitionPolicy` | `Source/OneBossFight/Tests/RPGBossPhaseAdaptersTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PHS-003 | `OneBossFight.Binding.PhasesCluster.Monotonicity` | `Source/OneBossFight/Tests/RPGBossPhasesClusterAdaptersTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PHS-004 | `OneBossFight.Binding.HealPunish.FairReaction` | `Source/OneBossFight/Tests/RPGBossHealPunishAdaptersTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-PHS-005 | `OneBossFight.Binding.GapCloser.AntiCheeseCounterplay` | `Source/OneBossFight/Tests/RPGBossGapCloserRulesTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-QA-001 | `OneBossFight.Framework.Runtime.DebugOverlayRegistration` | `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-QA-002 | `OneBossFight.Framework.Runtime.StructuredEventLog` | `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-QA-003 | `OneBossFight.Binding.EncounterRestart.ReproducibleScenarios` | `Source/OneBossFight/Tests/RPGBossEncounterRestartMatrixTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-QA-004 | `OneBossFight.Binding.CombatCatalog.TimeScaleParity` | `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-QA-005 | `OneBossFight.Benchmark.FrameStats.Gate` | `Source/OneBossFight/Tests/RPGAutomationTests.cpp` | Exact registration in stated file |
| BOSS-QA-006 | `OneBossFight.Binding.YawProbe.CameraReadability` | `Source/OneBossFight/Tests/RPGBossYawProbeTests.cpp` | Not found in stated file or any scanned test source |
| BOSS-QA-007 | `OneBossFight.Art.Tier1Visual.AccessibleFeedback` | `Source/OneBossFight/Tests/RPGTier1VisualRulesTests.cpp` | Not found in stated file or any scanned test source |

## X-C012 — validator false-pass paths

`Scripts/Tools/test_requirements_coverage_matrix.py` has four tests and validates file/ledger existence, 82-row count and ID-set equality, nonempty fields, source-file existence, and allowed enum membership. Its row loop does not compare `PrimaryAutomationTest` to a registration in `SourceFile`.

| Mutation to a valid row | Current validator behavior by source inspection | Consequence |
|---|---|---|
| Replace `PrimaryAutomationTest` with a made-up nonempty string | No registration lookup; accepted | Test-name mismatch false pass |
| Point `SourceFile` to another existing C++ file | Existence only; accepted | Wrong suite/source association false pass |
| Change a `Covered` row to `GateEnforced` | Enum membership only; accepted | Status semantics are not checked |
| Change `NativeUnit` to `AutomationGate` | Enum membership only; accepted | Coverage/status compatibility is not checked |
| Empty any required field | Explicit nonempty assertion fails | Guard is present |
| Change requirement ID set or row count | Count/set assertions fail | Guard is present |

This is a bounded static mutation matrix, not an executed mutation test. The validator's own offline test was run separately: **4/4 passed**; that pass only establishes its implemented assertions.

## X-C014 — category/status semantics

The current CSV contains 73 `NativeUnit/Covered`, 8 `NativeIntegration/Covered`, and 1 `AutomationGate/GateEnforced` rows. These pairs are internally plausible, with no empty or out-of-enum category/status values. However, the script does not validate their meaning, evidence quality, or compatibility. V-A054's 82/82 statement is therefore structurally supported as a complete requirement-ID inventory, while the stronger exact registered-test mapping is not supported by current source.

## Disposition

Prior C094 / V-A081 accepted the missing registration check as a verification refinement and scheduled it in Queue W; this review now finds the actual CSV identifiers fail that exact check at 77 rows. Preserve the matrix unchanged for its owner; Antigravity/Claude should reconcile identifiers or explicitly scope the field as suite-level mapping, then add registration-aware validation. No AG-owned files were edited.
