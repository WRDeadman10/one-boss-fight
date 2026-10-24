"""Imports (or re-imports in place) AG's engine-ready Lord Shiva shrine /Game/OneBossFight/Environment/Shrine/SM_Boss01_ShivaShrine from Import/Boss01/Weapons/Shrine and prints what the engine reads (log prefix [Shrine]): bounds, vertex count, UV channels, slots, sockets, and the centroids of the vertices per height band (the front of the statue must face +Y: the face and the chest centroid y > 0). The slots get the arena's stand-in materials; saves the mesh. Run with Scripts/run_in_editor.py."""
import os
import unreal

log = lambda m: unreal.log("[Shrine] " + m)
proj = unreal.SystemLibrary.get_project_directory()
DEST, NAME = "/Game/OneBossFight/Environment/Shrine", "SM_Boss01_ShivaShrine"
t = unreal.AssetImportTask()
t.filename = os.path.join(proj, "Import", "Boss01", "Weapons", "Shrine", NAME + ".fbx").replace("/", os.sep)
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
log("bounds min (%.1f %.1f %.1f) max (%.1f %.1f %.1f), verts %d, uv channels %d" % (box.min.x, box.min.y, box.min.z, box.max.x, box.max.y, box.max.z, L.get_number_verts(m, 0), L.get_num_uv_channels(m, 0)))
slots = [str(s.material_slot_name) for s in m.get_editor_property("static_materials")]
log("slots %s" % slots)
for sk in ("SOCKET_Interact", "SOCKET_Glow", "Interact", "Glow"):
    s = m.find_socket(sk)
    if s:
        log("socket %s at %s" % (sk, s.relative_location))
d = m.get_static_mesh_description(0)
pts = [d.get_vertex_position(unreal.VertexID(i)) for i in range(d.get_vertex_count())]
for lo, hi in ((0, 60), (60, 120), (120, 180), (180, 240), (240, 301)):
    sel = [p for p in pts if lo <= p.z < hi]
    if sel:
        log("z %d..%d: %d verts, centroid x %.1f y %.1f, x %.0f..%.0f, y %.0f..%.0f" % (lo, hi, len(sel), sum(p.x for p in sel) / len(sel), sum(p.y for p in sel) / len(sel), min(p.x for p in sel), max(p.x for p in sel), min(p.y for p in sel), max(p.y for p in sel)))
wanted = {"M_Boss01_Shiva_Stone": "MI_Arena_Stone", "M_Boss01_Shiva_Metal": "MI_Arena_Pillar", "M_Boss01_Shiva_Cloth": "MI_Arena_Slab", "M_Boss01_Shiva_Rock": "MI_Arena_Stone"}
for i, s in enumerate(m.get_editor_property("static_materials")):
    n = str(s.material_slot_name)
    if n in wanted:
        m.set_material(i, unreal.load_asset("/Game/OneBossFight/Environment/Materials/" + wanted[n]))
log("save: %s" % unreal.EditorAssetLibrary.save_asset(DEST + "/" + NAME, only_if_is_dirty=False))
log("DONE")
