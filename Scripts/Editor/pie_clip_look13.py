"""Look at the Report 12 clips on the final body in PIE (log prefix [ClipLook12]): the boss gets SK_Boss01_Body with crown, mantle, gauntlet and the sword, plays each clip of SHOTS (a clip name of the review scratch folder
/Game/OneBossFight/_Review12 and a time) frozen at that time, one 1280x720 shot per entry; the sword's tip height above the floor is logged for every shot (the dormant and wake clips plant the sword in the floor).
Camera offset from Saved/look_cfg.txt as "x,y,yaw" (default 330,330,28). Based on pie_body_look_short.py. Run review_report12.py first (it imports the clips), end with cleanup_review12.py."""
import os
import unreal

log = lambda m: unreal.log("[ClipLook13] " + m)
_sf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "body_scale.txt")
SCALE = float(open(_sf).read().strip()) if os.path.exists(_sf) else 100.0
R = "/Game/OneBossFight/_Review13/"
SHOTS = [("AN_Boss01_A1_QuickSlash", 0.0), ("AN_Boss01_A1_QuickSlash", 0.2), ("AN_Boss01_A1_QuickSlash", 0.35), ("AN_Boss01_A1_QuickSlash", 0.42), ("AN_Boss01_A1_QuickSlash", 0.5), ("AN_Boss01_A1_QuickSlash", 0.8),
         ("AN_Boss01_A3a_Combo1", 0.2), ("AN_Boss01_A3a_Combo1", 0.4), ("AN_Boss01_A3a_Combo1", 0.5), ("AN_Boss01_A3b_Combo2", 0.15), ("AN_Boss01_A3b_Combo2", 0.28), ("AN_Boss01_A3b_Combo2", 0.4),
         ("AN_Boss01_A2_Raise", 0.3), ("AN_Boss01_A2_ApexHold", 0.5), ("AN_Boss01_A2_Slam", 0.1), ("AN_Boss01_A2_Slam", 0.17), ("AN_Boss01_A2_Slam", 0.5),
         ("AN_Boss01_Wake", 1.5), ("AN_Boss01_Wake", 2.5)]
_cf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "look_cfg.txt")
CAM = tuple(float(v) for v in open(_cf).read().strip().split(",")) if os.path.exists(_cf) else (330.0, 330.0, 28.0)
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0, "i": 0}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def sword_tip(boss, mesh):
    """The tip of the attached test sword in world space and its height above the boss mesh's floor (the mesh component sits at the capsule bottom)."""
    for c in boss.get_components_by_class(unreal.StaticMeshComponent):
        sm = c.static_mesh
        if sm is not None and sm.get_name() == "SM_Boss01_Greatsword":
            box = sm.get_bounding_box()
            xf = c.get_world_transform()
            tip = unreal.MathLibrary.transform_location(xf, unreal.Vector(0, 0, box.max.z))
            floor = mesh.get_world_location().z
            return tip, tip.z - floor
    return None, None


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
        for piece in ("SK_Boss01_Crown", "SK_Boss01_Mantle", "SK_Boss01_BrazierGauntlet"):
            comp(boss, "RPGCombatDebug").debug_add_skeletal_piece(unreal.load_asset("/Game/OneBossFight/Boss01/Body/" + piece))
        log("body set, scale %.1f" % SCALE)
        s["step"] = 1
        s["wait"] = s["t"] + 12.0  # a cold shader cache compiles for a while
        return
    if s["step"] == 1:
        if s["i"] >= len(SHOTS):
            unreal.unregister_slate_post_tick_callback(handle)
            handle = None
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
            log("done")
            return
        clip, t = SHOTS[s["i"]]
        pp = unreal.Vector(bl.x + CAM[0], bl.y + CAM[1], bl.z + 20)
        yaw0 = unreal.MathLibrary.find_look_at_rotation(pp, bl).yaw
        pawn.set_actor_location_and_rotation(pp, unreal.Rotator(0, 0, yaw0 + 140), False, True)
        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-3, yaw=yaw0 + CAM[2]))
        anim = unreal.load_asset(R + clip)
        mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        mesh.play_animation(anim, False)
        mesh.set_position(t, False)
        mesh.set_play_rate(0.0)
        s["step"] = 2
        s["wait"] = s["t"] + 1.8
        return
    if s["step"] == 2:
        tip, height = sword_tip(boss, mesh)
        unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
        log("shot %d: %s t=%.2f sword tip %s above the floor" % (s["i"] + 1, SHOTS[s["i"]][0], SHOTS[s["i"]][1], ("%.1f cm (world %.0f %.0f %.0f)" % (height, tip.x, tip.y, tip.z)) if tip is not None else "unknown"))
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
