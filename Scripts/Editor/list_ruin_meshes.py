"""
Lists the copied Megascans / custom static meshes with size (cm), Nanite flag and vertex count, plus the surface material instances. Log prefix [Meshes].
Run with Scripts/run_in_editor.py. Loading every mesh takes a minute the first time.
"""
import unreal, re

log = lambda m: unreal.log("[Meshes] " + m)
ar = unreal.AssetRegistryHelpers.get_asset_registry()
pat = re.compile(r"(Church|Brick_Ruins|Broken_Brick|Modular_Ruins|Stone_Wall_Trim|Roman|Stone_Structure|Dead_Tree|Skull|Sword|Chain|Barrel|Crate|Table|Pole|Beam|Stakes|Mushroom|Coffin|Vase|Rubble|Slab|Limestone|Medieval|Door|Arch|Bridge|Candle|Lantern|Bells|Flame|Fog|Spike)", re.I)
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for root in ("/Game/MS/3D", "/Game/CustomAssets"):
    for ad in ar.get_assets_by_path(root, recursive=True):
        if str(ad.asset_class_path.asset_name) != "StaticMesh":
            continue
        n = str(ad.asset_name)
        if not pat.search(n) and not pat.search(str(ad.package_path)):
            continue
        try:
            m = ad.get_asset()
            e = m.get_bounds().box_extent
            nan = m.get_editor_property("nanite_settings").get_editor_property("enabled")
            log("%-95s %5.0f x %5.0f x %5.0f nanite=%s verts=%d mats=%d" % (str(ad.package_name).replace("/Game/", ""), e.x * 2, e.y * 2, e.z * 2, nan, sub.get_number_verts(m, 0), len(m.static_materials)))
        except Exception as ex:
            log("ERR %s %s" % (n, ex))
for ad in ar.get_assets_by_path("/Game/MS/Surfaces", recursive=True) + ar.get_assets_by_path("/Game/MS/Decals", recursive=True):
    if str(ad.asset_class_path.asset_name) in ("MaterialInstanceConstant", "Material"):
        log("MAT %s" % str(ad.package_name).replace("/Game/", ""))
