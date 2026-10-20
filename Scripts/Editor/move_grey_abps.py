"""Moves the retargeted animation Blueprints that the batch left at /Game into the mirrored GreystonePack folders and saves them."""
import json
import unreal

DEST = "/Game/OneBossFight/GreystonePack"
PACK = "/Game/AdvancedARPGCombat"
log = lambda m: unreal.log("[GreyAbp] " + m)
survey = json.load(open(unreal.Paths.project_saved_dir() + "pack_anim_survey.json"))
mapping = json.load(open(unreal.Paths.project_saved_dir() + "greystone_retarget_map.json"))
reg = unreal.AssetRegistryHelpers.get_asset_registry()
roots = [str(d.asset_name) for d in reg.get_assets_by_path("/Game", recursive=False)]
log("assets at /Game root: %s" % [n for n in roots if "Grey" in n][:30])
for r in survey:
    if r["class"] != "AnimBlueprint" or r["path"] in mapping:
        continue
    cand = "/Game/%s_Grey" % r["name"]
    if not unreal.EditorAssetLibrary.does_asset_exist(cand):
        continue
    sub = r["path"][len(PACK):].rsplit("/", 1)[0]
    target = "%s%s/%s_Grey" % (DEST, sub, r["name"])
    if unreal.EditorAssetLibrary.rename_asset(cand, target):
        mapping[r["path"]] = target
        log("%s -> %s" % (r["name"], target))
json.dump(mapping, open(unreal.Paths.project_saved_dir() + "greystone_retarget_map.json", "w"))
unreal.EditorAssetLibrary.save_directory(DEST)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
log("mapping has %d entries" % len(mapping))
