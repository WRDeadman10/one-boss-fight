"""
PIE frame capture of montages on the pack player: plays each clip of CLIPS on the idle player (boss removed) and takes a high resolution screenshot every
SHOT_EVERY seconds, logging the file index so the frames can be looked at in order. Screenshots land in Saved/Screenshots/WindowsEditor/. Log prefix [ShotsPie].
Open L_SevarogArena first; run with Scripts/run_in_editor.py (editor throttling off, see PROJECT_STATE).
"""
import unreal

log = lambda m: unreal.log("[ShotsPie] " + m)
A = "/Game/AdvancedARPGCombat/"
CLIPS = [
    ("roll", A + "Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage", 1.0),
    ("dodge", A + "MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage", 1.0),
]
SHOT_EVERY = 0.1
SHOTS_PER_CLIP = 10
state = {"phase": "start", "t": 0.0, "clip": 0, "t0": 0.0, "shots": 0, "next_shot": 0.0}
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
    if s["t"] > 80.0:
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
    inst = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance()
    if s["phase"] == "wait":
        if s["t"] > 12.0:  # shaders compile on the first PIE of a session: give it time so the frames are not grey
            for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character):
                if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C":
                    a.destroy_actor()
            s.update(phase="play", t=0.0, next_shot=0.0)
            pawn.set_actor_location_and_rotation(unreal.Vector(-1800, 0, 110), unreal.Rotator(0, 0, 0), False, True)
            pc.set_control_rotation(unreal.Rotator(0, 0, 0))
        return
    if s["phase"] == "play":
        if s["t"] > 1.5:
            if s["clip"] >= len(CLIPS):
                finish("done")
                return
            name, path, rate = CLIPS[s["clip"]]
            inst.montage_play(unreal.load_asset(path), rate)
            s.update(phase="shoot", t0=s["t"], shots=0, next_shot=s["t"])
            log("== %s: playing" % name)
        return
    if s["phase"] == "shoot":
        if s["t"] >= s["next_shot"] and s["shots"] < SHOTS_PER_CLIP:
            unreal.SystemLibrary.execute_console_command(w, "HighResShot 640x360")
            log("   %s shot %d at t=%.2f (dist %.0f)" % (CLIPS[s["clip"]][0], s["shots"], s["t"] - s["t0"], (pawn.get_actor_location() - unreal.Vector(-1800, 0, 110)).length()))
            s["shots"] += 1
            s["next_shot"] += SHOT_EVERY
        if s["shots"] >= SHOTS_PER_CLIP and s["t"] > s["next_shot"] + 0.5:
            s["clip"] += 1
            s.update(phase="play", t=0.0)
            pawn.set_actor_location_and_rotation(unreal.Vector(-1800, 0, 110), unreal.Rotator(0, 0, 0), False, True)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
