"""Gate 2 / G2-3, informational: A5 in a natural fight. The boss is awake and NOT held (the pack's behaviour tree runs); the player is teleported to 700 cm in front of it and drinks with the real input (IA_UseTool)
every 8 s, four times. Logs, per round, what the heal punish did (accepted or which discard reason, released, javelin result, interrupted by the pack) and the boss's montage when the heal started.
Nothing is asserted; the point is to see whether the pack's own attacks and the throw coexist. Run pie_debug_overlay.py once after an editor start first. Log prefix [A5N].
"""
import math
import unreal

log = lambda m: unreal.log("[A5N] " + m)
USE = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_UseTool"
S = {"phase": "start", "t": 0.0, "i": 0, "next": 0.0, "now": 0.0, "heal_until": 0.0, "mem": {}}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def place(pawn, boss, dist):
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    p = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, unreal.MathLibrary.find_look_at_rotation(p, bl).yaw, 0), False, True)


def counters(pu):
    return (pu.get_heal_event_count(), pu.get_accepted_count(), pu.get_released_count(), pu.get_discarded_busy_count(), pu.get_discarded_range_count(), pu.get_discarded_sight_count(),
            pu.get_discarded_cooldown_count(), pu.get_discarded_pending_count(), pu.get_cancelled_count(), pu.get_javelin_hit_count(), pu.get_javelin_dodged_count(), pu.get_javelin_world_count())


NAMES = ("heals", "accepted", "released", "busy", "range", "sight", "cooldown", "pending", "cancelled", "javelin hit", "dodged", "world")


def _tick(dt):
    global handle
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, next=9.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None:
        return
    if pc is not None and s["now"] < s["heal_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(USE), unreal.Vector(1, 0, 0))
    if s["t"] < s["next"]:
        return
    pu, tr, dbg, enc = comp(boss, "RPGBossHealPunish"), comp(boss, "RPGAttackTracker"), comp(boss, "RPGCombatDebug"), comp(boss, "RPGBossEncounter")
    if s["i"] == 0:
        enc.wake()
        dbg.debug_refill_player()
        s["next"] = 5.0
    elif s["i"] % 2 == 1 and s["i"] <= 7:
        dbg.debug_refill_player()
        place(pawn, boss, 700)
        mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)
        inst = mc[0].get_anim_instance() if mc else None
        mont = inst.get_current_active_montage() if inst else None
        s["mem"] = {"c": counters(pu), "mont": mont.get_name() if mont else "none", "inst": tr.get_attack_instance(), "hp": None}
        s["heal_until"] = s["now"] + 0.2
        s["next"] = 6.0
    elif s["i"] % 2 == 0 and s["i"] <= 8:
        c0, c1 = s["mem"]["c"], counters(pu)
        log("round %d: boss montage at the heal '%s'; %s; boss attacks tracked since: %d, now %s" % (s["i"] // 2, s["mem"]["mont"], ", ".join("%s +%d" % (n, b - a) for n, a, b in zip(NAMES, c0, c1) if b != a) or "no counter moved", tr.get_attack_instance() - s["mem"]["inst"], tr.get_current_move()))
        s["next"] = 2.0
    else:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("done")
        return
    s["i"] += 1
    s["t"] = 0.0


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
