"""Gate 2 / G2-3: the A5 heal punish (Freeze 16 A5, tests P01 to P08). The boss is frozen awake; the player stands in front of it.
H0 real input: IA_UseTool plays the drink montage and the boss sees it (heal start = montage edge). P01 a legal heal queues one throw: telegraph, release near 0.45 s, a javelin that travels and hits a player who stays put, after the drink animation
(dodgeable on the heal exit). P02 out of range (300 and 1200 cm) queues nothing. P03 a wall between boss and player queues nothing. P04 a heal during a committed attack (A2) and during a stance break is ignored and does not touch the attack.
P05 five heal events in one frame queue one punish, a heal during the throw and a heal inside the cooldown are discarded, the cooldown ends and the next heal is accepted. P06 dodging on the heal exit (backward roll i-frames pass it, a side roll leaves its line;
informational scan of the press times). P07 a reset clears a pending request and destroys a javelin in flight. P08 a missing clip is a safe failure with a log line. P09 the boss dying clears the pending request.
Run pie_debug_overlay.py once after an editor start first. Log prefix [A5].
"""
import math
import unreal

log = lambda m: unreal.log("[A5] " + m)
USE = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_UseTool"
MOVE = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Move"
DODGE_KEY = "Gamepad_FaceButton_Right"
results = []
S = {"phase": "start", "t": 0.0, "i": 0, "next": 0.0, "mem": {}, "heal_until": 0.0, "real": False, "walls": [], "now": 0.0, "events": [], "last": {}, "heal_t": None, "stick": None, "stick_until": 0.0, "keys": {}}
handle = None


def check(name, ok, detail=""):
    results.append(ok)
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


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


def place(pawn, boss, dist, ang_deg):
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw + ang_deg)
    p = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(p, bl).yaw
    pawn.set_actor_location_and_rotation(p, unreal.Rotator(0, 0, look), False, True)


def parts(boss):
    return comp(boss, "RPGBossHealPunish"), comp(boss, "RPGAttackTracker"), comp(boss, "RPGCombatDebug"), comp(boss, "RPGBossEncounter")


def snap(pu, tr):
    return {"heal": pu.get_heal_event_count(), "acc": pu.get_accepted_count(), "rel": pu.get_released_count(), "busy": pu.get_discarded_busy_count(), "range": pu.get_discarded_range_count(),
            "sight": pu.get_discarded_sight_count(), "cool": pu.get_discarded_cooldown_count(), "pend": pu.get_discarded_pending_count(), "canc": pu.get_cancelled_count(),
            "hit": pu.get_javelin_hit_count(), "dodged": pu.get_javelin_dodged_count(), "world": pu.get_javelin_world_count(), "inst": tr.get_attack_instance(), "intr": tr.get_interrupted_count()}


def delta(a, b):
    return {k: b[k] - a[k] for k in b}


def key(pc, name, down):
    if S["keys"].get(name, False) != down:
        S["keys"][name] = down
        unreal.RPGInputTestUtils.set_key_down(pc, name, down)


def hook_heal(boss):
    pu = comp(boss, "RPGBossHealPunish")
    pu.notify_heal_started_for_test()


def real_heal():
    S["heal_until"] = S["now"] + 0.2


def javelins(w):
    return [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "RPGBossJavelin"]


def spawn_wall(boss):
    """A 40 x 800 x 600 cm wall 350 cm in front of the boss, across its line to the player."""
    bl = boss.get_actor_location()
    fwd = boss.get_actor_forward_vector()
    comp(boss, "RPGCombatDebug").debug_spawn_wall(unreal.Vector(bl.x + fwd.x * 350, bl.y + fwd.y * 350, bl.z), boss.get_actor_rotation(), unreal.Vector(0.4, 8, 6))


def remove_walls(boss):
    comp(boss, "RPGCombatDebug").debug_clear_walls()


def rewake(boss):
    pu, tr, dbg, enc = parts(boss)
    enc.wake()
    enc.hold_for_test(True)
    dbg.debug_refill_player()
    tr.enter_combat()


# ---- steps ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
def s_wake(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    rewake(boss)
    pu.set_editor_property("cooldown", 0.5)
    place(pawn, boss, 700, 0)


def s_h0_start(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0)
    S["mem"] = {"s": snap(pu, tr), "hp": health(pawn), "yaw": boss.get_actor_rotation().yaw}
    real_heal()


def s_h0_seen(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    S["real"] = d["heal"] == 1
    check("H0 the real heal (IA_UseTool) is seen as one heal start", S["real"], "heal events +%d, accepted +%d, pending %s" % (d["heal"], d["acc"], pu.is_pending()))
    check("P01 a legal heal queues exactly one throw", d["acc"] == 1 and (pu.is_pending() or d["rel"] == 1), "accepted +%d" % d["acc"])
    if not S["real"]:
        log("INFO real input did not start a heal here: logic steps use the test hook")


def s_h0_done(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P01 one release, one A5 attack instance", d["rel"] == 1 and d["inst"] == 1, "released +%d instances +%d" % (d["rel"], d["inst"]))
    check("P01 A5 committed near 0.45 s with the release in its window", 0.35 <= tr.get_last_commit_position() <= 0.6 and 0.35 <= tr.get_last_active_start_position() <= 0.65, "commit %.2f active %.2f" % (tr.get_last_commit_position(), tr.get_last_active_start_position()))
    check("P06 a player who stays put is hit (stationary)", d["hit"] == 1, "javelin hits +%d" % d["hit"])
    hit_at = next((t for (t, e) in S["events"] if e == "hit" and t >= (S["heal_t"] or 0)), None)
    if hit_at is not None and S["heal_t"] is not None:
        rel = hit_at - S["heal_t"]
        check("P06 the javelin arrives after the drink animation ends (dodgeable on the heal exit)", rel >= 1.15, "hit %.2f s after the heal start (drink ends at 1.13 s)" % rel)
    check("P01 heading locked from the release (no yaw drift)", tr.get_max_yaw_drift_after_commit() < 0.5, "drift %.2f" % tr.get_max_yaw_drift_after_commit())
    check("P01 no tracked move left running, no javelin left", not pu.is_pending() and len(javelins(w)) == 0)


def s_p02_a(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 300, 0)
    S["mem"] = {"s": snap(pu, tr)}
    hook_heal(boss)


def s_p02_a_check(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P02 a heal at 300 cm (too close) queues nothing", d["acc"] == 0 and d["range"] == 1 and not pu.is_pending(), "accepted +%d range +%d" % (d["acc"], d["range"]))
    place(pawn, boss, 1200, 0)
    S["mem"] = {"s": snap(pu, tr)}
    hook_heal(boss)


def s_p02_b_check(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P02 a heal at 1200 cm (too far) queues nothing", d["acc"] == 0 and d["range"] == 1 and not pu.is_pending(), "accepted +%d range +%d" % (d["acc"], d["range"]))


def s_p03(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    place(pawn, boss, 700, 0)
    spawn_wall(boss)
    S["mem"] = {"s": snap(pu, tr)}


def s_p03_heal(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    hook_heal(boss)


def s_p03_check(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P03 a wall between boss and player: nothing queued", d["acc"] == 0 and d["sight"] == 1 and not pu.is_pending(), "accepted +%d sight +%d" % (d["acc"], d["sight"]))
    remove_walls(boss)


def s_p04_start(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 500, 0)
    S["mem"] = {"s": snap(pu, tr)}
    check("P04 the committed attack (A2) starts", tr.start_move("A2"))


def s_p04_heal(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    S["mem"]["move"] = str(tr.get_current_move())
    hook_heal(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P04 a heal during a committed slam is discarded", d["acc"] == 0 and d["busy"] == 1 and not pu.is_pending(), "accepted +%d busy +%d, move %s" % (d["acc"], d["busy"], S["mem"]["move"]))
    check("P04 the slam goes on", str(tr.get_current_move()) == "A2", "move %s" % tr.get_current_move())


def s_p04_done(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P04 the slam ran to its end, no javelin was thrown", d["inst"] == 1 and d["intr"] == 0 and d["rel"] == 0, "instances +%d interrupted +%d released +%d" % (d["inst"], d["intr"], d["rel"]))


def s_p04b_stagger(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 600, 0)
    comp(boss, "RPGBossStagger").force_break_for_test()
    S["mem"] = {"s": snap(pu, tr)}


def s_p04b_heal(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    stag = comp(boss, "RPGBossStagger")
    staggered = stag.is_staggered()
    hook_heal(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P04 a heal during a stance break is discarded", staggered and d["acc"] == 0 and d["busy"] == 1 and not pu.is_pending(), "staggered %s accepted +%d busy +%d" % (staggered, d["acc"], d["busy"]))
    enc.reset_for_test()


def s_rewake(w, pc, pawn, boss):
    rewake(boss)
    pu, tr, dbg, enc = parts(boss)
    pu.set_editor_property("cooldown", 4.0)
    place(pawn, boss, 700, 0)


def s_p05_start(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0)
    S["mem"] = {"s": snap(pu, tr)}
    for _ in range(5):
        hook_heal(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P05 five heal events in one frame queue one punish", d["heal"] == 5 and d["acc"] == 1 and d["pend"] == 4, "events +%d accepted +%d pending-discarded +%d busy +%d range +%d sight +%d cooldown +%d" % (d["heal"], d["acc"], d["pend"], d["busy"], d["range"], d["sight"], d["cool"]))


def s_p05_mid(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    hook_heal(boss)  # during the throw
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P05 a heal during the throw is discarded", d["acc"] == 1 and d["pend"] + d["busy"] >= 5 and d["rel"] <= 1, "accepted +%d discarded %d" % (d["acc"], d["pend"] + d["busy"] - 0))


def s_p05_cool(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    a = snap(pu, tr)
    log("INFO cooldown left %.2f s" % pu.get_cooldown_remaining())
    hook_heal(boss)
    d = delta(a, snap(pu, tr))
    check("P05 a heal inside the cooldown is discarded", d["acc"] == 0 and d["cool"] == 1, "accepted +%d cooldown +%d, left %.2f s" % (d["acc"], d["cool"], pu.get_cooldown_remaining()))
    check("P05 one javelin so far", pu.get_released_count() - S["mem"]["s"]["rel"] == 1)


def s_p05_after(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0)
    a = snap(pu, tr)
    S["mem"]["a"] = a
    log("INFO cooldown left %.2f s" % pu.get_cooldown_remaining())
    hook_heal(boss)
    d = delta(a, snap(pu, tr))
    check("P05 after the cooldown the next heal is accepted", d["acc"] == 1, "accepted +%d" % d["acc"])


def s_p05_after_done(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P05 two javelins in all", d["rel"] == 2, "released +%d" % d["rel"])


def s_p06_setup(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    pu.set_editor_property("cooldown", 0.5)


def make_p06(offset, mode):
    """Real heal, then a roll pressed offset seconds after the heal start (mode back = no stick, side = stick left, fwd = stick forward, into the javelin)."""
    side = mode != "back"
    tag = "%s roll at heal+%.2f" % (mode, offset)

    def start(w, pc, pawn, boss):
        pu, tr, dbg, enc = parts(boss)
        dbg.debug_refill_player()
        place(pawn, boss, 700, 0)
        S["mem"] = {"s": snap(pu, tr), "hp": health(pawn)}
        S["heal_t"] = None
        if S["real"]:
            real_heal()
        else:
            hook_heal(boss)
            S["heal_t"] = S["now"]

    def press(w, pc, pawn, boss):
        key(pc, DODGE_KEY, True)
        if side:
            S["stick"] = (-1.0, 0.0) if mode == "side" else (0.0, 1.0)
            S["stick_until"] = S["now"] + 0.6

    def release(w, pc, pawn, boss):
        key(pc, DODGE_KEY, False)

    def result(w, pc, pawn, boss):
        pu, tr, dbg, enc = parts(boss)
        d = delta(S["mem"]["s"], snap(pu, tr))
        S.setdefault("p06", []).append((tag, d["hit"], d["dodged"], d["world"]))
        log("INFO P06 %s: hits %d, i-frame pass %d, world %d" % (tag, d["hit"], d["dodged"], d["world"]))

    return [(0.6, start), (offset, press), (0.08, release), (2.0, result)]


def s_p06_summary(w, pc, pawn, boss):
    rows = S.get("p06", [])
    by_tag = {r[0]: r for r in rows}
    exit_ok = [t for t in ("side roll at heal+1.13", "side roll at heal+1.30", "side roll at heal+1.50") if by_tag.get(t) and by_tag[t][1] == 0]
    check("P06 a side roll pressed on the heal exit (1.13, 1.30, 1.50 s after the heal start) leaves the javelin's line", len(exit_ok) == 3, "%s" % rows)
    back_hit = [r[0] for r in rows if r[0].startswith("back") and r[1] == 1]
    log("INFO P06 a backward roll along the flight line does not dodge: hit in %d of %d presses (%s)" % (len(back_hit), len([r for r in rows if r[0].startswith("back")]), back_hit))


def tag_obj(name):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % name)
    return t


def s_p06i_start(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0)
    pawn.call_method("AddOwnedGameplayTag", args=(tag_obj("Status.Invulnerable"),))
    S["mem"] = {"s": snap(pu, tr), "hp": health(pawn)}
    hook_heal(boss)


def s_p06i_check(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    hp1 = health(pawn)
    pawn.call_method("RemoveOwnedGameplayTag", args=(tag_obj("Status.Invulnerable"),))
    check("P06 an invulnerable player (i-frames) is passed through: no damage, counted as dodged", d["rel"] == 1 and d["hit"] == 0 and d["dodged"] == 1 and hp1 == S["mem"]["hp"], "released +%d hits +%d dodged +%d health %s -> %s" % (d["rel"], d["hit"], d["dodged"], S["mem"]["hp"], hp1))


def s_p07_pending(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0)
    S["mem"] = {"s": snap(pu, tr)}
    hook_heal(boss)
    check("P07 a request is pending", pu.is_pending())


def s_p07_reset(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    enc.reset_for_test()


def s_p07_check(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P07 a reset clears the pending request, no javelin", not pu.is_pending() and d["rel"] == 0 and d["canc"] == 1 and len(javelins(w)) == 0, "released +%d cancelled +%d" % (d["rel"], d["canc"]))
    check("P07 the reset also clears the cooldown", pu.get_cooldown_remaining() == 0.0, "left %.2f" % pu.get_cooldown_remaining())
    rewake(boss)


def s_p07_flight_start(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 1000, 0)
    S["mem"] = {"s": snap(pu, tr)}
    hook_heal(boss)


def s_p07_flight_reset(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    check("P07 a javelin is in flight", len(javelins(w)) == 1, "javelins %d" % len(javelins(w)))
    enc.reset_for_test()


def s_p07_flight_check(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P07 a reset destroys the javelin in flight without a hit", len(javelins(w)) == 0 and d["hit"] == 0 and d["rel"] == 1, "javelins %d hits +%d" % (len(javelins(w)), d["hit"]))
    rewake(boss)


def s_p08_start(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0)
    attacks = list(tr.get_editor_property("attacks"))
    idx = next(i for i, a in enumerate(attacks) if str(a.get_editor_property("move_id")) == "A5")
    S["mem"] = {"s": snap(pu, tr), "idx": idx, "path": str(attacks[idx].get_editor_property("clip_path"))}
    attacks[idx].set_editor_property("clip_path", "/Game/OneBossFight/Boss01/Animations/DoesNotExist.DoesNotExist")
    tr.set_editor_property("attacks", attacks)
    hook_heal(boss)


def s_p08_check(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P08 a missing clip: nothing queued, no javelin, no crash", d["acc"] == 0 and d["busy"] == 1 and not pu.is_pending() and d["rel"] == 0, "accepted +%d busy +%d" % (d["acc"], d["busy"]))
    attacks = list(tr.get_editor_property("attacks"))
    attacks[S["mem"]["idx"]].set_editor_property("clip_path", S["mem"]["path"])
    tr.set_editor_property("attacks", attacks)


def s_p09_start(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_refill_player()
    place(pawn, boss, 700, 0)
    S["mem"] = {"s": snap(pu, tr)}
    hook_heal(boss)


def s_p09_kill(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    dbg.debug_kill_boss()


def s_p09_check(w, pc, pawn, boss):
    pu, tr, dbg, enc = parts(boss)
    d = delta(S["mem"]["s"], snap(pu, tr))
    check("P09 the boss dying clears the pending request: no javelin", not pu.is_pending() and d["rel"] == 0 and len(javelins(w)) == 0, "released +%d cancelled +%d" % (d["rel"], d["canc"]))


STEPS = [
    (9.0, s_wake),
    (1.0, s_h0_start), (0.15, s_h0_seen), (2.6, s_h0_done),
    (0.5, s_p02_a), (0.2, s_p02_a_check), (0.1, s_p02_b_check),
    (0.3, s_p03), (0.5, s_p03_heal), (0.2, s_p03_check),
    (0.5, s_p04_start), (0.7, s_p04_heal), (3.2, s_p04_done),
    (0.5, s_p04b_stagger), (0.2, s_p04b_heal), (1.0, s_rewake),
    (4.0, s_p05_start), (0.5, s_p05_mid), (1.8, s_p05_cool), (3.2, s_p05_after), (2.6, s_p05_after_done),
    (0.5, s_p06_setup),
]
for _off in (1.00, 1.13, 1.20, 1.30, 1.40, 1.50, 1.60):
    STEPS += make_p06(_off, "back")
for _off in (1.13, 1.30, 1.50):
    STEPS += make_p06(_off, "side")
for _off in (1.20, 1.40):
    STEPS += make_p06(_off, "fwd")
STEPS += [
    (0.1, s_p06_summary),
    (3.0, s_p06i_start), (2.8, s_p06i_check),
    (0.5, s_p07_pending), (0.15, s_p07_reset), (0.3, s_p07_check), (3.0, s_p07_flight_start), (0.6, s_p07_flight_reset), (0.4, s_p07_flight_check),
    (3.0, s_p08_start), (0.2, s_p08_check),
    (0.5, s_p09_start), (0.2, s_p09_kill), (0.6, s_p09_check),
]


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, next=STEPS[0][0])
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None:
        return
    pu = comp(boss, "RPGBossHealPunish")
    if pc is not None and s["now"] < s["heal_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(USE), unreal.Vector(1, 0, 0))
    if pc is not None and s["stick"] is not None:
        if s["now"] < s["stick_until"]:
            unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(MOVE), unreal.Vector(s["stick"][0], s["stick"][1], 0))
        else:
            s["stick"] = None
    if pu is not None:
        # event times (for the arrival time of the javelin and the heal start)
        last = s["last"]
        heal_n, hit_n = pu.get_heal_event_count(), pu.get_javelin_hit_count()
        if heal_n > last.get("heal", heal_n):
            s["heal_t"] = s["now"]
            s["events"].append((s["now"], "heal"))
        if hit_n > last.get("hit", hit_n):
            s["events"].append((s["now"], "hit"))
        last["heal"], last["hit"] = heal_n, hit_n
    if s["t"] < s["next"]:
        return
    if s["i"] >= len(STEPS):
        finish()
        return
    _, fn = STEPS[s["i"]]
    try:
        fn(w, pc, pawn, boss)
    except Exception:
        import traceback
        check("step %d (%s) raised" % (s["i"], fn.__name__), False, traceback.format_exc())
    s["i"] += 1
    s["t"] = 0.0
    s["next"] = STEPS[s["i"]][0] if s["i"] < len(STEPS) else 0.5


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        check("tick raised", False)
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
