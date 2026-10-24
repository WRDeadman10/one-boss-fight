"""Third part of the engine review of Antigravity's deliveries (log prefix [Review13c]): imports the fog gate frame and the statue (static meshes) into the scratch folder /Game/OneBossFight/_Review13 and prints bounds, triangles, material slots and sockets as the engine reads them.
Run with Scripts/run_in_editor.py."""
import os
import unreal

log = lambda m: unreal.log("[Review13c] " + m)
proj = unreal.SystemLibrary.get_project_directory()
tools = unreal.AssetToolsHelpers.get_asset_tools()
DEST = "/Game/OneBossFight/_Review13"
MESHES = [("Weapons/FogGate/SM_Boss01_FogGateFrame.fbx", "SM_Boss01_FogGateFrame"), ("Weapons/CorpseStatue/SM_Boss01_CorpseStatue.fbx", "SM_Boss01_CorpseStatue"), ("Weapons/CorpseStatue/SM_Boss01_CorpseStatue_Sculpt.fbx", "SM_Boss01_CorpseStatue_Sculpt")]
for rel, name in MESHES:
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Boss01", rel).replace("/", os.sep)
    t.destination_path = DEST
    t.destination_name = name
    t.automated = True
    t.save = False
    t.replace_existing = True
    t.replace_existing_settings = True
    o = unreal.FbxImportUI()
    o.set_editor_property("import_mesh", True)
    o.set_editor_property("import_as_skeletal", False)
    o.set_editor_property("import_animations", False)
    o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
    t.options = o
    tools.import_asset_tasks([t])
    m = unreal.load_asset(DEST + "/" + name)
    if not m:
        log("FAIL %s did not import" % name)
        continue
    box = m.get_bounding_box()
    sz = box.max - box.min
    slots = [str(s.material_slot_name) for s in m.get_editor_property("static_materials")]
    sockets = [(n, str(m.find_socket(n).relative_location) if m.find_socket(n) else "missing") for n in ("MistCenter", "GateLeft", "GateRight")]
    log("%s: size %.0f x %.0f x %.0f cm, min (%.0f %.0f %.0f) max (%.0f %.0f %.0f), triangles %d, slots %s, sockets %s" % (name, sz.x, sz.y, sz.z, box.min.x, box.min.y, box.min.z, box.max.x, box.max.y, box.max.z, unreal.EditorStaticMeshLibrary.get_number_triangles(m, 0) if hasattr(unreal.EditorStaticMeshLibrary, "get_number_triangles") else -1, slots, sockets))
log("DONE")
