"""Sevarog on the pack, step 9 (KI-047): the mid-range attack closes the distance. AM_SevPack_Charge is the Overhead swing with URPGANS_ChargeToTarget over its wind-up
(the pawn is driven to the player so the hit lands) at 0.6 play rate, used by GA_Sev_MidRangeAttack. Also puts the benchmark runner in L_SevarogArena.
Idempotent, never deletes assets. Run in the open editor after steps 1-8 and 6 (director)."""
import re
import unreal

HEAD = open(r"C:/Users/winss/Documents/Unreal Projects/OneBossFight/Scripts/Editor/sevarog_pack_02_montages_abilities.py", encoding="utf-8").read()
exec(HEAD[:HEAD.index("ONLY_TOGGLE = globals()")])
log = lambda m: unreal.log("[SevPack9] " + m)
tools = unreal.AssetToolsHelpers.get_asset_tools()
lib = unreal.AnimationLibrary

charge = unreal.load_asset(MONT + "/AM_SevPack_Charge")
if charge is None:
    sequence = find_pack_asset("AnimSequence", "Swing3_Medium")
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    charge = tools.create_asset("AM_SevPack_Charge", MONT, unreal.AnimMontage, factory)
    unreal.RPGMontageUtils.set_montage_slot(charge, SLOT)
    length = charge.get_play_length()
    start, end = motion_window(sequence)
    lib.add_animation_notify_track(charge, "PackCombat")
    lib.add_animation_notify_state_event(charge, "PackCombat", 0.0, length * 0.9, load_class(ANS_DISABLE))
    rot = lib.add_animation_notify_state_event(charge, "PackCombat", 0.0, max(start * 0.9, 0.1), load_class(ANS_ROTATE))
    rot.set_editor_property("RotationInterpSpeed", 520.0)
    rot.set_editor_property("Desired Rotation Type", FACE_TARGET)
    dash = lib.add_animation_notify_state_event(charge, "PackCombat", 0.0, start + 0.02, unreal.RPGANS_ChargeToTarget)
    dash.set_editor_property("stop_distance", 200.0)
    dash.set_editor_property("max_speed", 2400.0)
    dash.set_editor_property("window_end_time", start)
    trace = lib.add_animation_notify_state_event(charge, "PackCombat", start, max(end - start, 0.05), load_class(ANS_COLLISION))
    trace.set_editor_property("Collision Target Tag", tag("TargetType.MainWeapon"))
    trace.set_editor_property("EventTag", tag("GameplayEvent.AttackHit"))
    trace.set_editor_property("TraceRadiusModifier", 0.0)
    lib.add_animation_notify_event(charge, "PackCombat", length * 0.9, load_class(AN_END))
    unreal.EditorAssetLibrary.save_loaded_asset(charge)
    log("charge montage created: %.2fs, dash until %.2fs, hit %.2f-%.2f" % (length, start, start, end))

ga = unreal.load_asset(ABIL + "/GA_Sev_MidRangeAttack")
cdo = unreal.get_default_object(ga.generated_class())
entry = ability_montage(cdo.get_editor_property("AttackMontages")[0], charge)
text = re.sub(r"(PlayRate_\d+_[0-9A-F]+)=[\d.]+", lambda m: "%s=0.600000" % m.group(1), entry.export_text())
entry.import_text(text)
cdo.set_editor_property("AttackMontages", [entry])
unreal.BlueprintEditorLibrary.compile_blueprint(ga)
unreal.EditorAssetLibrary.save_loaded_asset(ga)
log("GA_Sev_MidRangeAttack now uses AM_SevPack_Charge at 0.6 play rate")

# benchmark runner in the arena (the level is already open: loading maps from scripts crashes the editor)
world = unreal.EditorLevelLibrary.get_editor_world()
if world.get_name() == "L_SevarogArena":
    if not any(a.get_class().get_name() == "RPGBenchmarkRunner" for a in unreal.EditorLevelLibrary.get_all_level_actors()):
        runner = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.RPGBenchmarkRunner, unreal.Vector(0, 0, 100))
        runner.set_actor_label("BenchmarkRunner")
        log("benchmark runner placed")
    unreal.EditorLoadingAndSavingUtils.save_map(world, "/Game/OneBossFight/Levels/L_SevarogArena")
else:
    log("open L_SevarogArena to place the benchmark runner (current: %s)" % world.get_name())
