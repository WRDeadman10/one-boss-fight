# BL-91..95: hypotheses pass (all 26 BL-01 audit hypotheses)

Assigned by X-2201 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 19 of 20.

**Method:**
- 3 read-only classifiers (a workflow fan-out, inside the 3-agent cap) checked each hypothesis against its header and every test under `Source/OneBossFight/Tests/`, including the BL guard files.
- **I re-read the header for every proposed gap before writing an assertion.** One verdict was reclassified by hand: #15, from equivalent to genuine gap.

**Not done:** no production source changes, and no Unreal, build, PIE, commit or push.

**Verdicts (26):** covered 10, genuine_gap 10, equivalent 2, unreachable 2, decision_dependent 1, not_applicable 1.

## BL-94: genuine gaps asserted (new file `Source/OneBossFight/Tests/RPGBLHypothesisGapTests.cpp`, `OneBossFight.Framework.HypothesisGaps`)

These are 10 hypotheses. Each is deterministic, owner-independent, existing behavior; none is asserted elsewhere.

| Id | Header | What is asserted |
|---|---|---|
| H1 | `RPGAirAttackRules.h` | grounded with no clip → Pack, for light and heavy |
| H2 | `RPGBleedRules.h` | `ThresholdIncrease` 0 is valid: a proc leaves the threshold at 100 |
| H6 | `RPGBossDormantWakeRules.h` | an expected time of 0.05 is the grace (finishes at 0.05, not at 0.04) |
| H10 | `RPGBossStaggerResistRules.h` | an invalid phase-two override also neutralizes phase one (control: 0.8, then 1) |
| H12 | `RPGBossStuckRules.h` | a negative expected, moved or dt sample resets the accumulators |
| H14 | `RPGBossTrackRules.h` | `GroundedZ` with a NaN floor gives 0; a NaN half-height keeps the floor (control: 102) |
| H15 | `RPGBossTrackRules.h` | `Push` with depth 0 or less keeps the existing history |
| H20 | `RPGDodgeInputRules.h` | direction input without a clip → Roll |
| H23 | `RPGPackParryRules.h` | BossId 0 gives an empty key; `Reset()` forgets accepted keys |
| H25 | `RPGParryRules.h` | a negative cooldown is floored to the window (ReadyAt 1.25) |

H1 and H20 complete an input truth table. Their branch is shared with the asserted cases, so they are low value, but they are cheap and exact.

## Full classification

| # | Header | Hypothesis | Verdict | Evidence | Action |
|---|---|---|---|---|---|
| 1 | `RPGAirAttackRules.h` | Grounded AND no clip (Select(false,*,false)) not asserted, but same branch at :12 as asserted cases; negligible gap | **genuine_gap** | RPGAirAttackRules.h:12 (!bFalling // !bOptionalMontageAvailable); RPGAirAttackRulesTests.cpp:17-22 assert 6 of 8 input combos; Select(false,false,false) and Select(false,true,false) absent. Same branch, low value. | asserted in `RPGBLHypothesisGapTests.cpp` (H1) |
| 2 | `RPGBleedRules.h` | ThresholdIncrease=0 (valid, threshold never rises) not asserted | **genuine_gap** | RPGBleedRules.h:52 accepts ThresholdIncrease>=0, :69 Threshold=Min(Threshold+Increase,Max). RPGBleedGuardTests.cpp:46-49 only negative/non-finite; RPGBossBleedAdaptersTests.cpp:133 sets 0 only for config round-trip, never calls Apply. | asserted in `RPGBLHypothesisGapTests.cpp` (H2) |
| 3 | `RPGBossAggroRules.h` | Individual IsValid clauses (EnterCloseCm<0, DodgeRateWindowSeconds<=0, Enter<=Exit dodge) not each asserted; only one invalid ordering used | **covered** | RPGBossAggroRules.h:14-20; RPGBossAggroGuardTests.cpp:35-44 (each field NaN/+Inf/-Inf), :47-52 (ordering/sign clauses); header comment :3 points to RPGBossQueueEBoundaryTests.cpp:198,202 and RPGBossQueueEPolicyBoundaryTests.cpp:11-12 for EnterCloseCm>=0 / ExitClose>EnterClose | report only |
| 4 | `RPGBossAimHysteresisRules.h` | RPGBossYawProbeTests.cpp usage not inspected in detail | **covered** | RPGBossAimHysteresisRules.h:10-16; RPGBossYawProbeTests.cpp:26 calls Step, :34 TestEqual HysteresisCrossings==0; dedicated RPGBossAimHysteresisTests.cpp:8+ and RPGBossYawProbeGuardTests.cpp also exercise it | report only |
| 5 | `RPGBossCloseClipSwapRules.h` | Case table contents (lines before :27) not read; whether GS_Attack04 -> None and unknown/NAME_None rows are included is unconfirmed | **covered** | RPGBossCloseClipSwapRules.h:10-21; RPGBossCloseClipSwapTests.cpp:20 (GS_Attack04 -> "" i.e. NAME_None, close=true), :21 (unknown GS_LeapAttack -> None, false), :22 (empty/NAME_None -> None, false), asserted at :27-28 | report only |
| 6 | `RPGBossDormantWakeRules.h` | ExpectedSeconds between 0 and 0.15 (e.g. 0.05 -> grace 0.05) not asserted | **genuine_gap** | RPGBossDormantWakeRules.h:13 Grace=Min(0.15,Max(0,Expected)); RPGBossDormantWakeTests.cpp:12-22 use Expected 3.5, 0, -1, NaN, Inf only; no Expected in (0,0.15) | asserted in `RPGBLHypothesisGapTests.cpp` (H6) |
| 7 | `RPGBossOverlayRules.h` | RPGFrameworkRuntimeTests.cpp:890-892 loop may cover more invalid fields; not fully read | **covered** | RPGFrameworkRuntimeTests.cpp:887-894 loop sets Range,Cone,Posture,PostureMax,Health,MaxHealth to NaN/+Inf/-Inf each and asserts n/a and no nan/inf; :881 specific NaN Range/Inf Health string | report only |
| 8 | `RPGBossPunishLimiterRules.h` | FBossPunishLimiterMaximumAndOverflow (QueueE:111) may cover MaxUses=100; body not read | **covered** | RPGBossPunishLimiterRules.h:11 MaxUses<=100; RPGBossQueueEBoundaryTests.cpp:117 CanUse(S,100) true, :118 CanUse(S,101) false, :120-121 max counter refusal | report only |
| 9 | `RPGBossRules.h` | FRPGTransitionRulesTest also reads UObject CDOs (GetDefault, RPGAutomationTests.cpp:271-273) but rules themselves are pure | **not_applicable** | Hypothesis is an observation about the test reading CDOs, not an untested behaviour of RPGBossRules.h | report only |
| 10 | `RPGBossStaggerResistRules.h` | Invalid phase-two override also neutralizes phase 1 (shared guard L10) not explicitly asserted | **genuine_gap** | RPGBossStaggerResistRules.h:10 shared guard; tests only use invalid phase-two with Phase 2 (RPGBossQueueEBoundaryTests.cpp:47) and invalid phase-one with Phase 1 (:45-46); no Scale(1,valid,invalid) call anywhere | asserted in `RPGBLHypothesisGapTests.cpp` (H10) |
| 11 | `RPGBossStrafeRules.h` | Negative speed / Dir=-2 rejection only implied by zero-speed and Dir=0 cases | **covered** | RPGBossStrafeRules.h:15; RPGBossStrafeNextPositionGuardTests.cpp:33 (negative speed), :36 (negative delta), :38 (Dir -2) | report only |
| 12 | `RPGBossStuckRules.h` | Negative ExpectedCm/MovedCm/Dt reset path (line 21) not seen asserted separately from NaN case | **genuine_gap** | RPGBossStuckRules.h:20-26; only NaN Update tested (RPGBossStuckTests.cpp:29); no negative Expected/Moved/Dt Update in any test | asserted in `RPGBLHypothesisGapTests.cpp` (H12) |
| 13 | `RPGBossStuckRules.h` | AccumExpected<=0 guard (line 43) not explicitly asserted | **equivalent** | RPGBossStuckRules.h:43,47-48: AccumExpected is >=0 (negatives reset at :21); if 0, Ratio=Moved/0 is +inf (moved>0) or NaN (moved=0); both fail IsFinite at :48 and return false without setting the flag, same as the guard | report only |
| 14 | `RPGBossTrackRules.h` | GroundedZ non-finite input branch (line 120) maybe untested | **genuine_gap** | RPGBossTrackRules.h:118-120 non-finite branch; tests only RPGFrameworkRuntimeTests.cpp:708 (finite) and RPGBossFiniteRuleOverflowWitnessTests.cpp:47 (overflow, line 122 branch) | asserted in `RPGBLHypothesisGapTests.cpp` (H14) |
| 15 | `RPGBossTrackRules.h` | FDodgeHistory Depth<1 guard (line 81) not verified | **genuine_gap** | RPGBossTrackRules.h:81. Reclassified by hand from 'equivalent': with a prior entry, deleting `Depth<1` would let `while (Num>Depth) RemoveAt(0)` empty the history. `Push(Back,3); Push(Back,0)` keeps 1 entry with the guard and 0 without, so the case discriminates. No existing test uses Depth<1 (`RPGFrameworkRuntimeTests.cpp:745-748`). | asserted in `RPGBLHypothesisGapTests.cpp` (H15) |
| 16 | `RPGBossWarpCurveRules.h` | default switch branch (line 18) unreachable with valid enum | **covered** | RPGBossWarpCurveRules.h:18; RPGBossWarpCurveGuardTests.cpp:32 Fraction(.5, static_cast<ECurve>(99)) == 0 | report only |
| 17 | `RPGBuildRules.h` | Parse(Text) quote/space trimming paths not inspected in RPGBuildTests.cpp | **covered** | RPGBuildRules.h:119-121; RPGBuildTests.cpp:106 "  Dex  ", :107 quoted "Strength", :109 quoted empty, :110 spaces, asserted in loop :118-124 | report only |
| 18 | `RPGBuildRules.h` | DecisionName '?' fallback (line 172) unreachable with valid enum | **unreachable** | RPGBuildRules.h:164-172 switch covers all 5 EDecision values; RPGBuildTests.cpp:157-161 cover each; '?' only via out-of-range static_cast, which no caller does | report only |
| 19 | `RPGBuildRules.h` | LegacySlotOf out-of-range LegacySlot>=BuildCount (line 69) not verified | **unreachable** | RPGBuildRules.h:69 guards LegacySlot>=BuildCount(3). Every FEpoch comes from Compile, which rejects LegacySlot outside INDEX_NONE or 0..2 (RPGCombatCatalog.cpp:148). The test checks that rejection at RPGCombatCatalogTests.cpp:83-85. The <0 (INDEX_NONE) branch is covered at RPGCombatCatalogTests.cpp:73-74. No compiled epoch can hold a slot >=3. | report only |
| 20 | `RPGDodgeInputRules.h` | direction input with no clip case may be absent (3 of 4 combinations seen) | **genuine_gap** | RPGDodgeInputRules.h:20-24. RPGDodgeInputRulesTests.cpp:19, 21, 23 and 28 cover (true,true), (false,true) and (false,false). No test calls (true,false). | asserted in `RPGBLHypothesisGapTests.cpp` (H20) |
| 21 | `RPGEncounterGenerationRules.h` | OutError reset on success (line 15) and exact error strings may not be asserted | **covered** | Reset on success: RPGEncounterGenerationRulesTests.cpp:15-16 checks Error.IsEmpty() after CanAdvance(1,2). Exact strings: lines 19, 21 and 23 (GenerationNotIncreasing) and lines 25-28 (GenerationExhausted). Header lines 15-25. | report only |
| 22 | `RPGGuardCounterRules.h` | Proposed* constants (lines 24-26) are proposals; asserting them needs product decision | **decision_dependent** | RPGGuardCounterRules.h:23-26 labels these values 'PROPOSAL defaults only; the owner has not approved'. A grep for Proposed[A-Z] in Tests/*.cpp finds nothing. Pinning the values would mean choosing product timings. | report only |
| 23 | `RPGPackParryRules.h` | BossId==0 empty key (line 47) and Reset() (line 87) not seen asserted | **genuine_gap** | RPGPackParryRules.h:47-50 (BossId==0 returns an empty key) and :87-91 (Reset). RPGPackParryContactTests.cpp:61-82 always passes BossId 42 and never calls Deduplicator.Reset(). | asserted in `RPGBLHypothesisGapTests.cpp` (H23) |
| 24 | `RPGParryGradeRules.h` | Clamp at line 29 is dead code after the guard at 24 | **equivalent** | RPGParryGradeRules.h:23-27 returns early unless Offset and Window are finite, 0<=Offset<Window and Window>0. At line 29 Offset is therefore already in [0,Window), so FMath::Clamp(Offset,0,Window) = Offset (not <0 and <Window). The clamp cannot change the result. | report only |
| 25 | `RPGParryRules.h` | negative CooldownSeconds (absorbed by Max at line 19) not explicitly tested | **genuine_gap** | RPGParryRules.h:18-19 has no guard on negative CooldownSeconds, so ReadyAt = Now + Max(Window, Cooldown) = Now + Window. The only negative-argument check is RPGParryTests.cpp:29, which covers a negative window. RPGParryCooldownAdjacentBoundaryTests.cpp:15-20 and RPGParryPropertyTests.cpp:50-58 use positive cooldowns. | asserted in `RPGBLHypothesisGapTests.cpp` (H25) |
| 26 | `RPGTier1VisualRules.h` | RPGTier1VisualRules.cpp exists but was not read; IsTier1PreviewEnabled test at :29 may depend on build config | **covered** | I read RPGTier1VisualRules.cpp. Lines 21-28 return false outside UE_BUILD_DEVELOPMENT and the CVar value (default 0, line 14) inside it. The test at RPGTier1VisualRulesTests.cpp:28-30 sits inside #if !UE_BUILD_DEVELOPMENT, so it asserts only the non-Development path, which is fixed. The Development path depends on the runtime rpg.Art.Tier1 setting, so it is not deterministic. SelectEffect is covered at lines 18-27. | report only |

## Notes

- **Already resolved by earlier BL batches:** #3 (BL-10 Aggro clauses), #8 (BL-48 false positive), #11 (BL-62 strafe negative speed and Dir), #16 (BL-71 invalid `ECurve`).
- **Decision-dependent:** #22 (GuardCounter `Proposed*` values, labelled as an owner PROPOSAL). Left untested on purpose.
- **Not compiled or run:** pending the engine-lock acceptance build.
