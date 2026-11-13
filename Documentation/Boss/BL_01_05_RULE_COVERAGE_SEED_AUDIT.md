# BL-01..05: deterministic combat-rule coverage seed audit (source-only)

Assigned by X-2157 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 1 of 20. The output is this report only.

**Not done:** no production source or test edits, and no Unreal, build, PIE, commit or push. X-1991 and the runtime gates are untouched.

## Method

- **Inventory:** 3 read-only reviewers each read one third of the **64** `Source/OneBossFight/Player/*Rules.h` headers (a workflow fan-out, 3 agents, inside the 3-agent cap). Each also read the native automation tests under `Source/OneBossFight/Tests/` that use its header (154 of 156 test files define automation tests).
- **For each header they reported:** whether it is deterministic and owner-independent, its public functions, its test files, the exact boundaries asserted (with file:line), the **confirmed untested** behaviors (header line + the test files searched), and hypotheses.
- **My own verification:** I re-read the source and tests by hand for every gap used in the BL-06..09 proposals (Bleed, Approach, HitStop, StaggerAnim) and confirmed them. The remaining rows in the appendix are **reviewer-confirmed but not yet re-checked by me**. Each will be re-verified when it is implemented.

## BL-01: inventory

- Headers: **64**. Deterministic and owner-independent: **63**. The exception is `RPGTier1VisualRules.h`, which depends on visual and product data.
- **Every header has at least one native test file.** There are 137 header-to-test-file links in total.
- Headers whose exact boundary and error coverage the reviewers found complete (no confirmed gaps): `RPGAirAttackRules.h`, `RPGBossCloseClipSwapRules.h`, `RPGBossDormantWakeRules.h`, `RPGBossParryFeedbackRules.h`, `RPGBossStaggerResistRules.h`, `RPGBossStrafeResumeRules.h`, `RPGBuildRules.h`, `RPGDodgeActivationRules.h`, `RPGDodgeInputRules.h`, `RPGEncounterGenerationRules.h`, `RPGGuardCounterRules.h`, `RPGParryRules.h`, `RPGPresentationRules.h`.

## BL-02 / BL-03: coverage map and confirmed untested behaviors

- **Reported:** 97 untested behaviors across 51 headers. **95 need no product decision**: they assert existing, documented fail-closed or clamp behavior. The other 2 would mean choosing a design value; they are marked `[decision]` in the appendix and excluded.
- **Owner-independent backlog:** **94 behaviors across 49 headers**. This excludes the 2 `[decision]` items and `RPGTier1VisualRules.h`'s world/asset item. `RPGBossAimHysteresisRules.h` has only a decision item, so it drops out; `RPGParryCostRules.h` keeps 1 ordinary gap. The 49 headers are the 5 in BL-06..10 plus the 44 active headers in BL-11..85. Correction per X-2158/X-2160 and A-878.
- **BL-10 hand verification** (correction): the remaining Aggro `IsValid` clauses, promoted from hypothesis, are counted separately and are not part of the reviewer-sourced 94.
- **What the gaps are:** almost all are **unasserted guard clauses**: negative or zero finite inputs next to an already-tested NaN or inf, individual `IsValid` clauses, exact returned values where only ordering is tested, and `Name()`/`ToString` fallbacks.
- **What they are not:** no reviewer found a header without tests, and no behavioral defect was reported. These are coverage gaps, not bugs.
- **Hypotheses** (suspected, unconfirmed) are listed separately in the appendix and are not counted above.

## BL-04: five test-first tasks

All five are **new test files only**, asserting existing behavior. Each test is expected to pass on first build. If a new assertion fails, the source **and** the test are reviewed first: the failure may expose a test-spec error rather than a product defect (wording per X-2163). **Acceptance:** one lead acceptance build plus an automation run of the named test (engine-lock rules apply), and no production source change.

| Task | Header (gap lines) | New test file / automation name | Cases (all currently unasserted) |
|---|---|---|---|
| **BL-06** | `RPGBleedRules.h` `:50-56`, `:78-81`, `:36-44` | `Tests/RPGBleedGuardTests.cpp`, `OneBossFight.Framework.Bleed.Guards` | `Apply` returns `IgnoredAmount` with state unchanged for: a negative finite Amount; `InitialThreshold<=0`; `ThresholdIncrease<0`; `ThresholdMax<InitialThreshold`; `HpFraction<0` or non-finite; `Buildup<0` or NaN; `Threshold<=0`; `Procs<0`. `ProcDamage` returns 0 for `MaxHealth<=0`, `Health<=0`, non-finite inputs, `HpFraction<0`. `Name()` returns the exact string for all 7 results. |
| **BL-07** | `RPGBossApproachRules.h` `:11`, `:20`, `:31` | `Tests/RPGBossApproachGuardTests.cpp`, `OneBossFight.Framework.BossApproach.Guards` | `StepFraction(NaN)==0`; `StepCm` with `T1>1` or `TotalCm<0` gives 0; `PeakSpeedCm` with a negative distance or a negative duration gives 0 |
| **BL-08** | `RPGBossHitStopRules.h` `:12-13`, `:20-22` | `Tests/RPGBossHitStopGuardTests.cpp`, `OneBossFight.Framework.HitStop.Guards` | exact default values (.12/.08/.04); each non-finite field is invalid; `Late<0`, `Max<0`, `Late>Good` are invalid; the equality boundaries (`Perfect==Max`, all grades equal) are valid; an invalid config gives 0 for every grade |
| **BL-09** | `RPGBossStaggerAnimRules.h` `:33`, `:43-47` | `Tests/RPGBossStaggerAnimGuardTests.cpp`, `OneBossFight.Framework.Runtime.StaggerAnimGuards` | `Evaluate` returns `Finished` for a negative `StartLen` or `EndLen`, `Total<=0`, or `Start+End>Total`; a negative `Dt` returns `Start` (current documented branch order); `Validate` with a zero `StartLen` or `EndLen` returns `TooShort` |
| **BL-10** | `RPGBossAggroRules.h` `:16-19` (`IsValid`), `:23` | `Tests/RPGBossAggroGuardTests.cpp`, `OneBossFight.Framework.Aggro.Guards` | **Hand-verified (correction):** across all Aggro test files, the **only** invalid configs asserted are `EnterCloseCm=-1` (`RPGBossQueueEBoundaryTests.cpp:198,202`) and `ExitCloseCm==EnterCloseCm` (`RPGBossQueueEPolicyBoundaryTests.cpp:11-12`). Both are **removed** from this task. **Unasserted, so in scope:** a negative finite `DodgeRatePerSecond` preserves the band (`:23`); a non-finite config field; `ExitFarCm<=ExitCloseCm`; `EnterFarCm<=ExitFarCm`; `ExitDodgeRate<0`; `EnterDodgeRate<=ExitDodgeRate`; `DodgeRateWindowSeconds<=0`. **Every** invalid config and input case preserves the current band, and this is checked from each starting band (Balanced, Close, Far) with a range that would otherwise move it. **Every** `FConfig` field (`EnterCloseCm`, `ExitCloseCm`, `EnterFarCm`, `ExitFarCm`, `EnterDodgeRate`, `ExitDodgeRate`, `DodgeRateWindowSeconds`) gets its **own** NaN, +Inf and -Inf case (clarified per X-2163). |

## BL-05: 20-batch (100-task) queue outline

- **Batches 1-2 (BL-01..10):** this audit, then the five tasks above.
- **Batches 3-18 (BL-11..90):** each batch takes the next headers with confirmed no-decision gaps (list below), one new guard-test file per header, plus a hand re-verification of the gap first.
- **Batch 19 (BL-91..95):** the hypotheses pass. Confirm or drop each suspected gap.
- **Batch 20 (BL-96..100):** consolidated build and run evidence, coverage re-tally, and the lane closeout.

| Batch | Tasks | Headers (confirmed no-decision gaps) |
|---|---|---|
| 3 | BL-11..15 | `RPGBossArenaEdgeRules` (2), `RPGBossBakeFreshnessRules` (1), `RPGBossBlockChipRules` (1) |
| 4 | BL-16..20 | `RPGBossChannelDrainRules` (3), `RPGBossComboAbortRules` (1), `RPGBossComboRules` (4) |
| 5 | BL-21..25 | `RPGBossCueJitterRules` (1), `RPGBossCueRules` (1), `RPGBossDefenseRules` (1) |
| 6 | BL-26..30 | `RPGBossDesperationRules` (1), `RPGBossDifficultyRules` (1), `RPGBossEnrageRules` (1) |
| 7 | BL-31..35 | `RPGBossFatigueRules` (1), `RPGBossFeintRules` (1), `RPGBossGapCloserRules` (1) |
| 8 | BL-36..40 | `RPGBossGuardRules` (4), `RPGBossLeashRules` (1), `RPGBossMusicIntensityRules` (3) |
| 9 | BL-41..45 | `RPGBossOverlayRules` (2), `RPGBossParryFairRules` (3), `RPGBossPatternDetectRules` (3) |
| 10 | BL-46..50 | `RPGBossPoiseRegenRules` (3), `RPGBossPresentationRules` (1), `RPGBossPunishLimiterRules` (1) |
| 11 | BL-51..55 | `RPGBossPunishRules` (3), `RPGBossReactiveDodgeRules` (2), `RPGBossRecoveryWindowRules` (3) |
| 12 | BL-56..60 | `RPGBossRepeatPenaltyRules` (2), `RPGBossRetreatRules` (1), `RPGBossRules` (3) |
| 13 | BL-61..65 | `RPGBossStaminaPressureRules` (2), `RPGBossStrafeRules` (2), `RPGBossStuckRecoveryRules` (1) |
| 14 | BL-66..70 | `RPGBossStuckRules` (1), `RPGBossTelegraphScaleRules` (2), `RPGBossTrackRules` (2) |
| 15 | BL-71..75 | `RPGBossWarpCurveRules` (2), `RPGBossYawProbeRules` (1), `RPGDLSSPlayerSettingsRules` (1) |
| 16 | BL-76..80 | `RPGPackParryRules` (2), `RPGParryCostRules` (1), `RPGParryGradeRules` (1) |
| 17 | BL-81..85 | `RPGSwingRules` (2), `RPGTelegraphRules` (1), ~~`RPGTier1VisualRules`~~ (excluded: owner-dependent) |
| 18 | BL-86..90 | (slack: re-verification / reruns) |

That covers **44 active headers in batches 3-17**. The struck-through `RPGTier1VisualRules` entry is excluded, and batch 18 is slack for re-verification and rerun evidence. Correction per X-2160: this line previously said 45 headers in batches 3-18.

**Confirmed gaps vs hypotheses:** every count above is a reviewer-confirmed gap. The hypotheses are not scheduled until batch 19.

## Limits

- This is a static audit. **No test was compiled or run**, because a build needs the engine and the lead's acceptance build.
- Line numbers come from the reviewers and were checked by hand for the BL-06..10 gaps (BL-10 Aggro `IsValid` clauses hand-verified in C-1420; per A-879).
- `RPGTier1VisualRules.h` is excluded from owner-independent work.

## Appendix: confirmed untested behaviors by header (reviewer output)

**`RPGAirAttackRules.h`**, tests: Tests/RPGAirAttackRulesTests.cpp

- *hypothesis:* Grounded AND no clip (Select(false,*,false)) not asserted, but same branch at :12 as asserted cases; negligible gap

**`RPGBleedRules.h`**, tests: Tests/RPGAutomationTests.cpp; Tests/RPGCodexTests.cpp; Tests/RPGBleedRulesPropertyTests.cpp; Tests/RPGBossDamageBleedFiniteInputTests.cpp; Tests/RPGBossQueueEAdjacentBoundaryTests.cpp

- Negative finite Amount -> IgnoredAmount (`RPGBleedRules.h:50`)
- Invalid config guards (InitialThreshold<=0, ThresholdIncrease<0, ThresholdMax<InitialThreshold, HpFraction<0 or non-finite) return IgnoredAmount (`RPGBleedRules.h:51-54`)
- Invalid state guards (Buildup<0/non-finite, Threshold<=0, Procs<0) return IgnoredAmount (`RPGBleedRules.h:55-56`)
- ProcDamage returns 0 for MaxHealth<=0, Health<=0, non-finite inputs, or HpFraction<0 (`RPGBleedRules.h:78-81`)
- Name() strings for all EResult values other than Proc, and '?' fallback (`RPGBleedRules.h:36-44`)
- *hypothesis:* ThresholdIncrease=0 (valid, threshold never rises) not asserted

**Additional hand-verified Aggro cases (outside the reviewer-sourced 94):** negative finite `DodgeRatePerSecond` preserves the current band (`RPGBossAggroRules.h:23`). `EnterCloseCm<0` and `ExitCloseCm==EnterCloseCm` **are** asserted (`RPGBossQueueEBoundaryTests.cpp:198,202`; `RPGBossQueueEPolicyBoundaryTests.cpp:11-12`). The non-finite fields, `ExitFarCm<=ExitCloseCm`, `EnterFarCm<=ExitFarCm`, `ExitDodgeRate<0`, `EnterDodgeRate<=ExitDodgeRate` and `DodgeRateWindowSeconds<=0` are **unasserted**: no other `FConfig` mutation exists in any test file.

**`RPGBossAggroRules.h`**, tests: Tests/RPGBossAggroRulesTests.cpp; Tests/RPGBossQueueEBoundaryTests.cpp; Tests/RPGBossQueueEAdjacentBoundaryTests.cpp; Tests/RPGBossQueueEPolicyBoundaryTests.cpp

- Separate hand-verified additions are listed above and are not included in the reviewer-sourced 94.

**`RPGBossAimHysteresisRules.h`**, tests: Tests/RPGBossAimHysteresisTests.cpp; Tests/RPGBossYawProbeTests.cpp (includes header)

- [decision] Negative EnterDeg makes the cone unreachable (always false) (`RPGBossAimHysteresisRules.h:13-15`)
- *hypothesis:* RPGBossYawProbeTests.cpp usage not inspected in detail

**`RPGBossApproachRules.h`**, tests: Tests/RPGBossApproachTests.cpp

- StepFraction(NaN) returns 0 (`RPGBossApproachRules.h:11`)
- StepCm T1>1 and TotalCm<0 return 0 (`RPGBossApproachRules.h:20`)
- PeakSpeedCm negative TotalCm / negative duration return 0 (`RPGBossApproachRules.h:31`)

**`RPGBossArenaEdgeRules.h`**, tests: Tests/RPGBossArenaEdgeRulesTests.cpp; Tests/RPGBossQueueDEdgeTests.cpp (includes header only, no Evaluate call found)

- NaN Boss or Center returns zero result (`RPGBossArenaEdgeRules.h:12`)
- Negative radius/margin fail closed; Inward zero at center (`RPGBossArenaEdgeRules.h:12,14`)

**`RPGBossBakeFreshnessRules.h`**, tests: Tests/RPGBossBakeFreshnessRulesTests.cpp

- Both fingerprints zero (equal) is not fresh (`RPGBossBakeFreshnessRules.h:10`)

**`RPGBossBlockChipRules.h`**, tests: Tests/RPGBossBlockChipRulesTests.cpp

- Negative ChipFraction returns 0 (`RPGBossBlockChipRules.h:10`)

**`RPGBossChannelDrainRules.h`**, tests: Tests/RPGBossMoveCardTests.cpp

- TickCount returns exactly 65 at Ratio>=65 (cap) (`RPGBossChannelDrainRules.h:12`)
- TickCount Start<0, End<=Start, non-finite inputs return 0 (`RPGBossChannelDrainRules.h:10`)
- CappedHeal HealFraction>1 or <=0, BossHealth<0, BossMaxHealth<=0, non-finite return 0 (`RPGBossChannelDrainRules.h:19`)

**`RPGBossCloseClipSwapRules.h`**, tests: Tests/RPGBossCloseClipSwapTests.cpp

- *hypothesis:* Case table contents (lines before :27) not read; whether GS_Attack04 -> None and unknown/NAME_None rows are included is unconfirmed

**`RPGBossComboAbortRules.h`**, tests: Tests/RPGBossComboAbortRulesTests.cpp

- Negative AcceptedHits does not abort (`RPGBossComboAbortRules.h:10`)

**`RPGBossComboRules.h`**, tests: Tests/RPGBossComboTests.cpp; Tests/RPGBossComboPropertyTests.cpp; Tests/RPGBossComboParriedSampleTests.cpp

- EdgeDomain for negative MinRangeCm and negative MaxAbsYawDegrees, and infinite fields (`RPGBossComboRules.h:64`)
- Node with Id NAME_None -> Combo.DuplicateNode (`RPGBossComboRules.h:56`)
- Gate id is consumed (LastGateId set) even when Target check then fails (`RPGBossComboRules.h:80-81`)
- Infinite SignedYawDegrees gate -> Combo.Target (`RPGBossComboRules.h:81`)

**`RPGBossCueJitterRules.h`**, tests: Tests/RPGBossCueJitterRulesTests.cpp; Tests/RPGBossQueueEBoundaryTests.cpp

- CueIndex<0, JitterSeconds<0, SafeMax<SafeMin, non-finite SafeMin/SafeMax return 0 (`RPGBossCueJitterRules.h:10-11`)

**`RPGBossCueRules.h`**, tests: Tests/RPGBossCueTests.cpp; Tests/RPGBossCueSweepTests.cpp

- HoldSeconds Max exactly 3.0 accepted; infinite Max rejected (`RPGBossCueRules.h:27`)

**`RPGBossDefenseRules.h`**, tests: Tests/RPGBossDefenseTests.cpp; Tests/RPGBossDefenseSweepTests.cpp; Tests/RPGBossMoveCardTests.cpp; Tests/RPGBossQueueEBoundaryTests.cpp

- TelegraphOk negative PlayRate fails; BackstepDistanceOk negative; CooldownOk +inf fails (`RPGBossDefenseRules.h:19,21,22`)

**`RPGBossDesperationRules.h`**, tests: Tests/RPGBossDesperationRulesTests.cpp; Tests/RPGBossDesperationFullThresholdMutationTests.cpp

- HealthFraction <0 or >1, StartFraction<=0, MaxMultiplier<1 return 1; MaxMultiplier exactly 3 accepted (`RPGBossDesperationRules.h:11`)

**`RPGBossDifficultyRules.h`**, tests: Tests/RPGBossDifficultyRulesTests.cpp; Tests/RPGBossDifficultyEqualEndpointsMutationTests.cpp; Tests/RPGBossQueueEBoundaryTests.cpp

- IsValid rejects Min<=0, Max<Min, DamageMax>3, TelegraphMax>2, non-finite fields; Evaluate with invalid config returns neutral (`RPGBossDifficultyRules.h:12-14,18`)

**`RPGBossDormantWakeRules.h`**, tests: Tests/RPGBossDormantWakeTests.cpp

- *hypothesis:* ExpectedSeconds between 0 and 0.15 (e.g. 0.05 -> grace 0.05) not asserted

**`RPGBossEnrageRules.h`**, tests: Tests/RPGBossEnrageRulesTests.cpp; Tests/RPGBossQueueEBoundaryTests.cpp

- MaxDamageScale<1 or MaxSpeedScale<1 invalid; MaxDamageScale exactly 3 and MaxSpeedScale exactly 2 accepted (`RPGBossEnrageRules.h:16`)

**`RPGBossFatigueRules.h`**, tests: Tests/RPGBossFatigueRulesTests.cpp; Tests/RPGBossQueueEBoundaryTests.cpp

- GraceWhiffs<0, ReductionPerWhiff<0 or >1 or non-finite, MinRateScale>1 or non-finite return -1 (`RPGBossFatigueRules.h:11-12`)

**`RPGBossFeintRules.h`**, tests: Tests/RPGBossFeintRulesTests.cpp; Tests/RPGBossFeintMaxChanceBoundaryMutationTests.cpp

- Negative reaction, Fast<0, MinChance<0, MaxChance<MinChance, MaxChance>1, Slow==Fast return 0 (`RPGBossFeintRules.h:11`)

**`RPGBossGapCloserRules.h`**, tests: Tests/RPGBossGapCloserRulesTests.cpp; Tests/RPGBossGapCloserExitBoundaryMutationTests.cpp; Tests/RPGBossQueueEBoundaryTests.cpp; Tests/RPGBossQueueEAdjacentBoundaryTests.cpp

- Negative RangeCm or negative EnterRangeCm return false (`RPGBossGapCloserRules.h:10`)

**`RPGBossGuardRules.h`**, tests: Tests/RPGBossGuardTests.cpp OneBossFight.Framework.Guard.Rules; Tests/RPGBossBlockChipRulesTests.cpp OneBossFight.Framework.BlockChip.Rules (Classify only, L35)

- NaN/inf SinceFirstAttack rejected (`RPGBossGuardRules.h:30`)
- Phase clamp to +/-float max and negative resulting Clock (large negative phase) returns false (`RPGBossGuardRules.h:31-33`)
- Exact pulse edges: position 0.1 excluded, 0.5 period wrap (`RPGBossGuardRules.h:34-35`)
- CardOutcome with negative counts (treated as zero) (`RPGBossGuardRules.h:25`)

**`RPGBossHitStopRules.h`**, tests: Tests/RPGBossHitStopRulesTests.cpp OneBossFight.Framework.HitStop.Rules

- Non-finite config fields invalid (`RPGBossHitStopRules.h:12`)
- Late<0 and Max<0 invalid; Late>Good invalid (`RPGBossHitStopRules.h:13`)
- Equality boundaries (Perfect==Max, equal grades) valid (`RPGBossHitStopRules.h:13`)
- Exact returned values for Good/Late (only relative ordering asserted) (`RPGBossHitStopRules.h:20-22`)

**`RPGBossLeashRules.h`**, tests: Tests/RPGBossArenaLeashBoundaryTests.cpp FBossArenaLeashInsideRadius/ExactRadius/OneCentimeterOutside/UsesPlanarDistance/InvalidAndDisabledRadius; Tests/RPGBossQueueDEdgeTests.cpp FBossQueueDEdgeBoundaries, FBossLeashLargeFiniteCoordinate

- Negative finite radius disables leash (returns false) (`RPGBossLeashRules.h:17`)

**`RPGBossMusicIntensityRules.h`**, tests: Tests/RPGBossMusicIntensityRulesTests.cpp OneBossFight.Framework.MusicIntensity.Rules

- HealthFraction NaN/inf, <0, >1 returns 0 (`RPGBossMusicIntensityRules.h:10`)
- Boost NaN/negative and boundary 0/1 accepted (`RPGBossMusicIntensityRules.h:10`)
- Phase 0/negative fails closed (`RPGBossMusicIntensityRules.h:10`)

**`RPGBossOverlayRules.h`**, tests: Tests/RPGFrameworkRuntimeTests.cpp OneBossFight.Framework.Runtime.BossOverlayFormat (L873), .OverlayParry (L897)

- Num with Digits>=2 (%.2f branch) (`RPGBossOverlayRules.h:24`)
- bHasParryData with closed window (`RPGBossOverlayRules.h:31`)
- *hypothesis:* RPGFrameworkRuntimeTests.cpp:890-892 loop may cover more invalid fields; not fully read

**`RPGBossParryFairRules.h`**, tests: Tests/RPGBossParryFairTests.cpp OneBossFight.Framework.BossParryFair.Rules; Tests/RPGBossParryFairAdjacentBoundaryTests.cpp FBossParryFairAdjacentBoundaryTest; Tests/RPGBossTelegraphScaleRulesTests.cpp (indirect)

- Negative telegraph, negative window, negative reaction fail closed (`RPGBossParryFairRules.h:17-18`)
- Overflowing ReactionGap (tiny PlayRate) non-finite -> false (`RPGBossParryFairRules.h:23`)
- Infinity (not NaN) inputs (`RPGBossParryFairRules.h:15-16`)

**`RPGBossPatternDetectRules.h`**, tests: Tests/RPGBossPatternDetectRulesTests.cpp OneBossFight.Framework.PatternDetect.Rules

- Required boundary 100 accepted and 2 accepted at exact count (`RPGBossPatternDetectRules.h:11`)
- Corrupt negative/oversize Consecutive clamped (`RPGBossPatternDetectRules.h:12`)
- Invalid Required also resets state (state cleared, asserted only for None) (`RPGBossPatternDetectRules.h:11`)

**`RPGBossPoiseRegenRules.h`**, tests: Tests/RPGBossPoiseRegenRulesTests.cpp OneBossFight.Framework.PoiseRegen.Rules; Tests/RPGBossPoiseRegenZeroRampMutationTests.cpp; Tests/RPGBossQueueEBoundaryTests.cpp FBossPoiseRegenExactRampEndpoint, FBossPoiseRegenZeroDelayAndFlatScale, FBossPoiseRegenRampEndpointAdjacent

- Base<0, Base>1e6, Delay>1e6, Ramp>1e6 rejection (`RPGBossPoiseRegenRules.h:11`)
- MaxScale <1 or >3 rejected; MaxScale=3 accepted (`RPGBossPoiseRegenRules.h:11`)
- Negative SecondsSinceHit/Delay, NaN in other params (`RPGBossPoiseRegenRules.h:10-11`)

**`RPGBossPresentationRules.h`**, tests: Tests/RPGBossPresentationRulesTests.cpp OneBossFight.Framework.Presentation.Rules

- ShouldPlayDeath(false,true) (`RPGBossPresentationRules.h:10`)

**`RPGBossPunishLimiterRules.h`**, tests: Tests/RPGBossPunishLimiterRulesTests.cpp OneBossFight.Framework.PunishLimiter.Rules; Tests/RPGBossQueueEBoundaryTests.cpp FBossPunishLimiterMaximumAndOverflow, FBossPunishLimiterMaximumCounterFailsClosed

- MaxUses>100 rejected and 100 accepted (`RPGBossPunishLimiterRules.h:11`)
- *hypothesis:* FBossPunishLimiterMaximumAndOverflow (QueueE:111) may cover MaxUses=100; body not read

**`RPGBossPunishRules.h`**, tests: Tests/RPGBossPunishTests.cpp OneBossFight.Framework.Punish.Rules; Tests/RPGBossPunishSweepTests.cpp OneBossFight.Framework.Punish.Sweep; Tests/RPGFrameworkRuntimeTests.cpp OneBossFight.Framework.Runtime.PunishProfile; Tests/RPGBossDefenseTests.cpp, RPGBossDefenseSweepTests.cpp (indirect)

- RequiresRecoveryPunishCheck with NaN/negative cone and cone exactly 180 vs 179.9 boundary (`RPGBossPunishRules.h:16`)
- FPlayerMoves invalid on NaN, zero startups, negative reach; ReachCm=0 valid (`RPGBossPunishRules.h:23-24`)
- Negative run speed in TravelSeconds (`RPGBossPunishRules.h:29`)

**`RPGBossReactiveDodgeRules.h`**, tests: Tests/RPGBossReactiveDodgeRulesTests.cpp OneBossFight.Framework.ReactiveDodge.Rules; Tests/RPGBossQueueEBoundaryTests.cpp FBossReactiveDodgeMaximumHitBoundary, FBossReactiveDodgeNegativeHitCountFailsClosed

- HitsToStart<0 or >100 invalid; Base>Max invalid; negative/NaN Base/PerHit (`RPGBossReactiveDodgeRules.h:11-12`)
- Roll negative or >=1 rejected (`RPGBossReactiveDodgeRules.h:22`)

**`RPGBossRecoveryWindowRules.h`**, tests: Tests/RPGBossRecoveryWindowRulesTests.cpp OneBossFight.Framework.RecoveryWindow.Rules; Tests/RPGBossParryRecoveryWiringTests.cpp OneBossFight.Framework.ParryRecovery.WiringBoundary

- ScaledSeconds Scale<0 and >3 return -1; Scale=3 accepted (`RPGBossRecoveryWindowRules.h:37`)
- ScaledSeconds non-finite/non-positive card recovery with nonzero scale returns -1; zero scale returns 0 even with invalid recovery (`RPGBossRecoveryWindowRules.h:38-39`)
- Fractions <0 or >1, MinSeconds<=0 rejected (`RPGBossRecoveryWindowRules.h:16,18`)

**`RPGBossRepeatPenaltyRules.h`**, tests: Tests/RPGBossRepeatPenaltyRulesTests.cpp OneBossFight.Framework.RepeatPenalty.Rules

- RepeatCount>100 returns 0 (`RPGBossRepeatPenaltyRules.h:10`)
- Negative/NaN BaseWeight, negative/NaN scale (`RPGBossRepeatPenaltyRules.h:10`)

**`RPGBossRetreatRules.h`**, tests: Tests/RPGBossRetreatRulesTests.cpp OneBossFight.Framework.Retreat.Rules; Tests/RPGBossQueueEBoundaryTests.cpp FBossRetreatAdjacentThresholds, FBossRetreatNonfiniteThresholdsFailClosed; Tests/RPGBossQueueEAdjacentBoundaryTests.cpp FBossRetreatAdjacentRangeAndThreat; Tests/RPGBossRetreatCloseBoundaryMutationTests.cpp

- Negative CloseRangeCm, threshold <0 or >1, NaN range (`RPGBossRetreatRules.h:10-11`)

**`RPGBossRules.h`**, tests: Tests/RPGAutomationTests.cpp OneBossFight.Boss.TransitionRules (L223); Tests/RPGCodexTests.cpp OneBossFight.Codex.BossRulesEdges (L52); Tests/RPGFrameworkRuntimeTests.cpp OneBossFight.Framework.Runtime.HyperArmor (L561)

- ResolveTransition NaN/inf Health/Max/Fraction and Fraction<0 or >1 -> NotReady (`RPGBossRules.h:77-78`)
- Negative health -> Dead (`RPGBossRules.h:79`)
- Name() strings for both enums incl. ? fallback (`RPGBossRules.h:30-57`)
- *hypothesis:* FRPGTransitionRulesTest also reads UObject CDOs (GetDefault, RPGAutomationTests.cpp:271-273) but rules themselves are pure

**`RPGBossStaggerAnimRules.h`**, tests: Tests/RPGFrameworkRuntimeTests.cpp OneBossFight.Framework.Runtime.StaggerAnimRules (L777)

- Evaluate invalid geometry (negative lens, Total<=0, Start+End>Total) -> Finished (`RPGBossStaggerAnimRules.h:43`)
- Evaluate with negative Dt returns Start (`RPGBossStaggerAnimRules.h:46-47`)
- ValidatePhaseClip PhaseTwoId None, empty skeleton strings, empty Slot token (`RPGBossStaggerAnimRules.h:70-72`)
- Validate zero StartLen/EndLen -> TooShort (`RPGBossStaggerAnimRules.h:33`)

**`RPGBossStaggerResistRules.h`**, tests: Tests/RPGBossStaggerResistRulesTests.cpp OneBossFight.Framework.StaggerResist.Rules; Tests/RPGBossQueueEBoundaryTests.cpp FBossStaggerResistScaleEndpointsAndInvalids, FBossStaggerResistUnknownExtremePhases; Tests/RPGBossStaggerResistUnknownPhaseMutationTests.cpp

- *hypothesis:* Invalid phase-two override also neutralizes phase 1 (shared guard L10) not explicitly asserted

**`RPGBossStaminaPressureRules.h`**, tests: Tests/RPGBossStaminaPressureRulesTests.cpp OneBossFight.Framework.StaminaPressure.Rules

- Fraction >1 or NaN, LowThreshold <=0 or >1, MaxPressure <0, NaN params (`RPGBossStaminaPressureRules.h:10`)
- MaxPressure scaling other than 1 (e.g. 3 endpoint) (`RPGBossStaminaPressureRules.h:11`)

**`RPGBossStrafeRules.h`**, tests: Tests/RPGBossStrafeTests.cpp (OneBossFight.Framework.Strafe.Rules); Tests/RPGBossStrafeHoldBoundaryMutationTests.cpp (FBossStrafeHoldBoundaryMutationTest); Tests/RPGBossFiniteRuleOverflowWitnessTests.cpp; Tests/RPGFrameworkRuntimeTests.cpp

- DirectionAt returns 1 for negative/non-finite elapsed or non-positive holds (`RPGBossStrafeRules.h:56-58`)
- HoldSeconds non-finite Min/Max returns Min or 0 (`RPGBossStrafeRules.h:39-40`)
- *hypothesis:* Negative speed / Dir=-2 rejection only implied by zero-speed and Dir=0 cases

**`RPGBossStuckRecoveryRules.h`**, tests: Tests/RPGBossStuckRecoveryRulesTests.cpp (OneBossFight.Framework.StuckRecovery.Rules); Tests/RPGBossStuckRecoveryCapEightMutationTests.cpp; Tests/RPGBossQueueDEdgeTests.cpp (FBossQueueDEdgeBoundaries)

- MaxAttempts<=0 refused (`RPGBossStuckRecoveryRules.h:10`)

**`RPGBossStuckRules.h`**, tests: Tests/RPGBossStuckTests.cpp (OneBossFight.Framework.BossStuck.Rules); Tests/RPGBossQueueDEdgeTests.cpp

- IsStuck rejects negative MinRatio (`RPGBossStuckRules.h:42`)
- *hypothesis:* Negative ExpectedCm/MovedCm/Dt reset path (line 21) not seen asserted separately from NaN case
- *hypothesis:* AccumExpected<=0 guard (line 43) not explicitly asserted

**`RPGBossTelegraphScaleRules.h`**, tests: Tests/RPGBossTelegraphScaleRulesTests.cpp (OneBossFight.Framework.TelegraphScale.Rules)

- MinRateScale>1 or <=0 refused (`RPGBossTelegraphScaleRules.h:13`)
- ActiveStartSeconds<=0 refused (`RPGBossTelegraphScaleRules.h:13`)

**`RPGBossTrackRules.h`**, tests: Tests/RPGFrameworkRuntimeTests.cpp; Tests/RPGBossTurnLatchBoundaryTests.cpp (FBossTurnLatch* 5 tests); Tests/RPGBossQueueDEdgeTests.cpp; Tests/RPGBossTrackRulesSweepTests.cpp (OneBossFight.Framework.Track.Sweep); Tests/RPGBossWarpExactDurationBoundaryTests.cpp; Tests/RPGBossLosLeashDeadlineTests.cpp; Tests/RPGBossAbortTests.cpp; Tests/RPGBossFiniteRuleOverflowWitnessTests.cpp

- PlayerActivityName string mapping (`RPGBossTrackRules.h:146`)
- WatchdogTimeoutSeconds rejects negative ClipLength/BlendOut (`RPGBossTrackRules.h:150`)
- *hypothesis:* GroundedZ non-finite input branch (line 120) maybe untested
- *hypothesis:* FDodgeHistory Depth<1 guard (line 81) not verified

**`RPGBossWarpCurveRules.h`**, tests: Tests/RPGBossWarpCurveRulesTests.cpp (OneBossFight.Framework.WarpCurve.Rules)

- non-finite T01 returns 0 (`RPGBossWarpCurveRules.h:11`)
- negative OvershootAmount and exact 0.5 accept (`RPGBossWarpCurveRules.h:11`)
- *hypothesis:* default switch branch (line 18) unreachable with valid enum

**`RPGBossYawProbeRules.h`**, tests: Tests/RPGBossYawProbeTests.cpp (OneBossFight.Framework.BossYawProbe.Rules); Tests/RPGBossYawProbeExtremaBoundaryTests.cpp; Tests/RPGBossFiniteRuleOverflowWitnessTests.cpp

- negative Period returns 0 (`RPGBossYawProbeRules.h:11`)

**`RPGBuildRules.h`**, tests: Tests/RPGBuildTests.cpp (OneBossFight.Build.Rules, .Decide, .Assets, .DamageScaler); Tests/RPGCodexTests.cpp; Tests/RPGCombatCatalogTests.cpp

- *hypothesis:* Parse(Text) quote/space trimming paths not inspected in RPGBuildTests.cpp
- *hypothesis:* DecisionName '?' fallback (line 172) unreachable with valid enum
- *hypothesis:* LegacySlotOf out-of-range LegacySlot>=BuildCount (line 69) not verified

**`RPGDLSSPlayerSettingsRules.h`**, tests: Tests/RPGDLSSPlayerSettingsRulesTests.cpp (OneBossFight.Player.DLSSPlayerSettingsRules)

- Off with bSupported=false and out-of-range enum default branch -> TSR (`RPGDLSSPlayerSettingsRules.h:14,24`)

**`RPGDodgeInputRules.h`**, tests: Tests/RPGDodgeInputRulesTests.cpp (OneBossFight.Player.DodgeInputRules)

- *hypothesis:* direction input with no clip case may be absent (3 of 4 combinations seen)

**`RPGEncounterGenerationRules.h`**, tests: Tests/RPGEncounterGenerationRulesTests.cpp (FRPGEncounterGenerationAdvanceRules, FRPGEncounterGenerationSequenceProperty); Tests/RPGBossStartupActivationTests.cpp

- *hypothesis:* OutError reset on success (line 15) and exact error strings may not be asserted

**`RPGGuardCounterRules.h`**, tests: Tests/RPGGuardCounterRulesTests.cpp (OneBossFight.Player.GuardCounterRules)

- *hypothesis:* Proposed* constants (lines 24-26) are proposals; asserting them needs product decision

**`RPGPackParryRules.h`**, tests: Tests/RPGPackParryContactTests.cpp (FRPGPackParryCandidateRulesTest, FRPGPackParryPostureDefaultTest, FRPGPackParryAttackKeyTest)

- negative or non-finite RequiredSeconds/LossTolerance rejected (`RPGPackParryRules.h:35-36`)
- exact LossTolerance boundary (HealthNow == Before - tol confirms) (`RPGPackParryRules.h:40`)
- *hypothesis:* BossId==0 empty key (line 47) and Reset() (line 87) not seen asserted

**`RPGParryCostRules.h`**, tests: Tests/RPGParryCostTests.cpp (OneBossFight.Framework.ParryCost.Rules); Tests/RPGParryPropertyTests.cpp (OneBossFight.Parry.Property.Cost); Tests/RPGBossParryBoundaryUpgradeTests.cpp

- [decision] ParryRefund when Stamina > MaxStamina returns MaxStamina (lowers stamina) (`RPGParryCostRules.h:26`)
- StaminaAfter negative stamina/cost returns 0 (`RPGParryCostRules.h:17`)

**`RPGParryGradeRules.h`**, tests: Tests/RPGParryGradeTests.cpp (OneBossFight.Framework.ParryGrade.Rules); Tests/RPGParryPropertyTests.cpp (OneBossFight.Parry.Property.Grade); Tests/RPGBossParryBoundaryUpgradeTests.cpp

- infinite Offset/Window returns None (`RPGParryGradeRules.h:23`)
- *hypothesis:* Clamp at line 29 is dead code after the guard at 24

**`RPGParryRules.h`**, tests: Tests/RPGParryTests.cpp (OneBossFight.Framework.Parry.Rules, .PressSchedule); Tests/RPGParryAdjacentWindowBoundaryTests.cpp; Tests/RPGParryCooldownAdjacentBoundaryTests.cpp; Tests/RPGParryPropertyTests.cpp; Tests/RPGBossParryBoundaryUpgradeTests.cpp

- *hypothesis:* negative CooldownSeconds (absorbed by Max at line 19) not explicitly tested

**`RPGSwingRules.h`**, tests: Tests/RPGAutomationTests.cpp; Tests/RPGCodexTests.cpp

- Override with negative/NaN start or end<=start collapses to -1 (`RPGSwingRules.h:29`)
- NaN inputs to WindowOpen/StaminaExtra/NeedsRefresh and negative RefreshAfter (`RPGSwingRules.h:39,47,62-63`)

**`RPGTelegraphRules.h`**, tests: Tests/RPGCodexTests.cpp

- non-finite inputs to RateFor return 1 and TargetFor NaN/negative cvar return 0 (`RPGTelegraphRules.h:12,21`)

**`RPGTier1VisualRules.h`**, tests: Tests/RPGTier1VisualRulesTests.cpp (FRPGTier1VisualSelection)

- IsTier2PresentationEnabled and SpawnConfiguredEffect (world/asset dependent) (`RPGTier1VisualRules.h:26-29`)
- *hypothesis:* RPGTier1VisualRules.cpp exists but was not read; IsTier1PreviewEnabled test at :29 may depend on build config

## BL-06..10: implementation (X-2164; C, 2026-11-12)

**Five new test files only.** No production source edits, and no Unreal, build, PIE, commit or push. **The engine-lock acceptance build and automation run are pending with the lead.** These tests have **not** been compiled or run. I traced every assertion by hand against the header source, and each case group has a **positive control**, so a failed guard cannot pass vacuously.

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-06 | `Source/OneBossFight/Tests/RPGBleedGuardTests.cpp` | `OneBossFight.Framework.Bleed.Guards` | `Apply` → `IgnoredAmount` with the **state unchanged** (NaN-aware comparison) for invalid amount (zero, negative, NaN, ±Inf), each config guard (including non-finite threshold/fraction cases and invalid threshold ordering), and invalid state buildup/threshold/procs. Control: valid hit is `Added`. `ProcDamage` → 0 for invalid max health, health, and HpFraction (including non-finite cases). Control: 60. `Name()` gives exact text for all 7 values and `?` for an out-of-range value. |
| BL-07 | `.../RPGBossApproachGuardTests.cpp` | `OneBossFight.Framework.BossApproach.Guards` | `StepFraction(NaN)==0`; `StepCm` with `T1=1.0001` or a negative total gives 0; `PeakSpeedCm` with a negative distance or duration gives 0. Controls: full-range step = total; peak 150. |
| BL-08 | `.../RPGBossHitStopGuardTests.cpp` | `OneBossFight.Framework.HitStop.Guards` | exact defaults .12/.08/.04; NaN, +Inf and -Inf for **each** of the 4 fields; `Late<0`; `Max<0`; `Perfect<Good`, `Good<Late`, `Late>Good`. Each invalid config is `!IsValid` and gives 0 for Perfect, Good and Late. Valid equality cases: `Perfect==Max`, all grades equal, `Late` 0, all zero. |
| BL-09 | `.../RPGBossStaggerAnimGuardTests.cpp` | `OneBossFight.Framework.Runtime.StaggerAnimGuards` | `Evaluate` gives `Finished` for a negative Start or End, `Total` 0 or negative, or `Start+End>Total` (control: the same `Dt` is `Loop`); a negative `Dt` gives `Start`; `Validate` with a zero Start or End gives `…StaggerAnim.TooShort` (control: valid params give an empty result). |
| BL-10 | `.../RPGBossAggroGuardTests.cpp` | `OneBossFight.Framework.Aggro.Guards` | A negative finite dodge rate preserves each of the 3 bands; each band has a valid-config control that **does** move. Each of the 7 `FConfig` fields gets NaN, +Inf and -Inf. The isolated clauses `ExitFarCm==ExitCloseCm`, `EnterFarCm==ExitFarCm`, `ExitDodgeRate<0`, `EnterDodgeRate==ExitDodgeRate`, and `DodgeRateWindowSeconds` 0 or negative each preserve all 3 bands. `EnterCloseCm<0` and `ExitCloseCm==EnterCloseCm` are **not** retested: existing coverage is cited in the file header. |

**Unique names:** I checked that none of the five automation names or test classes collides with an existing one. The closest existing name is `OneBossFight.Framework.Runtime.PlaybackGuards`.

## Hypotheses resolved (BL-91..95)

Every hypothesis in the appendix above has been classified in `Documentation/Boss/BL_91_95_HYPOTHESES_PASS.md`: covered 10, genuine gap 10, equivalent 2, unreachable 2, decision-dependent 1, not applicable 1. The 10 genuine gaps are asserted in `Source/OneBossFight/Tests/RPGBLHypothesisGapTests.cpp`.
