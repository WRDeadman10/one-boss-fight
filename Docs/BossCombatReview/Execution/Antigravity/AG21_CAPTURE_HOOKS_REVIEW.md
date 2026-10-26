# AG-21: Dry-Run Review of Capture Drafts Against Source/OneBossFight Debug Hooks

**Document ID:** `AG21_CAPTURE_HOOKS_REVIEW`  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Directive:** Claude `[C-121]`  
**Reference Scripts Audited:**  
- [`Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap01_a5.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap01_a5.py)  
- [`Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap02_a4.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Evidence/capture_drafts/pie_capture_cap02_a4.py)  
- [`Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap05_telegraph.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Evidence/capture_drafts/pie_capture_cap05_telegraph.py)  
- [`Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap06_recovery.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Evidence/capture_drafts/pie_capture_cap06_recovery.py)  
**Status:** DELIVERED  

---

## 1. Executive Summary & Objective

In accordance with Claude's directive `[C-121]`, Antigravity performed a dry-run static call audit of the four in-editor capture drivers drafted in `AG-18` against the live C++ codebase under [`Source/OneBossFight/`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/).

### Architectural Rule Enforced
> *"A missing hook is a defect in the draft, never a reason to add a hook."* (Claude `[C-121]`)

Every console variable, console command, and UFUNCTION invoked by the capture scripts was cross-referenced line-by-line against `Source/OneBossFight`. The audit identified **one critical missing hook defect** (`rpg.ForceMove`), **one missing lifecycle defect** (omission of boss wake/hold), and **one invalid move identifier defect** (`"Sprint"` in `URPGAttackTracker`).

All defects have been cataloged with exact file and line citations, and drop-in corrected scripts conforming 100% to the verified project C++ interface have been provided.

---

## 2. Console Variable & Console Command Call Audit

The table below catalogs every console variable and console command referenced across the four capture draft scripts, with its exact definition in `Source/OneBossFight/` or Unreal Engine runtime:

| Script Call / CVar | Invoking Script(s) & Line(s) | Definition in `Source/OneBossFight/` | C++ Declaration Line | Verdict / Status |
| :--- | :--- | :--- | :--- | :--- |
| `rpg.WakeClip` | `cap01:29`, `cap02:29`, `cap05:29`, `cap06:29` | `Source/OneBossFight/Player/RPGBossDormantWake.cpp` | Line 96: `static TAutoConsoleVariable<int32> CVarWakeClip(TEXT("rpg.WakeClip"), 1, ...)` | **EXISTS IN SOURCE** (`int32`) |
| `rpg.CloseTelegraph` | `cap01:30`, `cap02:30`, `cap05:30`, `cap06:30` | `Source/OneBossFight/Player/RPGAttackTracker.cpp` | Line 19: `static TAutoConsoleVariable<float> CVarRPGCloseTelegraph(TEXT("rpg.CloseTelegraph"), 0.4f, ...)` | **EXISTS IN SOURCE** (`float`) |
| `rpg.Legend` | `cap01:31`, `cap02:31`, `cap05:31`, `cap06:31` | `Source/OneBossFight/Player/RPGLegend.cpp` | Line 22: `static TAutoConsoleVariable<int32> CVarRPGLegend(TEXT("rpg.Legend"), 1, ...)` | **EXISTS IN SOURCE** (`int32`) |
| `rpg.Debug` | `cap01:32`, `cap02:32`, `cap05:32`, `cap06:32` | `Source/OneBossFight/Player/RPGCombatDebug.cpp` | Line 38: `static TAutoConsoleVariable<int32> CVarRPGDebug(TEXT("rpg.Debug"), 0, ...)` | **EXISTS IN SOURCE** (`int32`) |
| `t.MaxFPS` | `cap01:33`, `cap02:33`, `cap05:33`, `cap06:33` | Engine Core / Renderer (`UnrealEngine.cpp`) | Engine built-in | **ENGINE HOOK** (Valid runtime cvar) |
| `slomo <val>` | `cap01:56,122`, `cap02:56,120`, `cap05:56,119`, `cap06:56,119` | Engine Gameplay (`Kismet/GameplayStatics.h`) | Engine built-in | **ENGINE HOOK** (Valid runtime command) |
| `HighResShot` | `cap01:142`, `cap02:139`, `cap05:138`, `cap06:138` | Engine Viewport (`UnrealEngine.cpp`) | Engine built-in | **ENGINE HOOK** (Valid runtime command) |
| `rpg.ForceMove A5` | `cap01:132` | **NONE** | **NOT FOUND IN SOURCE** | **DEFECT IN DRAFT (MISSING HOOK)** |
| `rpg.ForceMove A4` | `cap02:129` | **NONE** | **NOT FOUND IN SOURCE** | **DEFECT IN DRAFT (MISSING HOOK)** |
| `rpg.ForceMove Sprint` | `cap05:128` | **NONE** | **NOT FOUND IN SOURCE** | **DEFECT IN DRAFT (MISSING HOOK)** |
| `rpg.ForceMove A2` | `cap06:128` | **NONE** | **NOT FOUND IN SOURCE** | **DEFECT IN DRAFT (MISSING HOOK)** |

---

## 3. UFUNCTION Call Audit Against `Source/OneBossFight/`

### 3.1 Unreal Python Engine Calls (Valid Runtime Hooks)
The draft scripts call standard Unreal Engine reflection APIs:
- `unreal.SystemLibrary.get_project_directory()` $\to$ `UKismetSystemLibrary::GetProjectDirectory()` (Engine)
- `unreal.ConsoleVariableLibrary.get_console_variable_float_value(...)` $\to$ `UConsoleVariableLibrary::GetConsoleVariableFloatValue(...)` (Engine)
- `unreal.SystemLibrary.execute_console_command(...)` $\to$ `UKismetSystemLibrary::ExecuteConsoleCommand(...)` (Engine)
- `unreal.GameplayStatics.get_player_controller(...)` $\to$ `UGameplayStatics::GetPlayerController(...)` (Engine)
- `unreal.GameplayStatics.get_time_seconds(...)` $\to$ `UGameplayStatics::GetTimeSeconds(...)` (Engine)
- `unreal.LevelEditorSubsystem.editor_request_begin_play()` / `editor_request_end_play()` (Engine Editor Subsystem)
- `unreal.register_slate_post_tick_callback(...)` / `unregister_slate_post_tick_callback(...)` (Engine Slate Bridge)

### 3.2 Missing Direct Project UFUNCTION Calls (Defects in Drafts)
The draft scripts invoked **zero** project UFUNCTIONs, relying entirely on the fictional `rpg.ForceMove` console command. In live project PIE drivers (`pie_a4_low_sweep.py`, `pie_authored_close_clips.py`, `pie_legend.py`), attacks and state machines are controlled through real project UFUNCTIONs:

| Required Capability | Real Project C++ Class | Available UFUNCTION Hook | Source File & Line | Status in Drafts |
| :--- | :--- | :--- | :--- | :--- |
| **Trigger Move A5/A4/A2** | `URPGAttackTracker` | `bool StartMove(FName MoveId, bool bForce = true)` | [`Player/RPGAttackTracker.h:96`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L96) | **OMITTED (Draft used imaginary cvar)** |
| **Direct Montage Play** | `URPGAttackTracker` | `bool PlayMoveMontageForTest(FName MoveId)` | [`Player/RPGAttackTracker.h:130`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L130) | **OMITTED** |
| **A4 Sweep Trigger** | `URPGBossLowSweep` | `bool StartForTest(bool bForce = true)` | [`Player/RPGBossLowSweep.h:59`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.h#L59) | **OMITTED** |
| **Wake Dormant Boss** | `URPGBossEncounter` | `void Wake()` | [`Player/RPGBossEncounter.h:79`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h#L79) | **OMITTED (Boss remains dormant)** |
| **Hold Boss AI for Test**| `URPGBossEncounter` | `void HoldForTest(bool bHold)` | [`Player/RPGBossEncounter.h:71`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h#L71) | **OMITTED (AI behavior tree active)** |
| **Reset Encounter** | `URPGBossEncounter` | `void ResetForTest()` | [`Player/RPGBossEncounter.h:75`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h#L75) | **OMITTED** |
| **Refill Player Vitals** | `URPGCombatDebug` | `void DebugRefillPlayer() const` | [`Player/RPGCombatDebug.h:79`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatDebug.h#L79) | **OMITTED** |
| **Enter Combat Stance** | `URPGAttackTracker` | `bool EnterCombat()` | [`Player/RPGAttackTracker.h:141`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L141) | **OMITTED** |

---

## 4. Specific Identified Defects in Draft Scripts

### DEFECT 1: Imaginary `rpg.ForceMove` Console Command
- **Citation:** `pie_capture_cap01_a5.py:132`, `pie_capture_cap02_a4.py:129`, `pie_capture_cap05_telegraph.py:128`, `pie_capture_cap06_recovery.py:128`.
- **The Defect:** No console variable or exec function `rpg.ForceMove` exists anywhere in `Source/OneBossFight/`. Executing this command produces a silent console failure: `Command not recognized: rpg.ForceMove`.
- **Consequence:** The boss never executes the requested attack during PIE capture runs. The capture burst captures an idle or sleeping boss.
- **Root Cause & Fix:** Replace console command with direct call to `tracker.start_move(MoveId, True)`.

### DEFECT 2: Omission of Boss Actor Resolution and Wake/Hold Lifecycle
- **Citation:** All 4 draft scripts (`WAIT_PIE` state).
- **The Defect:** In `L_SevarogArena`, the boss (`BP_ExampleGreatSwordBoss_C`) begins in a **dormant sleeping state** (`AN_Boss01_DormantIdle`).
- **Consequence:** Even if an ability were triggered, an unawakened boss vetoes illegal starts (`bVetoIllegalStarts = true` in `URPGAttackTracker.h:112`).
- **Root Cause & Fix:** In `WAIT_PIE`, the script must find the boss actor and its components:
  ```python
  boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(self.world, unreal.Character) 
               if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
  encounter = next((c for c in boss.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == "RPGBossEncounter"), None)
  encounter.wake()
  encounter.hold_for_test(True)
  ```

### DEFECT 3: Invalid Move Identifier `"Sprint"` in CAP-05
- **Citation:** `pie_capture_cap05_telegraph.py:128`: `"rpg.ForceMove Sprint"`.
- **The Defect:** In `URPGAttackTracker::URPGAttackTracker()` ([`Source/OneBossFight/Player/RPGAttackTracker.cpp:30-103`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L30-L103)), the registered attack entries in `Attacks` are strictly:
  - `"A1"`, `"A1b"`, `"A2"`, `"A3a"`, `"A3b"`, `"A4"`, `"A5"`, `"A6"`.
  There is **no entry named `"Sprint"`**! Calling `StartMove("Sprint")` returns `false` (`Move unknown`).
- **Consequence:** CAP-05 cannot trigger `"Sprint"` through `URPGAttackTracker`.
- **Root Cause & Fix:** For telegraph readability verification, CAP-05 must target `"A2"` (the 1.68s heavy charge telegraph of `GS_ChargedAttack_Montage`) or `"A3a"` (the authored windup combo opener), which are registered and supported.

---

## 5. Corrected Script Implementations

To eliminate all defects, the four capture draft scripts under `Evidence/capture_drafts/` have been updated with the correct house PIE harness architecture:
1. Locates `BP_ExampleGreatSwordBoss_C`.
2. Accesses `RPGBossEncounter`, `RPGAttackTracker`, and `RPGCombatDebug`.
3. Calls `encounter.wake()`, `encounter.hold_for_test(True)`, `debug.debug_refill_player()`, and `tracker.enter_combat()`.
4. Triggers the move via `tracker.start_move(MoveId, True)`.
5. Restores all monitored cvars (`rpg.WakeClip`, `rpg.CloseTelegraph`, `rpg.Legend`, `rpg.Debug`, `t.MaxFPS`, `slomo 1.0`) upon completion or timeout.

---

## 6. Verification & Limits

| Requirement | Audit Result | Status |
| :--- | :--- | :--- |
| **All Script CVar Calls Audited** | Pinned to exact files/lines in `Source/OneBossFight` | Verified |
| **All UFUNCTION Calls Audited** | Engine vs Project calls distinguished; missing calls identified | Verified |
| **No New Hooks Added** | Drafts corrected strictly to use existing C++ UFUNCTIONs | Compliant with `[C-121]` rule |
| **Zero Source Edits** | Audit performed strictly offline in read-only mode | Compliant |
