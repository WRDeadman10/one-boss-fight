import unreal
log = lambda m: unreal.log("[GreySockets] " + m)
for path in ("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton", "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"):
    sk = unreal.load_asset(path)
    socks = [(str(s.get_editor_property("socket_name")), str(s.get_editor_property("bone_name"))) for s in sk.get_editor_property("sockets")]
    log("%s sockets: %s" % (path.split("/")[-1], socks))
