"""Sevarog on the pack, step 6: adds URPGSevarogDirector to BP_SevarogBossPack (needs the C++ built) and keeps AutoPossessAI on (the director holds the behaviour until the player is near). Idempotent (does nothing if the component is already there)."""
import unreal

log = lambda m: unreal.log("[SevPack6] " + m)
OUT = "/Game/OneBossFight/SevarogPack"
pawn = unreal.load_asset(OUT + "/BP_SevarogBossPack")
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
handles = list(sub.k2_gather_subobject_data_for_blueprint(pawn))
director = None
for h in handles:
    obj = lib.get_object(lib.get_data(h))
    if isinstance(obj, unreal.RPGSevarogDirector):
        director = obj
        log("director already present")
if director is None:
    params = unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=unreal.RPGSevarogDirector, blueprint_context=pawn)
    handle, reason = sub.add_new_subobject(params)
    log("added director: %s %s" % (handle, reason))
    director = lib.get_object(lib.get_data(handle))
    sub.rename_subobject(handle, "SevarogDirector")
director.set_editor_property("gate_radius", 1000.0)
director.set_editor_property("phase_roar_montage", unreal.load_asset("/Game/OneBossFight/Boss/AM_Sevarog_PhaseRoar"))
director.set_editor_property("entrance_ability", unreal.load_asset(OUT + "/Abilities/GA_Sev_EnterCombat").generated_class())
director.set_editor_property("lightning_ability", unreal.load_asset(OUT + "/Abilities/GA_Sev_Lightning").generated_class())
cdo = unreal.get_default_object(pawn.generated_class())
cdo.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)  # the controller must exist at BeginPlay: the pack's abilities read it when granted
unreal.BlueprintEditorLibrary.compile_blueprint(pawn)
unreal.EditorAssetLibrary.save_loaded_asset(pawn)
log("roar=%s lightning=%s auto_possess=%s" % (director.get_editor_property("phase_roar_montage").get_name(), director.get_editor_property("lightning_ability").get_name(), cdo.get_editor_property("auto_possess_ai")))
