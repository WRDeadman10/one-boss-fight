# DD-1 step 1 specification: catalog, weapon and build definitions behind a legacy facade (Claude, for Codex review)

Status: SPECIFICATION ONLY, not started. Preconditions (STEP0_BASELINE.md): baseline gate table and automation run on the current binary recorded; Codex accepts this specification. Behaviour-identical: every value, text, order and decision of today's three builds stays the same; the only new capability is that a fourth build (and a new weapon) can be added as DATA.

## Goal and non-goals

Goal: builds and their weapons come from data assets read through one registry; `RPGBuildRules` keeps its API and, when a catalog asset is present, answers from it; when it is absent or invalid it answers from today's table (the rollback). Non-goals: no combat, boss or phase behaviour change; no stat retuning; no change to the pack's equip call sequence (`RPGBuildLoadout::CallEquip`, the quickslot lock, the in-fight defer); no new weapon art; no edit of any pack asset; `URPGWeaponAttackTable` values unchanged.

## New code and assets (all new files unless stated)

1. `Source/OneBossFight/Player/RPGCombatCatalog.h/.cpp`: `URPGWeaponDefinition` (UPrimaryDataAsset: `WeaponId`, `StyleName` (the pack combat style asset name, today's key of the attack table), `ItemPath` (soft object path of the pack weapon item), `ActorClass` name, `AbilityClass` name, `HudWeaponWord`, `StyleAliases[]` (today `SwordAndShieldCombatStyle` for the sword, `TwinbladeCombatStyle` for the dex build), `Icon` soft texture), `URPGBuildDefinition` (`BuildId` as FName, `ConsoleName`, `Aliases[]` (str, dexterity, sword), `DisplayName`, `UiOrder`, `WeaponId`, `Icon`), and `URPGCombatCatalog` (UPrimaryDataAsset listing the builds and weapons, `SchemaVersion`). A registry namespace (`RPGCombatRegistry`) loads the catalog once (soft path in `Config/DefaultGame.ini` section for the project or a constant path `/Game/OneBossFight/Data/Catalog/DA_CombatCatalog`), validates it and exposes `BuildCount()`, `EntryByIndex/ById`, `ParseText`, `BuildOfStyle`. Validation rejects duplicate ids, empty style/item/ability, unknown weapon refs and aliases that collide, with the field path in the log; a failed validation falls back to the legacy table (logged once at Warning).
2. `Content/OneBossFight/Data/Catalog/`: `DA_CombatCatalog`, `DA_Weapon_Sword`, `DA_Weapon_Claymore`, `DA_Weapon_DualSwords`, `DA_Build_Starter`, `DA_Build_Strength`, `DA_Build_Dex`, created by a new script `Scripts/Editor/make_combat_catalog.py` that never overwrites an existing asset (same rule as `make_weapon_table.py`), values copied from `RPGBuildRules.h:50-52` and `BuildOfStyle`. The folder `/Game/OneBossFight/Data` is already always-cooked (`Config/DefaultGame.ini:22`).
3. Edited existing files (claim): `Source/OneBossFight/Player/RPGBuildRules.h` (the `Entry/BuildName/StyleOfBuild/BuildOfStyle/StyleMatchesBuild/Parse` functions delegate to the registry first, then the legacy table; `ERPGBuild` and `BuildCount` stay for old callers and tests; the registry's count is exposed as `BuildCountEffective()`), `Source/OneBossFight/UI/RPGBuildSelect.cpp/.h` and `RPGBuildSelectRules.h` (the three fixed rows become rows from the registry, same positions, same icons loaded softly; art for a fourth row comes from the data), `Source/OneBossFight/Player/RPGBuildLoadout.cpp/.h` only where it indexes the fixed table. `RPGWeaponAttackTable` stays as is (it is the compatibility view; its rows are keyed by `StyleName` exactly as now).

## Behaviour that must not change (parity witnesses, current binary)

`pie_builds` (103 checks), `pie_build_hyperarmor`, `pie_build_hud`, `pie_build_select`, `pie_flask_hud`, `pie_hyperarmor`, `pie_bleed`, `pie_stamina_cost`, `pie_hit_intake`, `pie_posture_hits`, `pie_build_fight_*` (balance rows, informational) and the 37 automation tests (`OneBossFight.Build.*` among them) all keep their meaning and totals; `rpg.Build` text parsing (case, quotes, aliases, empty/none/off) and the HUD line text are byte-identical.

## New proofs

- Automation test (new): the catalog assets equal the legacy table field by field (style, item path, actor, ability, HUD words, aliases, order); `Parse` and `BuildOfStyle` give the same results for a list of inputs including the aliases and an invalid text.
- Automation test (new): an in-memory catalog with a FOURTH build and a new weapon (no asset, built in the test) yields a fourth entry through `ParseText`, `BuildOfStyle` and the UI row list without any code path naming it; a malformed catalog (duplicate id, empty style, unknown weapon) is rejected with the field path and the legacy table answers.
- PIE driver (new, read-only checks): with the real catalog the HUD shows the same three rows and build line as before; with the catalog asset renamed away (rollback proof; the asset is restored by the same script) the legacy table answers and the same checks pass.
- Cook check: `Content.CookCoverage` automation test stays green with the new folder.

## Rollback

Delete or rename `DA_CombatCatalog` (or fail validation): `RPGBuildRules` answers from the legacy table, nothing else changes. Code rollback: revert the edited files from the pinned manifest (`STEP0_MANIFEST.json` hashes); the new files are unreferenced then. No git reset/clean/stash by anyone; the owner commits.

## Risks and open questions for Codex

1. Fourth-entry UI layout (rows are positioned for three): the spec keeps positions for three and only appends below; a layout rule for more rows needs a decision (proposal: the same row spacing downward).
2. `ERPGBuild` remains an enum for old callers, so a fourth build is addressed by `BuildId` (FName) only; the legacy `ERPGBuild` APIs return `Starter` for unknown ids: acceptable only if no new consumer uses the enum (rule: new code uses ids).
3. Style aliases live in data now; the dual and twinblade rows of `URPGWeaponAttackTable` stay keyed by style name: a new weapon needs its own rows in the table asset (data), no code.
4. The pack weapon item/actor/ability must exist in the pack for a new weapon: the spec does not create weapon content; the canary at P8 uses an existing pack weapon capability with new data (D02 canary).
5. The loadout's equip sequence is pack-specific (enumerators, slot bytes): unchanged by this step; a new weapon works only if it is equippable by that same sequence (to be checked in the canary, not assumed).

## Files claimed (mailbox claim before editing)

New: `RPGCombatCatalog.h/.cpp`, `Scripts/Editor/make_combat_catalog.py`, new tests in `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp`, new driver `Scripts/Editor/pie_combat_catalog.py` (+ one row in `RunDrivers.ps1`, owner-visible change to a dirty file: claimed for the one row only). Edited: `RPGBuildRules.h`, `RPGBuildSelect.cpp/.h`, `RPGBuildSelectRules.h`, `RPGBuildLoadout.cpp/.h`. Content: `Content/OneBossFight/Data/Catalog/*` (new). Nothing else.
