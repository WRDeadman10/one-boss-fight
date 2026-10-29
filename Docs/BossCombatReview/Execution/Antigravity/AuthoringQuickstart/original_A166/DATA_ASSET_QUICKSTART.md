# Practical Data Asset Authoring Quickstart: Weapon, Build & Boss

**Scope**: Offline Developer Cookbook & Details Panel Reference  
**Task Anchor**: AG-CONTENT-02 (per Codex directive `[X-269]`)  
**Companion File**: [`authoring_examples.json`](./authoring_examples.json)  
**Target Engine**: Unreal Engine 5.5.4 (Advanced ARPG Combat Pack)  

---

## 1. Executive Summary & Authoring Truth

This cookbook provides the project owner and designers with a concrete, hands-on guide answering:
> **"How do I author a custom weapon, player build, and boss using current native Data Assets and Details panels?"**

### User-Facing Reality & Integration Status
Before creating assets, understand the precise boundaries of the current codebase:
1. **Source Declarations Exposed**: The native C++ classes (`URPGWeaponDefinition`, `URPGBuildDefinition`, `URPGCombatCatalog`, `URPGBossDefinition`) exist and expose typed, editable properties to the Unreal Editor Details panel.
2. **Editor Details Workflow**: The workflows described below follow standard Unreal Engine `Content Browser -> Miscellaneous -> Data Asset` patterns derived from native source declarations. They are authoring blueprints, not an automated UI wizard.
3. **Player Catalog Runtime**: The combat catalog (`URPGCombatCatalogSubsystem` / `RPGCombatRegistry::Compile`) is functional and verified in unit tests. Validated weapons and builds compile into immutable content epochs.
4. **Boss Creation & Activation Pending**: While `URPGBossDefinition` compiles and validates in preflight test fixtures (`RPGBossProductionPreflightTests.cpp`, 110/110 tests green), **live level binding, runtime boss spawning, and startup activation are NOT yet released or complete**. A newly defined boss cannot be fought in-game until integration gates open.

---

## 2. Recipe 1: Custom Weapon Definition (`URPGWeaponDefinition`)

### Purpose
Defines the visual, combat, and animation style properties of a player-usable weapon.

* **Native Class**: `URPGWeaponDefinition` (inherits `UPrimaryDataAsset`)
* **Header**: `Source/OneBossFight/Player/RPGCombatCatalog.h` (line 56)
* **Inner Property Block**: `UPROPERTY(EditAnywhere) FRPGCatalogWeapon Definition;`

### Editor Step-by-Step
1. In the Content Browser, navigate to `/Game/OneBossFight/DataAssets/Weapons/` (or your target folder).
2. Right-click $
ightarrow$ **Miscellaneous** $
ightarrow$ **Data Asset**.
3. In the asset class picker, search and select **`RPGWeaponDefinition`** (or `URPGWeaponDefinition`).
4. Name the asset `DA_Weapon_<WeaponName>` (e.g., `DA_Weapon_Greatsword_Example`).
5. Open the asset. Expand the **Definition** category in the Details panel.

### Field Configuration Reference

| Property Name | Type | Required? | Example Value | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `WeaponId` | `FName` | **YES** | `Weapon_Greatsword_Example` | Unique alphanumeric identifier. Must match references in builds. |
| `StyleName` | `FName` | **YES** | `Greatsword` | Combat style name used by inventory style matching. |
| `StyleAsset` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/CombatStyles/CS_GreatSword.CS_GreatSword` | Primary style data asset. |
| `ItemPath` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/Core/Items/Weapons/GreatSword/DA_Item_GreatSword.DA_Item_GreatSword` | Inventory item data asset. |
| `ItemBaseClass` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/Core/Blueprints/Items/B_Item_Weapon.B_Item_Weapon_C` | Item Blueprint class. |
| `ActorClass` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/Core/Blueprints/Items/Equipable/Weapons/BP_Equipable_Greatsword.BP_Equipable_Greatsword_C` | Equipable weapon mesh actor. |
| `AbilityClass` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/CombatStyles/CS_GreatSword.CS_GreatSword_C` | Gameplay ability class for combat style. |
| `HudWeaponWord` | `FString` | **YES** | `GREATSWORD` | Word displayed on the HUD weapon slot widget. |
| `StyleAliases` | `TArray<FName>` | No | `["2H", "HeavyBlade"]` | Optional alias names recognized in console or debug commands. |
| `AliasHudWords` | `TMap<FName, FString>` | No | `{"2H": "2-HANDED"}` | Optional HUD text overrides when alias is active. |
| `Icon` | `FSoftObjectPath` | No | `/Game/AdvancedARPGCombat/UI/Textures/T_Weapon_Greatsword.T_Weapon_Greatsword` | UI texture icon. |
| `Actions` | `TArray<ERPGAttackKind>` | **YES** | `[LightAttack, HeavyAttack, SpecialAttack]` | List of supported attack actions (`RPGAttackKind.h`). |
| `bRequireExactRows` | `bool` | **YES** | `true` | **Enforce True for production**: Rejects weapons missing required attack table rows. |
| `ReferenceProvenance` | `FString` | No | `Authored production Greatsword` | Author audit notes. |

---

## 3. Recipe 2: Custom Player Build Definition (`URPGBuildDefinition`)

### Purpose
Bundles a weapon assignment with UI presentation and console commands to form a player archetype.

* **Native Class**: `URPGBuildDefinition` (inherits `UPrimaryDataAsset`)
* **Header**: `Source/OneBossFight/Player/RPGCombatCatalog.h` (line 64)
* **Inner Property Block**: `UPROPERTY(EditAnywhere) FRPGCatalogBuild Definition;`

### Editor Step-by-Step
1. Navigate to `/Game/OneBossFight/DataAssets/Builds/`.
2. Right-click $
ightarrow$ **Miscellaneous** $
ightarrow$ **Data Asset** $
ightarrow$ Select **`RPGBuildDefinition`**.
3. Name the asset `DA_Build_<BuildName>` (e.g., `DA_Build_Greatsword_Vanguard`).
4. Open the asset and configure the **Definition** fields.

### Field Configuration Reference

| Property Name | Type | Required? | Example Value | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `BuildId` | `FName` | **YES** | `Build_Greatsword_Vanguard` | Unique build identifier. |
| `ConsoleName` | `FString` | **YES** | `vanguard_gs` | Token for console switching (`rpg.Build vanguard_gs`). |
| `Aliases` | `TArray<FString>` | No | `["greatsword_heavy", "gs_vanguard"]` | Alternate console switch aliases. |
| `DisplayName` | `FString` | **YES** | `Vanguard Greatsword` | Title shown in the build select UI. |
| `UiOrder` | `int32` | **YES** | `1` | Integer sorting index for UI display list. |
| `LegacySlot` | `int32` | No | `0` | Backwards compatibility index (or `-1` / `INDEX_NONE`). |
| `WeaponId` | `FName` | **YES** | `Weapon_Greatsword_Example` | **CRITICAL**: Must match `WeaponId` of an authored `URPGWeaponDefinition`. |
| `Icon` | `FSoftObjectPath` | No | `/Game/AdvancedARPGCombat/UI/Textures/T_Build_Vanguard.T_Build_Vanguard` | Build portrait texture. |

---

## 4. Recipe 2b: Registering in the Combat Catalog (`URPGCombatCatalog`)

### Purpose
The central registry data asset read by `URPGCombatCatalogSubsystem` at game instance initialization.

* **Native Class**: `URPGCombatCatalog` (inherits `UPrimaryDataAsset`)
* **Header**: `Source/OneBossFight/Player/RPGCombatCatalog.h` (line 72)

### Steps
1. Open or create the primary catalog asset (e.g., `/Game/OneBossFight/DataAssets/DA_CombatCatalog.DA_CombatCatalog`).
2. Add your new weapon (`DA_Weapon_Greatsword_Example`) to the **Weapons** array.
3. Add your new build (`DA_Build_Greatsword_Vanguard`) to the **Builds** array.
4. **Validation Check**:
   - `SchemaVersion` must be `1`.
   - Every `BuildDefinition` must point to a `WeaponId` present in the `Weapons` list.
   - The subsystem compiles this catalog at startup into an immutable `FEpoch`.

---

## 5. Recipe 3: Boss Definition (`URPGBossDefinition`)

### Purpose
Defines boss combat attributes, health, posture regen, phase transitions, stagger/riposte timings, dormant/wake clips, and animations.

* **Native Class**: `URPGBossDefinition` (inherits `UPrimaryDataAsset`)
* **Header**: `Source/OneBossFight/Player/RPGEncounterBinding.h` (line 168)

### Editor Step-by-Step
1. Navigate to `/Game/OneBossFight/DataAssets/Boss/`.
2. Right-click $
ightarrow$ **Miscellaneous** $
ightarrow$ **Data Asset** $
ightarrow$ Select **`RPGBossDefinition`**.
3. Name the asset `DA_Boss_<BossName>` (e.g., `DA_Boss_EmberWarden_Example`).
4. Configure the sub-categories in Details.

### Detailed Category Reference

#### A. Header & Presentation
* `Schema`: `1` (Integer, default 1).
* `DefinitionId`: `Boss_EmberWarden_Example` (`FName`, unique boss ID).
* `PresentationId`: `EmberWarden` (`FName`, UI/telemetry display name).

#### B. Stats (`FRPGBossStatsConfig`)
* `MaxHealth`: `1200.0` (Total hit points).
* `MaxPosture`: `200.0` (Stagger meter cap).
* `PostureRegenDelay`: `3.0` (Seconds before posture begins recovering after taking damage).
* `PostureRegenRate`: `25.0` (Posture recovered per second).

#### C. Encounter Policy (`FRPGEncounterPolicyConfig`)
* `GateRadius`: `1200.0` (Distance in cm for boss detection gate. `0.0` disables gate).
* `bResetOnPlayerRespawn`: `true` (Resets boss position and dormant state when player respawns).

#### D. Stagger Policy (`FRPGStaggerPolicyConfig`)
Controls riposte vulnerability, window timings, and recovery rates (native defaults from `RPGBossStagger.h`):
* `StaggerSeconds`: `2.5` | `FreezeAtPosition`: `1.55` | `CriticalMultiplier`: `2.5`
* `RiposteRange`: `150.0` | `RiposteConeDegrees`: `120.0` | `RiposteFacingDegrees`: `120.0`
* `RiposteArmSeconds`: `1.2` | `RipostePlayerStartGap`: `150.0` | `RiposteAlignSeconds`: `0.3`
* `RiposteImpactSeconds`: `0.8` | `RiposteBaseDamage`: `40.0` | `CooldownSeconds`: `0.0`
* `GetUpRate`: `0.6` | `bHoldPostureAtZero`: `true`

#### E. Phase Flow & Dependencies (`FRPGPhaseFlowConfig` & `FRPGPhaseDependencyConfig`)
* `TransitionSeconds`: `1.8`
* `bUseRoarClip`: `true` (Plays RoarClip during phase transition).
* `bPausePostureInTransition`: `true`
* `bLockLeapUntilPhaseTwo`: `true`
* `AttackAbilityPrefix`: `GA_GS_Boss_`
* `LeapAbilityTag`: `Ability.Melee.LeapAttack`
* `PhaseDependencies.RoarClip`: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.AN_Boss01_PhaseRoar`
* `PhaseDependencies.TransitionMontage`: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Ability_R_Intro_Anim_Montage.Ability_R_Intro_Anim_Montage`
* `PhaseDependencies.ImmunityEffect`: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C`

#### F. Stagger Profile & Dormant Wake
* `StaggerProfile.bUseClips`: `true`
* `StaggerProfile.FallClip`: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall.AN_Boss01_StaggerFall`
* `StaggerProfile.DownClip`: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown`
* `StaggerProfile.RipostePlayerClip`: `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front.AN_Riposte_Player_Front`
* `StaggerProfile.RiposteBossClip`: `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction.AN_Riposte_Boss_Reaction`
* `DormantWake.DormantClip`: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_DormantIdle.AN_Boss01_DormantIdle`
* `DormantWake.WakeClip`: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Wake.AN_Boss01_Wake`

#### G. Skeleton & Animations Array (CRITICAL VALIDATION RULE)
* `Skeleton`: `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.SK_CombatMannequin`
* `Animations`: Explicitly list all 9 candidate sequence/montage assets.
> **Rule**: Every animation referenced in the sub-configs must report compatibility with `Skeleton`. Verified in DD14 preflight test (0 missing, 0 incompatible).

#### H. Phases Array (`TArray<FRPGPhaseConfig>`)
* Entry 0: `PhaseId`: `PhaseOne` | `EntryHealthFraction`: `1.0` | Multipliers: `1.0`
* Entry 1: `PhaseId`: `PhaseTwo` | `EntryHealthFraction`: `0.5` | `SpeedMultiplier`: `1.15` | `RateMultiplier`: `1.25` | `AttackMultiplier`: `1.3`

---

## 6. Recipe 4: Placed Encounter Binding (`FRPGPlacedParticipantBinding`)

### Purpose
Links a placed boss actor instance in the arena map to its authored `URPGBossDefinition`.

* **Native Struct**: `FRPGPlacedParticipantBinding`
* **Header**: `Source/OneBossFight/Player/RPGEncounterBinding.h` (line 232)

### Structure & Wiring
```text
[ Level Actor / Subsystem ]
        │
        ├── Slot: "BossCore"          (FName identifying the boss participant)
        ├── TargetSlot: "TargetOnly"  (FName identifying the player target)
        ├── Actor: [Placed Instance]  (Assigned in Level Editor Details panel to placed character)
        └── Definition: [DA_Boss_...] (Assigned to your authored URPGBossDefinition)
```

> [!WARNING]
> **Integration Status Gate**: While this struct exists for placement authoring, **runtime hydration and startup activation are NOT yet enabled**. Placed bindings will not start combat until the integration milestone is released.

---

## 7. Authoring Checklist & Verification

Before submitting newly authored Data Assets:
- [ ] `URPGWeaponDefinition::bRequireExactRows` is set to `true`.
- [ ] `URPGBuildDefinition::WeaponId` matches the exact `WeaponId` of your weapon asset.
- [ ] Both weapon and build assets are soft-referenced in `URPGCombatCatalog`.
- [ ] `URPGBossDefinition::Skeleton` matches `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin`.
- [ ] All 9 boss animations and montages import against that skeleton.
- [ ] All object paths point to cooked content paths under `/Game/` (never `/Engine/` or transient editor folders).
- [ ] JSON companion [`authoring_examples.json`](./authoring_examples.json) consulted for exact property spellings.

---

## Appendix: Source Dependency Hashes

| Header File | Relative Path | Verified Role |
| :--- | :--- | :--- |
| `RPGCombatCatalog.h` | `Source/OneBossFight/Player/RPGCombatCatalog.h` | Weapon, Build, and Catalog Data Assets |
| `RPGEncounterBinding.h` | `Source/OneBossFight/Player/RPGEncounterBinding.h` | Boss Definition & Placed Binding Structs |
| `RPGBossPhases.h` | `Source/OneBossFight/Player/RPGBossPhases.h` | Phase flow & dependency declarations |
| `RPGBossStagger.h` | `Source/OneBossFight/Player/RPGBossStagger.h` | Stagger policy & riposte declarations |
| `RPGBossDormantWake.h` | `Source/OneBossFight/Player/RPGBossDormantWake.h` | Dormant & wake clip declarations |
