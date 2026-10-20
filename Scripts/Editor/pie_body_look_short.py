"""Swaps the boss mesh for the imported SK_Boss01_Body in PIE (scale from Saved/body_scale.txt, default 100) and takes screenshots from the player camera: idle, then the A2 clips at set times. Log prefix [BodyLook]."""
import os
import unreal

log = lambda m: unreal.log("[BodyLook] " + m)
_sf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "body_scale.txt")
SCALE = float(open(_sf).read().strip()) if os.path.exists(_sf) else 100.0
SHOTS = [(None, 0.0), ("AN_Boss01_A2_Raise", 0.5), ("AN_Boss01_A2_ApexHold", 0.5), ("AN_Boss01_A2_Slam", 0.6), ("AN_Boss01_Wake", 3.3)]
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0, "i": 0}
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
            s.update(phase="run", t=0.0, wait=9.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None or s["t"] < s["wait"]:
        return
    mesh = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    bl = boss.get_actor_location()
    if s["step"] == 0:
        comp(boss, "RPGBossEncounter").hold_for_test(True)
        body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
        mesh.set_skeletal_mesh_asset(body)
        mesh.set_relative_scale3d(unreal.Vector(SCALE, SCALE, SCALE))
        comp(boss, "RPGCombatDebug").debug_attach_test_mesh(unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword"), "HeavySwordSocket_R", unreal.Rotator(0, 0, 0), unreal.Vector(0, 0, 0))
        log("body set, scale %.1f, bounds %s" % (SCALE, mesh.get_editor_property("bounds_scale")))
        s["step"] = 1
        s["wait"] = s["t"] + 2.5
        return
    if s["step"] == 1:
        if s["i"] >= len(SHOTS):
            unreal.unregister_slate_post_tick_callback(handle)
            handle = None
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
            log("done")
            return
        clip, t = SHOTS[s["i"]]
        pp = unreal.Vector(bl.x + 330, bl.y + 330, bl.z + 20)
        yaw0 = unreal.MathLibrary.find_look_at_rotation(pp, bl).yaw
        pawn.set_actor_location_and_rotation(pp, unreal.Rotator(0, 0, yaw0 + 140), False, True)
        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-3, yaw=yaw0 + 28))
        if clip:
            anim = unreal.load_asset("/Game/OneBossFight/Boss01/Animations/" + clip)
            mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            mesh.play_animation(anim, False)
            mesh.set_position(t, False)
            mesh.set_play_rate(0.0)
        s["step"] = 2
        s["wait"] = s["t"] + 2.5
        return
    if s["step"] == 2:
        unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
        log("shot %d: %s t=%.2f" % (s["i"] + 1, SHOTS[s["i"]][0], SHOTS[s["i"]][1]))
        s["i"] += 1
        s["step"] = 1
        s["wait"] = s["t"] + 0.8


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
