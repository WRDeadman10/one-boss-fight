"""Creates the weapon attack table asset /Game/OneBossFight/Data/DA_WeaponAttacks (log prefix [WeaponTable]) with the Freeze starting values that the class constructor fills in (Player/RPGWeaponAttackTable).
Run once: an existing asset is NEVER touched (it holds what the owner tuned; an asset that other assets or code reference must not be deleted and recreated). Run with Scripts/run_in_editor.py."""
import unreal

log = lambda m: unreal.log("[WeaponTable] " + m)
FOLDER = "/Game/OneBossFight/Data"
NAME = "DA_WeaponAttacks"
PATH = FOLDER + "/" + NAME

if not unreal.EditorAssetLibrary.does_directory_exist(FOLDER):
    unreal.EditorAssetLibrary.make_directory(FOLDER)
if unreal.EditorAssetLibrary.does_asset_exist(PATH):
    table = unreal.EditorAssetLibrary.load_asset(PATH)
    log("%s exists already, left as it is (%d rows)" % (PATH, len(table.get_editor_property("rows"))))
else:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    table = tools.create_asset(NAME, FOLDER, unreal.RPGWeaponAttackTable, unreal.DataAssetFactory())
    if table is None:
        log("FAILED to create %s" % PATH)
    else:
        unreal.EditorAssetLibrary.save_loaded_asset(table)
        log("created %s with %d rows" % (PATH, len(table.get_editor_property("rows"))))
for row in table.get_editor_property("rows") if table else []:
    log("   %-22s %-10s posture %5.1f stamina %5.1f bleed %5.1f  %s" % (row.get_editor_property("weapon"), row.get_editor_property("kind").name, row.get_editor_property("posture_damage"), row.get_editor_property("stamina_cost"), row.get_editor_property("bleed_buildup"), row.get_editor_property("note")))
log("done")
