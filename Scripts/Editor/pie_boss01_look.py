"""Plays Antigravity's A2 clips on the pack boss mesh (same skeleton) in PIE and takes high resolution shots at set times, front and side. Files: Saved/Screenshots/WindowsEditor/. Log prefix [B01Look]
lists the order. The boss is frozen (RPGBossEncounter.HoldForTest). Run after one warm-up PIE; open L_SevarogArena first."""
import unreal

log = lambda m: unreal.log("[B01Look] " + m)
CLIPS = [("AN_Boss01_A2_Raise", [0.0, 0.3, 0.6]), ("AN_Boss01_A2_ApexHold", [0.2, 0.7]), ("AN_Boss01_A2_Slam", [0.0, 0.1, 0.2, 0.5, 1.2])]
VIEWS = [("front", (650.0, 0.0), 180.0), ("side", (0.0, 650.0), -90.0)]
state = {"phase": "start", "t": 0.0, "i": 0, "step": "setup", "wait": 0.0, "shots": 0}
plan = [(c, t, v) for v in VIEWS for c, ts in CLIPS for t in ts]
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None or s["t"] < 9.0:
        return
    mesh = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    if s["step"] == "setup":
        comp(boss, "RPGBossEncounter").hold_for_test(True)
        s["step"] = "next"
        s["wait"] = s["t"]
        return
    if s["t"] - s["wait"] < 0.6:
        return
    if s["step"] == "next":
        if s["i"] >= len(plan):
            unreal.unregister_slate_post_tick_callback(handle)
            handle = None
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
            log("done")
            return
        clip, t, view = plan[s["i"]]
        name, (dx, dy), yaw = view
        bl = boss.get_actor_location()
        pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + dx, bl.y + dy, bl.z), unreal.Rotator(0, 0, yaw), False, True)
        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-4, yaw=yaw))
        boss.set_actor_rotation(unreal.Rotator(0, 0, 0), False)
        anim = unreal.load_asset("/Game/OneBossFight/Boss01/Animations/" + clip)
        mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        mesh.play_animation(anim, False)
        mesh.set_position(t, False)
        mesh.set_play_rate(0.0)
        s["step"] = "shoot"
        s["wait"] = s["t"]
        return
    if s["step"] == "shoot":
        unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
        s["shots"] += 1
        clip, t, view = plan[s["i"]]
        log("shot %d: %s t=%.2f view=%s" % (s["shots"], clip, t, view[0]))
        s["i"] += 1
        s["step"] = "next"
        s["wait"] = s["t"] + 0.6


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
