"""Sevarog on the pack, step 8: turn in place. The pack's behaviour tree calls GA_*_TurnInPlace when the target is outside the front cone; without it the boss
stands still when the player circles behind him. Sevarog has no turn animations, so all four turn montages are one short idle montage whose
ANS_SetDesiredRotation (face target, fast) turns the pawn. Never deletes assets."""
import re
import unreal

HEAD = open(r"C:/Users/winss/Documents/Unreal Projects/OneBossFight/Scripts/Editor/sevarog_pack_02_montages_abilities.py", encoding="utf-8").read()
exec(HEAD[:HEAD.index("ONLY_TOGGLE = globals()")])
log = lambda m: unreal.log("[SevPack8] " + m)
tools = unreal.AssetToolsHelpers.get_asset_tools()
lib = unreal.AnimationLibrary

turn = unreal.load_asset(MONT + "/AM_SevPack_Turn")
if turn is None:
    sequence = find_pack_asset("AnimSequence", "Idle")
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    turn = tools.create_asset("AM_SevPack_Turn", MONT, unreal.AnimMontage, factory)
    unreal.RPGMontageUtils.set_montage_slot(turn, SLOT)
    lib.add_animation_notify_track(turn, "PackCombat")
    rot = lib.add_animation_notify_state_event(turn, "PackCombat", 0.0, 0.5, load_class(ANS_ROTATE))
    rot.set_editor_property("RotationInterpSpeed", 900.0)
    rot.set_editor_property("Desired Rotation Type", FACE_TARGET)
    lib.add_animation_notify_event(turn, "PackCombat", 0.55, load_class(AN_END))
    unreal.EditorAssetLibrary.save_loaded_asset(turn)
    log("turn montage created, idle length %.2f" % turn.get_play_length())

ga = unreal.load_asset(ABIL + "/GA_Sev_TurnInPlace")
if ga is None:
    ga = tools.duplicate_asset("GA_Sev_TurnInPlace", ABIL, unreal.load_asset(GS + "GA_GS_Boss_TurnInPlace"))
cdo = unreal.get_default_object(ga.generated_class())
for prop in ("Turn Left 90", "Turn Right 90", "Turn Left 180", "Turn Right 180"):
    cdo.set_editor_property(prop, ability_montage(cdo.get_editor_property(prop), turn))
unreal.BlueprintEditorLibrary.compile_blueprint(ga)
unreal.EditorAssetLibrary.save_loaded_asset(ga)
log("GA_Sev_TurnInPlace ready")

style = unreal.load_asset(OUT_STYLE) if False else unreal.load_asset("/Game/OneBossFight/SevarogPack/SevarogCombatStyle")
entry = style.get_editor_property("AbilitiesSet")[0]
text = entry.export_text()
if "GA_Sev_TurnInPlace" not in text:
    cls = '"/Script/Engine.BlueprintGeneratedClass\'%s/GA_Sev_TurnInPlace.GA_Sev_TurnInPlace_C\'"' % ABIL
    text = re.sub(r"(Abilities_\d+_[0-9A-F]+=\()", lambda m: m.group(1) + cls + ",", text, count=1)
    entry.import_text(text)
    style.set_editor_property("AbilitiesSet", [entry])
    unreal.EditorAssetLibrary.save_loaded_asset(style)
log("style has turn ability: %s" % ("GA_Sev_TurnInPlace" in style.get_editor_property("AbilitiesSet")[0].export_text()))
