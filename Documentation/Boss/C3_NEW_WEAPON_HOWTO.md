# Designer Guide: Authoring a New Weapon with `new_weapon.py` (Track C3)

**Document:** `Documentation/Boss/C3_NEW_WEAPON_HOWTO.md`  
**Audience:** Technical Designers, Combat Designers, Systems Designers  
**Tools:** `Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py`, `Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_weapon_config.py`  
**Prerequisites:** Windowed Unreal Editor (5.5.4), PowerShell 5.1+, Python 3.10+  
**Status:** Canonical Authoring Reference  

---

## 1. Pack-Side Prerequisites (Unscriptable Assets)

`new_weapon.py` automates the mathematical and registration tiers of weapon authoring: it appends/updates combat table rows in `DA_WeaponAttacks.uasset`, instantiates `URPGWeaponDefinition` and `URPGBuildDefinition` assets, and registers them into the root `DA_CombatCatalog.uasset`.

However, the gameplay asset dependencies must be authored or retargeted in the editor beforehand. The script validates that these assets exist on disk before making any changes:

### 1.1 Pack Assets Required
1. **Combat Style DataAsset (`style_asset_path`)**:
   - Asset of type `URPGCombatStyle` (e.g. `/Game/AdvancedARPGCombat/CoreCombatSystem/DataAssets/CombatStyles/DA_PolearmCombatStyle.DA_PolearmCombatStyle`).
   - Defines character combo montages, stance overrides, weapon collision profiles, and active weapon slots.
2. **Item Definition DataAsset (`item_path`)**:
   - Asset of type `WeaponItem` or `DualWeaponItem` (e.g. `/Game/AdvancedARPGCombat/CoreCombatSystem/DataAssets/Items/Weapons/PolearmItem.PolearmItem`).
   - Configures inventory representation, mesh attachment sockets, and equipment attributes.
3. **Item Base Class (`item_base_class`)**:
   - Must reference the generated Blueprint class path ending in `_C` (e.g. `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/WeaponItem.WeaponItem_C`).
   - *Failure Mode*: If the `_C` suffix is omitted, the engine fails `Cast<UClass>(W.ItemBaseClass.TryLoad())` in [RPGCombatCatalog.cpp:185](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L185), rejecting the catalog with `<WeaponId>.References: unresolved/wrong type/cook policy`.
4. **Weapon Actor Blueprint Class (`actor_class`)**:
   - Blueprint actor spawned in character hand socket during combat (e.g. `/Game/AdvancedARPGCombat/CoreCombatSystem/Blueprints/Actors/BP_PolearmActor.BP_PolearmActor_C`).
5. **Gameplay Ability Class (`ability_class`)**:
   - Gameplay ability governing basic melee attack activation (e.g. `/Game/AdvancedARPGCombat/CoreCombatSystem/Blueprints/Abilities/GA_MeleeAttack.GA_MeleeAttack_C`).

### 1.2 The Cook-Root Rule (`DirectoriesToAlwaysCook`)
All referenced asset paths—especially `catalog.icon_path` and soft asset references—**must** reside within packages listed under `DirectoriesToAlwaysCook` in [Config/DefaultGame.ini:19-44](file:///C:/UnrealProject/OneBossFight/Config/DefaultGame.ini#L19-L44).
- The project UI root `/Game/OneBossFight/UI` is cooked (e.g. `/Game/OneBossFight/UI/Art/T_Boss01_Icon_Strength.T_Boss01_Icon_Strength`).
- Pack folders such as `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/InventoryEquipmentUI/Icons` are **NOT** in the cooked roots.
- *Failure Mode*: If an icon or asset path resides in an un-cooked root, the engine compile check `CookedDependency()` in [RPGCombatCatalog.cpp:103-123](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L103-L123) logs `icon broken (outside the cooked roots)`, and un-cooked asset references fail catalog compilation.

### 1.3 The Rows-vs-Style Rule
`DA_WeaponAttacks.uasset` is indexed by `(weapon, kind)` pairs:
- In `mode: "new_weapon"`, the validator enforces `[Weapon.Config.StyleAlreadyHasRows]`. The `style_name` must **not** already have rows in `DA_WeaponAttacks.uasset`.
- To edit combat attributes of an existing weapon style (e.g. tuning Starter Sword, Claymore, or Dual Swords), set `mode: "update_existing_style"`.

---

## 2. Configuration File Reference (`weapon_config.json`)

`new_weapon.py` reads a single JSON configuration file. Below is the canonical v1 schema demonstrating full row definition and catalog registration for a new weapon (`Polearm`):

```json
{
  "mode": "new_weapon",
  "style_name": "PolearmCombatStyle",
  "weapon_id": "FengMaoPolearm",
  "style_asset_path": "/Game/AdvancedARPGCombat/CoreCombatSystem/DataAssets/CombatStyles/DA_PolearmCombatStyle.DA_PolearmCombatStyle",
  "item_path": "/Game/AdvancedARPGCombat/CoreCombatSystem/DataAssets/Items/Weapons/PolearmItem.PolearmItem",
  "item_base_class": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/WeaponItem.WeaponItem_C",
  "actor_class": "/Game/AdvancedARPGCombat/CoreCombatSystem/Blueprints/Actors/BP_PolearmActor.BP_PolearmActor_C",
  "ability_class": "/Game/AdvancedARPGCombat/CoreCombatSystem/Blueprints/Abilities/GA_MeleeAttack.GA_MeleeAttack_C",
  "hud_weapon_word": "Polearm",
  "style_aliases": ["Polearm", "Spear"],
  "catalog": {
    "register": true,
    "weapon_asset_path": "/Game/OneBossFight/Data/Catalog/DA_Weapon_FengMaoPolearm.DA_Weapon_FengMaoPolearm",
    "build_asset_path": "/Game/OneBossFight/Data/Catalog/DA_Build_FengMaoPolearm.DA_Build_FengMaoPolearm",
    "catalog_root_path": "/Game/OneBossFight/Data/Catalog/DA_CombatCatalog.DA_CombatCatalog",
    "legacy_slot": -1,
    "icon_path": "/Game/OneBossFight/UI/Art/T_Boss01_Icon_Strength.T_Boss01_Icon_Strength",
    "require_exact_rows": true
  },
  "build": {
    "build_id": "FengMaoPolearmBuild",
    "console_name": "polearm",
    "aliases": ["spear", "halberd"],
    "display_name": "Feng Mao Polearm",
    "ui_order": 4
  },
  "attack_rows": [
    {
      "kind": "Light",
      "posture_damage": 16.0,
      "stamina_cost": 15.0,
      "bleed_buildup": 0.0,
      "health_damage_multiplier": 0.65,
      "hyperarmor_start": -1.0,
      "hyperarmor_end": -1.0,
      "note": "Light 3-hit combo primary"
    },
    {
      "kind": "Strong",
      "posture_damage": 32.0,
      "stamina_cost": 30.0,
      "bleed_buildup": 0.0,
      "health_damage_multiplier": 1.25,
      "hyperarmor_start": 0.15,
      "hyperarmor_end": 0.55,
      "note": "Strong thrust attack"
    },
    {
      "kind": "Charged",
      "posture_damage": 55.0,
      "stamina_cost": 45.0,
      "bleed_buildup": 0.0,
      "health_damage_multiplier": 1.85,
      "hyperarmor_start": 0.1,
      "hyperarmor_end": 0.8,
      "note": "Heavy sweep with hyperarmor"
    }
  ]
}
```

### 2.1 Complete Field-by-Field Reference

| Key | Status | Type | Description & Constraints | Failure Token |
| :--- | :--- | :--- | :--- | :--- |
| `mode` | Optional | String | `"new_weapon"` (default; requires unauthored style) or `"update_existing_style"`. | `[Weapon.Config.Mode]` |
| `style_name` | Mandatory | String | Matches `Name` of the combat style. Cannot be an enemy style (`SevarogCombatStyle`). | `[Weapon.Config.EnemyCombatStyle]`, `[Weapon.Config.StyleAlreadyHasRows]` |
| `weapon_id` | Mandatory | String | Unique weapon identifier in catalog. Must be non-empty. | `[Weapon.Config.Identity]` |
| `style_asset_path` | Mandatory | Asset Path | Soft object path to `URPGCombatStyle` asset. Must exist under cooked roots. | `[Weapon.Config.PathMissing]`, `[Weapon.Config.Path]` |
| `item_path` | Mandatory | Asset Path | Soft object path to pack item asset. Must exist under cooked roots. | `[Weapon.Config.PathMissing]`, `[Weapon.Config.Path]` |
| `item_base_class` | Mandatory | Class Path | Generated class path ending in `_C`. Blueprint must exist on disk. | `[Weapon.Config.ItemBaseClassPath]` |
| `actor_class` | Mandatory | Class Path | Generated class path ending in `_C` for the spawned weapon actor. | `[Weapon.Config.PathMissing]`, `[Weapon.Config.Path]` |
| `ability_class` | Mandatory | Class Path | Generated class path ending in `_C` for melee ability. | `[Weapon.Config.PathMissing]`, `[Weapon.Config.Path]` |
| `hud_weapon_word` | Mandatory | String | Short identifier word displayed on HUD. Non-empty. | `[Weapon.Config.Identity]` |
| `style_aliases` | Optional | Array[String] | Array of alternative name aliases for console matching. | `[Weapon.Config.Structure]` |
| `catalog.register` | Mandatory | Bool | When `true`, creates definition assets and updates root catalog. | `[Weapon.Config.Catalog.Structure]` |
| `catalog.weapon_asset_path` | Mandatory | Asset Path | Destination path for `URPGWeaponDefinition`. Must reside under `/Game/OneBossFight/Data/Catalog/`. | `[Weapon.Config.Catalog.Path]` |
| `catalog.build_asset_path` | Mandatory | Asset Path | Destination path for `URPGBuildDefinition`. Must reside under `/Game/OneBossFight/Data/Catalog/`. | `[Weapon.Config.Catalog.Path]` |
| `catalog.catalog_root_path` | Mandatory | Asset Path | Target catalog root asset (defaults to `/Game/OneBossFight/Data/Catalog/DA_CombatCatalog.DA_CombatCatalog`). | `[Weapon.Config.Catalog.Path]` |
| `catalog.legacy_slot` | Mandatory | Int | **Must be `-1`** (`INDEX_NONE`). Positive slots `0..2` reserved for legacy builds (`Starter`, `Strength`, `Dex`). | `[Weapon.Config.Catalog.LegacySlot]` |
| `catalog.icon_path` | Optional | Asset Path | Path to UI icon. Must reside under cooked root (e.g. `/Game/OneBossFight/UI`). | `[Weapon.Config.Catalog.IconCookRoot]` |
| `catalog.require_exact_rows`| Optional | Bool | Enforces that table must have exactly the declared action kinds. | `[Weapon.Config.Catalog.Structure]` |
| `build.build_id` | Mandatory | String | Unique build identifier (e.g. `FengMaoPolearmBuild`). | `[Weapon.Config.Build]` |
| `build.console_name` | Mandatory | String | Console switch argument for `rpg.Build <name>`. Cannot be `'none'`, `'off'`, or collide with legacy builds (`starter`, `strength`, `dex`). | `[Weapon.Config.Catalog.ReservedName]`, `[Weapon.Config.Catalog.AliasCollision]` |
| `build.aliases` | Optional | Array[String] | Alternative console names. Subject to same reserved/collision checks. | `[Weapon.Config.Catalog.AliasCollision]` |
| `build.display_name` | Mandatory | String | User-facing build title. Non-empty. | `[Weapon.Config.Build]` |
| `build.ui_order` | Mandatory | Int | Display order index on build selection menu. | `[Weapon.Config.Build]` |
| `attack_rows` | Mandatory | Array[Object] | Must include at least `Light`, `Strong`, and `Charged` kinds without duplicates. | `[Weapon.Config.AttackCoverage]` |
| `attack_rows[].posture_damage` | Mandatory | Float | Posture damage dealt to boss stance pool ($> 0.0$). | `[Weapon.Config.AttackDomain]` |
| `attack_rows[].stamina_cost` | Mandatory | Float | Player stamina consumed ($> 0.0$). | `[Weapon.Config.AttackDomain]` |
| `attack_rows[].bleed_buildup` | Mandatory | Float | Bleed status buildup applied ($\ge 0.0$). | `[Weapon.Config.AttackDomain]` |
| `attack_rows[].health_damage_multiplier` | Mandatory | Float | Damage multiplier applied to player base attack ($> 0.0$). | `[Weapon.Config.AttackDomain]` |
| `attack_rows[].hyperarmor_start/end` | Mandatory | Float | Hyperarmor active window relative to attack ($[-1.0, -1.0]$ for none). | `[Weapon.Config.HyperArmor]` |

---

## 3. Tool Command Lines

`new_weapon.py` runs inside the Unreal Editor process. Because the editor's working directory is engine binaries (`UE_5.5\Engine\Binaries\Win64`), **all file paths inside `-Script` must be absolute paths with forward slashes**.  
`-OutDir` must be absolute, the editor does not run from the repo root. Furthermore, `run_editor_script.ps1` requires mandatory `-OutDir` and `-Task` parameters.

### 3.1 Dry-Run Validation (Zero Writes)
Runs offline preflight checks against live table rows and physical asset existence without modifying assets:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1 `
  -Script "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/C3/example_polearm_weapon_v1.json" `
  -OutDir "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\C3\runs_v1\dry" `
  -Task "C3_v1_DryRun" `
  -NullRhi 1
```

> [!NOTE]
> The example config describes a weapon (`PolearmCombatStyle`) that may already exist in temporary review runs. If running on an already applied style in `new_weapon` mode, the validator will refuse with `[Weapon.Config.StyleAlreadyHasRows]`. Designers should copy the JSON, update the IDs and style name, or ensure previous test assets have been restored.

### 3.2 Full Row Insertion & Catalog Registration (`--apply`)
Executes row appending and definition asset creation:
1. Validates schema and asset existence via `validate_weapon_config.py`.
2. Appends attack rows to `DA_WeaponAttacks.uasset`.
3. Reads back every row from `DA_WeaponAttacks` to guarantee zero float drift or missing entries.
4. Creates `DA_Weapon_<WeaponId>` and `DA_Build_<WeaponId>` under `/Game/OneBossFight/Data/Catalog/`.
5. Appends both definitions to `DA_CombatCatalog.uasset` and saves all modified assets.
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1 `
  -Script "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/C3/example_polearm_weapon_v1.json --apply" `
  -OutDir "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\C3\runs_v1\apply" `
  -Task "C3_v1_Apply" `
  -NullRhi 1
```

---

## 4. PIE Proof & Verification (`-RealBuild <name>`)

Once registered, verify that the game runtime loads the new weapon from the data catalog and executes real swings hitting the boss.

### 4.1 Running the PIE Proof
Run the automated PIE driver targeting a framework proof level (e.g. `L_SevarogFrameworkProofF8`):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1 `
  -Map "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF8" `
  -OutDir "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\C3\runs_v1c\pie_polearm_real" `
  -Task "PIE_Polearm_Proof" `
  -RealBuild polearm `
  -RealSwing "0.0:Light,1.0:Light"
```

### 4.2 Runtime Switch Architecture
When `-RealBuild polearm` is passed:
1. **Console Execution**: The driver executes console command `rpg.Build polearm`.
2. **Catalog Compilation**: `URPGCombatRegistry::Compile()` compiles `DA_CombatCatalog.uasset`. On success, it logs:
   `[CombatCatalog] Compiled successfully (epoch=... source=data)`
3. **Loadout Equip**: `URPGBuildLoadout::CallEquip()` resolves `FengMaoPolearmBuild`, retrieves `PolearmItem`, and calls `Update Equip Slot Item` on `BP_EquipmentComponent_C`.
4. **Style Transition**: Player `CurrentCombatStyle` transitions to `PolearmCombatStyle`.
5. **Real Swings & Hit Intake**: Player swings execute real animations (`Primary_Melee_A_Slow`, etc.). On hit, `URPGHitIntake` extracts table row parameters and logs:
   `attack_row weapon=PolearmCombatStyle kind=Light found=1 posture=16 stamina=15 bleed=0 via=pending`
   `boss_hit damage=100.0 posture=16.0`
6. **Result**: Driver completes with `[F3D_RESULT] CompletedWithDamage`.

### 4.3 The 10-Second Pack-Style Warmup (KI-150)
> [!IMPORTANT]
> The Advanced ARPG Combat pack requires **~10 seconds** at startup to initialize gameplay ability tags, equipment montages, and combat styles.
> The automated driver waits for player `EnterCombat` and `Idle` before firing attacks. Never schedule real attacks at $t < 10.0\text{ s}$ from map load.

---

## 5. Restoring Repository State (Content Cleanliness)

Because authoring edits the shipped assets `DA_WeaponAttacks.uasset` and `DA_CombatCatalog.uasset`, testing temporary or proof weapons requires strict cleanup:

### 5.1 Reverting Shipped Assets
Revert modifications to the shared combat assets using git checkout:
```powershell
git checkout Content/OneBossFight/Data/DA_WeaponAttacks.uasset Content/OneBossFight/Data/Catalog/DA_CombatCatalog.uasset
```

### 5.2 Deleting Unreferenced Proof Assets
Delete the temporary definition assets created during testing **only after** the catalog has been restored:
```powershell
Remove-Item "Content\OneBossFight\Data\Catalog\DA_Weapon_FengMaoPolearm.uasset" -Force
Remove-Item "Content\OneBossFight\Data\Catalog\DA_Build_FengMaoPolearm.uasset" -Force
```

> [!CAUTION]
> As mandated by project policy in CLAUDE.md: "Never delete and recreate assets that other assets reference". If new weapon/build definition assets are deleted before `DA_CombatCatalog.uasset` is reverted, the catalog is left with broken unresolved references. Always run `git checkout` on the catalog first, and delete the unreferenced definition assets only afterwards.

---

## 6. Complete Validation Tokens & Troubleshooting

### 6.1 Offline Validator Tokens (`validate_weapon_config.py`)

| Error Token | Root Cause | Designer Action |
| :--- | :--- | :--- |
| `[Weapon.Config.Structure]` | JSON file is not a dictionary root or key structure is malformed. | Fix formatting so configuration root and blocks are JSON objects. |
| `[Weapon.Config.Mode]` | `mode` is neither `"new_weapon"` nor `"update_existing_style"`. | Set mode to `"new_weapon"` or `"update_existing_style"`. |
| `[Weapon.Config.Identity]` | `weapon_id`, `style_name`, or `hud_weapon_word` empty/missing. | Provide non-empty string for identifier or name. |
| `[Weapon.Config.EnemyCombatStyle]` | Style belongs to enemy or boss (`SevarogCombatStyle`). | Do not register boss combat styles as player weapons. |
| `[Weapon.Config.StyleAlreadyHasRows]` | Combat style already has rows in `mode: "new_weapon"`. | Use `mode: "update_existing_style"` to edit existing style, or choose a new style. |
| `[Weapon.Config.UnknownCombatStyle]` | `style_asset_path` or `style_name` does not match pack combat styles. | Use recognized player combat style (e.g. `PolearmCombatStyle`). |
| `[Weapon.Config.Path]` | Soft asset path is outside `DirectoriesToAlwaysCook` or format invalid. | Ensure referenced assets reside in cooked directories under `Config/DefaultGame.ini:19-44`. |
| `[Weapon.Config.PathMissing]` | Referenced asset does not exist on disk. | Verify asset package and name exist in `Content/`. |
| `[Weapon.Config.ItemBaseClassPath]` | `item_base_class` does not end in `_C` or Blueprint missing. | Specify generated class path ending in `_C` (e.g. `WeaponItem.WeaponItem_C`). |
| `[Weapon.Config.Build]` | `build` block missing or has empty `build_id`/`console_name`/`display_name`. | Supply all mandatory fields in `build` dictionary. |
| `[Weapon.Config.Catalog.Structure]` | `catalog` entry is not a JSON object. | Format `catalog` as a dictionary `{ "register": true, ... }`. |
| `[Weapon.Config.Catalog.Path]` | Definition asset paths not under `/Game/OneBossFight/Data/Catalog/`. | Move destination paths into `/Game/OneBossFight/Data/Catalog/`. |
| `[Weapon.Config.Catalog.LegacySlot]` | `legacy_slot` is not `-1`. | Set `"legacy_slot": -1`. Slots `0..2` are strictly reserved for legacy builds. |
| `[Weapon.Config.Catalog.ReservedName]` | `console_name` or alias is `'none'` or `'off'`. | Rename console build command to a unique gameplay word. |
| `[Weapon.Config.Catalog.AliasCollision]` | `console_name` or alias collides with legacy names. | Choose a name distinct from `starter`, `strength`, `dex`, `sword`, `str`, `dexterity`. |
| `[Weapon.Config.Catalog.IconPath]` | `icon_path` has invalid Unreal asset path format. | Use valid package.asset path for icon. |
| `[Weapon.Config.Catalog.IconCookRoot]` | `icon_path` is outside `DirectoriesToAlwaysCook`. | Move UI icon under `/Game/OneBossFight/UI` or other cooked root. |
| `[Weapon.Config.AttackCoverage]` | `attack_rows` empty, contains duplicates, or lacks `Light`/`Strong`/`Charged`. | Provide unique rows covering all 3 required archetype kinds. |
| `[Weapon.Config.InvalidAttackKind]` | Declared attack kind is missing or not in `RPGAttackKind` enum. | Use valid kind: `Light`, `Strong`, `Charged`, `Sprint`, `Jump`, `Falling`, `Special1`, `Special2`. |
| `[Weapon.Config.AttackDomain]` | Numeric value outside valid combat range. | Ensure `posture >= 0`, `stamina > 0` or `-1.0`, `bleed >= 0`, `health_damage_multiplier > 0`. |
| `[Weapon.Config.HyperArmor]` | Hyperarmor timing window invalid or non-finite. | Ensure `start < end` or set `[-1.0, -1.0]` for no hyperarmor. |

### 6.2 Engine Compile Failure Tokens (`RPGCombatCatalog.cpp:124-234`)

| Engine Diagnostic Token | Root Cause | Designer Action |
| :--- | :--- | :--- |
| `Catalog.Builds/Weapons: empty` | Root catalog has zero weapon or build definitions. | Add at least one weapon and build definition to catalog. |
| `Weapons.WeaponId: empty/duplicate` | Two weapon definitions share identical `WeaponId` or ID is empty. | Ensure each weapon definition has a unique non-empty identifier. |
| `.Style/Item/HudWord/Actions: required` | Mandatory weapon field (`StyleName`, `ItemPath`, `HudWeaponWord`, `Actions`) is missing. | Populate all mandatory fields on `FRPGCatalogWeapon`. |
| `.StyleAliases: empty/conflict` | Weapon style alias collides with another weapon definition. | Use unique style aliases across all catalog weapons. |
| `Builds.Id/WeaponId/DisplayName: invalid` | Build definition has empty ID, unmapped `WeaponId`, or empty display name. | Ensure `WeaponId` exists in catalog weapons array and names are populated. |
| `.LegacySlot: invalid/duplicate` | Authored build sets `LegacySlot` outside `[-1, 2]` or collides with existing slot. | Set `LegacySlot = -1` for all authored expansion builds. |
| `.Aliases: empty/reserved/collision` | Build console name or alias is `'none'`, `'off'`, or collides with another build. | Choose distinct, non-reserved console switch names. |
| `Builds.LegacySlot: three compatibility slots required` | Catalog does not contain all 3 legacy slots `0, 1, 2`. | Keep the 3 legacy compatibility builds intact in catalog root. |
| `Builds.LegacySlot: pinned three-build contract changed` | A legacy slot `0..2` property was modified. | Never modify legacy slots `0..2` when authoring expansion weapons. |
| `.References: unresolved/wrong type/cook policy` | Item class omitted `_C`, or asset failed `CookedDependency`. | Verify `_C` suffix on Blueprint classes and verify paths are in `DirectoriesToAlwaysCook`. |
| `icon broken (outside the cooked roots)` | UI icon is in an unpackaged or uncooked folder. | Move icon into `/Game/OneBossFight/UI/`. |
| `.Actions: required exact row missing` | Weapon has `bRequireExactRows=true` but `DA_WeaponAttacks` lacks exact row for kind. | Add exact matching row in `DA_WeaponAttacks` for the weapon style. |
