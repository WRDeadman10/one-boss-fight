"""Watches which montages the awake pack boss plays against a player that stays at close range (refilled and put back every 0.4 s). Logs each montage change with its start time, the distance
and the angle of the player in the boss's front. Log prefix [ComboWatch]. Runs 30 s after the wake. Needs a warm-up PIE (pie_debug_overlay.py) once after an editor start."""
import math
import unreal

log = lambda m: unreal.log("[ComboWatch] " + m)
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 9.0, "run": 0.0, "last": None, "last_t": 0.0, "since_put": 0.0}
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
    if pawn is None or boss is None or s["t"] < s["wait"]:
        return
    dbg = comp(boss, "RPGCombatDebug")
    if s["step"] == 0:
        dbg.debug_refill_player()
        bl = boss.get_actor_location()
        fwd = boss.get_actor_forward_vector()
        pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + fwd.x * 260, bl.y + fwd.y * 260, bl.z + 20), unreal.Rotator(0, 0, 0), False, True)
        comp(boss, "RPGBossEncounter").wake()
        s.update(step=1, run=0.0)
        return
    s["run"] += dt
    s["since_put"] += dt
    inst = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance()
    mont = inst.get_current_active_montage() if inst else None
    name = mont.get_name() if mont else None
    pos = inst.montage_get_position(mont) if mont else 0.0
    if name != s["last"]:
        bl = boss.get_actor_location()
        pl = pawn.get_actor_location()
        d = math.hypot(pl.x - bl.x, pl.y - bl.y)
        fwd = boss.get_actor_forward_vector()
        ang = math.degrees(math.atan2(pl.y - bl.y, pl.x - bl.x) - math.atan2(fwd.y, fwd.x))
        ang = (ang + 180) % 360 - 180
        log("t=%.2f montage %s -> %s (prev lasted %.2f s) player dist %.0f angle %.0f" % (s["run"], s["last"], name, s["run"] - s["last_t"], d, ang))
        s["last"], s["last_t"] = name, s["run"]
    if s["since_put"] > 0.4:
        s["since_put"] = 0.0
        dbg.debug_refill_player()
        bl = boss.get_actor_location()
        pl = pawn.get_actor_location()
        if math.hypot(pl.x - bl.x, pl.y - bl.y) > 330:
            fwd = boss.get_actor_forward_vector()
            pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + fwd.x * 260, bl.y + fwd.y * 260, bl.z + 20), unreal.Rotator(0, 0, 0), False, True)
    if s["run"] > 30.0:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("done")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
