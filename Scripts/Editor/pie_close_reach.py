"""Reach probe of the pack's real close attack with the authored clips swapped in (log prefix [Reach]): the player is put in front of the held boss at 60, 90 and 120 cm, the pack ability is started (it picks A1, A1b, A3a or A3b itself), and each trial logs whether the player lost health. The stage names come from the LogRPGAttack lines between two TRIAL markers (Scripts/Editor/pie_close_reach.py output is read with grep, nothing is asserted here: it is a measurement). Needs the editor in PIE after a warm-up like the other drivers."""
import math
import unreal

log = lambda m: unreal.log("[Reach] " + m)
S = {"phase": "start", "t": 0.0, "i": 0, "next": 9.0, "armed": False}
handle = None
DISTS = (90,)
# B10b: C7's authored misses were at actual actor yaw -162.2, while the old
# probe passed that value as pitch (`Rotator(0, yaw, 0)`) and logged yaw 180.0.
# Exercise the real orientations explicitly; this is a measurement probe, not a pass/fail driver.
YAWS = (180.0, -162.2)
TRIALS = 10


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def health(actor):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="Attribute.Health")')
    try:
        return c.call_method("Get Current Attribute Value", args=(t,))
    except Exception:
        return None


def place(pawn, boss, dist):
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    p = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, unreal.MathLibrary.find_look_at_rotation(p, bl).yaw), False, True)


def _tick(dt):
    global handle
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s["phase"] = "run"
            s["t"] = 0.0
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None or s["t"] < s["next"]:
        return
    tr, enc, dbg = comp(boss, "RPGAttackTracker"), comp(boss, "RPGBossEncounter"), comp(boss, "RPGCombatDebug")
    if not s["armed"]:
        unreal.SystemLibrary.execute_console_command(w, "rpg.CloseTelegraph 0")
        log("cvar rpg.CloseTelegraph set to 0 for this probe")
        enc.wake()
        enc.hold_for_test(True)
        dbg.debug_refill_player()
        tr.enter_combat()
        s.update(armed=True, t=0.0, next=3.0, step=0)
        return
    total = len(YAWS) * TRIALS
    n = s["step"] // 2
    if n >= total:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("DONE")
        return
    dist = DISTS[0]
    yaw = YAWS[n // TRIALS]
    if s["step"] % 2 == 0:
        mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
        inst = mc.get_anim_instance()
        if inst.get_current_active_montage():
            inst.montage_stop(0.05)
        dbg.debug_refill_player()
        boss.set_actor_rotation(unreal.Rotator(0, 0, yaw), False)
        place(pawn, boss, dist)
        s["hp0"] = health(pawn)
        actual_yaw = boss.get_actor_rotation().yaw
        yaw_error = abs((actual_yaw - yaw + 180.0) % 360.0 - 180.0)
        log("TRIAL %d dist %d requested yaw %.1f actual %.1f (error %.1f) start" % (n, dist, yaw, actual_yaw, yaw_error))
        tr.start_move("Close")
        s.update(t=0.0, next=2.0)
    else:
        hp1 = health(pawn)
        log("TRIAL %d dist %d yaw %.1f %s (health %s -> %s)" % (n, dist, yaw, "HIT" if hp1 is not None and s["hp0"] is not None and hp1 < s["hp0"] else "miss", s["hp0"], hp1))
        s.update(t=0.0, next=0.5)
    s["step"] += 1


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
