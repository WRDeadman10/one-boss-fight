"""
Stage 3 (option A): retargets the Advanced ARPG pack's player animation set from its UE5 combat mannequin to Greystone.
Run in the editor (execute_script, Slate needed). Creates IK_CombatMannequin and RTG_CombatMannequin_To_Greystone in
/Game/OneBossFight/GreystonePack, batch-retargets sequences, montages, blend spaces, aim offsets and animation Blueprints
(references between them remapped by the batch), then moves the duplicates under /Game/OneBossFight/GreystonePack/<pack
sub path>. Writes Saved/greystone_retarget_map.json (old package -> new package). Set DRY = True to only list.
"""
import json
import unreal

DRY = False
DEST = "/Game/OneBossFight/GreystonePack"
PACK = "/Game/AdvancedARPGCombat"
SRC_MESH = PACK + "/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin"
GREY_MESH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone"
SUFFIX = "_Grey"
SKIP_ABP = {"ABP_Manny", "ABP_Quinn", "ABP_Manny_PostProcess", "ABP_Quinn_PostProcess", "ABP_HumanoidEnemyCharacter", "ABP_MagicEnemy", "ABP_Bow", "ABP_AI_Bow",
            "ArcherEnemyABP", "ABP_BowLayer", "ALI_CombatAnimLayers"}  # the layer interface is not skeleton bound: reused as is
log = lambda m: unreal.log("[GreyRetarget] " + m)

reg = unreal.AssetRegistryHelpers.get_asset_registry()
survey = json.load(open(unreal.Paths.project_saved_dir() + "pack_anim_survey.json"))
wanted = []
for r in survey:
    if "SK_CombatMannequin" not in r["skeleton"] and r["class"] != "AnimBlueprint":
        continue
    if r["class"] == "PoseAsset":
        continue
    if r["class"] == "AnimBlueprint" and (r["name"] in SKIP_ABP or "SK_CombatMannequin" not in r["skeleton"]):
        continue
    wanted.append(r)
log("%d assets selected: %s" % (len(wanted), {c: sum(1 for w in wanted if w["class"] == c) for c in {w["class"] for w in wanted}}))
if DRY:
    for w in wanted:
        if w["class"] == "AnimBlueprint":
            log("ABP " + w["name"])
    raise SystemExit

src_mesh = unreal.load_asset(SRC_MESH)
grey_mesh = unreal.load_asset(GREY_MESH)
unreal.EditorAssetLibrary.make_directory(DEST)

# IK rig for the pack mannequin, chains generated from the bone names, plus the retargeter.
rig_path = DEST + "/IK_CombatMannequin"
if unreal.EditorAssetLibrary.does_asset_exist(rig_path):
    unreal.EditorAssetLibrary.delete_asset(rig_path)
tools = unreal.AssetToolsHelpers.get_asset_tools()
rig = tools.create_asset("IK_CombatMannequin", DEST, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
rc = unreal.IKRigController.get_controller(rig)
rc.set_skeletal_mesh(src_mesh)
log("auto chains for mannequin: %s root %s" % (rc.apply_auto_generated_retarget_definition(), rc.get_retarget_root()))
unreal.EditorAssetLibrary.save_loaded_asset(rig)

rtg_path = DEST + "/RTG_CombatMannequin_To_Greystone"
if unreal.EditorAssetLibrary.does_asset_exist(rtg_path):
    unreal.EditorAssetLibrary.delete_asset(rtg_path)
rtg = tools.create_asset("RTG_CombatMannequin_To_Greystone", DEST, unreal.IKRetargeter, unreal.IKRetargetFactory())
ctl = unreal.IKRetargeterController.get_controller(rtg)
ctl.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, rig)
ctl.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, unreal.load_asset("/Game/OneBossFight/Characters/Greystone/IK_Greystone"))
ctl.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, src_mesh)
ctl.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, grey_mesh)
ctl.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
unreal.EditorAssetLibrary.save_loaded_asset(rtg)
log("retargeter created")

datas = [unreal.EditorAssetLibrary.find_asset_data(w["path"]) for w in wanted]
results = unreal.IKRetargetBatchOperation.duplicate_and_retarget(datas, src_mesh, grey_mesh, rtg, "", "", "", SUFFIX, True)
log("batch returned %d assets" % len(results))
mapping = {}
for old, new in zip(wanted, results):
    pass
# The batch returns the duplicates; match by name (old name + suffix).
by_name = {str(r.asset_name): r for r in results}
for w in wanted:
    new = by_name.get(w["name"] + SUFFIX)
    if new is None:
        log("no result for " + w["name"])
        continue
    sub = w["path"][len(PACK):].rsplit("/", 1)[0]
    target = "%s%s/%s" % (DEST, sub, str(new.asset_name))
    if unreal.EditorAssetLibrary.rename_asset(str(new.package_name), target):
        mapping[w["path"]] = target
    else:
        log("move failed " + str(new.package_name))
# duplicates created because of include-referenced that are not in `wanted`
extra = [r for r in results if str(r.asset_name).replace(SUFFIX, "") not in {w["name"] for w in wanted}]
for r in extra:
    target = "%s/Extra/%s" % (DEST, str(r.asset_name))
    unreal.EditorAssetLibrary.rename_asset(str(r.package_name), target)
    log("extra: %s -> %s" % (r.package_name, target))
json.dump(mapping, open(unreal.Paths.project_saved_dir() + "greystone_retarget_map.json", "w"), indent=0)
unreal.EditorAssetLibrary.save_directory(DEST)
log("done: %d moved" % len(mapping))
