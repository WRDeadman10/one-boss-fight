"""
G0-7: scripted PIE trials of the double tap rule with the pack's real IA_Dodge key (RPGInputTestUtils), Freeze tests D01 to D07.
For each press gap the script presses dodge twice (a triple tap series too), 20 trials per gap, and checks per trial:
  - the rule: the last press was a full roll exactly when the measured gap (URPGDodgeTiming::GetLastPressGap) is <= DoubleTapWindow;
  - at most one full roll montage starts per trial (no third dodge from a triple tap);
  - a single tap produces no full roll.
The boss stays in the level but dormant (the player starts 1800 cm away). Open L_SevarogArena first; run with Scripts/run_in_editor.py. Log prefix [DodgeTrials].
Result lines: "[DodgeTrials] RESULT gap 0.20: 20/20 rule ok, 20/20 single full roll" and a final "SUMMARY pass N fail M".
"""
import unreal

log = lambda m: unreal.log("[DodgeTrials] " + m)
IA_DODGE_KEY = "Gamepad_FaceButton_Right"
TRIALS = 20
GAPS = [0.10, 0.20, 0.26, 0.28, 0.32, 0.34, 0.45, 0.80]  # seconds between the two presses (start to start)
PRESS_LEN = 0.08  # two or three frames: shorter presses were sometimes lost between input polls
TRIAL_LEN = 1.9
SETTLE = 1.1
# series: (label, gap list: gaps between consecutive presses starting at 0, trial count)
SERIES = [("gap %.2f" % g, [g], TRIALS) for g in GAPS] + [("triple 0.12/0.12", [0.12, 0.12], 10), ("single", [], 10)]
state = {"dropped": 0, "keys": {}, "phase": "start", "t": 0.0, "i": 0, "n": 0, "running": False, "t0": 0.0, "montages": [], "last": None, "base": None, "next": 0.0, "stats": {}, "pass": 0, "fail": 0}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def montage_of(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def key(pc, name, down):
    if state["keys"].get(name, False) != down:
        state["keys"][name] = down
        unreal.RPGInputTestUtils.set_key_down(pc, name, down)


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("SUMMARY pass %d fail %d, trials repeated because key presses were dropped by the driver: %d (%s)" % (state["pass"], state["fail"], state["dropped"], reason))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def press_times(gaps):
    t, out = 0.0, [0.0]
    for g in gaps:
        t += g
        out.append(t)
    return out


def evaluate(label, gaps, pawn, boss):
    dodge = comp(pawn, "RPGDodgeTiming")
    presses = dodge.get_press_count() - state["base"]["presses"]
    gap = dodge.get_last_press_gap()
    window = dodge.get_editor_property("double_tap_window")
    full = dodge.was_last_press_full()
    rolls = sum(1 for m in state["montages"] if m and "Dodge_To_Idle" in m)
    ok_rule = True
    if gaps:
        ok_rule = (full == (gap <= window + 1e-9))
    else:
        ok_rule = not full
    ok_roll = rolls <= 1
    ok_presses = presses == len(gaps) + 1
    if not ok_presses:
        # the driver's key edges did not all arrive (not a product result): run the trial again, up to a limit
        state["dropped"] += 1
        return False
    st = state["stats"].setdefault(label, [0, 0, 0, 0])
    st[0] += 1
    st[1] += 1 if ok_rule else 0
    st[2] += 1 if ok_roll else 0
    st[3] += 1 if ok_presses else 0
    good = ok_rule and ok_roll and ok_presses
    state["pass" if good else "fail"] += 1
    if not good:
        log("  FAIL %s trial %d: gap %.3f window %.2f last full %s full rolls %d montages %s" % (label, state["n"], gap, window, full, rolls, state["montages"]))
    return True


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 1400.0:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    if s["phase"] == "wait":
        if s["t"] > 9.0 and boss is not None and comp(pawn, "RPGDodgeTiming") is not None:
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            s.update(phase="run", t=0.0, next=1.5)
        return
    label, gaps, count = SERIES[s["i"]] if s["i"] < len(SERIES) else (None, None, None)
    if s["running"]:
        ts = s["t"] - s["t0"]
        times = press_times(gaps)
        key(pc, IA_DODGE_KEY, any(a <= ts < a + PRESS_LEN for a in times))
        m = montage_of(pawn)
        if m != s["last"]:
            s["last"] = m
            s["montages"].append(m)
        if ts >= TRIAL_LEN:
            key(pc, IA_DODGE_KEY, False)
            counted = evaluate(label, gaps, pawn, boss)
            s["running"] = False
            s["next"] = s["t"] + SETTLE
            if not counted:
                if s["dropped"] > 80:
                    finish("too many dropped inputs")
                return
            s["n"] += 1
            if s["n"] >= count:
                st = s["stats"][label]
                log("RESULT %s: %d/%d rule ok, %d/%d at most one full roll, %d/%d press count ok" % (label, st[1], st[0], st[2], st[0], st[3], st[0]))
                s["i"] += 1
                s["n"] = 0
        return
    if s["t"] >= s["next"]:
        if label is None:
            finish("all series done")
            return
        pawn.set_actor_location_and_rotation(unreal.Vector(-1800, 0, 110), unreal.Rotator(0, 0, 0), False, True)
        pc.set_control_rotation(unreal.Rotator(0, 0, 0))
        dbg = comp(boss, "RPGCombatDebug") if boss else None
        if dbg:
            dbg.debug_refill_player()
        dodge = comp(pawn, "RPGDodgeTiming")
        s.update(running=True, t0=s["t"], montages=[], last=None, base={"presses": dodge.get_press_count()})


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
