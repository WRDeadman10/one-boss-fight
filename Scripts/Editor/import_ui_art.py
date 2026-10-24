"""Imports AG's UI art from Import/Boss01/UI into /Game/OneBossFight/UI/Art (log prefix [UIArt]): the three build icons and the flask counter textures (full, half, empty, plate), as UI textures (no mips, clamp, sRGB, UI compression, never streamed). Re-imports in place. Run with Scripts/run_in_editor.py."""
import os
import unreal

log = lambda m: unreal.log("[UIArt] " + m)
proj = unreal.SystemLibrary.get_project_directory()
DEST = "/Game/OneBossFight/UI/Art"
NAMES = ["T_Boss01_Icon_Starter", "T_Boss01_Icon_Strength", "T_Boss01_Icon_Dex", "T_Boss01_Flask_Full", "T_Boss01_Flask_Half", "T_Boss01_Flask_Empty", "T_Boss01_FlaskPlate"]
tools = unreal.AssetToolsHelpers.get_asset_tools()
for n in NAMES:
    t = unreal.AssetImportTask()
    t.filename = os.path.join(proj, "Import", "Boss01", "UI", n + ".png").replace("/", os.sep)
    t.destination_path, t.destination_name = DEST, n
    t.automated, t.save, t.replace_existing = True, False, True
    tools.import_asset_tasks([t])
    tex = unreal.load_asset(DEST + "/" + n)
    tex.set_editor_property("srgb", True)
    tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property("address_x", unreal.TextureAddress.TA_CLAMP)
    tex.set_editor_property("address_y", unreal.TextureAddress.TA_CLAMP)
    tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
    tex.set_editor_property("never_stream", True)
    log("%s %dx%d saved: %s" % (n, tex.blueprint_get_size_x(), tex.blueprint_get_size_y(), unreal.EditorAssetLibrary.save_asset(DEST + "/" + n, only_if_is_dirty=False)))
log("DONE")
