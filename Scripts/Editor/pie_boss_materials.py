"""AGI-4 check (log prefix [BossMat]): in PIE the boss gets the Boss 01 body, crown, mantle and gauntlet; the M_Boss01_* instances on them get dynamic copies and
PhaseGlow, Dissolve and HitFlash are set per shot. Each parameter is read back (PASS/FAIL) and a 1280x720 screenshot is taken per state.
Ends with RESULT n/m passed. Run with Scripts/run_in_editor.py after the warm-up; stop a stuck run with pie_stop.py and restart the editor."""
import unreal

log = lambda m: unreal.log("[BossMat] " + m)
SHOTS = [("baseline", 0.0, 0.0, 0.0), ("phase glow 1", 1.0, 0.0, 0.0), ("hit flash 1", 0.0, 0.0, 1.0), ("dissolve 0.45", 0.0, 0.45, 0.0), ("dissolve 0.8", 0.0, 0.8, 0.0)]
CAM = (240.0, 240.0, 28.0)
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0, "i": 0, "mids": [], "ok": 0, "n": 0}
handle = None


def check(name, ok, detail=""):
    state["n"] += 1
    state["ok"] += 1 if ok else 0
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def collect_mids(boss):
    mids = []
    for c in boss.get_components_by_class(unreal.MeshComponent):
        for idx, mat in enumerate(c.get_materials()):
            if mat and mat.get_name().startswith("M_Boss01_") and isinstance(mat, unreal.MaterialInstanceConstant):
                mid = c.create_dynamic_material_instance(idx, mat)
                mids.append((c.get_name(), mat.get_name(), mid))
    return mids


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
        mesh.set_skeletal_mesh_asset(unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body"))
        mesh.set_relative_scale3d(unreal.Vector(100.0, 100.0, 100.0))
        for piece in ("SK_Boss01_Crown", "SK_Boss01_Mantle", "SK_Boss01_BrazierGauntlet"):
            comp(boss, "RPGCombatDebug").debug_add_skeletal_piece(unreal.load_asset("/Game/OneBossFight/Boss01/Body/" + piece))
        s["mids"] = collect_mids(boss)
        names = sorted(set(m[1] for m in s["mids"]))
        log("dynamic instances: %d on %s" % (len(s["mids"]), names))
        check("pieces carry Boss01 instances (crown, mantle, gauntlet)", {"M_Boss01_BlackPlate", "M_Boss01_EmberGlow", "M_Boss01_CrimsonCloth", "M_Boss01_GoldTrim"} <= set(names), str(names))
        s["step"] = 1
        s["wait"] = s["t"] + 25.0  # a cold shader cache compiles the body and the pieces during the first seconds
        return
    if s["step"] == 1:
        if s["i"] >= len(SHOTS):
            unreal.unregister_slate_post_tick_callback(handle)
            handle = None
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
            log("RESULT %d/%d passed" % (s["ok"], s["n"]))
            return
        label, phase, dis, flash = SHOTS[s["i"]]
        pp = unreal.Vector(bl.x + CAM[0], bl.y + CAM[1], bl.z + 20)
        yaw0 = unreal.MathLibrary.find_look_at_rotation(pp, bl).yaw
        pawn.set_actor_location_and_rotation(pp, unreal.Rotator(0, 0, yaw0 + 140), False, True)
        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-3, yaw=yaw0 + CAM[2]))
        bad = 0
        for _, _, mid in s["mids"]:
            mid.set_scalar_parameter_value("PhaseGlow", phase)
            mid.set_scalar_parameter_value("Dissolve", dis)
            mid.set_scalar_parameter_value("HitFlash", flash)
            got = (mid.get_scalar_parameter_value("PhaseGlow"), mid.get_scalar_parameter_value("Dissolve"), mid.get_scalar_parameter_value("HitFlash"))
            if abs(got[0] - phase) > 1e-4 or abs(got[1] - dis) > 1e-4 or abs(got[2] - flash) > 1e-4:
                bad += 1
        check("%s: PhaseGlow/Dissolve/HitFlash read back on all %d instances" % (label, len(s["mids"])), bad == 0 and len(s["mids"]) > 0, "mismatches %d" % bad)
        s["step"] = 2
        s["wait"] = s["t"] + 1.5
        return
    if s["step"] == 2:
        unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
        log("shot %d: %s" % (s["i"] + 1, SHOTS[s["i"]][0]))
        s["i"] += 1
        s["step"] = 1
        s["wait"] = s["t"] + 1.0


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
