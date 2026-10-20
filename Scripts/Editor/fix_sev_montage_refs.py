"""Re-points the Sevarog abilities at their entrance, exit and death montages. Those three montages were deleted and recreated at the same path during
development, which emptied the saved references (the abilities then enabled combat without playing anything). Run check_sev_abilities.py to see the state.
Never delete and recreate an asset that other assets reference: edit it in place."""
import unreal

HEAD = open(r"C:/Users/winss/Documents/Unreal Projects/OneBossFight/Scripts/Editor/sevarog_pack_02_montages_abilities.py", encoding="utf-8").read()
exec(HEAD[:HEAD.index("ONLY_TOGGLE = globals()")])
log = lambda m: unreal.log("[SevFix] " + m)
ent = unreal.load_asset(MONT + "/AM_SevPack_Entrance")
ext = unreal.load_asset(MONT + "/AM_SevPack_Exit")
death = unreal.load_asset(MONT + "/AM_SevPack_Death")
set_single_montage("GA_Sev_EnterCombat", "Enter Combat Montage", ent)
set_single_montage("GA_Sev_ExitCombat", "ExitCombatMontage", ext)
ga = unreal.load_asset(ABIL + "/GA_Sev_Death")
cdo = unreal.get_default_object(ga.generated_class())
template = unreal.get_default_object(unreal.load_asset(ABIL + "/GA_Sev_EnterCombat").generated_class()).get_editor_property("Enter Combat Montage")
cdo.set_editor_property("DeathMontages", [ability_montage(template, death)])
ga.modify()
unreal.BlueprintEditorLibrary.compile_blueprint(ga)
unreal.EditorAssetLibrary.save_loaded_asset(ga, False)
log("done")
