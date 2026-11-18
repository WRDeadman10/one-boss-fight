# BT-87: Source-Only Audit of Opt-In Greystone Route Isolation

**Author:** Antigravity (Implementer)
**Date:** 2026-11-17
**Scope:** Source-only isolation and safety verification for `rpg.GreystonePlayerTestPawn` in `L_SevarogArena`.
**Constraint:** Strict source-only audit; 0 builds, 0 Unreal Editor launches, 0 PIE runs, 0 asset/config mutations, 0 git commits/pushes.

---

## 1. Executive Summary

This audit verifies that the opt-in Greystone test pawn route introduced in C-1257 / C-1622 is strictly isolated, fails closed to the canonical mannequin route by default, contains zero persistent disk mutations, and compiles out completely in Shipping configurations.

| Verification Item | Audit Status | Key Evidence |
| :--- | :--- | :--- |
| **CVar Default State** | **PASS (0 / Disabled)** | `TAutoConsoleVariable<int32> CVarGreystonePlayerTestPawn(TEXT("rpg.GreystonePlayerTestPawn"), 0, ...)` |
| **Shipping Exclusion** | **PASS (Compiled Out)** | Enclosed in `#if !UE_BUILD_SHIPPING` at declaration and call sites. |
| **Config Persistence** | **PASS (Zero Entries)** | `Config/DefaultGame.ini` and `Config/DefaultEngine.ini` contain 0 references. |
| **Default Pawn Preservation** | **PASS (Exact Mannequin)** | When CVar == 0, replacement code path is bypassed completely; GameMode spawns default mannequin. |
| **Driver & Runner No-Save** | **PASS (No Saves)** | Driver contains 0 `save_package`/`save_map`/`save_asset` calls; Runner enforces byte-level config hash match. |
| **CVar Cleanup Verification** | **PASS (Real Readback)** | Driver executes `rpg.GreystonePlayerTestPawn 0` and verifies readback == `"0"`. |

---

## 2. Detailed Source-Level Invariants

### 2.1 CVar Declaration & Default Value
- **Source:** [RPGPlayerMovesSubsystem.cpp](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp#L116-L119)
- **Implementation:**
  ```cpp
  #if !UE_BUILD_SHIPPING
  static TAutoConsoleVariable<int32> CVarGreystonePlayerTestPawn(
      TEXT("rpg.GreystonePlayerTestPawn"), 0,
      TEXT("Development-only C-1257 test switch: 1 replaces the first spawned pack player pawn with /Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer; 0 keeps the configured mannequin pawn. Not compiled into Shipping."), ECVF_Default);
  #endif
  ```
- **Finding:** Statically registered with default value `0`. In Shipping builds (`UE_BUILD_SHIPPING=1`), the symbol does not exist.

### 2.2 Gate & Replacement Isolation
- **Source:** [RPGPlayerMovesSubsystem.cpp](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp#L441-L449) and [lines 1010-1019](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp#L1010-L1019)
- **Implementation:**
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
- **Finding:**
  1. The route hook is evaluated only when `CVarGreystonePlayerTestPawn.GetValueOnGameThread() != 0`.
  2. When the CVar is `0` (the default), the hook is skipped, leaving the GameMode-spawned mannequin pawn (`BP_CombatCharacter_C` / `SKM_CombatMannequin_Simple`) in full possession.
  3. Inside `ReplacePackPlayerWithGreystoneForTest`, an immediate re-check (`if (... || CVarGreystonePlayerTestPawn.GetValueOnGameThread() == 0) return;`) provides secondary fail-closed protection.

### 2.3 Configuration Invariants
- **Audit Target:** `Config/DefaultGame.ini`, `Config/DefaultEngine.ini`, `Config/DefaultInput.ini`.
- **Finding:** Zero occurrences of `rpg.GreystonePlayerTestPawn` across all configuration files. The switch is purely memory-resident and runtime-transient.

### 2.4 Smoke Driver & Runner Non-Mutation Discipline
- **Driver:** [pie_greystone_visual_smoke.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_greystone_visual_smoke.py)
  * Sets CVar transiently via `unreal.SystemLibrary.execute_console_command(None, "rpg.GreystonePlayerTestPawn 1")`.
  * Restores CVar in `cleanup()` via `execute_console_command(None, "rpg.GreystonePlayerTestPawn 0")`.
  * Verifies real readback via `unreal.SystemLibrary.get_console_variable_string_value("rpg.GreystonePlayerTestPawn") == "0"`.
  * Never calls any package or asset save API.
- **Runner:** [run_greystone_visual_smoke.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_greystone_visual_smoke.ps1)
  * Verifies `DefaultGame.ini` SHA256 pre-execution.
  * In `finally`, verifies `DefaultGame.ini` SHA256 matches `$originalConfigHash` before releasing locks; if modified or unreadable, locks are retained and `RECOVERY_NEEDED` is reported without auto-overwrite.

---

## 3. Relevant Canonical Source Hashes (SHA256)

| Component | Path | SHA256 Hash |
| :--- | :--- | :--- |
| `runner` | `Scripts/Editor/run_greystone_visual_smoke.ps1` | `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F` |
| `driver` | `Scripts/Editor/pie_greystone_visual_smoke.py` | `68CF485F54858B943A5D7B1DE2D209768898E0F143B79E550D06B35836EB4AF1` |
| `retarget_cpp` | `Source/OneBossFightEditor/Private/RPGGreystoneRuntimeRetargetLibrary.cpp` | `22A04C1A5B12AAC1A045EC33AB2E346064D55FBABA83FA5E25FA2E749C5778AF` |
| `moves_cpp` | `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp` | `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838` |

---

## 4. Conclusion & Blockers

- **Route Isolation Status:** **CLEAN / VERIFIED**.
- **Blockers:** Zero source-level blockers.
- **Runtime Block:** As documented, any execution of `BT-83` remains strictly gated on fresh Owner approval bound to the updated runner hash `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F`.
