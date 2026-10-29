# AG-CONTENT08: Typed Profile Coverage Matrix (Revision A-189)

## 1. Overview & Scope
This document provides the authoritative coverage matrix of all 12 native boss components declared under `Source/OneBossFight/Player/RPGBoss*.h`.
The previous baseline has been preserved byte-for-byte under `original_A188/`.
This revision updates the matrix following the combined DD21+DD22 run verification accepted in Tech Lead Claude's `[C-269]` / `[C-270]`:
- `URPGBossShockwave` (DD21) and `URPGBossHealPunish` (DD22) are now fully **MEASURED** (Codex X-304 run, Claude C-269 acceptance, 153 unique Success, exit code 0).
- The last measured verification for all five wired components (`URPGBossStagger`, `URPGBossPhases`, `URPGBossEncounter`, `URPGBossDormantWake`, `URPGBossPosture`) is updated to the latest suite total of 153 unique Success.
- The total authored property count across all 12 headers is explicitly verified as 112 fields (7 + 5 + 12 + 2 + 4 + 14 + 5 + 8 + 18 + 4 + 8 + 25 = 112).

Negative Constraints:
- Zero percentage calculations are performed or stated.
- No global completeness claim across architectural requirements is made; all qualifications are scoped to isolated typed configuration, reflection, and headless test automation contracts.

---

## 2. Component Coverage Matrix (12 Native Boss Components, 112 Authored Fields)

| Component Class | Header & Authored Field Count | Typed Profile & Struct | Adapter Files & Test Automation Names | Last Measured Verification Run | Open KI Identifiers | Preflight / Registry Wiring Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`URPGBossBleed`** | `Source/OneBossFight/Player/RPGBossBleed.h:21`<br>**7 authored fields** (`:30`, `:34`, `:38`, `:42`, `:46`, `:50`, `:53`) | **DD19**<br>`FRPGBleedConfig`<br>(`RPGEncounterBinding.h:139-152`) | Adapters: `RPGBossBleedAdapters.h`, `RPGBossBleedAdapters.cpp`<br>Tests: `OneBossFight.Binding.Bleed.Assign`, `Validation`, `Isolation`, `Rejections`, `Compile`, `Authoring`<br>(`RPGBossBleedAdaptersTests.cpp:251, 397, 548, 602, 754, 890`) | Codex X-300 / Claude C-263<br>Folder: `Docs/BossCombatReview/Execution/Codex/DD19/`<br>**135 unique Success** (exit 0) | KI-119, KI-124, KI-126, KI-128 | **UNWIRED**<br>(Not in `RPGBossHydrationPreflight.cpp:65-74`, `:143-146`) |
| **`URPGBossCloseClipSwap`** | `Source/OneBossFight/Player/RPGBossCloseClipSwap.h:18`<br>**5 authored fields** (`:26`, `:29`, `:32`, `:35`, `:38`) | **NONE**<br>(Static rule struct `FRPGBossCloseClipSwapRules` in `RPGBossCloseClipSwapRules.h:12-25` only) | Adapters: `NONE`<br>Tests: `OneBossFight.Boss.CloseClipSwapRules`<br>(`RPGBossCloseClipSwapTests.cpp:9`, static rules only, no typed adapter profile) | **UNKNOWN** for typed profile<br>(Rules test verified in suite runs, e.g. DD21+DD22 full 153 unique Success) | KI-061, KI-102 | **UNWIRED**<br>(Not in `RPGBossHydrationPreflight.cpp:65-74`, `:143-146`) |
| **`URPGBossDeath`** | `Source/OneBossFight/Player/RPGBossDeath.h:40`<br>**12 authored fields** (`:51`, `:55`, `:59`, `:63`, `:66`, `:70`, `:74`, `:78`, `:82`, `:85`, `:89`, `:93`) | **NONE** | Adapters: `NONE`<br>Tests: `NONE` | **UNKNOWN** for typed profile | KI-070, KI-071 | **UNWIRED**<br>(Not in `RPGBossHydrationPreflight.cpp:65-74`, `:143-146`) |
| **`URPGBossDormantWake`** | `Source/OneBossFight/Player/RPGBossDormantWake.h:24`<br>**2 authored fields** (`:66`, `:68`) | **DD11 / DD12**<br>`FRPGDormantWakeAssetsConfig`<br>(`RPGEncounterBinding.h:128-136`)<br>`FRPGBossDormantWakeAssets`<br>(`RPGBossDormantWakeAdapters.h:13-20`) | Adapters: `RPGBossDormantWakeAdapters.h`, `RPGBossDormantWakeAdapters.cpp`<br>Tests: `OneBossFight.Binding.DormantWake.Assign`, `Validation`, `Isolation`, `Rejections`, `Compile`, `Authoring`<br>(`RPGBossDormantWakeAdaptersTests.cpp:235, 373, 482, 533, 701, 842`) | Codex X-304 / Claude C-269<br>Folder: `Docs/BossCombatReview/Execution/Codex/DD22/run_2026-10-29/`<br>**153 unique Success** (exit 0) | KI-119, KI-121, KI-123 | **WIRED**<br>(In Preflight: `RPGBossHydrationPreflight.cpp:71`, `:145`; Prep: `RPGBossHydrationPreparation.cpp:246`; Registry: `RPGBossPreparationRegistry.cpp:512`) |
| **`URPGBossEncounter`** | `Source/OneBossFight/Player/RPGBossEncounter.h:19`<br>**4 authored fields** (`:28`, `:32`, `:36`, `:40`) | **DD10 / DD12**<br>`FRPGEncounterScalarsConfig`<br>(`RPGEncounterBinding.h:30-39`)<br>`FRPGBossEncounterScalars`<br>(`RPGBossEncounterPolicyAdapters.h:13-22`) | Adapters: `RPGBossEncounterPolicyAdapters.h/.cpp`, `RPGBossEncounterClusterAdapters.h/.cpp`<br>Tests: `OneBossFight.Binding.EncounterPolicy.Assign`, `Validation`, `Isolation`, `Rejections`, `Compile`, `Authoring`<br>(`RPGBossEncounterPolicyAdaptersTests.cpp:161, 228, 298, 358, 428, 496`); `EncounterCluster.Assign`, `Validation`, `Isolation`, `Rejections`<br>(`RPGBossEncounterClusterAdaptersTests.cpp:173, 276, 387, 444`) | Codex X-304 / Claude C-269<br>Folder: `Docs/BossCombatReview/Execution/Codex/DD22/run_2026-10-29/`<br>**153 unique Success** (exit 0) | KI-119, KI-121, KI-123 | **WIRED**<br>(In Preflight: `RPGBossHydrationPreflight.cpp:70`, `:145`; Prep: `RPGBossHydrationPreparation.cpp:246`; Registry: `RPGBossPreparationRegistry.cpp:512`) |
| **`URPGBossHealPunish`** | `Source/OneBossFight/Player/RPGBossHealPunish.h:25`<br>**14 authored fields** (`:33`, `:37`, `:40`, `:44`, `:48`, `:54`, `:57`, `:60`, `:65`, `:68`, `:72`, `:76`, `:80`, `:141`) | **DD22**<br>`FRPGHealPunishConfig`<br>(`RPGEncounterBinding.h:185-204`) | Adapters: `RPGBossHealPunishAdapters.h`, `RPGBossHealPunishAdapters.cpp`<br>Tests: `OneBossFight.Binding.HealPunish.Assign`, `Validation`, `Isolation`, `Rejections`, `Compile`, `Authoring`<br>(`RPGBossHealPunishAdaptersTests.cpp:253, 416, 569, 623, 777, 915`) | Codex X-304 / Claude C-269<br>Folder: `Docs/BossCombatReview/Execution/Codex/DD22/run_2026-10-29/`<br>**153 unique Success** (focused 6/6, full 153, exit 0) | KI-130 | **UNWIRED**<br>(Plan defined in `RPGBossHealPunishAdapters.cpp:115-139`; not in `RPGBossHydrationPreflight.cpp:65-74`, `:143-146`) |
| **`URPGBossLook`** | `Source/OneBossFight/Player/RPGBossLook.h:22`<br>**5 authored fields** (`:30`, `:33`, `:37`, `:40`, `:44`) | **NONE**<br>(DD23 Work Order ordered in C-269, source in progress) | Adapters: `NONE`<br>Tests: `NONE` | **UNKNOWN** for typed profile | KI-055 | **UNWIRED**<br>(Not in `RPGBossHydrationPreflight.cpp:65-74`, `:143-146`) |
| **`URPGBossLowSweep`** | `Source/OneBossFight/Player/RPGBossLowSweep.h:21`<br>**8 authored fields** (`:29`, `:33`, `:37`, `:41`, `:44`, `:48`, `:52`, `:55`) | **DD20**<br>`FRPGLowSweepConfig`<br>(`RPGEncounterBinding.h:155-167`) | Adapters: `RPGBossLowSweepAdapters.h`, `RPGBossLowSweepAdapters.cpp`<br>Tests: `OneBossFight.Binding.LowSweep.Assign`, `Validation`, `Isolation`, `Rejections`, `Compile`, `Authoring`<br>(`RPGBossLowSweepAdaptersTests.cpp:251, 397, 548, 602, 754, 890`) | Codex X-301 / Claude C-264<br>Folder: `Docs/BossCombatReview/Execution/Codex/DD20/`<br>**141 unique Success** (exit 0) | KI-125, KI-127, KI-128 | **UNWIRED**<br>(Not in `RPGBossHydrationPreflight.cpp:65-74`, `:143-146`) |
| **`URPGBossPhases`** | `Source/OneBossFight/Player/RPGBossPhases.h:23`<br>**18 authored fields** (`:31`, `:35`, `:39`, `:42`, `:45`, `:52`, `:55`, `:58`, `:62`, `:66`, `:70`, `:73`, `:76`, `:79`, `:83`, `:87`, `:90`, `:113`) | **DD13**<br>`FRPGBossPhaseFlowScalars`<br>(`RPGEncounterBinding.h:65-79`)<br>`FRPGBossPhaseFlowFireball`<br>(`:81-93`)<br>`FRPGBossPhaseFlowAssets`<br>(`:95-103`)<br>`FRPGPhaseFlowPlan`<br>(`RPGBossPhasesClusterAdapters.h:18-29`) | Adapters: `RPGBossPhaseFlowAdapters.h/.cpp`, `RPGBossPhaseAdapters.h/.cpp`, `RPGBossPhasesClusterAdapters.h/.cpp`<br>Tests: `OneBossFight.Binding.PhaseFlow.Assign`, `Validation`, `Isolation`, `Rejections`, `Compile`, `Authoring`<br>(`RPGBossPhaseFlowAdaptersTests.cpp:186, 276, 365, 428, 507, 583`); `PhasesCluster.Assign`, `Validation`, `Isolation`, `Rejections`<br>(`RPGBossPhasesClusterAdaptersTests.cpp:176, 279, 390, 447`) | Codex X-304 / Claude C-269<br>Folder: `Docs/BossCombatReview/Execution/Codex/DD22/run_2026-10-29/`<br>**153 unique Success** (exit 0) | KI-119, KI-121, KI-123 | **WIRED**<br>(In Preflight: `RPGBossHydrationPreflight.cpp:69`, `:145`; Prep: `RPGBossHydrationPreparation.cpp:246`; Registry: `RPGBossPreparationRegistry.cpp:512`) |
| **`URPGBossPosture`** | `Source/OneBossFight/Player/RPGBossPosture.h:22`<br>**4 authored fields** (`:31`, `:35`, `:39`, `:43`) | **DD14**<br>`FRPGPostureScalarsConfig`<br>(`RPGEncounterBinding.h:54-61`)<br>`FRPGBossPostureScalars`<br>(`RPGBossStatsAdapters.h:14-22`) | Adapters: `RPGBossStatsAdapters.h`, `RPGBossStatsAdapters.cpp`<br>Tests: `OneBossFight.Binding.StatsAdapters.Assign`, `Isolation`, `Validation`, `HealthOverride`, `Rejections`<br>(`RPGBossStatsAdaptersTests.cpp:141, 204, 263, 343, 405`) | Codex X-304 / Claude C-269<br>Folder: `Docs/BossCombatReview/Execution/Codex/DD22/run_2026-10-29/`<br>**153 unique Success** (exit 0) | KI-119, KI-121, KI-123 | **WIRED**<br>(In Preflight: `RPGBossHydrationPreflight.cpp:72`, `:145`; Prep: `RPGBossHydrationPreparation.cpp:246`; Registry: `RPGBossPreparationRegistry.cpp:512`) |
| **`URPGBossShockwave`** | `Source/OneBossFight/Player/RPGBossShockwave.h:22`<br>**8 authored fields** (`:30`, `:34`, `:39`, `:42`, `:45`, `:49`, `:53`, `:57`) | **DD21**<br>`FRPGShockwaveConfig`<br>(`RPGEncounterBinding.h:170-182`) | Adapters: `RPGBossShockwaveAdapters.h`, `RPGBossShockwaveAdapters.cpp`<br>Tests: `OneBossFight.Binding.Shockwave.Assign`, `Validation`, `Isolation`, `Rejections`, `Compile`, `Authoring`<br>(`RPGBossShockwaveAdaptersTests.cpp:251, 397, 548, 602, 754, 890`) | Codex X-304 / Claude C-269<br>Folder: `Docs/BossCombatReview/Execution/Codex/DD22/run_2026-10-29/`<br>**153 unique Success** (focused 6/6, full 153, exit 0) | KI-129 | **UNWIRED**<br>(Plan defined in `RPGBossShockwaveAdapters.cpp:92-114`; not in `RPGBossHydrationPreflight.cpp:65-74`, `:143-146`) |
| **`URPGBossStagger`** | `Source/OneBossFight/Player/RPGBossStagger.h:27`<br>**25 authored fields** (`:36`, `:40`, `:44`, `:49`, `:52`, `:56`, `:59`, `:70`, `:73`, `:76`, `:80`, `:83`, `:87`, `:91`, `:129`, `:134`, `:152`, `:155`, `:158`, `:163`, `:166`, `:169`, `:173`, `:184`, `:225`) | **DD10 / DD11**<br>`FRPGStaggerProfileConfig`<br>(`RPGEncounterBinding.h:107-124`)<br>`FRPGBossStaggerScalars`<br>(`RPGBossStaggerPolicyAdapters.h:13-30`)<br>`FRPGStaggerPlan`<br>(`RPGBossStaggerClusterAdapters.h:18-29`) | Adapters: `RPGBossStaggerPolicyAdapters.h/.cpp`, `RPGBossStaggerClusterAdapters.h/.cpp`<br>Tests: `OneBossFight.Binding.StaggerPolicy.Assign`, `Validation`, `Isolation`, `Rejections`<br>(`RPGBossStaggerPolicyAdaptersTests.cpp:184, 274, 363, 426`); `StaggerCluster.Assign`, `Validation`, `Isolation`, `Rejections`<br>(`RPGBossStaggerClusterAdaptersTests.cpp:176, 279, 390, 447`) | Codex X-304 / Claude C-269<br>Folder: `Docs/BossCombatReview/Execution/Codex/DD22/run_2026-10-29/`<br>**153 unique Success** (exit 0) | KI-119, KI-121, KI-123 | **WIRED**<br>(In Preflight: `RPGBossHydrationPreflight.cpp:68`, `:145`; Prep: `RPGBossHydrationPreparation.cpp:246`; Registry: `RPGBossPreparationRegistry.cpp:512`) |

---

## 3. Gap Analysis

### 3.1 Components With No Typed Profile (3 Components)
The following 3 native boss components have no typed authoring struct declared in `RPGEncounterBinding.h`, no adapter implementation, and no dedicated typed adapter test suite:
1. **`URPGBossCloseClipSwap`** (`Source/OneBossFight/Player/RPGBossCloseClipSwap.h:18`, 5 authored fields):
   - Only static rules struct `FRPGBossCloseClipSwapRules` exists in `Source/OneBossFight/Player/RPGBossCloseClipSwapRules.h:12-25`.
   - Test `OneBossFight.Boss.CloseClipSwapRules` tests static pure rules logic, not an encounter-bound component adapter or authoring profile.
2. **`URPGBossDeath`** (`Source/OneBossFight/Player/RPGBossDeath.h:40`, 12 authored fields):
   - Handles dual-mode death behavior (Pack montage vs native clip sequence), ragdoll scheduling, and remains placement.
   - Zero typed configuration records or binding adapters currently exist in the codebase.
3. **`URPGBossLook`** (`Source/OneBossFight/Player/RPGBossLook.h:22`, 5 authored fields):
   - Cosmetic leader-pose attachment component (body mesh, modular pieces, static sword mesh, attachment socket).
   - Zero typed configuration records currently exist in `Source/OneBossFight/Player/RPGEncounterBinding.h`. DD23 Work Order released by Lead Claude in `[C-269]` (source implementation in progress by Codex).

### 3.2 Components Typed But UNWIRED (4 Components)
The following 4 components have complete typed C++ struct definitions and adapter suites in `Source/`, but are NOT wired into the production preflight batch, batch preparation, or reservation registry:
1. **`URPGBossBleed`** (DD19, `FRPGBleedConfig`, 7 fields):
   - Defined in `RPGEncounterBinding.h:139-152` and `RPGBossBleedAdapters.h/.cpp`.
   - Excluded from `RPGBossHydrationPreflight.cpp:65-74` (`MakeBossCorePlans` builds exactly 5 plans; Bleed is omitted) and `:143-146` (`ManagedCoreConsumerClasses` omits Bleed).
2. **`URPGBossLowSweep`** (DD20, `FRPGLowSweepConfig`, 8 fields):
   - Defined in `RPGEncounterBinding.h:155-167` and `RPGBossLowSweepAdapters.h/.cpp`.
   - Excluded from `RPGBossHydrationPreflight.cpp:65-74` and `:143-146`.
3. **`URPGBossShockwave`** (DD21, `FRPGShockwaveConfig`, 8 fields):
   - Defined in `RPGEncounterBinding.h:170-182` and `RPGBossShockwaveAdapters.h/.cpp`.
   - Excluded from `RPGBossHydrationPreflight.cpp:65-74` and `:143-146`.
4. **`URPGBossHealPunish`** (DD22, `FRPGHealPunishConfig`, 14 fields):
   - Defined in `RPGEncounterBinding.h:185-204` and `RPGBossHealPunishAdapters.h/.cpp`.
   - Excluded from `RPGBossHydrationPreflight.cpp:65-74` and `:143-146`.

### 3.3 Components Typed But UNMEASURED (0 Components)
Following the combined DD21+DD22 run verification (Codex X-304 / Claude C-269), **zero** typed profiles remain unmeasured:
- `URPGBossShockwave` (DD21) measured at 6/6 focused and included in full 153/153 unique Success.
- `URPGBossHealPunish` (DD22) measured at 6/6 focused and included in full 153/153 unique Success.

---

## 4. Verification Evidence & Artifact References
- **DD10-DD14 Base Runs:** C-225 to C-231, documented in `Documentation/TEST_PLAN.md:157-161`.
- **DD15-DD16 Batch Preparation Runs:** C-232, X-278, documented in `Documentation/TEST_PLAN.md:162-163`.
- **DD17-DD18 Reservation Registry Run:** X-290, Claude verification in `Docs/BossCombatReview/Execution/Claude/DD18/run_2026-10-28/` (129 unique Success).
- **DD19 Bleed Execution:** Codex X-300 / Claude C-263 in `Docs/BossCombatReview/Execution/Codex/DD19/` (135 unique Success).
- **DD20 LowSweep Execution:** Codex X-301 / Claude C-264 in `Docs/BossCombatReview/Execution/Codex/DD20/` (141 unique Success).
- **DD21+DD22 Combined Execution:** Codex X-304 / Claude C-269 in `Docs/BossCombatReview/Execution/Codex/DD22/run_2026-10-29/` (153 unique Success; focused Shockwave 6/6, focused HealPunish 6/6, full 153/153).
- **DD23 Look Work Order:** Claude C-269 (source handoff in progress).
