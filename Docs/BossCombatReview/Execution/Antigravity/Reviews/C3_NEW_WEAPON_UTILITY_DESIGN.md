# Track C3: "New Weapon" Editor Utility — Design Inputs & Architecture Specification

**Author:** Antigravity (Pair Programming Agent)  
**Lead / Reviewer:** Claude (Boss Combat Lead)  
**Date:** 2026-10-31  
**Task Order:** `[C-473]` (Track C3: Design Inputs for "New Weapon" Utility)  
**Status:** DELIVERED (Read-Only Architectural Specification & Pipeline Mapping)  
**Reference Document:** `Docs/BossCombatReview/Execution/Antigravity/Reviews/C5_WEAPON_DATA_AUDIT.md`  

---

## 1. Executive Summary & Purpose

Following the Track C5 Weapon Data Audit ([C5_WEAPON_DATA_AUDIT.md](file:///C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Reviews/C5_WEAPON_DATA_AUDIT.md)), this document establishes the engineering design inputs for the **Track C3 "New Weapon" Utility** (`new_weapon.py`).

In the One Boss Fight architecture, weapon combat is split across two core layers:
1. **The Pack Combat Execution Layer** (Advanced ARPG Combat Pack): Handles animation montage playback, input buffering, weapon actor attachment, collision sweeps, and upfront stamina deduction.
2. **The Project Combat Data & Tuning Layer** (`URPGCombatCatalog`, `URPGWeaponAttackTable`): Governs build selection (`rpg.Build <Name>`), combat style resolution, per-hit stance break posture damage, custom stamina overrides, status bleed buildup, damage scaling multipliers, and montage hyperarmor windows.

This specification answers four critical architectural requirements:
- **Minimal Designer Data Surface**: Synthesizes the exact data a designer must provide to establish a new weapon.
- **Pack Blueprint Demarcation**: Explicitly delineates which assets are pack Blueprints that **cannot** be generated offline from Python vs. which data assets can be scripted today.
- **Config Schema & Pure Offline Validator**: Proposes a declarative JSON schema and validation rules mirroring `URPGWeaponAttackTable` and `URPGCombatCatalog` C++ constraints.
- **Build $\leftrightarrow$ Style Mapping & PIE Proof**: Explains where the `Build <-> Style` association is defined across the legacy fallback and the data-driven catalog epoch, and defines the automated unattended PIE proof command line.

---

## 2. Minimal Data Required for a New Weapon

A designer adding a new weapon (e.g., Katana, Halberd, Twinblades, Mace) must configure the following data surface:

### 2.1 Weapon Identity & Catalog Metadata
- **`WeaponId`** (`FName`): Unique technical symbol identifying the weapon (e.g. `Katana`, `Twinblade`, `Greatsword`).
- **`HudWeaponWord`** (`FString`): Short designer-facing display label for HUD line presentation (e.g. `"Katana"`, `"Dual Swords"`, `"Claymore"`).
- **`BuildId`** (`FName`): Unique build identifier associated with this weapon (e.g. `KatanaBuild`, `Dex`, `Strength`).
- **`ConsoleName`** (`FString`): Token accepted by the `rpg.Build` console command (e.g. `katana`, `dex`, `strength`).
- **`Aliases`** (`TArray<FString>`): Alternative shorthand tokens accepted by console parser (e.g. `["nodachi", "samurai"]`).
- **`DisplayName`** (`FString`): Full build display name rendered in loadout UI / HUD (e.g. `"Dexterity Katana"`).
- **`UiOrder`** (`int32`): Integer sorting rank in build selection menus.

### 2.2 Pack Weapon Assets (Authored Prerequisites)
The weapon relies on 5 pack-level Blueprint and animation assets that must exist on disk:
1. **Combat Style Asset** (`BP_CombatStyle` DataAsset): Governs player base locomotion overlay AnimBP layer, idle pose, camera distance, and turn rate.
2. **Combat Style Name** (`StyleName` / `FName`): Name of the combat style asset (e.g. `KatanaCombatStyle`), matching `BP_CombatComponent.CurrentCombatStyle`.
3. **Weapon Inventory Item** (`WeaponItem` / `DualWeaponItem` DataAsset): Defines inventory icon, display description, item weight, and equipment slot index (`11` for weapon).
4. **Weapon Actor Blueprint** (`BP_BaseWeapon` subclass): Spawns the visual weapon mesh and trace sockets (`ActiveAttachSocket`) for blade capsule sweeps.
5. **Gameplay Ability Blueprint** (`GA_*_Melee` derived from `GA_Player_MeleeBase_Combined`): Contains `AttackMontages` combo chain array, `Ability_E_Anim_Montage` (strong attack), `ChargedAttack_Montage` (charged attack), and jump attack montages.

### 2.3 Attack Table Tuning Rows (`DA_WeaponAttacks`)
For each supported attack kind (`Light`, `Strong`, `Charged`, `JumpLight`, `JumpHeavy`, `Knockdown`), the designer authors combat numbers in `FRPGWeaponAttackRow`:
- **`PostureDamage`** (`float` $\ge 0.0$): Stance break points subtracted from boss posture pool (e.g. Light = 12.0, Strong = 24.0, JumpHeavy = 35.0).
- **`StaminaCost`** (`float`): Total stamina cost. If $-1.0$, preserves the pack's default cost ($15.0\text{ pt}$ via `GE_MeleeAttackCost`). If positive, `URPGSwingTracker` deducts/refunds the delta `StaminaCost - 15.0`.
- **`BleedBuildup`** (`float` $\ge 0.0$): Status buildup points added to boss bleed pool (e.g. $20.0$ for bleed weapons; $0.0$ for non-bleed).
- **`HealthDamageMultiplier`** (`float` $\ge 0.0$): Multiplier scaling pack base health damage ($1.0$ = neutral pack damage; $0.39$ for starter sword; $> 1.0$ for heavy strikes).
- **`HyperArmorStart` / `HyperArmorEnd`** (`float` in seconds): Active poise immunity window during montage playback ($Start \ge 0.0$ and $End > Start$), or $-1.0$ for no hyperarmor.
- **`Note`** (`FString`): Provenance string (e.g. `"Katana Light 1-4 combo"`).

---

## 3. Scripted Today vs. Pack-Authored Asset Demarcation

An essential principle of the One Boss Fight engineering workflow is avoiding fragile, half-cooked generation of complex assets that Unreal Editor and the pack author more effectively.

### 3.1 Pack Blueprints that CANNOT Be Created from Python / Offline (Stated Plainly)
The following assets **cannot** be generated headlessly from pure Python:
1. **`GA_*_Melee` Gameplay Ability Blueprints**: Inherit from `GA_Player_MeleeBase_Combined`. They contain compiled Kismet bytecode (`FKismetBytecode`), complex event graph node topologies, and montage delegates. Python cannot author Blueprint node networks cleanly.
2. **`BP_*` Weapon Actor Blueprints**: Inherit from `BP_BaseWeapon`. They define actor component hierarchies (`StaticMeshComponent`, particle trail emitters, attach sockets).
3. **`UAnimMontage` Assets**: Contain DCC skeletal animation curve tracks, montage section markers, and timeline-placed `AnimNotifyState` markers (`AnimNotifyState_InputBuffer`, `AN_SetCollisionState`).
4. **`BP_CombatStyle` Data Assets**: Pack-specific data structures holding linked animation blueprint class references (`UAnimInstance`) and camera spring-arm configurations.

> [!IMPORTANT]
> **Designer Prerequisite Rule**:  
> The 5 pack assets listed above must be authored or duplicated in the Unreal Editor / DCC **before** running the weapon scripting utility. A new weapon utility must take these existing asset paths as inputs.

### 3.2 What CAN Be Scripted Today (The Automated Data Layer)
Editor Python scripts (`unreal.EditorAssetLibrary`, `unreal.AssetTools`) and offline validators can author and verify:
1. **Appending Rows to `DA_WeaponAttacks.uasset`**: Reading existing `Rows`, appending new validated `FRPGWeaponAttackRow` entries for `(Weapon, Kind)`, and saving the table without touching other weapons.
2. **Creating `URPGWeaponDefinition` (`DA_Weapon_<Weapon>.uasset`)**: Authoring the data asset wrapping `FRPGCatalogWeapon` with all soft object paths and properties read back.
3. **Creating `URPGBuildDefinition` (`DA_Build_<Weapon>.uasset`)**: Authoring the build data asset wrapping `FRPGCatalogBuild`.
4. **Updating `URPGCombatCatalog` (`DA_CombatCatalog.uasset`)**: Appending the new `WeaponDefinition` and `BuildDefinition` soft references to `Weapons` and `Builds` arrays.
5. **Offline Validation**: Validating the entire JSON specification before editor invocation to guarantee fail-closed execution.

---

## 4. Proposed Weapon Config Schema & Offline Validator

### 4.1 Specification Schema (`new_weapon.json`)

```json
{
  "weapon_id": "Katana",
  "style_name": "KatanaCombatStyle",
  "hud_weapon_word": "Katana",
  "style_asset_path": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/CombatStyles/KatanaCombatStyle.KatanaCombatStyle",
  "item_path": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Items/Weapons/KatanaItem.KatanaItem",
  "item_base_class": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Items/Weapons/WeaponItem.WeaponItem_C",
  "actor_class": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/BP_Katana.BP_Katana_C",
  "ability_class": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_Katana_Melee.GA_Katana_Melee_C",
  "style_aliases": [],
  "actions": ["Light", "Strong", "Charged", "JumpLight", "JumpHeavy", "Knockdown"],
  "build": {
    "build_id": "KatanaBuild",
    "console_name": "Katana",
    "aliases": ["samurai", "nodachi"],
    "display_name": "Dexterity Katana",
    "ui_order": 4
  },
  "attack_rows": [
    {
      "kind": "Light",
      "posture_damage": 12.0,
      "stamina_cost": 12.0,
      "bleed_buildup": 20.0,
      "health_damage_multiplier": 1.0,
      "hyperarmor_start": -1.0,
      "hyperarmor_end": -1.0,
      "note": "Katana standard light strike"
    },
    {
      "kind": "Strong",
      "posture_damage": 22.0,
      "stamina_cost": 25.0,
      "bleed_buildup": 35.0,
      "health_damage_multiplier": 1.15,
      "hyperarmor_start": 0.25,
      "hyperarmor_end": 0.55,
      "note": "Katana thrust with hyperarmor"
    },
    {
      "kind": "Charged",
      "posture_damage": 30.0,
      "stamina_cost": 35.0,
      "bleed_buildup": 50.0,
      "health_damage_multiplier": 1.4,
      "hyperarmor_start": 0.35,
      "hyperarmor_end": 0.85,
      "note": "Katana iaido charged slash"
    },
    {
      "kind": "JumpHeavy",
      "posture_damage": 28.0,
      "stamina_cost": 30.0,
      "bleed_buildup": 30.0,
      "health_damage_multiplier": 1.25,
      "hyperarmor_start": 0.2,
      "hyperarmor_end": 0.6,
      "note": "Katana falling overhead strike"
    },
    {
      "kind": "JumpLight",
      "posture_damage": 10.0,
      "stamina_cost": 15.0,
      "bleed_buildup": 15.0,
      "health_damage_multiplier": 0.9,
      "hyperarmor_start": -1.0,
      "hyperarmor_end": -1.0,
      "note": "Katana aerial slash (pack falling attack)"
    },
    {
      "kind": "Knockdown",
      "posture_damage": 40.0,
      "stamina_cost": 40.0,
      "bleed_buildup": 50.0,
      "health_damage_multiplier": 1.5,
      "hyperarmor_start": 0.1,
      "hyperarmor_end": 0.9,
      "note": "Katana sweep knockdown"
    }
  ]
}
```

### 4.2 Field-by-Field Validation Rules & Failure Tokens

The offline validator (`validate_weapon_config.py`) checks all domain constraints:

| Config Field | Constraint / Domain Invariant | Failure Token |
| :--- | :--- | :--- |
| `weapon_id`, `style_name` | Non-empty alphanumeric string, not `"None"` or empty. | `Weapon.Config.Identity` |
| `hud_weapon_word` | Non-empty string $\le 32$ characters. | `Weapon.Config.Identity` |
| Asset Paths (`*_path`, `*_class`) | Must start with `/Game/`, contain package dot separator (`Package.Asset`). | `Weapon.Config.Path` |
| `build.build_id`, `console_name` | Non-empty string, unique against catalog builds. | `Weapon.Config.Build` |
| `build.ui_order` | Integer $\ge 0$. | `Weapon.Config.Build` |
| `attack_rows` | `Num() >= 1`, unique `kind` per weapon style. Required kinds: `Light`, `Strong`, `Charged`, `JumpHeavy`, `JumpLight`, `Knockdown` (mirrors Strength archetype in `DA_WeaponAttacks`). | `Weapon.Config.AttackCoverage` |
| `posture_damage` | Finite float $\ge 0.0$. | `Weapon.Config.AttackDomain` |
| `stamina_cost` | $-1.0$ (preserve pack) OR finite float $> 0.0$. | `Weapon.Config.AttackDomain` |
| `bleed_buildup` | Finite float $\ge 0.0$. | `Weapon.Config.AttackDomain` |
| `health_damage_multiplier` | Finite float $> 0.0$ (typically $0.1$ to $5.0$). | `Weapon.Config.AttackDomain` |
| `hyperarmor_start`, `end` | Both $-1.0$ (disabled) OR $0.0 \le \text{Start} < \text{End}$. | `Weapon.Config.HyperArmor` |

---

## 5. Build $\leftrightarrow$ Style Mapping & PIE Proof Execution

### 5.1 Where the Build $\leftrightarrow$ Style Mapping is Defined

In the One Boss Fight codebase, build and style resolution exists in two distinct places:

#### 1. Legacy Hardcoded Fallback (`RPGBuildRules.h`)
- **Location**: [RPGBuildRules.h:22-103](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildRules.h#L22-L103)
- **Mechanism**: Hardcodes a static table of 3 builds via RPGBuildRules::Entry() and maps styles via BuildOfStyle():
  * `ERPGBuild::Starter` $\leftrightarrow$ `SwordCombatStyle` (`ToughSword`)
  * `ERPGBuild::Strength` $\leftrightarrow$ `ClaymoreCombatStyle` (`KwangSword`)
  * `ERPGBuild::Dex` $\leftrightarrow$ `DualSwordCombatStyle` (`DualSteelSwords`)
- **Limitation**: Hardcoded C++ enum; cannot accommodate a 4th or 5th weapon without recompiling the project.

#### 2. Primary Data-Driven Epoch Mapping (`RPGCombatCatalog.cpp`)
- **Location**: [RPGCombatCatalog.h:73-102](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.h#L73-L102), [RPGCombatCatalog.cpp:26-75](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L26-L75)
- **Mechanism**:
  1. `URPGCombatCatalogSubsystem` loads `DA_CombatCatalog.uasset` at engine startup and compiles an immutable `FEpoch`.
  2. `FEpoch::Builds` contains `FRPGCatalogBuild` entries, each pointing to a `WeaponId`.
  3. `FEpoch::Weapons` contains `FRPGCatalogWeapon` entries, each defining `StyleName` and `StyleAliases`.
  4. Bidirectional mapping is implemented via:
     * `FEpoch::Matches(FName Style, FName BuildId)` ([RPGCombatCatalog.cpp:40-45](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L40-L45)): Returns true if `Style == Weapon.StyleName` or `Weapon.StyleAliases.Contains(Style)`.
     * `FEpoch::StyleToBuild(FName Style, FName& OutId)` ([RPGCombatCatalog.cpp:46-57](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L46-L57)): Finds which build owns the combat style.
     * `FEpoch::Parse(const FString& Text, FName& OutId)` ([RPGCombatCatalog.cpp:29-39](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L29-L39)): Parses `rpg.Build <Text>` into `BuildId`.
- **Runtime Flow**:
  When a designer registers `DA_Weapon_Katana` and `DA_Build_Katana` in `DA_CombatCatalog`, the game instance subsystem automatically incorporates `rpg.Build Katana` and maps it directly to `KatanaCombatStyle` without touching C++.

### 5.2 Unattended PIE Proof Execution

To prove that a newly authored weapon functions in-game, the designer executes the unattended PIE driver via `run_pie.ps1`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1 `
  -Map "/Game/OneBossFight/FrameworkProof/L_SevarogC1v1FrameworkProof" `
  -OutDir "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\C3\runs\pie_proof" `
  -Task "PIE_NewWeapon_Katana_Proof" `
  -RealBuild Katana `
  -RealSwing "0.0:Light,1.0:Light,2.0:Strong"
```

> [!IMPORTANT]
> **Driver Extension for New Weapons (`REAL_STYLE`)**:  
> In `drive_pie.py`, `-RealBuild` executes `rpg.Build "<ConsoleName>"` via `execute_console_command`. However, the driver currently relies on a static dictionary `REAL_STYLE = {'Starter': 'SwordCombatStyle', 'Strength': 'ClaymoreCombatStyle', 'Dex': 'DualSwordCombatStyle'}` to resolve the expected style (`want`) on `RPGBuildLoadout.get_actual_style_name()`.  
> For a new weapon, `drive_pie.py` must extend `REAL_STYLE` dynamically by querying `URPGCombatCatalogSubsystem` / `FEpoch` or reading the weapon config, mapping `<ConsoleName>` to `StyleName` so the 10-second warmup and attack injection know when the player's weapon equip has completed.

### 5.3 Proof Log Milestones & Verification Signatures
The automated driver inspects `editor_raw.log` for the following verification sequence:
1. **Build Selection**: `build Katana chosen (rpg.Build 'Katana')` from `RPGBuildLoadout.cpp:557`.
2. **Combat Style Equipping**: `SetCurrentCombatStyle: KatanaCombatStyle` from `BP_CombatComponent`.
3. **Player Real Swing Injection**: `LogRPGSwing: REAL swing ... IA_NormalAttack` from `RPGSwingTracker.cpp`.
4. **Hit Intake Row Lookup**: `attack_row weapon=KatanaCombatStyle kind=Light posture=12 bleed=20 found=1` from `RPGHitIntake.cpp:167`.
5. **Boss Damage Intake**: `boss_hit ... damage=... posture=...` from `RPGHitIntake.cpp:538`.
6. **Clean PIE Termination**: `[F3D_RESULT] CompletedWithDamage` from `drive_pie.py`.

---

## 6. Architecture of the `new_weapon.py` Utility

The proposed `new_weapon.py` utility follows the unified single-session pattern proven in `new_boss.py` (Track C1):

```
┌────────────────────────────────────────────────────────┐
│               new_weapon.py <config.json>              │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
  1. Preflight Offline Validation (validate_weapon_config.py)
     - Validate JSON schema, domains, and asset paths
     - Stop immediately on domain or syntax error
                           │
                           ▼
  2. Verify Referenced Pack Assets (in-engine)
     - Verify CombatStyle, WeaponItem, WeaponActor, AbilityClass exist
     - Fail closed if prerequisites are missing
                           │
                           ▼
  3. Author DA_WeaponAttacks Rows
     - Load /Game/OneBossFight/Data/DA_WeaponAttacks
     - Refuse if (Weapon, Kind) rows already exist
     - Append new FRPGWeaponAttackRow entries and save
                           │
                           ▼
  4. Author Catalog Assets & Link
     - Create DA_Weapon_<Id> (URPGWeaponDefinition)
     - Create DA_Build_<Id> (URPGBuildDefinition)
     - Append to DA_CombatCatalog (URPGCombatCatalog) and save
                           │
                           ▼
  5. Read-Back Verification & Summary Output
     - Read back all saved properties from disk
     - Log [NEWWEAPON_SUCCESS] summary payload
```

---

## 7. Next Steps & Implementation Milestones

1. **Deliverable 1**: Architectural design inputs document ([C3_NEW_WEAPON_UTILITY_DESIGN.md](file:///C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Reviews/C3_NEW_WEAPON_UTILITY_DESIGN.md)).
2. **Deliverable 2**: Companion offline re-open test ([test_reopen_c3_weapon_design.py](file:///C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Reviews/test_reopen_c3_weapon_design.py)).
3. **Deliverable 3**: Pinned evidence hash in `evidence_sha256.txt`.
4. **Follow-On Work (Upon Lead Claude Approval)**:
   - Author pure schema validator: `validate_weapon_config.py`.
   - Author example configuration: `example_new_weapon.json`.
   - Author editor script: `new_weapon.py`.
