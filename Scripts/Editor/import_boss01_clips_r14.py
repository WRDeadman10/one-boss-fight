"""Imports the clips accepted on the numbers from Antigravity's Brief 13/14 deliveries (log prefix [ImportClips14]) into /Game/OneBossFight/Boss01/Animations as assets that nothing references yet (an older delivery of the same name is replaced in place when no asset references it): DormantIdle, Wake, A1_QuickSlash, A3a_Combo1, A3b_Combo2, A2_Raise, A2_ApexHold, A2_Slam.
An asset is never deleted and recreated; DeathLegend is compared with the scratch import of /Game/OneBossFight/_Review13 (run review_report13.py first) and re-imported IN PLACE (the same asset, so every reference stays) only when the project's copy has worse feet (lowest ball below -1 cm or lowest ankle below 3 cm).
Nothing is wired to the game here. Run with Scripts/run_in_editor.py."""
import os
import unreal

log = lambda m: unreal.log("[ImportClips14] " + m)
proj = unreal.SystemLibrary.get_project_directory()
SKEL = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"
DEST = "/Game/OneBossFight/Boss01/Animations"
SCRATCH = "/Game/OneBossFight/_Review13/"
tools = unreal.AssetToolsHelpers.get_asset_tools()
skel = unreal.load_asset(SKEL)
POSE = unreal.AnimPoseExtensions
WORLD = unreal.AnimPoseSpaces.WORLD
NEW = [("AN_Boss01_DormantIdle", 5.0), ("AN_Boss01_Wake", 3.5), ("AN_Boss01_A1_QuickSlash", 1.2), ("AN_Boss01_A3a_Combo1", 0.8), ("AN_Boss01_A3b_Combo2", 1.3333), ("AN_Boss01_A2_Raise", 0.6), ("AN_Boss01_A2_ApexHold", 1.1667), ("AN_Boss01_A2_Slam", 1.3667)]


def options():
    o = unreal.FbxImportUI()
    o.set_editor_property("import_mesh", False)
    o.set_editor_property("import_as_skeletal", False)
    o.set_editor_property("import_animations", True)
    o.set_editor_property("skeleton", skel)
    o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    return o


def do_import(name, replace):
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Boss01", "Animations", name + ".fbx").replace("/", os.sep)
    t.destination_path = DEST
    t.destination_name = name
    t.automated = True
    t.save = True
    t.replace_existing = replace
    t.replace_existing_settings = replace
    t.options = options()
    tools.import_asset_tasks([t])
    return unreal.load_asset(DEST + "/" + name)


def feet(anim):
    length = anim.get_editor_property("sequence_length")
    la, lb = 9999.0, 9999.0
    for i in range(13):
        opts = unreal.AnimPoseEvaluationOptions()
        opts.set_editor_property("should_retarget", False)
        opts.set_editor_property("extract_root_motion", False)
        p = POSE.get_anim_pose_at_time(anim, max(0.0, length * i / 12.0 - (0.0001 if i == 12 else 0.0)), opts)
        for b in ("foot_l", "foot_r"):
            la = min(la, POSE.get_bone_pose(p, b, WORLD).translation.z)
        for b in ("ball_l", "ball_r"):
            lb = min(lb, POSE.get_bone_pose(p, b, WORLD).translation.z)
    return la, lb


for name, want in NEW:
    path = DEST + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        a = unreal.load_asset(path)
        old = a.get_editor_property("sequence_length")
        # an older delivery of this clip: replaced IN PLACE (the same asset, every reference stays) only when nothing references it (checked 2026-10-24: no referencer for any of the eight)
        if unreal.EditorAssetLibrary.find_package_referencers_for_asset(path, True):
            log("%s (length %.4f) is referenced: left as it is" % (name, old))
            continue
        a = do_import(name, True)
        L = a.get_editor_property("sequence_length")
        log("%s %s: older delivery (length %.4f) replaced in place, now length %.4f (intended %.4f)" % ("PASS" if abs(L - want) < 0.002 else "FAIL", name, old, L, want))
        continue
    a = do_import(name, False)
    if a:
        L = a.get_editor_property("sequence_length")
        log("%s %s imported, length %.4f (intended %.4f)" % ("PASS" if abs(L - want) < 0.002 else "FAIL", name, L, want))
    else:
        log("FAIL %s did not import" % name)

# DeathLegend: compare, replace in place only if the project's copy has worse feet
cur_path = DEST + "/AN_Boss01_DeathLegend"
cur = unreal.load_asset(cur_path)
new = unreal.load_asset(SCRATCH + "AN_Boss01_DeathLegend")
if cur and new:
    ca, cb = feet(cur)
    na, nb = feet(new)
    log("DeathLegend in the project: lowest ankle %.1f, ball %.1f; the delivered clip: ankle %.1f, ball %.1f" % (ca, cb, na, nb))
    if cb < -1.0 or ca < 3.0:
        again = do_import("AN_Boss01_DeathLegend", True)
        a2, b2 = feet(again)
        log("DeathLegend re-imported in place: lowest ankle %.1f, ball %.1f" % (a2, b2))
    else:
        log("DeathLegend in the project already has good feet: left as it is")
else:
    log("DeathLegend comparison skipped (the project copy or the scratch copy is missing)")
log("DONE")
