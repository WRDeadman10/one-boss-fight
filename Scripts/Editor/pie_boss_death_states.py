"""
The boss's death clip where the other systems are busy (review D of RPGBossDeath): three scenarios, each in its own PIE (a dead boss is destroyed by the pack, so one death per PIE; the driver stops and starts PIE itself).
  K  the boss dies in the kneel of a stance break (the kneel loop is playing, the get-up is waiting): the death clip must take over from the kneel loop and stay.
  R  the boss dies during the phase two roar (the roar montage is playing): the death clip takes over from the roar.
  D  the encounter is reset while the boss is dying: the dead boss stays dead (the reset is refused and counted), the clip keeps playing.
Every scenario is sampled every 0.2 s for 5 s after the kill (the pack destroys the dead boss about 4.35 s later, KI-083) and checks: the death is seen once and the clip plays within 1.5 s (K, R: the earlier montage is gone),
the mesh never simulates physics while the clip plays, the mesh keeps its place on the capsule (same attach parent, relative location within 1 cm: the ragdoll's throw is taken out again), the pelvis stays between 55 cm above the floor and the standing height,
the clip is not restarted more than once, and the pack's own sword (static mesh Weapon Mesh) stays hidden while the look is on.
Log prefix [DeathStates]; ends with RESULT n/m passed. Run pie_debug_overlay.py once after an editor start first.
"""
import unreal

log = lambda m: unreal.log("[DeathStates] " + m)
CLIP = "AN_Boss01_DeathLegend"
SAMPLE_SECONDS = 5.0
SAMPLE_STEP = 0.2
SCENARIOS = ["K", "R", "D"]
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "killed": False, "gone": 0.0, "floor": 0.0, "idx": 0, "stop_t": 0.0}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    if actor is None:
        return None
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def actors():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def P():
    w, pc, pawn, boss = actors()
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"),
            "death": comp(boss, "RPGBossDeath"), "stg": comp(boss, "RPGBossStagger"), "ph": comp(boss, "RPGBossPhases")}


def until(cond, timeout, step=0.0):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield step
    return True


def fresh():
    p = P()
    p["enc"].reset_for_test()
    yield 0.8
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["dbg"].debug_refill_player()
    p["tr"].enter_combat()
    comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
    yield 2.2


def leader(boss):
    """The pack's mesh (the look's followers are named RPGLook...)."""
    return next(c for c in boss.get_components_by_class(unreal.SkeletalMeshComponent) if not c.get_name().startswith("RPGLook"))


def pelvis(boss):
    return leader(boss).get_socket_location("pelvis").z - S["floor"]


def pack_weapons(boss):
    return [c for c in boss.get_components_by_class(unreal.StaticMeshComponent) if "Weapon" in c.get_name() and not c.get_name().startswith("RPGLook")]


def placement(boss):
    mesh = leader(boss)
    parent = mesh.get_attach_parent()
    return {"parent": parent.get_name() if parent else None, "loc": mesh.get_editor_property("relative_location")}


def dist3(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2) ** 0.5


def take(q, t, pre):
    boss, death = q["boss"], q["death"]
    mesh = leader(boss)
    now = placement(boss)
    weapons = pack_weapons(boss)
    s = {"t": t, "anim": q["dbg"].debug_boss_montage_anim_name(), "sim": bool(mesh.is_simulating_physics()), "pelvis": pelvis(boss), "state": None, "counts": None,
         "same_parent": now["parent"] == pre["parent"], "drift": dist3(now["loc"], pre["loc"]),
         "weapons_visible": [w.get_name() for w in weapons if not w.get_editor_property("hidden_in_game")], "weapons": len(weapons), "stage": None}
    if death is not None:
        s["state"] = death.get_death_state_name()
        s["counts"] = {"deaths": death.get_death_count(), "plays": death.get_clip_play_count(), "restarts": death.get_clip_restart_count(), "holds": death.get_pose_hold_count(), "physics_off": death.get_physics_off_count()}
    if q["stg"] is not None:
        s["stage"] = q["stg"].get_clip_stage_name()
    return s


def sample_after_kill(label, pre, extra=None):
    """Kills the boss and samples it for SAMPLE_SECONDS (or until the pack destroys it). Returns (samples, gone_at, kill_time)."""
    p = P()
    S["killed"] = True
    t_kill = S["now"]
    p["dbg"].debug_kill_boss()
    samples = []
    gone_at = None
    while S["now"] - t_kill < SAMPLE_SECONDS:
        q = P()
        if q["boss"] is None:
            gone_at = S["now"] - t_kill
            break
        samples.append(take(q, S["now"] - t_kill, pre))
        if extra:
            extra(q, S["now"] - t_kill)
        yield SAMPLE_STEP
    for s in samples:
        log("%s t=%.2f clip '%s' simulating %s pelvis %.0f state %s stage %s drift %.2f weapons visible %s" % (label, s["t"], s["anim"], s["sim"], s["pelvis"], s["state"], s["stage"], s["drift"], s["weapons_visible"]))
    log("%s the boss %s" % (label, "is gone at t=%.2f (destroyed by the pack)" % gone_at if gone_at is not None else "still exists after %.1f s" % SAMPLE_SECONDS))
    S["samples"], S["gone_at"] = samples, gone_at


def judge(label, samples, gone_at, stand, takeover=True):
    """The checks every scenario shares."""
    if not samples:
        check("%s the boss was sampled after the kill" % label, False, "it was gone at once")
        return
    counts = next((s["counts"] for s in reversed(samples) if s["counts"]), {})
    log("%s counters %s" % (label, counts))
    seen = [s["t"] for s in samples if s["state"] in ("dying", "dead")]
    check("%s the death is seen within 0.5 s (first at %s) and counted once (%s)" % (label, "%.2f" % seen[0] if seen else "never", counts.get("deaths")), bool(seen) and seen[0] <= 0.5 and counts.get("deaths") == 1)
    clip_t = [s["t"] for s in samples if s["anim"] == CLIP]
    check("%s the death clip plays within 1.5 s (first at %s; montages seen %s)" % (label, "%.2f" % clip_t[0] if clip_t else "never", sorted(set(s["anim"] for s in samples))), bool(clip_t) and clip_t[0] <= 1.5)
    if takeover and clip_t:
        after = [s for s in samples if s["t"] >= clip_t[0] + 0.2]
        others = sorted(set(s["anim"] for s in after if s["anim"] != CLIP))
        check("%s after the takeover no other montage plays (%d samples, others %s)" % (label, len(after), others), len(after) >= 3 and not others)
    playing = [s for s in samples if s["anim"] == CLIP]
    check("%s the mesh does not simulate physics while the clip plays (%d samples, %d simulating)" % (label, len(playing), sum(1 for s in playing if s["sim"])), len(playing) >= 3 and not any(s["sim"] for s in playing))
    worst = max(s["drift"] for s in samples)
    check("%s the mesh keeps its place on the capsule (same attach parent %s, largest drift %.2f cm)" % (label, all(s["same_parent"] for s in samples), worst), all(s["same_parent"] for s in samples) and worst < 1.0)
    early = [s for s in samples if s["t"] <= 3.0]
    lo, hi = min(s["pelvis"] for s in early), max(s["pelvis"] for s in early)
    check("%s the pelvis stays between 55 cm above the floor and the standing height (%.0f to %.0f, standing %.0f)" % (label, lo, hi, stand), lo >= 55.0 and hi <= 160.0)
    check("%s the clip was started %s time(s) and restarted %s time(s) (at most 1)" % (label, counts.get("plays"), counts.get("restarts")), counts.get("plays", 0) >= 1 and counts.get("restarts", 99) <= 1)
    with_weapon = [s for s in samples if s["weapons"] > 0]
    visible = sorted(set(w for s in with_weapon for w in s["weapons_visible"]))
    check("%s the pack's own sword stays hidden (%d samples with a weapon mesh, visible: %s)" % (label, len(with_weapon), visible), len(with_weapon) >= 1 and not visible)


def setup_standing():
    p = P()
    try:
        half = p["boss"].get_components_by_class(unreal.CapsuleComponent)[0].get_scaled_capsule_half_height()
    except Exception:
        half = 90.0
    S["floor"] = p["boss"].get_actor_location().z - half
    return pelvis(p["boss"]), placement(p["boss"])


def scen_kneel():
    yield from fresh()
    yield 0.5
    stand, pre = setup_standing()
    p = P()
    p["stg"].set_cooldown_for_test(0.0)
    p["stg"].force_break_for_test()
    reached = yield from until(lambda: P()["stg"].get_clip_stage_name() == "down", 4.0)
    yield 0.6
    q = P()
    check("K1 the stance break reached the kneel before the kill (stage %s, pelvis %.0f cm)" % (q["stg"].get_clip_stage_name(), pelvis(q["boss"])), reached and q["stg"].is_staggered())
    yield from sample_after_kill("K", pre)
    judge("K", S["samples"], S["gone_at"], stand)
    kneel_left = [s["stage"] for s in S["samples"] if s["t"] >= 1.0]
    log("K stagger stage seen from 1 s on: %s" % sorted(set(str(x) for x in kneel_left)))


def scen_roar():
    yield from fresh()
    yield 0.5
    stand, pre = setup_standing()
    p = P()
    p["dbg"].debug_set_boss_health_fraction(0.55)
    started = yield from until(lambda: P()["ph"].is_in_transition(), 3.0)
    yield 0.5
    q = P()
    check("R1 the roar was playing at the kill (transition %s, montage %s)" % (q["ph"].is_in_transition(), q["dbg"].debug_boss_montage_anim_name()), started and q["ph"].is_in_transition())
    yield from sample_after_kill("R", pre)
    judge("R", S["samples"], S["gone_at"], stand)


def scen_reset():
    yield from fresh()
    yield 0.5
    stand, pre = setup_standing()
    p = P()
    resets0, refusals0 = p["enc"].get_reset_count(), p["enc"].get_death_reset_refusals()
    holder = {}

    def extra(q, t):
        # 1.0 s after the kill the encounter is reset, as the respawn of the player would do; the counters are read 0.4 s later (the boss is destroyed by the pack about 4.4 s after the kill)
        if t >= 1.0 and "done" not in holder:
            holder["done"] = True
            q["enc"].reset_for_test()
            log("D the encounter reset was requested %.2f s after the kill" % t)
        elif t >= 1.4 and "done" in holder and "resets" not in holder:
            holder["resets"] = q["enc"].get_reset_count()
            holder["refusals"] = q["enc"].get_death_reset_refusals()

    yield from sample_after_kill("D", pre, extra)
    samples, gone_at = S["samples"], S["gone_at"]
    judge("D", samples, gone_at, stand)
    if "resets" in holder:
        check("D1 the reset was refused and counted (resets %d -> %d, refusals %d -> %d)" % (resets0, holder["resets"], refusals0, holder["refusals"]), holder["resets"] == resets0 and holder["refusals"] == refusals0 + 1)
    else:
        check("D1 the boss lived long enough to read the refusal counters", False)
    after = [s for s in samples if s["t"] >= 1.2]
    check("D2 after the refused reset the clip keeps playing and the pelvis stays low (%d samples, montages %s, pelvis %s)" % (len(after), sorted(set(s["anim"] for s in after)), ["%.0f" % s["pelvis"] for s in after][:6]),
          len(after) >= 3 and all(s["anim"] == CLIP for s in after) and all(s["pelvis"] < 160.0 for s in after))


def script():
    yield from {"K": scen_kneel, "R": scen_roar, "D": scen_reset}[SCENARIOS[S["idx"]]]()


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def next_scenario():
    S["idx"] += 1
    S.update(phase="stopping", gen=None, killed=False, gone=0.0, wait=0.0, stop_t=S["now"])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    if s["phase"] == "stopping":
        if world() is None and s["now"] - s["stop_t"] > 1.5:
            if s["idx"] >= len(SCENARIOS):
                finish()
            else:
                s.update(phase="start", t=0.0)
        elif s["now"] - s["stop_t"] > 20.0:
            check("PIE stopped between the scenarios", False)
            finish()
        return
    w, pc, pawn, boss = actors()
    if s["now"] - s.get("hb", 0.0) > 15.0:
        s["hb"] = s["now"]
        log("heartbeat: scenario %s, %.0f s, pawn %s, boss %s, wait %.2f" % (SCENARIOS[min(s["idx"], len(SCENARIOS) - 1)], s["now"], pawn.get_name() if pawn else None, boss.get_name() if boss else None, s["wait"]))
    if s["t"] > 120.0 and s["gen"] is not None:
        check("the scenario %s finished in time" % SCENARIOS[s["idx"]], False, "stopped after 120 s")
        next_scenario()
        return
    if boss is None and not s["killed"]:
        # before the kill a missing boss is a failed setup; after it the pack destroying the boss is the expected end and the scenario goes on without it
        s["gone"] += dt
        if s["gone"] > 15.0 and s["gen"] is not None:
            check("the boss exists (it was gone for 15 s before the kill)", False)
            next_scenario()
        return
    s["gone"] = 0.0
    if pawn is None and boss is not None:
        return
    if s["wait"] > 0:
        s["wait"] -= dt
        return
    if s["gen"] is None:
        if s["t"] < 9.0:
            return
        s["gen"] = script()
    try:
        s["wait"] = float(next(s["gen"]))
    except StopIteration:
        next_scenario()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        check("tick raised", False)
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
