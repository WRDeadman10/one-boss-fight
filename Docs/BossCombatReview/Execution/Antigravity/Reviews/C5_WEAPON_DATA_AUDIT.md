# Track C5: Weapon Data Audit — Hardcoded vs Data-Driven Inventory

> **Document Context**:  
> - **Slice / Roadmap Track**: Track C5 (pre-requisite for Track C3: Editor Utility "New Weapon")  
> - **Lead Order**: Claude `[C-452]` (2026-10-31)  
> - **Author**: Antigravity  
> - **Review Target**: Complete offline audit of weapon data across pack assets and project C++ code  
> - **Test Suite Companion**: `Docs/BossCombatReview/Execution/Antigravity/Reviews/test_reopen_c5_weapon_data_audit.py`

---

## 1. Executive Summary

This audit establishes the boundary between **Data-Driven** weapon parameters (authored in primary data assets and editable by designers without recompilation) and **Hardcoded** values (compiled into C++ classes, Blueprint graphs, or Gameplay Effects) across the Advanced ARPG Combat Pack and the One Boss Fight project.

### Core Architecture Findings
1. **Catalog Definition Layer (`URPGCombatCatalog`, `URPGWeaponDefinition`)**:
   - Weapon identities, asset references, and UI labels are **Data-Driven** in `Content/OneBossFight/Data/Catalog/` (`DA_Weapon_Sword.uasset`, `DA_Weapon_Claymore.uasset`, `DA_Weapon_DualSwords.uasset`).
   - However, the C++ catalog implementation maintains hardcoded fallbacks and legacy mappings in `Source/OneBossFight/Player/RPGCombatCatalog.cpp:88-125`.
2. **Combat Tuning Layer (`URPGWeaponAttackTable`, `DA_WeaponAttacks`)**:
   - Stance break posture damage, custom stamina costs, bleed buildup, damage scaling multipliers, and hyperarmor windows are **Data-Driven** in `Content/OneBossFight/Data/DA_WeaponAttacks.uasset`.
   - However, `URPGWeaponAttackTable::FillDefaults()` in `Source/OneBossFight/Player/RPGWeaponAttackTable.cpp:37-77` hardcodes starting values for Strength (`ClaymoreCombatStyle`, `SwordCombatStyle`) and Dexterity (`DualSwordCombatStyle`, `TwinbladeCombatStyle`), including a hardcoded `0.39f` health damage multiplier for `SwordCombatStyle` and hardcoded hyperarmor windows.
3. **Pack Gameplay Ability Layer (`GA_Player_MeleeBase_Combined`, `GA_*_Melee`)**:
   - Combo montage chains (`AttackMontages`, `StrongAttackMontages`, `ChargedAttackMontages`) are **Data-Driven** within derived Blueprint abilities (`GA_Sword_Melee.uasset`, `GA_Claymore_Melee.uasset`, `GA_DuaSword_Melee.uasset`).
   - Melee stamina consumption is **Hardcoded** in the pack's `GE_MeleeAttackCost.uasset` (literal `-15.0f` at byte offset `0x1bc6`), requiring `URPGSwingTracker` to apply post-hoc differential adjustments via `StaminaExtra`.
   - Attack power enums and poise damage defaults are defined in `BP_AttackData.uasset` (`PoiseDamage = 20.0f` at byte offset `0x86c`), while actual damage calculations execute through `GE_MeleeDamage.uasset`.
4. **Equipment & Slot Wiring**:
   - The weapon equipment slot is hardcoded as enum index 11 (`constexpr int32 WeaponSlotEnumerator = 11` in `Source/OneBossFight/Player/RPGBuildRules.h:27`). `URPGBuildLoadout.cpp:123` dynamically resolves this against `E_EquipSlots` at runtime.

---

## 2. Comprehensive Weapon Parameter Inventory Table

| Weapon Value / Parameter | Storage Location (Asset or C++ File:Line) | Type | Consumer / Architecture Role | Evidence Citation (Line / Byte Offset) |
|---|---|---|---|---|
| **Weapon Identifier** (`WeaponId`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.WeaponId`) | Data-Driven | `RPGCombatCatalog`, `RPGBuildLoadout` build matching | `RPGCombatCatalog.h:16`; `DA_Weapon_Sword.uasset` @ `0xd7a` (`Sword`), `DA_Weapon_Claymore.uasset` @ `0xd46` (`Claymore`) |
| **Combat Style Name** (`StyleName`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.StyleName`) | Data-Driven | Matched against `BP_CombatComponent.CurrentCombatStyle` | `RPGCombatCatalog.h:17`; `DA_Weapon_Claymore.uasset` @ `0x459` (`ClaymoreCombatStyle`) |
| **Combat Style Asset** (`StyleAsset`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.StyleAsset`) | Data-Driven | Pack style loading, camera and anim layer binding | `RPGCombatCatalog.h:18`; `DA_Weapon_Claymore.uasset` @ `0x239` (`ClaymoreCombatStyle`) |
| **Inventory Item Path** (`ItemPath`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.ItemPath`) | Data-Driven | `URPGBuildLoadout::CallEquip` via `Update Equip Slot Item` | `RPGCombatCatalog.h:19`; `DA_Weapon_Claymore.uasset` @ `0x1e2` (`KwangSword`), `DA_Weapon_Sword.uasset` @ `0x1df` (`ToughSword`) |
| **Item Base Class** (`ItemBaseClass`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.ItemBaseClass`) | Data-Driven | Type validation (`WeaponItem` vs `DualWeaponItem`) | `RPGCombatCatalog.h:20`; `DA_Weapon_DualSwords.uasset` @ `0x17e` (`DualWeaponItem`) |
| **Weapon Actor Class** (`ActorClass`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.ActorClass`) | Data-Driven | Preflight and verification of spawned weapon actor | `RPGCombatCatalog.h:21`; `DA_Weapon_Claymore.uasset` @ `0x29c` (`BP_KwangSword`), `DA_Weapon_Sword.uasset` @ `0x2ee` (`BP_ToughSword`) |
| **Gameplay Ability Class** (`AbilityClass`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.AbilityClass`) | Data-Driven | Melee ability binding to input | `RPGCombatCatalog.h:22`; `DA_Weapon_Claymore.uasset` @ `0x30b` (`GA_Claymore_Melee`), `DA_Weapon_Sword.uasset` @ `0x236` (`GA_Sword_Melee`) |
| **HUD Display Word** (`HudWeaponWord`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.HudWeaponWord`) | Data-Driven | `GetBuildLine()`, `RPGBuildSelect` UI text | `RPGCombatCatalog.h:23`; `DA_Weapon_Sword.uasset` @ `0xdf6` (`Sword`), `DA_Weapon_DualSwords.uasset` @ `0xdc4` (`Dual Swords`) |
| **Style Aliases** (`StyleAliases`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.StyleAliases`) | Data-Driven | Allows auxiliary styles (e.g. `SwordAndShieldCombatStyle`) | `RPGCombatCatalog.h:24`; `DA_Weapon_Sword.uasset` @ `0x6be` (`SwordAndShieldCombatStyle`) |
| **Supported Actions** (`Actions`) | `DA_Weapon_*.uasset` (`FRPGCatalogWeapon.Actions`) | Data-Driven | Catalog coverage validation against attack table | `RPGCombatCatalog.h:27`; `DA_Weapon_Sword.uasset` @ `0x3dd` (`Actions`) |
| **Attack Table Asset Path** | C++ macro `URPGWeaponAttackTable::AssetPath()` | Hardcoded | Path to `/Game/OneBossFight/Data/DA_WeaponAttacks` | `Source/OneBossFight/Player/RPGWeaponAttackTable.h:84` |
| **Attack Table Fallback Row** | `URPGWeaponAttackTable::FillDefaults()` | Hardcoded | Default poise 20.f, stamina -1.f, bleed 0.f | `Source/OneBossFight/Player/RPGWeaponAttackTable.cpp:39` |
| **Strength Posture Damage** | `DA_WeaponAttacks.uasset` / `FillDefaults()` | Both (Data + C++ default) | Stance break drain (Light 18, Strong 30, Heavy 38) | `DA_WeaponAttacks.uasset` @ `0x3bb`; `RPGWeaponAttackTable.cpp:45, 52` |
| **Dexterity Posture Damage** | `DA_WeaponAttacks.uasset` / `FillDefaults()` | Both (Data + C++ default) | Stance break drain (Light 6, Strong 10, Heavy 14) | `DA_WeaponAttacks.uasset` @ `0x3bb`; `RPGWeaponAttackTable.cpp:70-74` |
| **Health Damage Multiplier** | `DA_WeaponAttacks.uasset` / `FillDefaults()` | Both (Data + C++ default) | Scaler adjustment (0.39f for starter sword, 1.0f others) | `DA_WeaponAttacks.uasset` @ `0x3d1`; `RPGWeaponAttackTable.cpp:64` |
| **Pack Melee Stamina Baseline** | Pack `GE_MeleeAttackCost.uasset` | Hardcoded Asset | Pack upfront deduction (-15.0f per melee swing) | `GE_MeleeAttackCost.uasset` @ `0x1bc6` (float `-15.0f`) |
| **Assumed Pack Stamina Cost** | `RPGSwingTracker.cpp` C++ constant | Hardcoded | Baseline subtracted before `StaminaCost` delta | `Source/OneBossFight/Player/RPGSwingTracker.cpp:22` (`StaminaTag`), `RPGSwingTracker.cpp:259` |
| **Strength Stamina Cost** | `DA_WeaponAttacks.uasset` / `FillDefaults()` | Both (Data + C++ default) | 35.f per heavy swing for Claymore (-1.f starter) | `DA_WeaponAttacks.uasset` @ `0x3f9`; `RPGWeaponAttackTable.cpp:44` |
| **Dexterity Stamina Cost** | `DA_WeaponAttacks.uasset` / `FillDefaults()` | Both (Data + C++ default) | 10.f per swing for Dual Swords / Twinblades | `DA_WeaponAttacks.uasset` @ `0x3f9`; `RPGWeaponAttackTable.cpp:70-74` |
| **Dexterity Bleed Buildup** | `DA_WeaponAttacks.uasset` / `FillDefaults()` | Both (Data + C++ default) | 20.f status buildup applied to `URPGBossBleed` | `DA_WeaponAttacks.uasset` @ `0x1a5`; `RPGWeaponAttackTable.cpp:70-74`; `RPGHitIntake.cpp:546` |
| **Strength HyperArmor Windows** | `DA_WeaponAttacks.uasset` / `FillDefaults()` / `set_weapon_windows.py` | Both (Data + C++ default) | Active window: Strong/Jump (0.352-0.618s), Charged (0.423-1.005s) | `DA_WeaponAttacks.uasset` @ `0x342`, `0x32c`; `RPGWeaponAttackTable.cpp:54-58`; `set_weapon_windows.py:15` |
| **Weapon Equipment Slot Index** | `RPGBuildRules.h` `WeaponSlotEnumerator` | Hardcoded | Indexes weapon equip slot in `BP_EquipmentComponent` | `Source/OneBossFight/Player/RPGBuildRules.h:27` (`WeaponSlotEnumerator = 11`) |
| **Weapon Loadout Startup Delay** | `RPGBuildLoadout.h` `StartupDelaySeconds` | Hardcoded C++ (Configurable UPROPERTY) | Delay before applying initial build weapon (1.0s) | `Source/OneBossFight/Player/RPGBuildLoadout.h:40` |
| **Combo Chain Montages** | Derived `GA_*_Melee.uasset` (`AttackMontages`) | Data-Driven | Sequenced light attack montages A -> B -> C -> D | `GA_Claymore_Melee.uasset` @ `0x39c`; `GA_DuaSword_Melee.uasset` @ `0x3a0` |
| **Strong / Charged Montages** | Derived `GA_*_Melee.uasset` | Data-Driven | `Ability_E_Anim_Montage`, `ChargedAttack_Montage` | `GA_Claymore_Melee.uasset` @ `0x645`, `0x44d` |
| **Combo Chain Reset Time** | `GA_Player_MeleeBase_Combined.uasset` (`ResetAttackTime`) | Blueprint Property | Cadence window before combo index resets to 0 | `GA_Player_MeleeBase_Combined.uasset` (Blueprint variable) |
| **Input Buffer Window** | Montage Notify States (`AnimNotifyState_InputBuffer`) | Data-Driven (Anim Asset) | Queues successive attacks in `BP_InputBufferComponent` | `GA_Player_MeleeBase_Combined.uasset` (`InputBufferComponent`) |
| **Weapon Trace Sockets** | Weapon Static/Skeletal Mesh (`ActiveAttachSocket`) | Data-Driven | Sweep trace line from Start Socket to End Socket | `ToughSword.uasset` @ `0xb61` (`ActiveAttachSocket`) |
| **Pack Poise Damage Default** | `BP_AttackData.uasset` (`PoiseDamage`) | Hardcoded Asset | Default poise damage before project posture table | `BP_AttackData.uasset` @ `0x86c` (`PoiseDamage`) |

---

## 3. Architectural Breakdown by Subsystem

### 3.1 Combat Catalog Layer (`URPGCombatCatalog`, `URPGWeaponDefinition`)
- **Location**: `Source/OneBossFight/Player/RPGCombatCatalog.h:13-68`
- **Data Assets**: `Content/OneBossFight/Data/Catalog/DA_CombatCatalog.uasset` points to `DA_Weapon_Sword.uasset`, `DA_Weapon_Claymore.uasset`, and `DA_Weapon_DualSwords.uasset`.
- **Runtime Consumer**: `URPGCombatCatalogSubsystem` (GameInstance subsystem) compiles an immutable `FEpoch` at engine startup. When `rpg.Build` changes, `URPGBuildLoadout::SetBuild` queries `FEpoch::Weapon(WeaponId)` to retrieve the `ItemPath` and `StyleName`.
- **Hardcoding Risk**: `RPGCombatRegistry::Legacy()` in `Source/OneBossFight/Player/RPGCombatCatalog.cpp:88-125` hardcodes string paths and parameters for Starter, Strength, and Dex builds as a fallback if the primary asset is absent.

### 3.2 Weapon Attack Table (`URPGWeaponAttackTable`, `DA_WeaponAttacks`)
- **Location**: `Source/OneBossFight/Player/RPGWeaponAttackTable.h:15-86`
- **Data Asset**: `Content/OneBossFight/Data/DA_WeaponAttacks.uasset` contains 24 structured rows (4 weapons × 6 attack kinds).
- **Runtime Consumers**:
  1. `URPGHitIntake::ProcessPending()` (`Source/OneBossFight/Player/RPGHitIntake.cpp:167, 538, 546`): Looks up `(CurrentCombatStyle, AttackKind)`. If found, extracts `PostureDamage` (forwarded to `URPGBossPosture::ApplyPostureDamage`) and `BleedBuildup` (forwarded to `URPGBossBleed::AddBuildup`).
  2. `URPGSwingTracker::RecordSwing()` (`Source/OneBossFight/Player/RPGSwingTracker.cpp:59, 282`): Extracts `StaminaCost` and calculates `StaminaExtra = Wanted - 15.0f`. Also extracts `HyperArmorStart` / `HyperArmorEnd` to grant temporary poise immunity during montage playback.
- **Hardcoding Risk**: `URPGWeaponAttackTable::FillDefaults()` in `Source/OneBossFight/Player/RPGWeaponAttackTable.cpp:37-77` hardcodes the exact values for Claymore, Sword, DualSwords, and Twinblades. If a new weapon is introduced in data, but no row is added to `DA_WeaponAttacks.uasset`, it silently falls back to `Fallback` (poise 20.f, stamina -1.f, bleed 0.f).

### 3.3 Pack Gameplay Abilities & Timing
- **Base Class**: `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_Player_MeleeBase_Combined.uasset`
- **Derived Weapon Abilities**:
  - `GA_Sword_Melee.uasset` (1-Handed sword combo)
  - `GA_Claymore_Melee.uasset` (2-Handed heavy claymore combo)
  - `GA_DuaSword_Melee.uasset` (Dual-wielding fast combo)
- **Combo Sequence Execution**:
  - The base ability tracks `CurrentAttackIndex`. On each trigger, it fetches `AttackMontages[CurrentAttackIndex]`, increments the index, and sets a timer (`ResetAttackTime`) to reset the combo to 0 if the player delays their next attack.
  - Inputs are captured during animation playback via `BP_InputBufferComponent` listening to `AnimNotifyState_InputBuffer`.
- **Hardcoding Risk**: `GE_MeleeAttackCost.uasset` hardcodes `-15.0f` stamina at byte offset `0x1bc6`. The pack ability does not support per-weapon stamina costs natively without the project's `URPGSwingTracker` override layer.

---

## 4. Top 10 Values Needed in a "New Weapon" Editor Utility (Track C3)

A designer authoring a new weapon via an Editor Utility Widget (e.g. `EUW_NewWeapon`) must configure the following 10 fields to establish a fully functional, validated weapon definition without writing C++:

1. **`WeaponId` & `HudWeaponWord`**: Unique identifier symbol (FName) and user-facing display label (FString) for HUD presentation and console commands (`rpg.Build <Id>`).
2. **`CombatStyleAsset`**: Path to the pack's `BP_CombatStyle` data asset governing animation layers, stance poses, and camera offsets.
3. **`InventoryItemPath`**: Path to the `WeaponItem` or `DualWeaponItem` data asset defining inventory icon, description, and item modifiers.
4. **`WeaponActorClass`**: Blueprint class derived from `BP_BaseWeapon` (or `BP_BaseShieldWeapon`) that spawns the physical weapon mesh and collision trace components.
5. **`MeleeAbilityClass`**: Gameplay ability derived from `GA_Player_MeleeBase_Combined` containing the montage attack arrays.
6. **`AttackMontages` (Light Combo Chain)**: Ordered array of animation montages for the normal light attack sequence (e.g. Light 1, 2, 3, 4).
7. **`Heavy & Special Montages`**: Dedicated montages for Strong Attack (`Ability_E`), Charged Attack, and Jump/Falling Attack.
8. **`PostureDamage` per Attack Kind**: Stance break damage values authored into `DA_WeaponAttacks` for Light, Strong, Charged, and JumpHeavy attacks.
9. **`StaminaCost` per Attack Kind**: Exact stamina consumption per attack (or `-1.0` to preserve the pack's 15.0 default).
10. **`HyperArmorWindows` (Start / End)**: Active hyperarmor duration (in seconds of montage playback) for committed heavy swings to prevent boss interruptions.

---

## 5. Cooked & Binary-Only Elements (Offline Limitations)

During this offline read-only audit, the following structures could **not** be fully parsed without an active Unreal Engine editor environment:
1. **Blueprint Virtual Machine Bytecode**: The inner node networks of `GA_Player_MeleeBase_Combined.uasset` (e.g. mathematical branch calculations, dynamic type casts) are stored as compiled Kismet bytecode (`FKismetBytecode`) and cannot be disassembled offline.
2. **AnimNotify Track Float Timestamps**: While `AnimNotifyState` references (`AN_SetCollisionState`, `AN_InputBuffer`) appear in the asset name table of `UAnimMontage` files, their exact start/end float timestamps on the montage timeline require `UAnimMontage` deserialization via Unreal reflection or the `unreal.AnimationLibrary` Python API.
3. **Dynamic Blueprint Enums**: Enums defined entirely in Blueprint assets (such as `E_EquipSlots.uasset` and `E_CombatStyle.uasset`) store enumerator names in their serialized tables, but their runtime byte assignments are position-dependent and must be queried via reflection (as done in `RPGBuildLoadout.cpp:123-143`).

---

## 6. Verification & Test Suite

The companion script `Docs/BossCombatReview/Execution/Antigravity/Reviews/test_reopen_c5_weapon_data_audit.py` validates:
- All 15 C++ file and line citations cited in Section 2 across `RPGWeaponAttackTable`, `RPGCombatCatalog`, `RPGBuildRules`, `RPGBuildLoadout`, `RPGHitIntake`, and `RPGSwingTracker`.
- All binary byte offsets and literal values across `DA_WeaponAttacks.uasset`, `DA_Weapon_*.uasset`, `GE_MeleeAttackCost.uasset`, and `BP_AttackData.uasset`.
- Pure CRLF formatting and non-empty content.
