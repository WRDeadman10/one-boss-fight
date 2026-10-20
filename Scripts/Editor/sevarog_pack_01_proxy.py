"""Sevarog on the pack, step 1: SM_SevarogScytheProxy, a copy of the pack boss's weapon static mesh whose sockets (trace points) lie along
Sevarog's scythe, from bone weapon_r to bone root_weapon_end_r. The weapon component is hidden in the boss Blueprint: only the socket
positions matter (the pack's ANS_CollisionTrace sweeps between the weapon mesh sockets). Run in the open editor."""
import unreal

log = lambda m: unreal.log("[SevPack1] " + m)
OUT = "/Game/OneBossFight/SevarogPack"
SRC_MESH = "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Meshes/Weapons/Paragon/SM_KwangSword"
PROXY = OUT + "/SM_SevarogScytheProxy"
SEQ_ROOT = "/Game/ParagonSevarog"
BASE_BONE, TIP_BONE = "weapon_r", "root_weapon_end_r"
SOCKET_COUNT = 6

unreal.EditorAssetLibrary.make_directory(OUT)
if unreal.EditorAssetLibrary.does_asset_exist(PROXY):
    unreal.EditorAssetLibrary.delete_asset(PROXY)
mesh = unreal.EditorAssetLibrary.duplicate_asset(SRC_MESH, PROXY)

# Tip position in the weapon_r bone frame, from the idle pose.
registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous([SEQ_ROOT], True)
idle = None
for a in registry.get_assets_by_path(SEQ_ROOT, recursive=True):
    if str(a.asset_class_path.asset_name) == "AnimSequence" and str(a.asset_name) == "Idle":
        idle = a.get_asset()
chain_tip = list(reversed(unreal.AnimationLibrary.find_bone_path_to_root(idle, TIP_BONE)))
chain_base = list(reversed(unreal.AnimationLibrary.find_bone_path_to_root(idle, BASE_BONE)))


def component_transform(chain):
    t = unreal.Transform()
    for bone in chain:
        local = unreal.AnimationLibrary.get_bone_pose_for_time(idle, bone, 0.0, False)
        t = unreal.MathLibrary.compose_transforms(local, t)
    return t


tip_c, base_c = component_transform(chain_tip), component_transform(chain_base)
rel = unreal.MathLibrary.compose_transforms(tip_c, base_c.inverse())
tip_local = rel.translation
log("tip in weapon_r frame = %s (length %.1f cm)" % (tip_local, tip_local.length()))

# Replace the sword's sockets by trace points along the scythe.
probe = unreal.new_object(unreal.StaticMeshComponent)
probe.set_static_mesh(mesh)
before = [str(n) for n in probe.get_all_socket_names()]
log("sockets before: %s" % before)
for name in before:
    old = mesh.find_socket(name)
    if old:
        mesh.remove_socket(old)
for i in range(SOCKET_COUNT):
    f = i / (SOCKET_COUNT - 1)
    sock = unreal.StaticMeshSocket(mesh)
    sock.set_editor_property("socket_name", "Trace_%d" % i)
    sock.set_editor_property("relative_location", unreal.Vector(tip_local.x * f, tip_local.y * f, tip_local.z * f))
    mesh.add_socket(sock)
probe.set_static_mesh(None)
probe.set_static_mesh(mesh)
log("sockets after: %s" % [str(n) for n in probe.get_all_socket_names()])
unreal.EditorAssetLibrary.save_loaded_asset(mesh)
