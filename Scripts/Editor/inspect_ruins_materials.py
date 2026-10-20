"""Texture and key scalar values of candidate Deadly Ruins material instances. Headless."""
import unreal
log = lambda m: unreal.log("[RuinsMat] " + m)
lib = unreal.MaterialEditingLibrary
for n in ("MI_Floor_Relief", "MI_TIling_Brick_floor", "MI_Rockwall_Large", "MI_TIling_Metal"):
    mi = unreal.load_asset("/Game/Deadly_Ruins/Materials/Instances/" + n)
    parent = mi.get_editor_property("parent")
    log("%s parent=%s" % (n, parent.get_name()))
    for t in lib.get_texture_parameter_names(mi):
        v = lib.get_material_instance_texture_parameter_value(mi, t)
        log("   tex %s = %s" % (t, v.get_name() if v else None))
    for sname in ("WorldAlign Material Tiling", "Object Tiling Amount", "World Blend Opacity", "Tiling", "Detail Tiling", "Object Tile Mask Power"):
        if sname in [str(x) for x in lib.get_scalar_parameter_names(mi)]:
            log("   %s = %s" % (sname, lib.get_material_instance_scalar_parameter_value(mi, sname)))
