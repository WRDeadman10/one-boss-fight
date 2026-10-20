import unreal
log = lambda m: unreal.log("[GreySock2] " + m)
g = unreal.load_asset("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone")
c = unreal.new_object(unreal.SkeletalMeshComponent)
c.set_skeletal_mesh_asset(g)
for n in ("WeaponSocket_R", "ShieldSocket", "HeavySwordSocket_R", "ConsumableItemSocket", "HipSheath_L"):
    log("%s on component: %s | on mesh: %s" % (n, c.does_socket_exist(n), g.find_socket(n)))
