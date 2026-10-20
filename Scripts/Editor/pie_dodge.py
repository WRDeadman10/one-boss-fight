"""
PIE measurement of the dodge input with the pack's real IA_Dodge pressed through URPGInputTestUtils: a tap, a hold (while pushing forward), and a double tap.
For each scenario it logs every montage change of the player with the time since the first press, plus travel distance and peak speed. The boss is destroyed
in the PIE world first so nothing interrupts. Open L_SevarogArena first; run with Scripts/run_in_editor.py. Log prefix [DodgePie].
"""
import unreal

log = lambda m: unreal.log("[DodgePie] " + m)
DODGE = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Dodge"
# scenario name -> list of (press start, press end) in seconds from the scenario start; move = push forward the whole time
# (name, [(press start, press end)], moving, [attack input times])
# moving: False (no stick), True (stick forward) or an (x, y) stick vector (x right, y forward); the control rotation (camera) faces +X, yaw 0
SCENARIOS = [
    ("warm-up tap", [(0.0, 0.08)], False, []),
    ("tap, no stick (expect backward: heading 180)", [(0.0, 0.08)], False, []),
    ("tap, stick forward (expect heading 0)", [(0.0, 0.08)], True, []),
    ("tap, stick left (expect heading -90)", [(0.0, 0.08)], (-1.0, 0.0), []),
    ("tap, stick right (expect heading 90)", [(0.0, 0.08)], (1.0, 0.0), []),
    ("fast double tap, no stick (backward quick then backward roll)", [(0.0, 0.07), (0.14, 0.21)], False, []),
    ("fast double tap, stick forward", [(0.0, 0.07), (0.14, 0.21)], True, []),
    ("hold 1.2 s, stick forward (sprint)", [(0.0, 1.2)], True, []),
]
DODGE_KEY = "Gamepad_FaceButton_Right"  # "SpaceBar" for the keyboard
STICK = True  # moving scenarios push the left stick (IA_Move) instead of W
KEEP_BOSS = False
SCENARIO_LENGTH = 3.2
SETTLE = 3.0  # seconds of rest between scenarios (sprint and dodge states settle)
state = {"keys": {}, "phase": "start", "t": 0.0, "running": None, "next_i": 0, "next_start": 0.0, "t0": 0.0, "last_montage": None, "start_loc": None, "peak": 0.0}
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
    """Sends a key edge only when its state changes."""
    if state["keys"].get(name, False) != down:
        state["keys"][name] = down
        ok = unreal.RPGInputTestUtils.set_key_down(pc, name, down)
        log("   key %s %s -> %s" % (name, "down" if down else "up", ok))


def attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return c.call_method("Get Current Attribute Value", args=(t,)) if c else None
    except Exception:
        return None


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 150.0:  # checked first: later branches return early
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
    move = pawn.get_components_by_class(unreal.CharacterMovementComponent)[0]
    if s["phase"] == "wait":
        if not s.get("boss_removed") and not KEEP_BOSS:
            s["boss_removed"] = True
            for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character):
                if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C":
                    a.destroy_actor()
        if s["t"] > 9.0:
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            s.update(phase="run", t=0.0, next_start=1.5)
        return
    # a scenario runs for SCENARIO_LENGTH seconds after its first press
    if s["running"] is not None:
        name, presses, moving, attacks = SCENARIOS[s["running"]]
        ts = s["t"] - s["t0"]
        if STICK:
            if moving:
                vec = moving if isinstance(moving, tuple) else (0.0, 1.0)
                unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Move"), unreal.Vector(vec[0], vec[1], 0))
        else:
            key(pc, "W", moving)
        key(pc, DODGE_KEY, any(a <= ts < b for a, b in presses))  # a real key press: Dodge, Sprint (hold) and Jump all see it
        if any(a <= ts < a + 0.12 for a in attacks):
            unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack"), unreal.Vector(1, 0, 0))
        m = montage_of(pawn)
        speed = move.velocity.length()
        s["peak"] = max(s["peak"], speed)
        s["frames"] = s.get("frames", 0) + 1
        s["sum_dt"] = s.get("sum_dt", 0.0) + dt
        if m is not None and int(ts * 20) != s.get("trace_t", -1):
            s["trace_t"] = int(ts * 20)
            log("     trace t=%.2f dist from start %.0f speed %.0f yaw %.0f montage %s" % (ts, (pawn.get_actor_location() - s["start_loc"]).length(), speed, pawn.get_actor_rotation().yaw, m))
        if m != s["last_montage"]:
            s["last_montage"] = m
            log("  [%s] t=%.2f montage -> %s (speed %.0f, falling %s)" % (name, ts, m, speed, move.is_falling()))
        if ts >= SCENARIO_LENGTH:
            key(pc, "W", False)
            key(pc, DODGE_KEY, False)
            moved = (pawn.get_actor_location() - s["start_loc"]).length()
            log("[%s] stamina now %s" % (name, attr(pawn, "Attribute.Stamina")))
            d = pawn.get_actor_location() - s["start_loc"]
            import math
            log("[%s] heading %.0f deg (camera yaw 0), final yaw %.0f" % (name, math.degrees(math.atan2(d.y, d.x)) if d.length() > 30 else float("nan"), pawn.get_actor_rotation().yaw))
            log("[%s] done: moved %.0f cm, peak speed %.0f, avg frame %.0f ms" % (name, moved, s["peak"], 1000.0 * s.get("sum_dt", 0.0) / max(1, s.get("frames", 1))))
            s["frames"] = 0
            s["sum_dt"] = 0.0
            s["running"] = None
            s["next_start"] = s["t"] + SETTLE
        return
    if s["t"] >= s["next_start"]:
        if s["next_i"] >= len(SCENARIOS):
            finish("all scenarios done")
            return
        # back to the player start, facing the arena centre (the previous scenario may have run into the wall)
        pawn.set_actor_location_and_rotation(unreal.Vector(-1800, 0, 110), unreal.Rotator(0, 0, 0), False, True)
        pc.set_control_rotation(unreal.Rotator(0, 0, 0))
        s.update(running=s["next_i"], t0=s["t"], last_montage=None, start_loc=pawn.get_actor_location(), peak=0.0)
        log("== scenario: %s (avg frame %.0f ms) stamina %s health %s" % (SCENARIOS[s["next_i"]][0], 1000.0 * dt, attr(pawn, "Attribute.Stamina"), attr(pawn, "Attribute.Health")))
        s["next_i"] += 1


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
