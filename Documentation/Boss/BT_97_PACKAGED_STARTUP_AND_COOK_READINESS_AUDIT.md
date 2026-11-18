# BT-97: Audit of Packaged Startup and Map Cook Readiness

Date: 2026-11-18 (Asia/Kolkata)
Author: Antigravity (Implementer)
Reviewer: Codex (Tech Lead)
Task ID: BT-97
Status: Complete (Ready for Review)

---

## 1. Executive Summary

Following the successful completion of the Greystone opt-in visual smoke in PIE (`BT-83 Run 4`, receipt `accepted=true`, `result=PASS`), task `BT-97` conducts an independent, read-only architectural audit of the project startup defaults, cook configuration, and dependency closure for the packaged game target on `/Game/OneBossFight/Maps/L_SevarogArena`.

### Key Verdict:
- **Map & GameMode Startup**: **CONFIGURED AT ROOT LEVEL, BUT PACKAGED GREYSTONE GAMEPLAY IS NOT READY OR VERIFIED**. `L_SevarogArena` is the configured `GameDefaultMap`, `BP_AdvancedGameMode` is the `GlobalDefaultGameMode`, and cook directory roots are specified. However:
  - **No Packaged Build Has Been Tested**: Automated PIE visual smoke proves in-editor runtime retargeting only; no packaged build or cook has been executed or verified for Greystone.
  - **Shipping Build Gate**: The test pawn replacement hook and CVar are **completely compiled out of Shipping builds** (`#if !UE_BUILD_SHIPPING` in [RPGPlayerMovesSubsystem.cpp](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp#L116-L121)). A Shipping package will unconditionally spawn the pack mannequin pawn (`BP_CombatPlayerCharacter`).
  - **Development Build Interim Path**: In Development packages, the hook exists but defaults to `0`, requiring explicit runtime parameterization via `-Cvar "rpg.GreystonePlayerTestPawn 1"`.
  - **Alignment with C-1257 Policy**: Per established project decisions (C-1257), the mannequin remains the intentional default player pawn until all Greystone fit gates close (anim notifies/readbacks, paired root-motion distance, combat trace/parry, and Owner video review). Flipping the Shipping default pawn is intentionally gated and must not be altered now.
- **Cook Scope & Transitive Hard References**: `BP_GreystoneERPlayer` is cooked via `+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Player/Greystone")`. Binary uasset analysis proves that primary Greystone assets (`Greystone.uasset`, `Greystone_Skeleton.uasset`, `RTG_CombatMannequin_To_Greystone.uasset`, `IK_Greystone.uasset`, `IK_CombatMannequin.uasset`) are hard-referenced. An explicit top-level cook entry for `/Game/ParagonGreystone` is an **optional, unproven defensive idea** rather than a demonstrated dependency gap.

---

## 2. Startup Defaults & Packaging Configuration

### 2.1 Engine Startup Maps & GameMode
Located in [Config/DefaultEngine.ini](file:///c:/UnrealProject/OneBossFight/Config/DefaultEngine.ini#L1-L7):
```ini
[/Script/EngineSettings.GameMapsSettings]
GameDefaultMap=/Game/OneBossFight/Maps/L_SevarogArena.L_SevarogArena
EditorStartupMap=/Game/OneBossFight/Maps/L_SevarogArena.L_SevarogArena
GlobalDefaultGameMode=/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_AdvancedGameMode.BP_AdvancedGameMode_C
GameInstanceClass=/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_AdvancedGameInstance.BP_AdvancedGameInstance_C
```
- **Evidence**: `L_SevarogArena` is configured as the default startup map. When the standalone game executable launches without map parameters, it targets `L_SevarogArena`.
- **GameMode**: Launches `BP_AdvancedGameMode`, which initializes the combat subsystem and possesses the player pawn.

### 2.2 UAT BuildCookRun Map Scope
Located in [Scripts/Package.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Package.ps1#L60-L68):
```powershell
$Maps = '/Game/OneBossFight/Maps/L_SevarogArena'
& $Uat BuildCookRun `
    "-project=$Project" `
    -platform=Win64 `
    "-clientconfig=$Configuration" `
    -build -cook -stage -pak `
    "-map=$Maps" `
    "-stagingdirectory=$StageDir" `
    -NoP4 -utf8output
```
- **Evidence**: `Package.ps1` explicitly restricts the cooked map scope to `-map=/Game/OneBossFight/Maps/L_SevarogArena`, ensuring extraneous test maps are excluded from staged packages.

---

## 3. Player Pawn & Runtime Retarget Dependency Chain Trace

### 3.1 C++ Test Pawn Replacement Architecture
Located in [Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp#L116-L121):
```cpp
#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarGreystonePlayerTestPawn(
    TEXT("rpg.GreystonePlayerTestPawn"), 0,
    TEXT("Development-only C-1257 test switch: 1 replaces the first spawned pack player pawn with /Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer; 0 keeps the configured mannequin pawn. Not compiled into Shipping."), ECVF_Default);

constexpr TCHAR GreystoneTestPawnClassPath[] = TEXT("/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer.BP_GreystoneERPlayer_C");
#endif
```
And the spawn hook in [RPGPlayerMovesSubsystem.cpp#L441-L449](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp#L441-L449):
```cpp
#if !UE_BUILD_SHIPPING
if (World && World->IsGameWorld() && CVarGreystonePlayerTestPawn.GetValueOnGameThread() != 0
    && bSpawnIsPackPlayer && Actor->GetClass()->GetPathName() != GreystoneTestPawnClassPath)
{
    World->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateUObject(
        this, &URPGPlayerMovesSubsystem::ReplacePackPlayerWithGreystoneForTest, TWeakObjectPtr<APawn>(Cast<APawn>(Actor))));
    return;
}
#endif
```

#### Architectural Impact:
1. **Shipping Builds (`UE_BUILD_SHIPPING`)**:
   - Both `CVarGreystonePlayerTestPawn` and `ReplacePackPlayerWithGreystoneForTest` are completely elided by preprocessor macros.
   - `BP_AdvancedGameMode` spawns its baseline configured pawn: the mannequin `BP_CombatPlayerCharacter`.
   - **Greystone is unreachable in Shipping builds** by design under C-1257 until formal fit gates close.
2. **Development Builds (`!UE_BUILD_SHIPPING`)**:
   - The hook is compiled in, but the CVar default is `0`.
   - Running `Saved/StagedBuilds/Windows/OneBossFight.exe` directly spawns the mannequin.
   - To spawn Greystone in a packaged Development build, the runner must pass `-ExecCmds="rpg.GreystonePlayerTestPawn 1"` (e.g. `.\Scripts\PlayDevBuild.ps1 -Cvar 'rpg.GreystonePlayerTestPawn 1'`).

---

### 3.2 Asset Cook Scope & Reference Traversal

#### Always-Cooked Root:
In [Config/DefaultGame.ini](file:///c:/UnrealProject/OneBossFight/Config/DefaultGame.ini#L52-L53):
```ini
; C-1257 keeps the isolated Greystone child and its wrappers cookable for the post-gate switch smoke; its Development test CVar is compiled out of Shipping and the default pawn is unchanged.
+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Player/Greystone")
```
This forces the UAT cooker to include:
- `BP_GreystoneERPlayer.uasset`
- `ABP_Greystone_RuntimeRetarget.uasset`
- Associated attack montages (`AM_ER_*`)

#### Transitive Dependency Chain:
Direct binary inspection of the uasset import tables confirms hard UObject references:
1. `BP_GreystoneERPlayer.uasset`:
   - Hard imports `/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone` (`SkeletalMeshAsset` property on `GreystoneRuntimeVisual`).
   - Hard imports `/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget` (`AnimClass` property on `GreystoneRuntimeVisual`).
   - Hard imports `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple` (`SkeletalMeshAsset` property on `CharacterMesh0`).
   - Hard imports `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter` (`AnimClass` property on `CharacterMesh0`).
2. `ABP_Greystone_RuntimeRetarget.uasset`:
   - Hard imports `/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton`.
   - Hard imports `/Game/OneBossFight/GreystonePack/RTG_CombatMannequin_To_Greystone`.
3. `RTG_CombatMannequin_To_Greystone.uasset`:
   - Hard imports `/Game/OneBossFight/Characters/Greystone/IK_Greystone`.
   - Hard imports `/Game/OneBossFight/GreystonePack/IK_CombatMannequin`.
   - Hard imports `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin`.

#### Cook Inclusion Assessment:
Because `BP_GreystoneERPlayer` is in `DirectoriesToAlwaysCook`, the cooker traces these hard UProperty/UObject references recursively. Primary meshes, skeletons, retargeter assets, and IK rigs are pulled into the package dependency graph.

---

## 4. Known Unknowns (Verifiable Only by Real Cook/Build)

While static tracing confirms hard reference linkages, the following items can only be proven definitively by an authorized UAT cook and packaged test run:

1. **Greystone Material & Texture Transitive Closure**:
   - Primary meshes are hard-referenced. However, whether all material instances, parent shaders, and textures are fully captured without soft-reference dropouts can only be verified by inspecting a real UAT cook log for `LogCook: Warning: Unable to find package...`.
   - Adding a top-level cook entry for `/Game/ParagonGreystone` remains an unproven, optional defensive consideration unless an actual cook failure demonstrates a missing package.
2. **Runtime IKRig Plugin Loading in Packaged Client**:
   - `ABP_Greystone_RuntimeRetarget` uses native node `AnimNode_RetargetPoseFromMesh`.
   - A real packaged execution must confirm that the `IKRig` runtime plugin initializes without missing module errors in standalone client mode.
3. **Pawn In-Place Replacement Timing in Standalone Window**:
   - In PIE, `SetTimerForNextTick` executes cleanly. In a standalone packaged process (without editor scaffolding, with full window initialization and async shader compilation), empirical execution is required to verify that replacing the pawn on tick 1 produces no camera glitch, input loss, or HUD race condition.
4. **Offline Test Suite Boundary**:
   - The automation test `OneBossFight.Content.CookCoverage` ([RPGAutomationTests.cpp#L1250](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGAutomationTests.cpp)) scans only `Source/OneBossFight`. It does not scan editor modules.

---

## 5. Implementation & Packaging Path

1. **Interim Development Playtest Path**:
   - To test Greystone in a packaged build, package under `Development` configuration:
     ```powershell
     .\Scripts\Package.ps1 -Configuration Development
     ```
   - Launch with the explicit opt-in CVar using [PlayDevBuild.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/PlayDevBuild.ps1):
     ```powershell
     .\Scripts\PlayDevBuild.ps1 -Cvar "rpg.GreystonePlayerTestPawn 1"
     ```
   - If (and only if) UAT cook logs report missing soft-referenced assets in `/Game/ParagonGreystone`, consider evaluating whether an additional cook entry is warranted.
2. **Production / Shipping Alignment (C-1257)**:
   - Shipping builds will continue to spawn the mannequin default pawn.
   - Permanent repointing of the default player pawn to Greystone remains strictly gated by the remaining C-1257 fit gates (paired root motion, combat trace/parry, Owner video review) and must not be altered prematurely.

---

## 6. Verification Status

- **Static Inspection Only**: 0 builds executed, 0 Unreal Editor launches, 0 PIE runs, 0 asset/config mutations, 0 git commits/pushes.
- **Documentation Link Check**:
  ```bash
  python c:\UnrealProject\OneBossFight\Scripts\Tools\check_doc_links.py
  # Result: broken_links=0
  ```
