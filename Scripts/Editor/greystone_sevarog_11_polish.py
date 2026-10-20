"""Polish pass (needs the C++ built): Greystone's baked-in sword and shield are hidden by bone with URPGHideBones (instead of hiding material slot 3, which also hid
fur), and the Sevarog director gets the lightning strike effects. Idempotent. Run in the open editor."""
import unreal

log = lambda m: unreal.log("[Polish11] " + m)
GREY = "/Game/OneBossFight/GreystonePack/BP_GreystonePlayer"
SEV = "/Game/OneBossFight/SevarogPack/BP_SevarogBossPack"
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary


def find_component(bp, cls):
    handles = list(sub.k2_gather_subobject_data_for_blueprint(bp))
    for h in handles:
        obj = lib.get_object(lib.get_data(h))
        if isinstance(obj, cls):
            return obj, handles
    return None, handles


grey = unreal.load_asset(GREY)
hider, handles = find_component(grey, unreal.RPGHideBones)
if hider is None:
    params = unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=unreal.RPGHideBones, blueprint_context=grey)
    handle, reason = sub.add_new_subobject(params)
    hider = lib.get_object(lib.get_data(handle))
    sub.rename_subobject(handle, "HideBakedWeapons")
    log("added HideBones component: %s" % reason)
hider.set_editor_property("bone_names", ["sword_bottom", "shield_inner"])
cdo = unreal.get_default_object(grey.generated_class())
cdo.get_editor_property("mesh").set_editor_property("override_materials", [])  # slot 3 shows again, only the baked weapon bones are hidden
grey.modify()
unreal.BlueprintEditorLibrary.compile_blueprint(grey)
unreal.EditorAssetLibrary.save_loaded_asset(grey, False)
log("Greystone: hidden bones %s, material overrides cleared" % list(hider.get_editor_property("bone_names")))

sev = unreal.load_asset(SEV)
director, _ = find_component(sev, unreal.RPGSevarogDirector)
director.set_editor_property("strike_telegraph_effect", unreal.load_asset("/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Circle"))
director.set_editor_property("strike_bolt_effect", unreal.load_asset("/Game/BeamPack/Niagara/LaserBeam/NS_Thunder_Beam7"))
sev.modify()
unreal.BlueprintEditorLibrary.compile_blueprint(sev)
unreal.EditorAssetLibrary.save_loaded_asset(sev, False)
log("director strike effects set")
