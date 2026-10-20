"""
PIE check of the boss's phase two (URPGBossPhases): wake the boss, push it below 50% health, and log the transition (roar clip, held behaviour), then the buffs (walk
speed, Attack attribute, attack montage play rates in the log of the component) and the fireballs it casts at the player (the player stands 900 cm away and is kept alive).
Finally the player is killed: after the respawn the encounter reset must bring the boss back to phase one (speed and Attack restored). Log prefix [P2Pie].
Open L_SevarogArena first; run with Scripts/run_in_editor.py (editor throttling off).
"""
import unreal

log = lambda m: unreal.log("[P2Pie] " + m)
state = {"phase": "start", "t": 0.0, "stage": "wake", "t0": 0.0, "last_m": None, "pawn_id": None, "heal_t": 0.0, "events": [], "speed1": None, "attack1": None, "projectiles": set()}
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
    try:
        return c.call_method("Get Current Attribute Value", args=(t,)) if c else None
    except Exception:
        return None


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


def speed_of(boss):
    return boss.get_components_by_class(unreal.CharacterMovementComponent)[0].get_editor_property("max_walk_speed")


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
    if s["t"] > 150.0:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next(iter([a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"]), None) if w else None
    if pawn is None or boss is None:
        return
    enc, ph = comp(boss, "RPGBossEncounter"), comp(boss, "RPGBossPhases")
    if ph is None or enc is None:
        finish("boss has no phases or encounter component")
        return
    if s["pawn_id"] is None:
        s["pawn_id"] = pawn.get_name()
    new_pawn = pawn.get_name() != s["pawn_id"]
    m = montage_of(boss)
    sp = speed_of(boss)
    if s["stage"] in ("fireballs",) and ph.is_phase_two() and (round(sp), ) not in s.setdefault("speeds", set()):
        s["speeds"].add((round(sp),))
        log("   boss max walk speed now %.0f (phase one speeds were 600 walk / 800 sprint)" % sp)
    if m != s["last_m"]:
        s["last_m"] = m
        log("   boss montage -> %s (phase two %s, transition %s, speed %.0f)" % (m, ph.is_phase_two(), ph.is_in_transition(), speed_of(boss)))
    for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
        n = a.get_name()
        if "FireBallProjectile" in n and n not in s["projectiles"]:
            s["projectiles"].add(n)
            log("   projectile %s spawned at %.0f,%.0f,%.0f" % (n, a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z))
    s["heal_t"] += dt
    if s["heal_t"] > 0.3 and s["stage"] != "die":
        s["heal_t"] = 0.0
        set_attr(pawn, "Attribute.Health", 100.0)
    el = s["t"] - s["t0"]

    if s["stage"] == "wake" and s["t"] > 7.0:
        s["speed1"], s["attack1"] = speed_of(boss), attr(boss, "Attribute.Attack")
        log("phase one: walk speed %.0f, Attack attribute %s, hp %s" % (s["speed1"], s["attack1"], attr(boss, "Attribute.Health")))
        pawn.set_actor_location_and_rotation(unreal.Vector(-900, 0, 110), unreal.Rotator(0, 0, 0), False, True)
        enc.wake()
        s.update(stage="settle", t0=s["t"])
    elif s["stage"] == "settle" and el > 4.0:
        log("== pushing the boss to 240 HP (48%)")
        set_attr(boss, "Attribute.Health", 240.0)
        s.update(stage="transition", t0=s["t"])
    elif s["stage"] == "transition":
        if ph.is_in_transition() and not s.get("saw_transition"):
            s["saw_transition"] = True
            log("   transition started, boss montage %s" % m)
        if s.get("saw_transition") and not ph.is_in_transition():
            check("phase two started once the boss fell under 50%", ph.is_phase_two() and ph.get_phase_two_count() == 1, "(count %d)" % ph.get_phase_two_count())
            check("walk speed raised", speed_of(boss) > s["speed1"] * 1.15, "(%.0f -> %.0f)" % (s["speed1"], speed_of(boss)))
            a2 = attr(boss, "Attribute.Attack")
            check("Attack attribute raised", s["attack1"] is not None and a2 is not None and a2 > s["attack1"] * 1.2, "(%s -> %s)" % (s["attack1"], a2))
            s.update(stage="fireballs", t0=s["t"])
        elif el > 15.0:
            check("phase two started", False, "(no transition)")
            finish("no transition")
    elif s["stage"] == "fireballs":
        # keep the player at 900 cm so the boss has a fireball distance and the melee does not interrupt
        d = boss.get_actor_location() - pawn.get_actor_location()
        flat = unreal.Vector(d.x, d.y, 0)
        if flat.length() < 700.0 or flat.length() > 1500.0:
            side = unreal.Vector(-d.x, -d.y, 0).normal()
            pawn.set_actor_location(boss.get_actor_location() + side * 900.0 + unreal.Vector(0, 0, 10 - boss.get_actor_location().z + 100), False, True)
        set_attr(boss, "Attribute.Health", 200.0) if (attr(boss, "Attribute.Health") or 0) < 120 else None
        if el > 28.0:
            check("boss casts fireballs in phase two", ph.get_fireball_count() >= 1 and len(s["projectiles"]) >= 1, "(%d fireballs, %d projectiles seen)" % (ph.get_fireball_count(), len(s["projectiles"])))
            s.update(stage="die", t0=s["t"])
            log("== killing the player")
            set_attr(pawn, "Attribute.Health", 0.0)
    elif s["stage"] == "die":
        if new_pawn:
            s["pawn_id"] = pawn.get_name()
            s.update(stage="after", t0=s["t"])
    elif s["stage"] == "after" and el > 3.0:
        check("encounter reset puts the boss back to phase one", (not ph.is_phase_two()) and round(speed_of(boss)) in (300, 600, 800), "(phase two %s, speed %.0f; the pack's own speeds are 300, 600 and 800, scaled ones would be 360, 720, 960)" % (ph.is_phase_two(), speed_of(boss)))
        check("Attack attribute restored", abs((attr(boss, "Attribute.Attack") or 0) - (s["attack1"] or 0)) < 0.5, "(%s vs %s)" % (attr(boss, "Attribute.Attack"), s["attack1"]))
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
