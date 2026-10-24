# B12 — Build Icons and Flask Overlay

## Implemented

- `UI/RPGBuildSelect` soft-loads the three imported 256 px build icons in `BeginPlay`, before the panel can open. `URPGBuildSelectWidget` draws each optional 32 px icon 112 px left of its existing row text. A missing texture collapses only that icon; its text, row selection, keyboard keys and mouse hit area are unchanged.
- Added `UI/RPGFlaskHudRules.h`, `UI/RPGFlaskHud.h/.cpp` and `Tests/RPGFlaskHudTests.cpp`. The overlay reads the live pack `HealthPotion` item through `BP_EquipmentComponent_C.EquipmentSlots[].Items[].Item_/Amount_`; it never writes the item or the pack widget. The pack evidence is the HealthPotion asset's `MaxCount` and `GA_ConsumeHealthPotion` references, and the pack `WB_QuickSlot` fields `EquipmentSlots`, `Items_`, `Item_`, and `Amount_`.
- The first populated reflected amount is recorded as the starting maximum. Fill rules: unavailable for no count or no maximum; `0` is Empty; a positive count `<= 2/3` is Half; strictly `> 2/3` is Full. Thus a normal 10-count spawn displays Full for 7--10, Half for 1--6, Empty at 0.
- The overlay is created only when all plate and three flask textures load. It is a 160 x 96 bottom-left own UMG widget at `(22, -22)`, using the supplied plate's 68 x 74 icon frame and 64 x 64 number field. The pack widget is neither found nor mutated: the own overlay is drawn over that corner at viewport Z 60.
- `RPGPlayerMovesSubsystem` attaches the overlay to the player. `/Game/OneBossFight/UI` is now always cooked. `pie_flask_hud.py`, `RunDrivers.ps1` (minimum 7), `TEST_PLAN.md` `FLASK-01`, and an automation fill-rule test cover the contract.

## Symbol Check

- `URPGFlaskHud::{GetFlaskCount,GetFlaskMaximum,GetFlaskFillState,IsOverlayShown,RefreshForTest}` are declared in `Source/OneBossFight/UI/RPGFlaskHud.h:46-59` and are the only new component calls made by the driver.
- The driver’s `debug_set_player_health` maps to `URPGCombatDebug::DebugSetPlayerHealth`, declared in `Source/OneBossFight/Player/RPGCombatDebug.h:83`; `inject_action` maps to `RPGInputTestUtils::InjectAction`, declared in `Source/OneBossFight/Combat/RPGInputTestUtils.h:25`.
- No component receives `set_editor_property`; the driver uses one real `IA_UseTool` injected press after lowering the player health through the existing debug test helper.

## Validation

- Ran `python -I` AST parsing for `Scripts/Editor/pie_flask_hud.py`: passed.
- Re-read all changed C++ and reflection field names against the pack uasset string tables and the existing loadout reflection implementation.
- I did **not** build, start the editor, run PIE, package, or run the automation tests. Claude must compile and run `OneBossFight.UI.FlaskFill` and `pie_flask_hud.py`.
