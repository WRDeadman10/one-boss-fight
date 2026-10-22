"""Imports the Boss 01 clips accepted from Antigravity's Report 12 into /Game/OneBossFight/Boss01/Animations (log prefix [ImportClips]).
The six clips (PhaseRoar, StaggerFall, StaggerDown, Riposte_Player_Front, Riposte_Boss_Reaction, DeathLegend) are new assets: nothing that exists is replaced or deleted (a clip that already exists in the project is skipped and reported,
because other assets and the code reference it: delete nothing, replace by hand when the owner says so). The dormant idle and wake clips are NOT imported here (Brief 13 returns their sword).
Each clip is imported onto the mannequin skeleton the boss body uses, saved, and its length is read back and compared with the intended one. Run with Scripts/run_in_editor.py."""
import os
import unreal

log = lambda m: unreal.log("[ImportClips] " + m)
proj = unreal.SystemLibrary.get_project_directory()
SKEL = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"
DEST = "/Game/OneBossFight/Boss01/Animations"
tools = unreal.AssetToolsHelpers.get_asset_tools()
skel = unreal.load_asset(SKEL)

# name, intended length in seconds (30 fps)
CLIPS = [
    ("AN_Boss01_PhaseRoar", 1.8),
    ("AN_Boss01_StaggerFall", 0.7),
    ("AN_Boss01_StaggerDown", 1.0),
    ("AN_Riposte_Player_Front", 1.6),
    ("AN_Riposte_Boss_Reaction", 2.0),
    ("AN_Boss01_DeathLegend", 3.5),
]

results = []


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def options():
    o = unreal.FbxImportUI()
    o.set_editor_property("import_mesh", False)
    o.set_editor_property("import_as_skeletal", False)
    o.set_editor_property("import_animations", True)
    o.set_editor_property("skeleton", skel)
    o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    return o


check("the mannequin skeleton loads", skel is not None, SKEL)
for name, length in CLIPS:
    path = DEST + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        existing = unreal.load_asset(path)
        check("%s already in the project: skipped, length %.4f s" % (name, existing.get_editor_property("sequence_length")), abs(existing.get_editor_property("sequence_length") - length) < 0.001)
        continue
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Boss01", "Animations", name + ".fbx").replace("/", os.sep)
    t.destination_path = DEST
    t.destination_name = name
    t.automated = True
    t.save = True
    t.replace_existing = False
    t.replace_existing_settings = False
    t.options = options()
    tools.import_asset_tasks([t])
    asset = unreal.load_asset(path)
    got = asset.get_editor_property("sequence_length") if asset else -1.0
    check("%s imported, length %.4f s (intended %.1f)" % (name, got, length), asset is not None and abs(got - length) < 0.001, "asset %s" % (asset.get_path_name() if asset else None))
clip = unreal.load_asset(DEST + "/AN_Riposte_Player_Front")
if clip is not None and not clip.get_editor_property("enable_root_motion"):
    clip.set_editor_property("enable_root_motion", True)  # the player's strike travels 90 cm by its root motion; see set_riposte_root_motion.py
    unreal.EditorAssetLibrary.save_loaded_asset(clip)
check("the player's riposte clip has root motion switched on", clip is not None and clip.get_editor_property("enable_root_motion"))
log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
