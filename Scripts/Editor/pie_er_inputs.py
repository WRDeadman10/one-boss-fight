"""
PIE proof of the Elden Ring gamepad inputs (owner 2026-11-06, "All three"; lead, Claude). Real key presses through the whole input mapping
(URPGInputTestUtils.set_key_down), no action injection:
  E1 the Elden Ring context is active on the player (URPGDodgeTiming.is_elden_ring_input_active)
  E2 R1 starts the light attack on PRESS (a light montage plays while the key is still held)
  E3 an R2 tap plays the strong attack
  E4 an R2 hold plays the charged attack
  E5 a standing double tap of the dodge key gives no long roll (bDoubleTapLongRoll off): the long-roll montage never plays and no press is "full"
Map: L_SevarogArena (default data route). The boss is held (hold_for_test) and the player stands 9 m away, so nothing interrupts the swings.
Montage names are logged for every case; checks match by substring (light "Primary", strong "Ability_E", charged "Charged", long roll "Dodge_To_Idle").
Log prefix [ERInputs]. Writes no asset; sets no component property in PIE (KI-083).
"""
import unreal

log = lambda m: unreal.log("[ERInputs] " + m)
state = {"phase": "start", "t": 0.0, "res": [], "case": 0, "ct": 0.0, "seen": [], "key_down": False}
handle = None

# (name, key, hold seconds, expected substring, forbidden substring)
# E4 runs first: its charged attack also draws the sword (the pack's EnterCombat tag did not draw it in run pie1), so E2/E3 swing a drawn weapon.
CASES = [
    ("W0 warm-up R2 hold (not counted: draws the sword)", "Gamepad_RightTrigger", 0.70, "", None),
    ("E4 R2 hold plays the charged attack", "Gamepad_RightTrigger", 0.70, "Charged", None),
    ("E2 R1 press starts the light attack while held", "Gamepad_RightShoulder", 0.30, "Primary", None),
    ("E3 R2 tap plays the strong attack", "Gamepad_RightTrigger", 0.12, "Ability_E", "Charged"),
]
CASE_LENGTH = 3.0


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def montage(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def check(name, ok, detail=""):
    state["res"].append((name, ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    bad = [n for n, ok in state["res"] if not ok]
    log("SUMMARY %d checks, %d failed %s" % (len(state["res"]), len(bad), bad))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wake", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None:
        if s["t"] > 60.0:
            check("E0 PIE world has the player and the boss", False)
            finish()
        return
    dodge = comp(pawn, "RPGDodgeTiming")
    dbg = comp(boss, "RPGCombatDebug")
    enc = comp(boss, "RPGBossEncounter")
    if s["phase"] == "wake":
        if s["t"] > 6.0 and "held" not in s:
            if enc:
                enc.hold_for_test(True)
            bl = boss.get_actor_location()
            pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + 900, bl.y, bl.z), unreal.Rotator(0, 0, 180), False, True)
            pc.set_control_rotation(unreal.Rotator(0, 0, 180))
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            s["held"] = s["t"]
        if "held" in s and s["t"] - s["held"] > 12.0:
            check("E1 Elden Ring input context active on the player", bool(dodge and dodge.is_elden_ring_input_active()))
            s.update(phase="case", case=0, ct=0.0, seen=[])
        return
    if dbg:
        dbg.debug_refill_player()
    if s["phase"] == "case":
        name, key, hold, want, forbid = CASES[s["case"]]
        s["ct"] += dt
        if s["ct"] <= dt + 1e-6 and not s["key_down"]:
            unreal.RPGInputTestUtils.set_key_down(pc, key, True)
            s["key_down"] = True
            s["held_seen"] = []
        m = montage(pawn)
        if m and (not s["seen"] or s["seen"][-1] != m):
            s["seen"].append(m)
        if s["key_down"] and m:
            s["held_seen"].append(m)
        if s["key_down"] and s["ct"] >= hold:
            unreal.RPGInputTestUtils.set_key_down(pc, key, False)
            s["key_down"] = False
        if s["ct"] >= CASE_LENGTH:
            seen = s["seen"]
            ok = any(want in x for x in seen) and not (forbid and any(forbid in x for x in seen))
            if name.startswith("E2"):
                ok = ok and any(want in x for x in s["held_seen"])  # started before the release
            if name.startswith("W0"):
                log("warm-up montages=%s" % seen)
            else:
                check(name, ok, "montages=%s while_held=%s" % (seen, sorted(set(s["held_seen"]))))
            s["case"] += 1
            s.update(ct=0.0, seen=[])
            if s["case"] >= len(CASES):
                s.update(phase="dodge", ct=0.0, seen=[], presses=0)
        return
    if s["phase"] == "dodge":
        s["ct"] += dt
        m = montage(pawn)
        if m and (not s["seen"] or s["seen"][-1] != m):
            s["seen"].append(m)
        # two taps 0.15 s apart while standing: down at 0.0 and 0.15, up at 0.07 and 0.22
        for at, down in ((0.0, True), (0.07, False), (0.15, True), (0.22, False)):
            key = "k%.2f" % at
            if s["ct"] >= at and key not in s:
                s[key] = True
                unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Right", down)
        if s["ct"] >= 3.0:
            full = dodge.was_last_press_full() if dodge else None
            check("E5 standing double tap gives no long roll", (full is False) and not any("Dodge_To_Idle" in x for x in s["seen"]),
                  "last_press_full=%s presses=%s montages=%s" % (full, dodge.get_press_count() if dodge else None, s["seen"]))
            finish()
            s["phase"] = "done"


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
