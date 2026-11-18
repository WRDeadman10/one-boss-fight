# C-1651 Startup Map Audit & Owner Play Guide

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2694]`, Task `BT-173`
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)
- **Status:** COMPLETE (Static source, config, and asset redirector audit confirmed; zero discrepancies found)

---

## 1. Executive Summary & Verification Outcome

Per Lead Codex directive `[X-2694]`, Antigravity performed a comprehensive static audit of project map configuration, engine initialization routes, package launch scripts, and asset redirectors following the full workspace release commit `17291f11`.

- **Audit Result:** **100% PASS.** The canonical arena map `/Game/OneBossFight/Maps/L_SevarogArena` is unambiguously configured as the primary startup and gameplay map across all engine and automation entry points.
- **Legacy Route Safety:** The legacy asset path `/Game/OneBossFight/Levels/L_SevarogArena` is a verified `ObjectRedirector` pointing directly to `/Game/OneBossFight/Maps/L_SevarogArena.L_SevarogArena`. Opening either path in the Unreal Editor resolves to the latest 521 KB map.
- **Entity Identity Confirmation:** The default encounter correctly spawns **Sevarog** against the canonical **Mannequin** player pawn; `EmberWarden` is strictly an offline authoring fixture, and `Greystone` player pawn remains an opt-in experimental Development mode (`rpg.GreystonePlayer 1`).

---

## 2. Static Configuration & Script Routing Audit

### 2.1. Engine & Game Configuration (`Config/`)
- `Config/DefaultEngine.ini` lines 2-4:
  ```ini
  [/Script/EngineSettings.GameMapsSettings]
  GameDefaultMap=/Game/OneBossFight/Maps/L_SevarogArena.L_SevarogArena
  EditorStartupMap=/Game/OneBossFight/Maps/L_SevarogArena.L_SevarogArena
  GlobalDefaultGameMode=/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_AdvancedGameMode.BP_AdvancedGameMode_C
  ```
  Both `GameDefaultMap` (runtime packaged game) and `EditorStartupMap` (Unreal Editor launch) point to `Maps/L_SevarogArena`.

- `Config/DefaultGame.ini` lines 38-40:
  ```ini
  +DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Levels")
  +DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Maps")
  ```
  Both `Maps` and `Levels` directories are registered for cooking to ensure binary assets and redirectors are packaged cleanly.

### 2.2. Package & Automation Scripts (`Scripts/`)
- `Scripts/Package.ps1:59`:
  ```powershell
  $Maps = '/Game/OneBossFight/Maps/L_SevarogArena'
  ```
  Cooks and stages exclusively the latest map.
- `Scripts/PlayDevBuild.ps1:22`:
  ```powershell
  $args2 = @('/Game/OneBossFight/Maps/L_SevarogArena', '-windowed', '-ResX=1920', '-ResY=1080', '-ForceRes', '-nosplash', '-log')
  ```
  Launches the staged Development build directly into `Maps/L_SevarogArena` with sound enabled.
- `Scripts/RunBenchmark.ps1:23`:
  ```powershell
  [string]$Map = '/Game/OneBossFight/Maps/L_SevarogArena'
  ```
  Executes automated benchmark profiling on `Maps/L_SevarogArena`.

---

## 3. Physical Asset & Redirector Analysis

Inspection of physical `.umap` packages on disk:

| Asset Path | Disk Location | File Size | Cryptographic SHA-256 | Internal Object Class & Role |
|---|---|---|---|---|
| `/Game/OneBossFight/Maps/L_SevarogArena` | `Content/OneBossFight/Maps/L_SevarogArena.umap` | **521,767 bytes** | `F5EB4E74421A12D2448D994EB3F31299F2CABBACA2AFD861EE448EE961D56C28` | `UWorld` — The actual, full playable boss duel arena map. |
| `/Game/OneBossFight/Levels/L_SevarogArena` | `Content/OneBossFight/Levels/L_SevarogArena.umap` | **1,521 bytes** | `A6D72E7FD38154747B235BFBF9702487C2F668452A26FE5F5D5555BFAF428DF4` | `UObjectRedirector` -> `/Script/Engine.World'/Game/OneBossFight/Maps/L_SevarogArena.L_SevarogArena'`. |

**Verdict:** There is zero risk of the Owner loading a stale or divergent level by following old documentation referencing `Levels/L_SevarogArena`; the engine redirector transparently resolves to `Maps/L_SevarogArena`.

---

## 4. Boss & Player Entity Routing

1. **Boss Identity (Sevarog vs EmberWarden):**
   - `DA_Boss_EmberWarden_Draft.uasset` is an isolated typed ABI fixture located in `Content/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/`. It is only referenced by offline automated ABI unit tests (`RPGBossAuthoredDraftPreflightTests.cpp`).
   - The active encounter definition (`DA_Sevarog_Framework_Encounter.uasset`) and profile (`DA_Boss_Sevarog_FrameworkProfile_Production.uasset`) explicitly configure **Sevarog** (`ParagonSevarog`).
2. **Player Identity (Mannequin vs Greystone):**
   - By default, the game mode (`BP_AdvancedGameMode`) spawns the canonical Advanced ARPG **Combat Mannequin** (`SKM_CombatMannequin_Simple` with `ABP_CombatCharacter_C`).
   - **Greystone** player pawn (`BP_GreystoneERPlayer`) is an experimental Development-only visual opt-in via CVar `rpg.GreystonePlayer 1` (or `Play_Greystone_Visual_Experimental.bat`). Normal launches retain the Mannequin player until root motion and combat trace gates are formally accepted.

---

## 5. Owner Open & Play Instructions

### Option A: Playing in Unreal Editor (PIE)
1. Open the project in Unreal Editor 5.5 (`-nosound` recommended for editor work).
2. In the **Content Drawer / Content Browser**, navigate to:
   ```text
   Content > OneBossFight > Maps
   ```
3. Double-click **`L_SevarogArena`** to load the arena level.
4. Press the green **Play** button on the main toolbar (or press `Alt + P`) to start Play-in-Editor.
5. Control the player character using standard Soulslike controls (WASD to move, Space to dodge, Left Click to attack, Right Click to block).

### Option B: Playing the Packaged Development Build
1. To play the staged packaged build with **sound ON** and full logging:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Scripts\PlayDevBuild.ps1
   ```
2. Alternatively, run the batch launcher from the staged root:
   ```text
   Saved\StagedBuilds\Windows\Play_Default.bat
   ```
3. The game will launch windowed in 1920x1080 resolution directly into `Maps/L_SevarogArena`.

---

## 6. Strict Discipline Confirmation

- **Zero Asset Modifications:** No `.umap`, `.uasset`, or `.ini` files modified.
- **Zero Unreal Editor Launches:** Static inspection performed via filesystem and parser scripts.
- **Zero Builds or Cooks:** No UAT processes executed.
