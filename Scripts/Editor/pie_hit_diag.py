"""Why does a forced A2 not hurt? Part 1: the pack AI fights a standing player (health changes logged with the boss montage). Part 2: the boss is held and A2 is started by hand at several distances.
Log prefix [HitDiag]."""
import unreal

log = lambda m: unreal.log("[HitDiag] " + m)
state = {"t": 0.0, "phase": "start", "part": 0, "hp": None, "stage_t": 0.0, "dist_i": 0}
handle = None
DISTS = [260, 220, 180, 140]


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def hp(actor):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="Attribute.Health")')
    return c.call_method("Get Current Attribute Value", args=(t,))


def montage(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return ("%s %.2f" % (m.get_name(), inst.montage_get_position(m))) if m else None


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start" and s["t"] > 0.5:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        s.update(phase="play", t=0.0)
        return
    if s["phase"] != "play":
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if w is None:
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    if pawn is None or boss is None:
        return
    t = s["t"]
    cur = hp(pawn)
    if s["hp"] is not None and cur < s["hp"] - 0.01:
        log("part %d: player health %.0f -> %.0f, boss montage %s, distance %.0f" % (s["part"], s["hp"], cur, montage(boss), (pawn.get_actor_location() - boss.get_actor_location()).length()))
        s["hp"] = cur
    elif s["hp"] is None or cur > s["hp"]:
        s["hp"] = cur
    dbg = comp(boss, "RPGCombatDebug")
    if s["part"] == 0 and t > 9.0:
        pawn.set_actor_location_and_rotation(unreal.Vector(boss.get_actor_location().x + 350, boss.get_actor_location().y, boss.get_actor_location().z), unreal.Rotator(0, 180, 0), False, True)
        s.update(part=1, stage_t=t)
        log("part 1: pack AI, player stands 350 cm away")
    elif s["part"] == 1:
        if int((t - s["stage_t"]) * 2) % 2 == 0 and int(t - s["stage_t"]) % 4 == 3 and dbg and cur < 40:
            dbg.debug_refill_player()
        if t - s["stage_t"] > 8:
            comp(boss, "RPGBossEncounter").hold_for_test(True)
            s.update(part=2, stage_t=t, dist_i=0, started=False)
            log("part 2: boss held, forced A2 at several distances")
    elif s["part"] == 2:
        el = t - s["stage_t"]
        if not s["started"] and montage(boss) is None and el > 1.5:
            if s["dist_i"] >= len(DISTS):
                unreal.unregister_slate_post_tick_callback(handle)
                handle = None
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
                log("done")
                return
            d = DISTS[s["dist_i"]]
            boss.set_actor_rotation(unreal.Rotator(0, 0, 0), False)
            pawn.set_actor_location_and_rotation(unreal.Vector(boss.get_actor_location().x + d, boss.get_actor_location().y, boss.get_actor_location().z), unreal.Rotator(0, 180, 0), False, True)
            if dbg:
                dbg.debug_refill_player()
            log("forced A2 at %d cm: %s" % (d, comp(boss, "RPGAttackTracker").start_move("A2")))
            s.update(started=True, st=t)
        if s["started"] and t - s["st"] > 4.0:
            s.update(started=False, dist_i=s["dist_i"] + 1)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
