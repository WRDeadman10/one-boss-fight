"""
The boss's death clip (G2-9, A-12; URPGBossDeath, see Documentation/DEATH_CLIP_NOTES.md): the boss is held awake, killed through the pack's attribute (debug_kill_boss: health 0 and the pack's Ability.Dead) and sampled every 0.2 s for 8 s
(does it exist, which clip its montage plays, is its mesh simulating physics, the pelvis height above the floor, the component's state). Checks:
  D1 the death component is on the boss and says "alive" before the kill (its mode is logged)
  D2 the death is seen once: the state leaves "alive" within 0.5 s and the death count is 1
  D3 the death clip plays: the boss's montage plays AN_Boss01_DeathLegend (read from the montage's own segment) in the first 1.5 s
  D4 the body lives until the collapse is over (the pack destroys a dead boss a few seconds after its death, KI-083): at least 2.6 s
  D5 the pelvis ends low (kneeling: below 90 cm above the floor and at least 40 cm under the standing value)
  D6 during the first 3 s the pelvis stays between 55 cm above the floor and 160 cm (the clip's standing height): no fall through the floor, no throw by the ragdoll
  D7 the mesh does not simulate physics while the clip plays (the pack's ragdoll must not fight it)
  D8 the final pose stays: from 3.2 s on the pelvis moves less than 3 cm (needs the boss to live that long, else skipped)
  D9 the mode did its part: OwnClip started the clip (restarted it at most once, froze the pose once the boss lived past HoldAtSeconds, took the pack's ragdoll out of physics at least once), PackMontage filled the pack's DeathMontages
  D10 the mesh keeps its place on the capsule (same attach parent, relative location within 1 cm of the value before the kill) and the pack's own sword (static mesh Weapon Mesh) stays hidden (the boss look is on)
The mode-less scenarios that stress the clip (kill in the kneel, in the roar, reset while dying) are in pie_boss_death_states.py.
The mode is the component's default; Saved/boss_death_mode.txt overrides it through the test hooks: "own" (OwnClip), "pack" (PackMontage), "pack_guard" (PackMontage with the pose guard).
The dead boss is destroyed by the pack, so this is the last scenario of its PIE run; a boss that disappears ends the run with the checks made so far.
Log prefix [BossDeath]; ends with RESULT n/m passed. Run pie_debug_overlay.py once after an editor start first.
"""
import os
import unreal

log = lambda m: unreal.log("[BossDeath] " + m)
CLIP = "AN_Boss01_DeathLegend"
SAMPLE_SECONDS = 8.0
SAMPLE_STEP = 0.2
_mf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "boss_death_mode.txt")
MODE_FILE = open(_mf).read().strip() if os.path.exists(_mf) else ""
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "killed": False, "gone": 0.0, "floor": 0.0}
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
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"), "death": comp(boss, "RPGBossDeath")}


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


def mesh_of(boss):
    # the pack's mesh: the boss look's followers (RPGLook...) are skeletal mesh components too
    return next(c for c in boss.get_components_by_class(unreal.SkeletalMeshComponent) if not c.get_name().startswith("RPGLook"))


def placement(boss):
    mesh = mesh_of(boss)
    parent = mesh.get_attach_parent()
    return {"parent": parent.get_name() if parent else None, "loc": mesh.get_editor_property("relative_location")}


def pack_weapons(boss):
    return [c for c in boss.get_components_by_class(unreal.StaticMeshComponent) if "Weapon" in c.get_name() and not c.get_name().startswith("RPGLook")]


def pelvis(boss):
    """Height of the pelvis above the floor (the capsule's bottom, measured before the kill)."""
    return mesh_of(boss).get_socket_location("pelvis").z - S["floor"]


def take(q, t):
    boss, death = q["boss"], q["death"]
    mesh = mesh_of(boss)
    now = placement(boss)
    pre = S["pre"]
    d = now["loc"] - pre["loc"]
    s = {"t": t, "anim": q["dbg"].debug_boss_montage_anim_name(), "sim": bool(mesh.is_simulating_physics()), "pelvis": pelvis(boss), "state": None, "held": None, "counts": None,
         "same_parent": now["parent"] == pre["parent"], "drift": (d.x ** 2 + d.y ** 2 + d.z ** 2) ** 0.5, "weapons": len(pack_weapons(boss)), "weapons_visible": [w.get_name() for w in pack_weapons(boss) if not w.get_editor_property("hidden_in_game")]}
    if death is not None:
        s["state"] = death.get_death_state_name()
        s["held"] = death.is_pose_held()
        s["counts"] = {"deaths": death.get_death_count(), "plays": death.get_clip_play_count(), "restarts": death.get_clip_restart_count(), "holds": death.get_pose_hold_count(),
                       "physics_off": death.get_physics_off_count(), "pack_sets": death.get_pack_set_count(), "pack": death.get_last_pack_result()}
    return s


def script():
    yield from fresh()
    yield 0.5
    p = P()
    death = p["death"]
    check("D1 the death component is on the boss", death is not None)
    if death is None:
        return
    if MODE_FILE.startswith("own"):
        death.set_death_mode_for_test("own")
    elif MODE_FILE.startswith("pack"):
        death.set_death_mode_for_test("pack")
        death.set_guard_pack_death_for_test(MODE_FILE == "pack_guard")
    yield 1.2  # the first tick after the mode change loads what the mode needs (and, for the pack's mode, fills DeathMontages)
    p = P()
    death = p["death"]
    mode = death.get_death_mode_name()
    own = mode == "own_clip"
    check("D1 the state is 'alive' before the kill (mode %s)" % mode, death.get_death_state_name() == "alive", "pack: %s" % death.get_last_pack_result())
    try:
        half = p["boss"].get_components_by_class(unreal.CapsuleComponent)[0].get_scaled_capsule_half_height()
    except Exception:
        half = 90.0
    S["floor"] = p["boss"].get_actor_location().z - half
    S["pre"] = placement(p["boss"])
    stand = pelvis(p["boss"])
    log("mode %s, standing pelvis %.0f cm above the floor (floor z %.0f), montage before the kill '%s'" % (mode, stand, S["floor"], p["dbg"].debug_boss_montage_anim_name()))

    # the kill; from here on the boss may disappear at any time (the pack destroys it), the generator keeps running without it
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
        samples.append(take(q, S["now"] - t_kill))
        yield SAMPLE_STEP
    for s in samples:
        log("t=%.2f clip '%s' simulating %s pelvis %.0f state %s held %s" % (s["t"], s["anim"], s["sim"], s["pelvis"], s["state"], s["held"]))
    log("the boss %s" % ("is gone at t=%.2f (destroyed by the pack)" % gone_at if gone_at is not None else "still exists after %.1f s" % SAMPLE_SECONDS))
    if not samples:
        check("D2 the boss was sampled after the kill", False, "it was gone at once")
        return
    counts = next((s["counts"] for s in reversed(samples) if s["counts"]), {})
    log("counters %s" % counts)

    seen = [s["t"] for s in samples if s["state"] in ("dying", "dead")]
    deaths = max([s["counts"]["deaths"] for s in samples if s["counts"]] or [0])
    check("D2 the death is seen within 0.5 s (first at %s) and counted once (%s)" % ("%.2f" % seen[0] if seen else "never", deaths), bool(seen) and seen[0] <= 0.5 and deaths == 1)
    clip_t = [s["t"] for s in samples if s["anim"] == CLIP]
    # the clip must be there in three samples in a row from its first appearance (a clip that flickers does not count)
    first = next((i for i, s in enumerate(samples) if s["anim"] == CLIP), None)
    run3 = first is not None and len(samples) >= first + 3 and all(s["anim"] == CLIP for s in samples[first:first + 3])
    check("D3 the death clip plays (%s seen first at %s, three samples in a row %s)" % (CLIP, "%.2f" % clip_t[0] if clip_t else "never", run3), bool(clip_t) and clip_t[0] <= 1.5 and run3, "montages seen: %s" % sorted(set(s["anim"] for s in samples)))
    lived = gone_at if gone_at is not None else SAMPLE_SECONDS
    check("D4 the body lives until the collapse is over (%.1f s, needs 2.6 s)" % lived, lived >= 2.6)
    late = [s for s in samples if s["t"] >= 2.6]
    if late:
        end = late[-1]["pelvis"]
        check("D5 the pelvis ends low: %.0f cm above the floor (kneeling: below 90, the clip's kneel is 47.7 cm x the mesh scale 1.5 = 72 cm; standing %.0f, at least 40 cm lower)" % (end, stand), end < 90.0 and stand - end >= 40.0)
    else:
        log("D5 skipped: no sample after 2.6 s")
    early = [s for s in samples if s["t"] <= 3.0]
    lo, hi = min(s["pelvis"] for s in early), max(s["pelvis"] for s in early)
    check("D6 the pelvis stays between 55 cm above the floor and the clip's standing height (146) in the first 3 s (%.0f to %.0f, pack idle standing %.0f): no fall through the floor, no throw by the ragdoll" % (lo, hi, stand), lo >= 55.0 and hi <= 160.0)
    playing = [s for s in samples if s["anim"] == CLIP]
    if len(playing) >= 3:
        check("D7 the mesh does not simulate physics while the clip plays (%d samples, %d simulating)" % (len(playing), sum(1 for s in playing if s["sim"])), not any(s["sim"] for s in playing))
    else:
        check("D7 the clip played in at least 3 samples to judge the physics (%d)" % len(playing), False)
    held = [s for s in samples if s["t"] >= 3.2]
    if len(held) >= 3:
        span = max(s["pelvis"] for s in held) - min(s["pelvis"] for s in held)
        check("D8 the final pose stays: the pelvis moves %.1f cm from 3.2 s on (%d samples, the clip plays: %s)" % (span, len(held), all(s["anim"] == CLIP for s in held)), span < 3.0)
    else:
        log("D8 skipped: the boss was gone before 3.2 s (%d samples after it)" % len(held))
    if own:
        ok = counts.get("plays", 0) >= 1 and counts.get("restarts", 99) <= 1 and counts.get("physics_off", 0) >= 1 and (counts.get("holds", 0) >= 1 or lived < 3.1)
        check("D9 OwnClip: the clip was started (%s time(s), %s restart(s)) and the pose frozen (%s time(s)); the mesh was taken out of physics %s time(s)" % (counts.get("plays"), counts.get("restarts"), counts.get("holds"), counts.get("physics_off")), ok)
    else:
        check("D9 PackMontage: the pack's DeathMontages was filled (%s time(s): %s)" % (counts.get("pack_sets"), counts.get("pack")), counts.get("pack_sets", 0) >= 1)
    worst = max(s["drift"] for s in samples)
    with_weapon = [s for s in samples if s["weapons"] > 0]
    visible = sorted(set(w for s in with_weapon for w in s["weapons_visible"]))
    if own:
        check("D10 the mesh keeps its place on the capsule (same parent %s, largest drift %.2f cm) and the pack's sword stays hidden (%d samples with a weapon mesh, visible: %s)" % (all(s["same_parent"] for s in samples), worst, len(with_weapon), visible),
              all(s["same_parent"] for s in samples) and worst < 1.0 and len(with_weapon) >= 1 and not visible)
    else:
        log("D10 skipped in the pack's mode (the pack's ragdoll moves the mesh): drift %.1f cm, pack sword visible: %s" % (worst, visible))


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
            s.update(phase="run", t=0.0)
        return
    w, pc, pawn, boss = actors()
    if s["now"] - s.get("hb", 0.0) > 15.0:
        s["hb"] = s["now"]
        log("heartbeat: %.0f s, pawn %s, boss %s, wait %.2f" % (s["now"], pawn.get_name() if pawn else None, boss.get_name() if boss else None, s["wait"]))
    if s["now"] > 150.0 and s["gen"] is not None:
        check("the run finished in time", False, "stopped after 150 s")
        finish()
        return
    if boss is None and not s["killed"]:
        # before the kill a missing boss is a failed setup; after it the pack destroying the boss is the expected end and the scenario goes on without it
        s["gone"] += dt
        if s["gone"] > 15.0 and s["gen"] is not None:
            check("the boss exists (it was gone for 15 s before the kill)", False)
            finish()
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
        finish()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        check("tick raised", False)
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
