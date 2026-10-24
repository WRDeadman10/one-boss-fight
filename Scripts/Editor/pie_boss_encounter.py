"""
PIE check of the boss encounter flow (URPGBossEncounter): the boss must sleep at home while the player is far, wake when the player walks inside the gate, fight and
chase, and after the player dies and respawns it must be back at its start with full health and poise, dormant again, and wake again when approached. Real input is not
needed here (the player walks with movement input and is killed by setting its health to 0). Log prefix [EncPie]. Open L_SevarogArena first; run with
Scripts/run_in_editor.py (editor throttling off).
"""
import unreal

log = lambda m: unreal.log("[EncPie] " + m)
state = {"phase": "start", "t": 0.0, "stage": "far", "stage_t0": 0.0, "pawn_id": None, "last_m": None, "heal_t": 0.0, "last_dorm": None, "events": []}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    return c.call_method("Get Current Attribute Value", args=(t,)) if c else None


def max_attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    return c.call_method("GetMaxAttributeValue", args=(t,)) if c else None


def set_attr(actor, tag, value):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    c.call_method("Set Current Attribute Value", args=(t, value))


def montage_of(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def check(name, ok, detail=""):
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    state["events"].append((name, ok))


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 160.0:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, stage_t0=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next(iter([a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"]), None) if w else None
    if boss is None:
        return
    enc = comp(boss, "RPGBossEncounter")
    if enc is None:
        finish("boss has no RPGBossEncounter component")
        return
    if pawn is None:
        return
    if s["pawn_id"] is None:
        s["pawn_id"] = pawn.get_name()
    new_pawn = pawn.get_name() != s["pawn_id"]
    dorm = enc.is_dormant()
    if dorm != s["last_dorm"]:
        s["last_dorm"] = dorm
        log("   boss dormant -> %s (stage %s, boss at %.0f,%.0f, player %.0f cm away)" % (dorm, s["stage"], boss.get_actor_location().x, boss.get_actor_location().y, (boss.get_actor_location() - pawn.get_actor_location()).length()))
    m = montage_of(boss)
    if m != s["last_m"]:
        s["last_m"] = m
        log("   boss montage -> %s (at %.0f,%.0f)" % (m, boss.get_actor_location().x, boss.get_actor_location().y))
    s["heal_t"] += dt
    if s["heal_t"] > 0.4 and s["stage"] not in ("die",):
        s["heal_t"] = 0.0
        set_attr(pawn, "Attribute.Health", 100.0)
    home = enc.get_home_transform().translation
    d = boss.get_actor_location() - pawn.get_actor_location()
    flat = unreal.Vector(d.x, d.y, 0)
    el = s["t"] - s["stage_t0"]

    if s["stage"] == "far":  # sleeping while the player is far
        if el > 8.0:
            moved = (boss.get_actor_location() - home).length()
            check("boss sleeps while the player is far", dorm and moved < 5.0 and (m is None), "(dormant %s, moved %.0f cm, montage %s)" % (dorm, moved, m))
            s.update(stage="approach", stage_t0=s["t"])
    elif s["stage"] == "approach":  # walk in: the boss must wake inside the gate
        pawn.add_movement_input(flat.normal(), 1.0, False)
        if not dorm:
            check("boss wakes inside the gate", flat.length() <= 1300.0, "(player %.0f cm away, gate 1200)" % flat.length())
            s.update(stage="fight", stage_t0=s["t"])
        elif el > 30.0:
            check("boss wakes inside the gate", False, "(never woke)")
            finish("no wake")
    elif s["stage"] == "fight":  # let it chase and attack, away from home
        if flat.length() > 300.0 and el < 3.0:
            pass
        if el > 7.0:
            away = (boss.get_actor_location() - home).length()
            check("boss fights and leaves its start", away > 150.0 and not dorm, "(%.0f cm from home, hp %s)" % (away, attr(boss, "Attribute.Health")))
            set_attr(boss, "Attribute.Health", 300.0)  # hurt, so the reset has something to heal
            set_attr(boss, "Attribute.Poise", 30.0)  # the pack's poise is pinned full by the posture component within 0.05 s: the pool below is what the reset has to restore
            comp(boss, "RPGCombatDebug").debug_set_boss_posture(30.0)
            log("   posture pool lowered to %.0f" % comp(boss, "RPGBossPosture").get_posture())
            s.update(stage="die", stage_t0=s["t"], die_pos=boss.get_actor_location())
            set_attr(pawn, "Attribute.Health", 0.0)
            log("== killing the player (boss at %.0f,%.0f, hp %s, poise %s)" % (boss.get_actor_location().x, boss.get_actor_location().y, attr(boss, "Attribute.Health"), attr(boss, "Attribute.Poise")))
    elif s["stage"] == "die":
        if new_pawn:
            s["pawn_id"] = pawn.get_name()
            s.update(stage="after_respawn", stage_t0=s["t"])
            log("== player respawned as %s" % pawn.get_name())
        elif el > 20.0:
            check("player respawns", False)
            finish("no respawn")
    elif s["stage"] == "after_respawn":
        if el > 3.0:
            at_home = (boss.get_actor_location() - home).length()
            hp, mx = attr(boss, "Attribute.Health"), max_attr(boss, "Attribute.Health")
            check("boss back at its start after the respawn", at_home < 10.0, "(%.1f cm from home)" % at_home)
            pool = comp(boss, "RPGBossPosture").get_posture()
            check("boss health, poise and posture pool full", hp is not None and mx is not None and abs(hp - mx) <= 0.5 and (attr(boss, "Attribute.Poise") or 0) >= 99.0 and pool >= 99.0, "(hp %s/%s poise %s posture pool %.1f)" % (hp, mx, attr(boss, "Attribute.Poise"), pool))
            check("boss dormant again", dorm and enc.get_reset_count() >= 1, "(dormant %s, resets %d, montage %s)" % (dorm, enc.get_reset_count(), m))
            s.update(stage="idle_far", stage_t0=s["t"])
    elif s["stage"] == "idle_far":
        if el > 5.0:
            check("boss stays asleep while the new player is far", dorm and (boss.get_actor_location() - home).length() < 10.0, "(%.0f cm away from the player)" % flat.length())
            s.update(stage="approach2", stage_t0=s["t"])
    elif s["stage"] == "approach2":
        pawn.add_movement_input(flat.normal(), 1.0, False)
        if not dorm:
            check("boss wakes again after the reset", True, "(player %.0f cm away)" % flat.length())
            s.update(stage="end", stage_t0=s["t"])
    elif s["stage"] == "end":
        if el > 4.0:
            fails = [n for n, ok in s["events"] if not ok]
            finish("%d checks, %d failed %s" % (len(s["events"]), len(fails), fails))


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
