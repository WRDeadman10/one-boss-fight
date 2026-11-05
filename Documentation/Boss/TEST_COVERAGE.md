# Pure-rule test coverage index (R56–R60)

Static source index of rule headers and test files that directly include them. The assertion number is the count of `TestTrue`, `TestFalse`, `TestEqual`, `TestNotEqual`, `TestNearlyEqual`, `TestNull`, and `TestNotNull` calls in the entire listed `.cpp` file, not a per-header attribution when that file covers multiple rules. It is a source count, not a test run or a coverage percentage. The scan covered 56 headers in scope (all 53 `*Rules.h` files plus `RPGBossMath.h`, `RPGDamageScale.h`, and `RPGBossTurnRateRamp.h`) and 94 test source files.

| Rule header | Directly including test source(s) | Assertions in each listed test source* |
|---|---|---:|
| `Source/OneBossFight/Player/RPGBleedRules.h` | `RPGAutomationTests.cpp`; `RPGBleedRulesPropertyTests.cpp`; `RPGCodexTests.cpp` | 339; 5; 93 |
| `Source/OneBossFight/Player/RPGBossAggroRules.h` | `RPGBossAggroRulesTests.cpp` | 12 |
| `Source/OneBossFight/Player/RPGBossAimHysteresisRules.h` | `RPGBossAimHysteresisTests.cpp`; `RPGBossYawProbeTests.cpp` | 21; 8 |
| `Source/OneBossFight/Player/RPGBossApproachRules.h` | `RPGBossApproachTests.cpp` | 17 |
| `Source/OneBossFight/Player/RPGBossArenaEdgeRules.h` | `RPGBossArenaEdgeRulesTests.cpp` | 8 |
| `Source/OneBossFight/Player/RPGBossBakeFreshnessRules.h` | `RPGBossBakeFreshnessRulesTests.cpp` | 4 |
| `Source/OneBossFight/Player/RPGBossBlockChipRules.h` | `RPGBossBlockChipRulesTests.cpp` | 7 |
| `Source/OneBossFight/Player/RPGBossCloseClipSwapRules.h` | `RPGBossCloseClipSwapTests.cpp` | 2 |
| `Source/OneBossFight/Player/RPGBossComboAbortRules.h` | `RPGBossComboAbortRulesTests.cpp` | 5 |
| `Source/OneBossFight/Player/RPGBossComboRules.h` | `RPGBossComboParriedSampleTests.cpp`; `RPGBossComboPropertyTests.cpp`; `RPGBossComboTests.cpp` | 4; 5; 52 |
| `Source/OneBossFight/Player/RPGBossCueJitterRules.h` | `RPGBossCueJitterRulesTests.cpp` | 3 |
| `Source/OneBossFight/Player/RPGBossCueRules.h` | `RPGBossCueSweepTests.cpp`; `RPGBossCueTests.cpp` | 5; 17 |
| `Source/OneBossFight/Player/RPGBossDefenseRules.h` | `RPGBossDefenseSweepTests.cpp`; `RPGBossDefenseTests.cpp` | 11; 13 |
| `Source/OneBossFight/Player/RPGBossDesperationRules.h` | `RPGBossDesperationRulesTests.cpp` | 8 |
| `Source/OneBossFight/Player/RPGBossDifficultyRules.h` | `RPGBossDifficultyRulesTests.cpp` | 8 |
| `Source/OneBossFight/Player/RPGBossDormantWakeRules.h` | `RPGBossDormantWakeTests.cpp` | 11 |
| `Source/OneBossFight/Player/RPGBossEnrageRules.h` | `RPGBossEnrageRulesTests.cpp` | 9 |
| `Source/OneBossFight/Player/RPGBossFatigueRules.h` | `RPGBossFatigueRulesTests.cpp` | 5 |
| `Source/OneBossFight/Player/RPGBossFeintRules.h` | `RPGBossFeintRulesTests.cpp` | 6 |
| `Source/OneBossFight/Player/RPGBossGapCloserRules.h` | `RPGBossGapCloserRulesTests.cpp` | 6 |
| `Source/OneBossFight/Player/RPGBossGuardRules.h` | `RPGBossGuardTests.cpp` | 10 |
| `Source/OneBossFight/Player/RPGBossHitStopRules.h` | `RPGBossHitStopRulesTests.cpp` | 7 |
| `Source/OneBossFight/Player/RPGBossMath.h` | `RPGAutomationTests.cpp`; `RPGCodexTests.cpp` | 339; 93 |
| `Source/OneBossFight/Player/RPGBossMusicIntensityRules.h` | `RPGBossMusicIntensityRulesTests.cpp` | 7 |
| `Source/OneBossFight/Player/RPGBossOverlayRules.h` | `RPGFrameworkRuntimeTests.cpp` | 340 |
| `Source/OneBossFight/Player/RPGBossParryFairRules.h` | `RPGBossParryFairTests.cpp` | 12 |
| `Source/OneBossFight/Player/RPGBossParryFeedbackRules.h` | `RPGBossParryFeedbackRulesTests.cpp` | 3 |
| `Source/OneBossFight/Player/RPGBossPatternDetectRules.h` | `RPGBossPatternDetectRulesTests.cpp` | 11 |
| `Source/OneBossFight/Player/RPGBossPoiseRegenRules.h` | `RPGBossPoiseRegenRulesTests.cpp` | 6 |
| `Source/OneBossFight/Player/RPGBossPresentationRules.h` | `RPGBossPresentationRulesTests.cpp` | 7 |
| `Source/OneBossFight/Player/RPGBossPunishLimiterRules.h` | `RPGBossPunishLimiterRulesTests.cpp` | 9 |
| `Source/OneBossFight/Player/RPGBossPunishRules.h` | `RPGBossPunishSweepTests.cpp` | 2 |
| `Source/OneBossFight/Player/RPGBossReactiveDodgeRules.h` | `RPGBossReactiveDodgeRulesTests.cpp` | 11 |
| `Source/OneBossFight/Player/RPGBossRecoveryWindowRules.h` | `RPGBossParryRecoveryWiringTests.cpp`; `RPGBossRecoveryWindowRulesTests.cpp` | 5; 9 |
| `Source/OneBossFight/Player/RPGBossRepeatPenaltyRules.h` | `RPGBossRepeatPenaltyRulesTests.cpp` | 5 |
| `Source/OneBossFight/Player/RPGBossRetreatRules.h` | `RPGBossRetreatRulesTests.cpp` | 6 |
| `Source/OneBossFight/Player/RPGBossRules.h` | `RPGAutomationTests.cpp`; `RPGCodexTests.cpp`; `RPGFrameworkRuntimeTests.cpp` | 339; 93; 340 |
| `Source/OneBossFight/Player/RPGBossStaggerAnimRules.h` | `RPGFrameworkRuntimeTests.cpp` | 340 |
| `Source/OneBossFight/Player/RPGBossStaggerResistRules.h` | `RPGBossStaggerResistRulesTests.cpp` | 5 |
| `Source/OneBossFight/Player/RPGBossStaminaPressureRules.h` | `RPGBossStaminaPressureRulesTests.cpp` | 7 |
| `Source/OneBossFight/Player/RPGBossStrafeResumeRules.h` | `RPGBossStrafeResumeRulesTests.cpp` | 5 |
| `Source/OneBossFight/Player/RPGBossStrafeRules.h` | `RPGBossStrafeTests.cpp` | 12 |
| `Source/OneBossFight/Player/RPGBossStuckRecoveryRules.h` | `RPGBossStuckRecoveryRulesTests.cpp` | 6 |
| `Source/OneBossFight/Player/RPGBossStuckRules.h` | `RPGBossStuckTests.cpp` | 13 |
| `Source/OneBossFight/Player/RPGBossTelegraphScaleRules.h` | `RPGBossTelegraphScaleRulesTests.cpp` | 12 |
| `Source/OneBossFight/Player/RPGBossTrackRules.h` | `RPGBossAbortTests.cpp`; `RPGBossTrackRulesSweepTests.cpp`; `RPGFrameworkRuntimeTests.cpp` | 4; 4; 340 |
| `Source/OneBossFight/Player/RPGBossTurnRateRamp.h` | `RPGBossTurnRateRampTests.cpp` | 6 |
| `Source/OneBossFight/Player/RPGBossWarpCurveRules.h` | `RPGBossWarpCurveRulesTests.cpp` | 8 |
| `Source/OneBossFight/Player/RPGBossYawProbeRules.h` | `RPGBossYawProbeTests.cpp` | 8 |
| `Source/OneBossFight/Player/RPGBuildRules.h` | `RPGBuildTests.cpp`; `RPGCodexTests.cpp`; `RPGCombatCatalogTests.cpp` | 87; 93; 141 |
| `Source/OneBossFight/Player/RPGDamageScale.h` | `RPGBuildTests.cpp`; `RPGCodexTests.cpp` | 87; 93 |
| `Source/OneBossFight/Player/RPGParryCostRules.h` | `RPGParryCostTests.cpp` | 18 |
| `Source/OneBossFight/Player/RPGParryGradeRules.h` | `RPGParryGradeTests.cpp` | 17 |
| `Source/OneBossFight/Player/RPGParryRules.h` | `RPGParryTests.cpp` | 27 |
| `Source/OneBossFight/Player/RPGSwingRules.h` | `RPGAutomationTests.cpp`; `RPGCodexTests.cpp` | 339; 93 |
| `Source/OneBossFight/Player/RPGTelegraphRules.h` | `RPGCodexTests.cpp` | 93 |

*Counts are file-wide and therefore repeat when one source directly includes multiple headers. Indirect includes are not attributed. These numbers do not measure branch coverage or prove assertions execute.
