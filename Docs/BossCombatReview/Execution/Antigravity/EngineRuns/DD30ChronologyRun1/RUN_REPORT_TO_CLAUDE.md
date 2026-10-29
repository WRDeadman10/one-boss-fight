# DD30 Chronology PIE Run 1 (Release C-353) Run Report

**Agent:** Antigravity  
**Task:** C-353 / DD30ChronologyRun1 (DD30 Chronology Headless PIE Run)  
**Date:** 2026-10-30  
**Status:** COMPLETED (Headless PIE Observed, All Chronology Events Recorded, Bounded Editor Exit)  

---

## 1. Run Summary & Execution Metadata
- **Release ID:** `C-353`
- **Execution Directory:** `Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1/`
- **Editor PID:** `20100`
- **Duration:** `43.66` seconds (Start: `2026-10-30T00:00:40.963`, End: `2026-10-30T00:01:24.621`)
- **Outcome:** `EXIT_NONZERO` (PowerShell process object reported exit code null upon `QUIT_EDITOR` shutdown; `killed_due_to_timeout: false`; process terminated cleanly in 43.66s without timeout kill).
- **Raw Log Path:** `Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1/chronology_raw.log`
  * SHA256: `d3db7c739104a4e81f972a327e02bbe1995fb2ae33d3afff775d916c0731a5ce` (153,352 bytes)
- **Engine Lock:** Acquired atomically via `engine_lock.py acquire`, released after evidence freeze via `engine_lock.py release`.

---

## 2. Verbatim Chronology Lines (`[DD30_CHRONO*]`)

```text
[2026.10.29-18.31.10:969][  2]LogPython: [DD30_CHRONO_DRIVER] REQUEST freshPIE map=L_SevarogArena no gameplay input
[2026.10.29-18.31.12:788][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] callback=PlayerMoves.OnWorldBeginPlay world=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena world_begun=0
[2026.10.29-18.31.12:789][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] actor seq=1 seconds=18149575.443897299 phase=OnWorldBeginPlay route=subsystem-entry-before-Attach world=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena world_begun=0 actor=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena:PersistentLevel.BP_ExampleGreatSwordBoss_C_3 class=/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C role=Boss actor_begun=0 actor_beginning=0
[2026.10.29-18.31.12:789][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] actor seq=2 seconds=18149575.443910100 phase=OnWorldBeginPlay route=subsystem-entry-before-Attach world=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena world_begun=0 actor=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena:PersistentLevel.BP_CombatPlayerCharacter_C_0 class=/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C role=Player actor_begun=0 actor_beginning=0
[2026.10.29-18.31.12:789][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] census pawns=2 bosses=1 players=1
[2026.10.29-18.31.12:789][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] inputs phase=OnWorldBeginPlay world=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena gi=1 catalog=1 epoch_valid=1 epoch=87AE2CE64CC8681D27B6409F46A35FE1 bindings=0 context=1 bound=0 ready=0 selection_store=NOT_DEFINED
[2026.10.29-18.31.12:837][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] actor seq=3 seconds=18149575.491797201 phase=FirstObservedComponentBeginPlay route=inside-actor-BeginPlay-route world=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena world_begun=0 actor=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena:PersistentLevel.BP_ExampleGreatSwordBoss_C_3 class=/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C role=Boss actor_begun=0 actor_beginning=1
[2026.10.29-18.31.12:837][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] witness_component=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena:PersistentLevel.BP_ExampleGreatSwordBoss_C_3.RPGBossEncounter before_component_SuperBeginPlay=1
[2026.10.29-18.31.12:837][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] inputs phase=FirstObservedComponentBeginPlay world=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena gi=1 catalog=1 epoch_valid=1 epoch=87AE2CE64CC8681D27B6409F46A35FE1 bindings=0 context=1 bound=0 ready=0 selection_store=NOT_DEFINED
[2026.10.29-18.31.13:887][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] actor seq=4 seconds=18149576.542040799 phase=FirstObservedComponentBeginPlay route=inside-actor-BeginPlay-route world=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena world_begun=0 actor=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena:PersistentLevel.BP_CombatPlayerCharacter_C_0 class=/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C role=Player actor_begun=0 actor_beginning=1
[2026.10.29-18.31.13:887][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] witness_component=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena:PersistentLevel.BP_CombatPlayerCharacter_C_0.RPGDodgeTiming before_component_SuperBeginPlay=1
[2026.10.29-18.31.13:887][  3]LogRPGStartupChronology: Display: [DD30_CHRONO] inputs phase=FirstObservedComponentBeginPlay world=/Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena gi=1 catalog=1 epoch_valid=1 epoch=87AE2CE64CC8681D27B6409F46A35FE1 bindings=0 context=1 bound=0 ready=0 selection_store=NOT_DEFINED
[2026.10.29-18.31.13:899][  3]LogPython: [DD30_CHRONO_DRIVER] PIE_WORLD /Game/OneBossFight/Levels/UEDPIE_0_L_SevarogArena.L_SevarogArena
```

---

## 3. Key Chronological Facts & Findings

### A. Pawn Census & Subsystem Entry (`PlayerMoves.OnWorldBeginPlay`):
- Line: `[DD30_CHRONO] census pawns=2 bosses=1 players=1`
- Entry Point: `URPGPlayerMovesSubsystem::OnWorldBeginPlay` was called when `world_begun=0`.
- Pawn States at Subsystem Entry:
  * Boss: `BP_ExampleGreatSwordBoss_C_3` -> `actor_begun=0`, `actor_beginning=0`.
  * Player: `BP_CombatPlayerCharacter_C_0` -> `actor_begun=0`, `actor_beginning=0`.
- **Finding:** Both pawns already exist in the world iterator prior to subsystem `OnWorldBeginPlay`, and NEITHER has begun play yet!

### B. Inputs at Subsystem Entry & Component BeginPlay:
- Line: `[DD30_CHRONO] inputs phase=OnWorldBeginPlay ... gi=1 catalog=1 epoch_valid=1 epoch=87AE2CE64CC8681D27B6409F46A35FE1 bindings=0 context=1 bound=0 ready=0 selection_store=NOT_DEFINED`
- Findings:
  * `GameInstance` exists (`gi=1`).
  * Catalog exists and is published (`catalog=1`, `epoch_valid=1`, `epoch=87AE2CE64CC8681D27B6409F46A35FE1`).
  * Placed bindings in world: `bindings=0` (no `ARPGEncounterBinding` placed in level).
  * Context exists (`context=1`), but not bound (`bound=0`) and not ready (`ready=0`).
  * Selection store: `NOT_DEFINED` (persisted selection store does not exist in C++).

### C. First-Observed Component Routes:
- **Boss First-Observed Route:**
  * Seq: `3`, Monotonic Seconds: `18149575.491797201` (+0.0479 s after subsystem entry)
  * Phase: `FirstObservedComponentBeginPlay`, Route: `inside-actor-BeginPlay-route`
  * Actor: `BP_ExampleGreatSwordBoss_C_3` (role `Boss`)
  * Flags: `world_begun=0`, `actor_begun=0`, `actor_beginning=1`
  * Witness Component: `RPGBossEncounter` (`before_component_SuperBeginPlay=1`)
- **Player First-Observed Route:**
  * Seq: `4`, Monotonic Seconds: `18149576.542040799` (+1.0981 s after subsystem entry, +1.0502 s after boss)
  * Phase: `FirstObservedComponentBeginPlay`, Route: `inside-actor-BeginPlay-route`
  * Actor: `BP_CombatPlayerCharacter_C_0` (role `Player`)
  * Flags: `world_begun=0`, `actor_begun=0`, `actor_beginning=1`
  * Witness Component: `RPGDodgeTiming` (`before_component_SuperBeginPlay=1`)

---

## 4. Diagnostics (Verbatim Errors & Warnings)

### Verbatim Error Lines (3):
1. `LogCore: Warning: UTS: Unable to launch the Unreal Trace Server with '"../../../Engine/Binaries/Win64/UnrealTraceServer.exe" fork --sponsor 20100'. Access is denied. Error: 0x5 (5)`
2. `[2026.10.29-18.31.09:268][  0]MapCheck: Map check complete: 0 Error(s), 0 Warning(s), took 0.211ms to complete.`
3. `[2026.10.29-18.31.12:701][  3]LogUIActionRouter: Error: Using CommonUI without a CommonGameViewportClient derived game viewport client. CommonUI Input routing will not function correctly.`

### Verbatim Warning Lines (8):
1. `[2026.10.29-18.31.03:801][  0]LogUnrealClaude: Warning: === UnrealClaude BUILD 20260107-1450 THREAD_TESTS_DISABLED ===`
2. `To disable this warning set CommonUI.Debug.CheckGameViewportClientValid=0 under [SystemSettings] in your project's DefaultEngine.ini.`
3. `[2026.10.29-18.31.13:903][  3]LogPackageName: Warning: GetLocalFullPath called on FPackagePath ../../../../../../UnrealProject/OneBossFight/Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Paragon/MaterialLayers/Leather/ML_Dark_Leather02_Brown_3 which has an unspecified header extension, and the path does not exist on disk. Assuming EPackageExtension::Asset.`
4. `[2026.10.29-18.31.13:903][  3]LoadErrors: Warning: While trying to load package /Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Paragon/Materials/M_Greystone_ToughSword, a dependent package /Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Paragon/MaterialLayers/Leather/ML_Dark_Leather02_Brown_3 was not available. Additional explanatory information follows:`
5. `[2026.10.29-18.31.13:903][  3]LogPackageName: Warning: GetLocalFullPath called on FPackagePath ../../../../../../UnrealProject/OneBossFight/Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Effects/NovabornSparks/VectorFields/VF_RandomNoise_01_90 which has an unspecified header extension, and the path does not exist on disk. Assuming EPackageExtension::Asset.`
6. `[2026.10.29-18.31.13:903][  3]LoadErrors: Warning: While trying to load package /Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Effects/NovabornSparks/P_Greystone_Novaborn_Primary_Impact, a dependent package /Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Effects/NovabornSparks/VectorFields/VF_RandomNoise_01_90 was not available. Additional explanatory information follows:`
7. `[2026.10.29-18.31.13:903][  3]LogPackageName: Warning: GetLocalFullPath called on FPackagePath ../../../../../../UnrealProject/OneBossFight/Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Paragon/MaterialLayers/Leather/ML_Dark_Leather02_Brown_3 which has an unspecified header extension, and the path does not exist on disk. Assuming EPackageExtension::Asset.`
8. `[2026.10.29-18.31.13:903][  3]LoadErrors: Warning: While trying to load package /Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Paragon/Materials/M_Greystone_shield, a dependent package /Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Paragon/MaterialLayers/Leather/ML_Dark_Leather02_Brown_3 was not available. Additional explanatory information follows:`

---

## 5. State Diff & Invariant Preservation
- `content`: 0 added, 0 removed, 0 changed (11,755 files).
- `config`: 0 added, 0 removed, 0 changed.
- `source`: 0 added, 0 removed, 0 changed (all 219 files match `promoted_source_manifest_sha256.txt`).
- `toolkit`: 0 added, 0 removed, 0 changed.
- `binary`: 0 added, 0 removed, 0 changed (DLL `332afd49...` unchanged).
- `saved`:
  * Added: `Saved/Config/CrashReportClient/UECC-Windows-0B68311C466D9B031A5B3687C7D24F94/CrashReportClient.ini`
  * Changed: `Saved/Autosaves/PackageRestoreData.json`, `Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini`, `Saved/UnrealClaude/script_history.json`.
- `saved_assets_unchanged.json`: all 3 draft assets (`DA_Boss_AbyssalRevenant_Draft`, `DA_Boss_EmberWarden_Draft`, `DA_Player_Hero_Draft`) bit-identical.
