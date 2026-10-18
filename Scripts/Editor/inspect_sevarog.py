"""Prints Sevarog's bones that look like a weapon, mesh size, and AnimBP asset names."""
import unreal

ROOT = "/Game/ParagonSevarog"
registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous([ROOT], True)
by = {}
for a in registry.get_assets_by_path(ROOT, recursive=True):
    by[(str(a.asset_class_path.asset_name), str(a.asset_name))] = a
mesh = by[("SkeletalMesh", "Sevarog")].get_asset()
comp = unreal.new_object(unreal.SkeletalMeshComponent)
comp.set_skeletal_mesh_asset(mesh)
bones = [str(comp.get_bone_name(i)) for i in range(comp.get_num_bones())]
unreal.log("[SevInspect] bones=%d weaponish=%s" % (len(bones), [b for b in bones if any(k in b.lower() for k in ("weapon", "scythe", "blade", "sword", "hand", "prop", "staff", "hammer"))]))
unreal.log("[SevInspect] animBPs=%s" % [k[1] for k in by if k[0] == "AnimBlueprint"])
unreal.log("[SevInspect] bounds=%s" % mesh.get_bounds())
