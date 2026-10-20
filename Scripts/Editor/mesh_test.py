"""
Spawns a row of candidate meshes at x = 700 (folder "MeshTest") with their bounds logged, so they can be compared in a viewport shot. Run again to clear and respawn.
Edit CANDIDATES (asset name regex, scale). Log prefix [MeshTest]. Run with Scripts/run_in_editor.py.
"""
import re
import unreal

# (asset name regex, scale, material instance name regex or None, yaw)
CANDIDATES = [
    (r"^SM_cloth$", 1.0, None, 90),
    (r"^SM_FogCard_01_N1$", 7.0, r"^MI_FogCard_01$", 90),
    (r"^SM_FogCard_01_N1$", 7.0, r"^MI_FogCard_02$", 90),
    (r"^SM_FogCard_01_N1$", 7.0, r"^MI_FogCard_03$", 90),
    (r"^SM_Rusty_Hanging_Chain_wcwsfitdw_04_N1$", 3.0, None, 90),
    (r"^SM_chandelier$", 1.0, None, 90),
]
ar = unreal.AssetRegistryHelpers.get_asset_registry()
catalog = {}
mats = {}
for ad in ar.get_assets_by_path("/Game", recursive=True):
    if str(ad.asset_class_path.asset_name) in ("MaterialInstanceConstant", "Material"):
        mats[str(ad.asset_name)] = str(ad.package_name)
for root in ("/Game/Deadly_Ruins", "/Game/CustomAssets", "/Game/MS/3D"):
    for ad in ar.get_assets_by_path(root, recursive=True):
        if str(ad.asset_class_path.asset_name) == "StaticMesh":
            catalog[str(ad.asset_name)] = str(ad.package_name)
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in sub.get_all_level_actors():
    if str(a.get_folder_path()) == "MeshTest":
        unreal.EditorLevelLibrary.destroy_actor(a)
for i, (pattern, scale, matpat, yaw) in enumerate(CANDIDATES):
    names = sorted(n for n in catalog if re.search(pattern, n))
    if not names:
        unreal.log("[MeshTest] no match " + pattern)
        continue
    mesh = unreal.EditorAssetLibrary.load_asset(catalog[names[0]])
    b = mesh.get_bounds()
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-800, -700 + i * 330, 150 - (b.origin.z - b.box_extent.z) * scale), unreal.Rotator(0, yaw, 0))
    a.static_mesh_component.set_static_mesh(mesh)
    if matpat:
        mn = sorted(n for n in mats if re.search(matpat, n))
        if mn:
            a.static_mesh_component.set_material(0, unreal.EditorAssetLibrary.load_asset(mats[mn[0]]))
    a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    a.set_actor_label("MeshTest_" + names[0])
    a.set_folder_path("MeshTest")
    unreal.log("[MeshTest] %d %s size=(%.0f,%.0f,%.0f) mats=%s" % (i, names[0], b.box_extent.x * 2, b.box_extent.y * 2, b.box_extent.z * 2, [m.material_interface.get_name() if m.material_interface else None for m in mesh.static_materials]))
