# V-A054: Combat Requirements Native Automation Coverage Matrix

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Task:** `V-A054` (Requirements coverage matrix: native tests to the 82 requirements)  
**Companion Artifacts:**
- CSV Matrix: [`requirements_automation_coverage_matrix.csv`](./requirements_automation_coverage_matrix.csv)
- Test Suite Validator: [`Scripts/Tools/test_requirements_coverage_matrix.py`](../../Scripts/Tools/test_requirements_coverage_matrix.py)
- Canonical Ledger: [`Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json`](../../Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json)

---

## 1. Overview & Purpose

The OneBossFight combat specification defines **82 canonical combat requirements** derived from the reference Soulslike boss encounter (Morgott/Ember Warden archetype). These requirements span spatial awareness, move eligibility, priority-driven execution, conditional combo branches, frame-accurate animation motion warping, swept collision hit detection, arena-aware locomotion, punishability windows, multi-meter defense, monotonic phase transitions, and diagnostic QA overlays.

This task maps every single one of the 82 canonical requirements to its authoritative **native C++ automation test** and corresponding source file in `Source/OneBossFight/Tests/`.

---

## 2. Coverage Summary by Section

| Section | Requirements Count | Primary Test Suites | Coverage Type | Status |
|---|:---:|---|---|:---:|
| **1. Awareness and observable context** | 8 | `RPGBossActivationTests`, `RPGBossMoveModelTests`, `RPGBossAggroRulesTests`, `RPGBossLosLeashDeadlineTests`, `RPGBossPatternDetectRulesTests` | NativeUnit | 8 / 8 Covered |
| **2. Eligibility, utility and selection** | 10 | `RPGBossMoveModelTests`, `RPGBossMoveCardTests`, `RPGBossMoveSelectorTests`, `RPGBossRepeatPenaltyRulesTests`, `RPGFrameworkRuntimeTests` | NativeUnit / Integration | 10 / 10 Covered |
| **3. Attack executor and state safety** | 8 | `RPGBossMoveModelTests`, `RPGBossExecutorHarnessTests`, `RPGBossAbortTests`, `RPGFrameworkRuntimeTests` | NativeUnit / Integration | 8 / 8 Covered |
| **4. Conditional combos** | 7 | `RPGBossComboTests`, `RPGBossComboPropertyTests`, `RPGBossComboAbortRulesTests`, `RPGBossComboFallbackTests` | NativeUnit | 7 / 7 Covered |
| **5. Animation, tracking and motion** | 8 | `RPGBossMoveCardTests`, `RPGBossTelegraphScaleRulesTests`, `RPGBossMoveCardHoldEndBoundaryTests`, `RPGBossTurnRateRampTests`, `RPGBossCloseClipSwapTests`, `RPGBossWarpCurveRulesTests` | NativeUnit | 8 / 8 Covered |
| **6. Hit detection and damage** | 12 | `RPGBossBakeFreshnessRulesTests`, `RPGBossBakedSampleEndpointMutationTests`, `RPGDamageScalerLowerWindowBoundaryTests`, `RPGFrameworkRuntimeTests`, `RPGParryTests`, `RPGBossBlockChipRulesTests`, `RPGBossShockwaveAdaptersTests`, `RPGBossHitStopRulesTests` | NativeUnit / Integration | 12 / 12 Covered |
| **7. Movement and arena** | 6 | `RPGBossApproachTests`, `RPGBossStrafeTests`, `RPGBossStrafeResumeRulesTests`, `RPGBossArenaEdgeRulesTests`, `RPGBossArenaLeashBoundaryTests`, `RPGBossRetreatRulesTests` | NativeUnit | 6 / 6 Covered |
| **8. Pacing and punishability** | 6 | `RPGBossMoveCardTests`, `RPGBossFatigueRulesTests`, `RPGBossRecoveryWindowRulesTests`, `RPGBossCueTests`, `RPGBossPunishLimiterRulesTests`, `RPGBossPunishTests` | NativeUnit | 6 / 6 Covered |
| **9. Defense, posture and interruption** | 5 | `RPGBossDamageBleedFiniteInputTests`, `RPGBossPoiseRegenRulesTests`, `RPGBossStaggerPolicyAdaptersTests`, `RPGBossStaggerResistRulesTests`, `RPGBossDefenseTests` | NativeUnit | 5 / 5 Covered |
| **10. Phases and anti-cheese reactions** | 5 | `RPGBossPhaseFlowAdaptersTests`, `RPGBossPhaseAdaptersTests`, `RPGBossPhasesClusterAdaptersTests`, `RPGBossHealPunishAdaptersTests`, `RPGBossGapCloserRulesTests` | NativeUnit | 5 / 5 Covered |
| **11. Debugging, QA, presentation and optional networking** | 7 | `RPGFrameworkRuntimeTests`, `RPGBossEncounterRestartMatrixTests`, `RPGCombatCatalogTests`, `RPGAutomationTests`, `RPGBossYawProbeTests`, `RPGTier1VisualRulesTests` | NativeIntegration / Gate | 7 / 7 Covered |
| **TOTAL** | **82** | **Full C++ Native Test Harness** | — | **100% (82/82)** |

---

## 3. Machine-Readable Artifacts & Automated Validation

1. **CSV Specification (`requirements_automation_coverage_matrix.csv`):**
   - Columns: `RequirementID`, `Section`, `Title`, `PrimaryAutomationTest`, `SourceFile`, `CoverageType`, `Status`.
   - Complete 82-row mapping covering every canonical requirement ID from `BOSS-AWR-001` through `BOSS-QA-007`.

2. **Automated Unit Test (`test_requirements_coverage_matrix.py`):**
   - Verified via `Scripts/Tools/test_requirements_coverage_matrix.py` (part of the 334-test offline suite).
   - Enforces four invariants:
     - The CSV matrix exists and matches `witness_status_v3.json` 1:1 on requirement IDs.
     - Exactly 82 canonical rows are present.
     - All referenced C++ source files exist on disk under `Source/OneBossFight/`.
     - Permitted enumerations for `CoverageType` and `Status` are strictly observed.
