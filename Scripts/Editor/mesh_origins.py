"""
Prints bounds origin (offset of the box centre from the pivot, cm) and size for the structural meshes used by the arena dressing. Log prefix [Origins].
Run with Scripts/run_in_editor.py (meshes are already built, so it is quick).
"""
import unreal, re

ar = unreal.AssetRegistryHelpers.get_asset_registry()
pat = re.compile(r"(Brick_Ruins|Broken_Brick|Ruins_Wall|Church_Ruin_Stone|ChurchRuin_Stone|ArchWay|ArchTop|Bridge|Arch_|StairArch|Roman_Column|Stone_Structure|Coffin|External_Column|Decoration_Stone|Vines)", re.I)
for root in ("/Game/MS/3D", "/Game/CustomAssets"):
    for ad in ar.get_assets_by_path(root, recursive=True):
        if str(ad.asset_class_path.asset_name) != "StaticMesh" or not pat.search(str(ad.asset_name)):
            continue
        m = ad.get_asset()
        b = m.get_bounds()
        o, e = b.origin, b.box_extent
        unreal.log("[Origins] %-70s origin=(%6.0f,%6.0f,%6.0f) size=(%5.0f,%5.0f,%5.0f)" % (str(ad.asset_name)[:70], o.x, o.y, o.z, e.x * 2, e.y * 2, e.z * 2))
