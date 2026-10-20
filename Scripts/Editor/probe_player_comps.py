import unreal
log = lambda m: unreal.log("[PComp] " + m)
for path in ("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter", "/Game/OneBossFight/GreystonePack/BP_GreystonePlayer"):
    bp = unreal.load_asset(path)
    cdo = unreal.get_default_object(bp.generated_class())
    log("== " + path.split("/")[-1])
    for c in cdo.get_components_by_class(unreal.SceneComponent):
        parent = c.get_attach_parent()
        log("  %-22s %-24s parent=%-18s loc=%s rot=%s scale=%s" % (c.get_name(), c.get_class().get_name(), parent.get_name() if parent else None,
            c.get_editor_property("relative_location"), c.get_editor_property("relative_rotation"), c.get_editor_property("relative_scale3d")))
    cap = cdo.get_editor_property("capsule_component")
    log("  capsule half height %s radius %s" % (cap.get_editor_property("capsule_half_height"), cap.get_editor_property("capsule_radius")))
