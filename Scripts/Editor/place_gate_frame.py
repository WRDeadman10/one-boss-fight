"""Imports Antigravity's M-08 fog gate frame (SM_Boss01_FogGateFrame) into /Game/OneBossFight/Environment/Gate, gives its three slots the arena's own materials and places it around the FogGate actor (log prefix [GateFrame]).
Idempotent: removes an earlier actor labelled FogGateFrame and re-imports the mesh in place (nothing references the mesh but that actor). Does NOT save: look at the result first, then save the level and the assets.
Run with Scripts/run_in_editor.py. Frame: 1070 x 168 x 723 cm, opening 800 cm wide centred on x = 0, depth along y, MistCenter socket at z 300 (Import/Boss01/Weapons/FogGate/SM_Boss01_FogGateFrame_Sockets.txt)."""
import os
import unreal

log = lambda m: unreal.log("[GateFrame] " + m)
proj = unreal.SystemLibrary.get_project_directory()
DEST = "/Game/OneBossFight/Environment/Gate"
MATS = "/Game/OneBossFight/Environment/Materials/"
SLOT_MATERIAL = {"M_Boss01_Arch_Stone": "MI_Arena_Stone", "M_Boss01_Arch_Trim": "MI_Arena_Pillar", "M_Boss01_Arch_Rune": "M_Gate_Rune"}

t = unreal.AssetImportTask()
t.filename = os.path.join(proj, "Import", "Boss01", "Weapons", "FogGate", "SM_Boss01_FogGateFrame.fbx").replace("/", os.sep)
t.destination_path = DEST
t.destination_name = "SM_Boss01_FogGateFrame"
t.automated = True
t.save = False
t.replace_existing = True
t.replace_existing_settings = True
o = unreal.FbxImportUI()
o.set_editor_property("import_mesh", True)
o.set_editor_property("import_as_skeletal", False)
o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
o.set_editor_property("import_materials", False)
o.set_editor_property("import_textures", False)
o.set_editor_property("import_animations", False)
t.options = o
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh = unreal.load_asset(DEST + "/SM_Boss01_FogGateFrame")
if not mesh:
    raise RuntimeError("frame did not import")
slots = [str(s.material_slot_name) for s in mesh.get_editor_property("static_materials")]
for i, name in enumerate(slots):
    mat = unreal.load_asset(MATS + SLOT_MATERIAL[name]) if name in SLOT_MATERIAL else None
    if mat:
        mesh.set_material(i, mat)
    log("slot %d %s -> %s" % (i, name, mat.get_name() if mat else "NONE"))

for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label() == "FogGateFrame":
        unreal.EditorLevelLibrary.destroy_actor(a)
gate = next(a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label() == "FogGate")
gl = gate.get_actor_location()
actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(gl.x, gl.y, 0.0), unreal.Rotator(0, 0, 90.0))
actor.set_actor_label("FogGateFrame")
actor.set_folder_path("Dressing")
comp = actor.static_mesh_component
comp.set_static_mesh(mesh)
comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
log("frame placed at %s yaw 90, opening 800 cm along world y" % actor.get_actor_location())
log("DONE")
