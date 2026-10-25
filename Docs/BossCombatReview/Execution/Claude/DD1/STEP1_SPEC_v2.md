# DD-1 step 1 specification, revision 2 (Claude, after Codex D06 R1 to R5; v1 `STEP1_SPEC.md` kept for provenance)

Status: SPECIFICATION ONLY, not started, nothing claimed. Preconditions before any file is touched: (a) the CLEAN step 0 baseline (fresh editor, `STEP0_BASELINE.md` supplement 1) is recorded and classified, (b) automation tests on the current binary are recorded, (c) Codex re-reviews this revision and accepts it. Behaviour-identical: every value, text, order, decision and call sequence of today's three builds stays the same; the new capability is that a fourth build and a new weapon can be added as DATA and travel the whole selection path.

## 0. What changed from v1 and why

| Codex finding | Change |
|---|---|
| R1 the fourth build cannot travel through the enum path | The stable `BuildId` (FName) travels through every step: parse, requested/chosen/equipped state, same-choice detection, queue and defer, `CallEquip` lookup, verification, HUD. The three legacy builds keep their enum slots through an adapter that exposes ONLY those three; an id with no legacy slot returns an explicit failure (`EResolve::UnknownId`), never an existing build. The old behaviour that an invalid ENUM value clamps to Dex (`RPGBuildRules.h:54`, `RPGCodexTests.cpp:124-130`) stays in the legacy enum API untouched and is tested separately from the new id path. The legacy-slot mapping is a pinned explicit field (`LegacySlot` 0/1/2 on the three shipped entries only), independent of `UiOrder`. |
| R2 one complete epoch, no per-lookup fallback | At startup the registry builds ONE immutable snapshot (`FRPGCombatEpoch`, value copies only: FName, FString, FSoftObjectPath, numbers; no pointer into an asset or a temporary string) from EITHER the validated catalog OR the built-in legacy table, publishes it once, and every related operation carries the epoch id. No lookup mixes the two sources; an unknown id in an accepted catalog is an error. No reload and no source switch during a fight or an equip transaction; a switch is possible only at a safe boundary (process start, or a test context before the world starts). Assets are used only while the snapshot is built; the snapshot owns its data, so asset reload or GC cannot invalidate it; world teardown and test contexts restore the previous epoch. Validation (whole closure, before publication): schema version; case-normalised unique `BuildId`, console names and aliases; reserved words empty/none/off rejected as names; every build names an existing weapon; the weapon item path resolves to an asset of the weapon-item class, the actor class and ability class names resolve (asset registry), the style name is non-empty; aliases do not collide with other styles; attack-table coverage is listed per weapon (missing rows use the table's fallback: a warning, not an error); soft dependencies are under a cooked directory; deterministic UI order (`UiOrder`, ties by `BuildId`). Diagnostics name the field path and the source of the snapshot. |
| R3 the rollback test mutated assets | No asset rename or delete anywhere. Source selection is a startup/test input: console variable `rpg.CatalogSource` (`auto` default: catalog if valid else legacy; `legacy`; `data`; `invalid` for a built-in malformed fixture) and a non-Shipping test injection (`RPGCombatRegistry::PushTestCatalog/PopTestCatalog`) used before the world starts; each mode is proven in a fresh PIE session (the existing multi-PIE driver pattern). Rollback of code: before editing any existing file its preimage (full copy plus sha256) is stored under `Claude/DD1/preimages/`; the edited files are clean in git today (not in the dirty list), so `git diff` is the exact reversal; no reset, checkout, stash or clean, ever. |
| R4 parity and fourth-row input underspecified | Witness list extended (section 3); the fourth-row input and layout are defined (section 4). |
| R5 baseline closure | `STEP0_BASELINE.md` supplement 1 and `STEP0_SUPPLEMENT1.json` (separate, versioned files; the first manifest is never overwritten). |

## 1. Goal and non-goals

Goal: builds and their weapons come from data through one registry; a fourth build and a new weapon are addable as data and work end to end through the selector and the loadout. Non-goals: no combat, boss, phase or balance change; no change to the pack's equip call sequence (enumerators, slot byte, quickslot lock, in-fight defer), startup delay and retries; no new weapon art or content; no edit of any pack asset; `URPGWeaponAttackTable` values unchanged (it stays the compatibility view, keyed by style name; a new weapon's rows are data in that asset).

## 2. Code and assets

New: `Source/OneBossFight/Player/RPGCombatCatalog.h/.cpp` (`URPGWeaponDefinition`, `URPGBuildDefinition`, `URPGCombatCatalog` UPrimaryDataAssets; `FRPGCombatEpoch` snapshot; `RPGCombatRegistry` build/validate/publish, `ResolveBuildId`, `ParseText`, `StyleToBuildId`, `LegacySlotOf`), `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp`, `Scripts/Editor/make_combat_catalog.py` (creates the seven assets, never overwrites; values copied from `RPGBuildRules.h:50-52` and `BuildOfStyle`), `Scripts/Editor/pie_combat_catalog.py` (one row in `RunDrivers.ps1`: that file is dirty and shared with the owner; only that one row is added). Assets: `Content/OneBossFight/Data/Catalog/DA_CombatCatalog`, `DA_Weapon_Sword/Claymore/DualSwords`, `DA_Build_Starter/Strength/Dex` (always-cooked directory, `Config/DefaultGame.ini:22`).

Edited existing files (the consumer closure from D06 and my own search): `Player/RPGBuildRules.h` (legacy functions keep signature and result; they delegate through the epoch's legacy-slot adapter), `UI/RPGBuildSelectRules.h` and `UI/RPGBuildSelect.cpp/.h` (rows, hit testing, keys, icons from the epoch), `Player/RPGBuildLoadout.h/.cpp` (state and decisions carry `BuildId`; `CallEquip`, verification and the HUD line resolve through the epoch; the old `ERPGBuild` members remain as a derived legacy view). `UI/RPGBossHud.cpp:488-491` consumes `GetBuildLine` and is a witness only (no edit unless the line source changes). No other file.

## 3. Parity witnesses (current binary, clean baseline)

Existing: `pie_builds` (103), `pie_build_hyperarmor` (20), `pie_build_hud` (8), `pie_build_select` (18), `pie_flask_hud` (7), `pie_hyperarmor`, `pie_bleed`, `pie_stamina_cost`, `pie_hit_intake`, `pie_posture_hits`, `pie_boss_hud`, the 37 automation tests (including `OneBossFight.Build.*` and the `RPGCodexTests` enum-99-to-Dex check).
Pinned behaviours to add as explicit assertions on the legacy path BEFORE the change and keep after: the `DescribeStyle` labels (Starter "Sword and Shield" versus "Sword", Dex "Dual Swords" versus "Twinblades"; `RPGBuildRules.h:257-294`), actual versus chosen build in the HUD line, off-build and unknown wording, the equipping / next-fight / not-equipped suffixes, an invalid choice leaving state unchanged, parser behaviour (quotes, case, spaces, str/dexterity/sword aliases, empty/none/off), same-choice semantics, queue and defer, the quickslot call order, startup delay and retries, the in-fight lock and the failed-equip classification.

## 4. Fourth-row input and layout (RPGBuildSelect)

First three rows: unchanged position, keys 1 to 3, hit rectangles and icon order. Rows beyond three: appended downward at the same row spacing, keys 4 to 9 map to rows 4 to 9 in `UiOrder`, mouse hit testing from the same row geometry, keyboard/focus navigation extends in order, the stack is clamped inside the viewport (rows that do not fit are neither drawn nor selectable, logged once), an absent icon draws a neutral text-only placeholder. `BuildCount = 3` stays only for the legacy API and tests; no dynamic UI or runtime loop uses it.

## 5. New proofs

1. Automation: the legacy snapshot and the catalog snapshot are field-for-field equal (style, item path, actor, ability, HUD words, aliases, legacy slot, order); `Parse`/`BuildOfStyle` agree on a list of inputs including aliases, quotes and invalid text; the legacy enum API still returns Dex for enum 99; an unknown BuildId returns `UnknownId` and never Starter.
2. Automation: malformed catalogs (duplicate id or alias, empty style, unknown weapon, reserved name, bad schema version, soft dependency outside a cooked folder) are rejected with the field path and publication falls back to the COMPLETE legacy snapshot with the reason logged; no mixed snapshot is constructible (the test attempts to build one and asserts it fails).
3. PIE end to end (new `pie_combat_catalog.py`, fresh PIE per mode via `rpg.CatalogSource`): with `data` and with `legacy` the same three rows, same build line and same equip results as before (actual resolved item, actor, ability, style, attack-table row); with an injected FOURTH build that uses an existing pack weapon capability (a test catalog; no asset written) the build selects through the real selector and loadout: equipped style/item/ability, attack-table fallback row, a choice made during a fight deferred to the next fight and applied after reset, reapply after player respawn, HUD line, invalid id rejected with no state change. The real canary with new art and rows stays at P8.
4. Cook: `Content.CookCoverage` stays green with the new folder; a cold packaged load later (P8) shows no missing-path fallback.

## 6. Rollback and boundaries

Rollback = `rpg.CatalogSource legacy` (and, for code, restoring the stored preimages): the legacy snapshot answers everything, nothing else changes; never mid-fight or mid-equip. New files become unreferenced. No git reset, clean, stash or checkout by anyone; the owner commits.

## 7. Files claimed when step 1 starts (mailbox claim first)

New: `RPGCombatCatalog.h/.cpp`, `RPGCombatCatalogTests.cpp`, `make_combat_catalog.py`, `pie_combat_catalog.py`, `Content/OneBossFight/Data/Catalog/*`, `Claude/DD1/preimages/*`. Edited: `RPGBuildRules.h`, `RPGBuildSelectRules.h`, `RPGBuildSelect.cpp/.h`, `RPGBuildLoadout.h/.cpp`, one row of `RunDrivers.ps1`. Nothing else.

## 8. Open points for Codex

1. Is a console variable for the source selection acceptable in Shipping (proposal: compiled out; Shipping always `auto`)?
2. Epoch publication point: game instance subsystem initialization (a fresh epoch per PIE session, which the proofs need) versus module startup.
3. Is the neutral placeholder icon rule enough, or must a missing icon fail validation for non-legacy builds?
