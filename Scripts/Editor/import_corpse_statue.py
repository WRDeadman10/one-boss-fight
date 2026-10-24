"""Imports (or re-imports in place) the corpse statue /Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue from Import/Boss01/Weapons/CorpseStatue and prints what the engine reads (log prefix [Statue]): bounds, triangles, UV channels, slots. The three slots get the arena stand-in materials (the remains actor overrides them with its own dissolve MIDs by slot name). Saves the mesh."""
import os
import unreal

log = lambda m: unreal.log("[Statue] " + m)
proj = unreal.SystemLibrary.get_project_directory()
DEST, NAME = "/Game/OneBossFight/Boss01/Remains", "SM_Boss01_CorpseStatue"
t = unreal.AssetImportTask()
t.filename = os.path.join(proj, "Import", "Boss01", "Weapons", "CorpseStatue", NAME + ".fbx").replace("/", os.sep)
t.destination_path, t.destination_name = DEST, NAME
t.automated, t.save, t.replace_existing, t.replace_existing_settings = True, False, True, True
o = unreal.FbxImportUI()
o.set_editor_property("import_mesh", True)
o.set_editor_property("import_as_skeletal", False)
o.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
o.set_editor_property("import_materials", False)
o.set_editor_property("import_textures", False)
o.set_editor_property("import_animations", False)
t.options = o
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
m = unreal.load_asset(DEST + "/" + NAME)
box = m.get_bounding_box()
L = unreal.EditorStaticMeshLibrary
log("bounds min (%.1f %.1f %.1f) max (%.1f %.1f %.1f), verts %d, triangles %d, uv channels %d" % (box.min.x, box.min.y, box.min.z, box.max.x, box.max.y, box.max.z, L.get_number_verts(m, 0), L.get_number_triangles(m, 0) if hasattr(L, "get_number_triangles") else -1, L.get_num_uv_channels(m, 0)))
wanted = {"M_Boss01_AshPlate": "MI_Arena_Stone", "M_Boss01_EmberCore": "M_Gate_Rune", "M_Boss01_AncientSteel": "MI_Arena_Pillar"}
for i, s in enumerate(m.get_editor_property("static_materials")):
    n = str(s.material_slot_name)
    if n in wanted:
        m.set_material(i, unreal.load_asset("/Game/OneBossFight/Environment/Materials/" + wanted[n]))
    log("slot %d %s" % (i, n))
log("save: %s" % unreal.EditorAssetLibrary.save_asset(DEST + "/" + NAME, only_if_is_dirty=False))
