# Practical Data Asset Authoring Quickstart: Weapon, Build & Boss

**Scope**: Offline Developer Cookbook & Details Panel Reference  
**Task Anchor**: AG-CONTENT-02 REV4 (Addresses Claude Interim Lead Review `[C-234]`)  
**Companion File**: [`authoring_examples.json`](./authoring_examples.json)  
**Target Engine**: Unreal Engine 5.5.4 (Advanced ARPG Combat Pack)  

---

## 1. Executive Summary & Authoring Truth

This cookbook provides the project owner and designers with a concrete, hands-on guide answering:
> **"How do I author a custom weapon, player build, and boss using current native Data Assets and Details panels?"**

### User-Facing Reality & Integration Status
Before creating assets, understand the precise boundaries of the current codebase:
1. **Source Declarations Exposed**: The native C++ classes (`URPGWeaponDefinition`, `URPGBuildDefinition`, `URPGCombatCatalog`, `URPGBossDefinition`, and `ARPGEncounterBinding`) exist and expose typed, editable properties to the Unreal Editor Details panel.
2. **Editor Details Workflow**: The workflows described below follow standard Unreal Engine `Content Browser -> Miscellaneous -> Data Asset` patterns derived from native source declarations. They represent manual authoring specifications, not an automated UI wizard.
3. **Player Catalog Runtime**: The combat catalog (`URPGCombatCatalogSubsystem` / `RPGCombatRegistry::Compile`, `RPGCombatCatalog.cpp:124`) is functional and verified in unit tests. It strictly enforces a pinned 3-build compatibility contract before compiling into immutable content epochs.
4. **Boss Creation & Activation Pending**: While `URPGBossDefinition` compiles and validates in preflight test fixtures (`RPGBossProductionPreflightTests.cpp`, where exactly 2 tests out of the 110 suite tests verify component preflight), **live level binding, runtime boss spawning, and startup activation are NOT yet released or complete**. A newly defined boss cannot be fought in-game until integration gates open.

---

## 2. Recipe 1: Weapon Definition Reference (`URPGWeaponDefinition`)

### Purpose & Style Identity Constraints
Defines the visual, combat, and animation style properties of a weapon.

* **Native Class**: `URPGWeaponDefinition` (inherits `UPrimaryDataAsset`)
* **Header**: `Source/OneBossFight/Player/RPGCombatCatalog.h` (line 48)
* **Inner Property Block**: `UPROPERTY(EditAnywhere) FRPGCatalogWeapon Definition;`

> [!CRITICAL]
> **Duplicate Style Collision Rule (`RPGCombatCatalog.cpp:130-140`)**:  
> The catalog compiler strictly forbids multiple weapons from sharing the same `StyleName` (`Styles.Contains(Style) && Styles[Style] != W.WeaponId`).  
> A custom weapon **cannot** reuse an existing style such as `ClaymoreCombatStyle` alongside the pinned `Strength` weapon.  
> **Truly New Weapon Requirements**: Authoring a completely new weapon requires:
> 1. A unique `StyleName` (e.g. `HalberdCombatStyle`, `DaggerCombatStyle`).
> 2. Matching unique style asset, item data asset, item base class, actor class, and ability class.
> 3. Unique attack rows in the weapon attack table (`RPGWeaponAttackTable`).  
> Until those unique assets and rows are authored, authoring a new weapon is **unresolved authoring work**. Below is the verified reference configuration for the pinned `Strength` weapon.

### Field Configuration Reference

| Property Name | Type | Required? | Example Value | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `Definition.WeaponId` | `FName` | **YES** | `Strength` | Unique FName identifier (`RPGBuildRules.h:37`). Must not collide with other weapons in catalog. |
| `Definition.StyleName` | `FName` | **YES** | `ClaymoreCombatStyle` | Pinned style name (`RPGBuildRules.h:37`) used as primary lookup key in attack tables. Cannot be shared across different `WeaponId`s. |
| `Definition.StyleAsset` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/ClaymoreCombatStyle.ClaymoreCombatStyle` | Style data asset (`RPGCombatCatalog.cpp:89`). Distinct ABI identity from `AbilityClass`. Package exists on disk. |
| `Definition.ItemPath` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Items/Weapons/KwangSword.KwangSword` | Pinned weapon item asset (`RPGBuildRules.h:37`). Package exists on disk. |
| `Definition.ItemBaseClass` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/WeaponItem.WeaponItem_C` | **REQUIRED** when resolving production assets (`RPGCombatCatalog.cpp:185-187`). Item must derive from ItemBaseClass (`Item->IsA(ItemBase)`). Evidence: offline serialized-name in pinned assets (`DA_Weapon_Claymore`, `KwangSword`) and package on disk (`Content/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/WeaponItem.uasset`, SHA-256 `3241309b...`). Class not loaded and `_C` kind is not runtime-verified. |
| `Definition.ActorClass` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/ClaymoreInstances/BP_KwangSword.BP_KwangSword_C` | Full soft class path to weapon actor spawned/attached to character socket (`RPGCombatCatalog.cpp:87`). Package exists on disk. |
| `Definition.AbilityClass` | `FSoftObjectPath` | **YES** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/GA_Claymore_Melee.GA_Claymore_Melee_C` | Full soft class path to gameplay ability granted while equipped (`RPGCombatCatalog.cpp:88`). Package exists on disk. |
| `Definition.HudWeaponWord` | `FString` | **YES** | `Claymore` | Short weapon name string displayed on player HUD (`RPGBuildRules.h:37`). |
| `Definition.StyleAliases` | `TArray<FName>` | No | `[]` | Optional alternate style names recognized in console or debug commands. |
| `Definition.AliasHudWords` | `TMap<FName, FString>` | No | `{}` | Optional HUD text overrides when alias is active. |
| `Definition.Icon` | `FSoftObjectPath` | No | `/Game/OneBossFight/UI/Art/T_Boss01_Icon_Strength.T_Boss01_Icon_Strength` | UI icon texture path (`RPGCombatCatalog.cpp:96`). Package exists on disk. |
| `Definition.Actions` | `TArray<ERPGAttackKind>` | **YES** | `[Light, Strong, Charged, JumpLight, JumpHeavy, Knockdown]` | Must match canonical `ERPGAttackKind` enum values (`RPGAttackKind.h:11`). `Unknown` is rejected. |
| `Definition.bRequireExactRows` | `bool` | **YES** | `true` | **Requested authored policy**: Set to `true` so compilation strictly rejects missing attack table rows. |
| `Definition.ReferenceProvenance` | `FString` | No | *(System Read-Only)* | **Read-Only** in Details (`VisibleAnywhere, BlueprintReadOnly`). Overwritten by compiler with resolved status. |

---

## 3. Recipe 2: Custom Player Build Definition (`URPGBuildDefinition`)

### Purpose
Creates an additive player build that references the existing `Strength` weapon without introducing duplicate weapon style conflicts.

* **Native Class**: `URPGBuildDefinition` (inherits `UPrimaryDataAsset`)
* **Header**: `Source/OneBossFight/Player/RPGCombatCatalog.h` (line 56)
* **Inner Property Block**: `UPROPERTY(EditAnywhere) FRPGCatalogBuild Definition;`

### Editor Step-by-Step
1. Navigate to `/Game/OneBossFight/Data/Catalog/`.
2. Right-click -> **Miscellaneous** -> **Data Asset** -> Select **`RPGBuildDefinition`**.
3. Name the asset `DA_Build_Custom_Vanguard`.
4. Open the asset and configure the **Definition** fields.

### Field Configuration Reference

| Property Name | Type | Required? | Example Value | Description & Validation Rules |
| :--- | :--- | :---: | :--- | :--- |
| `Definition.BuildId` | `FName` | **YES** | `Build_Custom_Vanguard` | Unique FName identifier. Must not collide with `Starter`, `Strength`, `Dex`. |
| `Definition.ConsoleName` | `FString` | **YES** | `vanguard` | Token for console switching (`rpg.Build vanguard`). |
| `Definition.Aliases` | `TArray<FString>` | No | `["vanguard_alt"]` | Alternate console switch aliases. |
| `Definition.DisplayName` | `FString` | **YES** | `Vanguard Claymore` | Title shown in the build select UI. |
| `Definition.UiOrder` | `int32` | **YES** | `3` | Recommended author convention: use `3+` for custom builds (slots `0, 1, 2` are enforced for legacy builds). |
| `Definition.LegacySlot` | `int32` | **YES** | `-1` | **CRITICAL COMPLIANCE**: Must be `-1` (`INDEX_NONE`). Slots 0, 1, 2 are strictly reserved for pinned legacy builds. |
| `Definition.WeaponId` | `FName` | **YES** | `Strength` | **CRITICAL**: References the existing `Strength` weapon, avoiding duplicate style conflicts. |
| `Definition.Icon` | `FSoftObjectPath` | No | `/Game/OneBossFight/UI/Art/T_Boss01_Icon_Strength.T_Boss01_Icon_Strength` | Build portrait texture. |

---

## 4. Recipe 2b: Registering in the Combat Catalog (`URPGCombatCatalog`)

### Purpose
The central registry data asset read by `URPGCombatCatalogSubsystem` at game instance initialization.

* **Native Class**: `URPGCombatCatalog` (inherits `UPrimaryDataAsset`)
* **Header**: `Source/OneBossFight/Player/RPGCombatCatalog.h` (line 64)
* **Canonical Asset Path**: `/Game/OneBossFight/Data/Catalog/DA_CombatCatalog.DA_CombatCatalog`

### Verified On-Disk Files vs Catalog Membership
The existing data assets live directly under `/Game/OneBossFight/Data/Catalog/`:
* **Existing Weapons**: `DA_Weapon_Sword.uasset`, `DA_Weapon_Claymore.uasset`, `DA_Weapon_DualSwords.uasset`
* **Existing Builds**: `DA_Build_Starter.uasset`, `DA_Build_Strength.uasset`, `DA_Build_Dex.uasset`
* **Existing Catalog**: `DA_CombatCatalog.uasset`

> [!NOTE]
> On-disk file presence does not prove serialized catalog membership. To make a build usable, it must be explicitly soft-referenced in `DA_CombatCatalog`'s arrays.

### Pinned Compatibility Contract Rule (`RPGCombatCatalog.cpp:124-170`)
`RPGCombatRegistry::Compile` enforces that:
1. `Slots.Num() == 3`: Exactly three builds must occupy `LegacySlot` values `0`, `1`, and `2`.
2. These three slots must match the pinned definitions from `RPGBuildRules::Entry`:
   - Slot 0: `Starter` (Sword)
   - Slot 1: `Strength` (Claymore)
   - Slot 2: `Dex` (Dual Swords)
3. Any new custom build must be added **additively** with `LegacySlot = -1` (`INDEX_NONE`).

### Startup Seam & Cook Limits
- **Startup Mode**: The catalog is latched at game instance startup under `data`, `legacy`, or `auto` mode. Changing catalog properties at runtime requires restarting the game instance.
- **Test Catalog Root**: Isolated unit test catalogs are restricted by native code to `/Game/OneBossFight/Data/TypedABIFixtures/` (defined at `RPGCombatCatalog.cpp:262`, enforced at line 269).
- **Cook Directory Policy**: Assets must be created directly under `/Game/OneBossFight/Data/Catalog/` to align with configured cook directories.

---

## 5. Recipe 3: Boss Definition (`URPGBossDefinition`)

### Purpose
Defines boss combat attributes, health, posture regen, phase transitions, stagger/riposte timings, dormant/wake clips, and animations.

* **Native Class**: `URPGBossDefinition` (inherits `UPrimaryDataAsset`)
* **Header**: `Source/OneBossFight/Player/RPGEncounterBinding.h` (line 168)

### Editor Step-by-Step
1. Navigate to `/Game/OneBossFight/Data/Boss/`.
2. Right-click -> **Miscellaneous** -> **Data Asset** -> Select **`RPGBossDefinition`**.
3. Name the asset `DA_Boss_<BossName>` (e.g., `DA_Boss_EmberWarden_Example`).
4. Configure the sub-categories in Details.

### Detailed Category Reference

#### A. Header & Presentation
* `Schema`: `1` (Integer, default 1).
* `DefinitionId`: `Boss_EmberWarden_Example` (`FName`, unique boss ID).
* `PresentationId`: `EmberWarden` (`FName`, metadata identity token; not a verified UI display name).

#### B. Stats (`FRPGBossStatsConfig`)
*(Demonstration authoring values; not approved gameplay balance)*
* `MaxHealth`: `1200.0`
* `MaxPosture`: `200.0`
* `PostureRegenDelay`: `3.0`
* `PostureRegenRate`: `25.0`

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

#### G. Phases Array (CRITICAL BACKEND VALIDATION RULE)
* **Backend Limit**: `ValidatePhases` (`RPGBossPhaseAdapters.cpp:107`) supports **exactly 1 transition record**.
* If an author provides `PhaseOne` and `PhaseTwo` in this array, `Phases.Num() > 1` triggers line 95:  
  `UnsupportedNativePhaseSet: 2 record(s)... the native backend represents exactly 1 transition`
* **Correct Authored Entry**: Provide only the transition phase:
  * `PhaseId`: `PhaseTwo`
  * `EntryHealthFraction`: `0.5`
  * `SpeedMultiplier`: `1.15` | `RateMultiplier`: `1.25` | `AttackMultiplier`: `1.3` (Demonstration choices)

#### H. Skeleton & Animations Array (CRITICAL COMPILER RULE)
* `Skeleton`: `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.SK_CombatMannequin`
  *(Must match skeleton reported by the observed CDO mesh `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple`, confirmed in DD14 `[C-232]` / `[X-271]`)*
* `Animations`: Explicitly list all 9 candidate sequence/montage assets.
* **Compiler Rule**: The compiler checks EVERY entry in `Definition.Animations` against `Definition.Skeleton`. In DD14, all 9 boss animations verified cleanly reporting `SK_CombatMannequin`.

#### I. Fields (51-Row Field Parity Manifest)
* `Fields`: Array of 51 `FRPGParityField` transport records (`RPGEncounterBinding.h:150`).
* **Implementation Contract**: This is an implementation validation contract ensuring parameter parity during migration. It is not an automated wizard that generates provenance.

---

## 6. Recipe 4: Placed Encounter Binding Actor (`ARPGEncounterBinding`)

### Purpose
Links placed character actor instances in the arena map to their authored definitions.

* **Native Class**: `ARPGEncounterBinding` (inherits `AActor`)
* **Header**: `Source/OneBossFight/Player/RPGEncounterBinding.h` (line 242)

### Structure & Wiring
In the Level Editor Details panel for a placed `ARPGEncounterBinding` actor:
1. `EncounterInstance`: Explicit unique `FGuid` (e.g. `e2a3c741-5912-4f3a-967b-12d8a57e3c90`). Empty or duplicate GUID is rejected by the world subsystem.
2. `Participants`: Must contain explicit entries for BOTH combatants with reciprocal target references:

```text
Participants:
  ├── [0] Boss Participant:
  │     ├── Slot: "Boss"
  │     ├── TargetSlot: "Player"
  │     ├── Actor: [Reference to Boss Character Actor placed in Level]
  │     └── Definition: DA_Boss_EmberWarden_Example
  │
  └── [1] Player Participant:
        ├── Slot: "Player"
        ├── TargetSlot: "Boss"
        ├── Actor: [Reference to Player Character Actor placed in Level]
        └── Definition: DA_Player_Participant_Example
```

> [!CRITICAL]
> **Production BindEncounter Participant Requirement (`RPGEncounterBinding.cpp:193-198`)**:  
> In non-synthetic production execution, every participant—including the `TargetOnly` player—must provide an explicit `Definition` whose `DefinitionId` and `Schema` match the participant config. Setting `Definition = nullptr` triggers `Result.Fail("explicit definition/config mismatch")`.

> [!NOTE]
> Slot names `"Boss"` and `"Player"` are example participant tokens; `"BossCore"` and `"TargetOnly"` are separate internal C0 role identifiers.

> [!WARNING]
> **Integration Status Gate**: The placed binding workflow is proposed from native source declarations. **Runtime level hydration, boss spawning, and startup combat activation are NOT yet released or complete**. Placed bindings will not start live combat until integration milestones open.

---

## 7. Authoring Checklist & Verification

Before submitting newly authored Data Assets:
- [ ] `Definition.bRequireExactRows` is set to `true`.
- [ ] `Definition.ItemBaseClass` is assigned and resolves (`Item->IsA(ItemBase)`). Path: `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/WeaponItem.WeaponItem_C`.
- [ ] `Definition.Actions` contains only canonical `ERPGAttackKind` enum values (`Light`, `Strong`, `Charged`, `JumpLight`, `JumpHeavy`, `Knockdown`).
- [ ] Custom builds reference an existing weapon or a uniquely styled weapon (no duplicate `StyleName`).
- [ ] Custom builds specify `Definition.LegacySlot = -1` (`INDEX_NONE`).
- [ ] The catalog retains all 3 pinned legacy builds in slots 0, 1, and 2 (`Starter`, `Strength`, `Dex`).
- [ ] `URPGBossDefinition::Phases` contains exactly 1 transition record (`PhaseTwo`) to satisfy `ValidatePhases` (`RPGBossPhaseAdapters.cpp:107`, line 95 message).
- [ ] `URPGBossDefinition::Skeleton` matches `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin`.
- [ ] In `ARPGEncounterBinding`, BOTH participants provide explicit matching `Definition` references.
- [ ] Companion [`authoring_examples.json`](./authoring_examples.json) consulted for exact field spellings and provenance tags.

---

## Appendix: Pinned Source Dependencies

| Header / Source File | Relative Path | Verified Role |
| :--- | :--- | :--- |
| `RPGAttackKind.h` | `Source/OneBossFight/Player/RPGAttackKind.h` | Canonical attack kind enum (`ERPGAttackKind`) |
| `RPGBuildRules.h` | `Source/OneBossFight/Player/RPGBuildRules.h` | Pinned 3-build compatibility table (`Starter`, `Strength`, `Dex`) |
| `RPGCombatCatalog.h` | `Source/OneBossFight/Player/RPGCombatCatalog.h` | Class declarations (`URPGWeaponDefinition:48`, `URPGBuildDefinition:56`, `URPGCombatCatalog:64`) |
| `RPGCombatCatalog.cpp` | `Source/OneBossFight/Player/RPGCombatCatalog.cpp` | Catalog compiler (`FEpoch::Compile:124`), duplicate style check (130-140), ItemBaseClass check (185-187), TestCatalogRoot (262, enforced at 269) |
| `RPGEncounterBinding.h` | `Source/OneBossFight/Player/RPGEncounterBinding.h` | Boss definition (`URPGBossDefinition:168`), binding actor (`ARPGEncounterBinding:242`) |
| `RPGEncounterBinding.cpp` | `Source/OneBossFight/Player/RPGEncounterBinding.cpp` | BindEncounter definition checks (193-198) |
| `RPGBossPhaseAdapters.h/.cpp` | `Source/OneBossFight/Player/RPGBossPhaseAdapters.*` | Phase validation rules (`ValidatePhases:107`, line 95 single transition message) |
| `RPGBossStagger.h` | `Source/OneBossFight/Player/RPGBossStagger.h` | Stagger policy & riposte declarations |
| `RPGBossDormantWake.h` | `Source/OneBossFight/Player/RPGBossDormantWake.h` | Dormant & wake clip declarations |
