"""Lists the Blueprint components (SCS subobjects) of the pack's great-sword boss and the weapon static mesh sockets."""
import unreal

log = lambda m: unreal.log("[BossComps] " + m)
BP = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss"
bp = unreal.load_asset(BP)
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles = sub.k2_gather_subobject_data_for_blueprint(bp)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
for h in handles:
    data = lib.get_data(h)
    obj = lib.get_object(data) if hasattr(lib, "get_object") else None
    log("%s | %s | inherited=%s" % (lib.get_display_name(data) if hasattr(lib, "get_display_name") else "?", obj.get_class().get_name() if obj else "?",
                                   lib.is_inherited_component(data) if hasattr(lib, "is_inherited_component") else "?"))
    if obj and isinstance(obj, unreal.StaticMeshComponent):
        mesh = obj.get_editor_property("static_mesh")
        log("    weapon static mesh=%s rel=%s vis=%s" % (mesh.get_path_name() if mesh else None, obj.get_editor_property("relative_location"), obj.get_editor_property("visible")))
        if mesh:
            log("    sockets=%s" % [str(s.get_editor_property("socket_name")) for s in mesh.get_editor_property("sockets")])
            log("    bounds=%s" % mesh.get_bounds())
