"""
PIE measurement of how far and how long montages move the pack player (root motion): plays each montage in MONTAGES directly on the idle player, one after the
other, at its PlayRate, and logs duration and travel. Open L_SevarogArena first; run with Scripts/run_in_editor.py. Log prefix [TravelPie].
"""
import unreal

log = lambda m: unreal.log("[TravelPie] " + m)
A = "/Game/AdvancedARPGCombat/"
# (label, asset, play rate)
MONTAGES = [
    ("dodge (pack default)", A + "MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage", 1.0),
    ("dodge x1.5", A + "MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage", 1.5),
    ("roll (pack, unused)", A + "Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage", 1.0),
]
state = {"phase": "start", "t": 0.0, "i": -1, "t0": 0.0, "loc": None, "len": 0.0}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 90.0:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    mesh = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    inst = mesh.get_anim_instance()
    if s["phase"] == "wait":
        if s["t"] > 6.0:
            for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character):
                if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C":
                    a.destroy_actor()
            s.update(phase="run", t=0.0, i=-1, t0=-10.0)
        return
    if s["i"] >= 0 and inst.get_current_active_montage() is None and s["t"] - s["t0"] > 0.2:
        label = MONTAGES[s["i"]][0]
        log("%s: lasted %.2f s (asset length %.2f), moved %.0f cm, height change %.0f" % (label, s["t"] - s["t0"], s["len"], (pawn.get_actor_location() - s["loc"]).length(), pawn.get_actor_location().z - s["loc"].z))
        s["i"] = -2
        s["t0"] = s["t"]
    if s["t"] - s["t0"] > 1.5 and (s["i"] < 0):
        nxt = s.get("next", 0)
        if nxt >= len(MONTAGES):
            finish("done")
            return
        label, path, rate = MONTAGES[nxt]
        montage = unreal.load_asset(path)
        s.update(i=nxt, next=nxt + 1, t0=s["t"], loc=pawn.get_actor_location(), len=montage.get_play_length())
        log("== playing %s (rate %.1f)" % (label, rate))
        inst.montage_play(montage, rate)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
