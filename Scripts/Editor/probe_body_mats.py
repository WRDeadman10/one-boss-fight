"""Prints the material slots of SK_Boss01_Body and the textures each referenced material uses (log prefix [BodyMats]); reports missing files."""
import unreal

log = lambda m: unreal.log("[BodyMats] " + m)
body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
for s in body.get_editor_property("materials"):
    mat = s.get_editor_property("material_interface")
    log("slot %s -> %s" % (s.get_editor_property("material_slot_name"), mat.get_path_name() if mat else None))
    if mat:
        try:
            tex = unreal.MaterialEditingLibrary.get_used_textures(mat) if hasattr(unreal.MaterialEditingLibrary, "get_used_textures") else []
        except Exception as e:
            tex = []
            log("   textures ERR %s" % e)
        for t in tex:
            log("   texture %s" % (t.get_path_name() if t else None))
