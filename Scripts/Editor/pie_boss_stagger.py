"""
PIE check of the boss stance break (URPGBossStagger): the player (kept alive) hits the pack boss with real heavy presses until its poise breaks, then lands a light and
a heavy hit while it is down (critical window), then waits for the get-up and the boss to attack again. Logs the boss's montage, position, health, poise, the
component's state and, for every hit, the health lost. Log prefix [StaggerPie]. Open L_SevarogArena first; run with Scripts/run_in_editor.py (editor throttling off).
"""
import unreal

log = lambda m: unreal.log("[StaggerPie] " + m)
ACTIONS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
state = {"phase": "start", "t": 0.0, "press": None, "press_until": -1.0, "next_press": 0.0, "last_hp": None, "last_m": None, "stage": "break", "window_presses": 0,
         "t_break": None, "t_down_end": None, "attacks_after": 0, "heal_t": 0.0}
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


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


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


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 150.0:
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
    boss = next(iter([a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"]), None) if w else None
    if pawn is None or boss is None:
        return
    stag = comp(boss, "RPGBossStagger")
    if stag is None:
        finish("boss has no RPGBossStagger component")
        return
    s["heal_t"] += dt
    if s["heal_t"] > 0.4:
        s["heal_t"] = 0.0
        t = unreal.GameplayTag()
        t.import_text('(TagName="Attribute.Health")')
        comp(pawn, "BP_AttributesComponent_C").call_method("Set Current Attribute Value", args=(t, 100.0))
    hp = attr(boss, "Attribute.Health")
    if s["last_hp"] is not None and hp < s["last_hp"] - 0.01:
        log("   boss hp %.0f -> %.0f (lost %.0f) stage=%s staggered=%s critical window=%s" % (s["last_hp"], hp, s["last_hp"] - hp, s["stage"], stag.is_staggered(), stag.is_critical_window_open()))
    s["last_hp"] = hp
    m = montage_of(boss)
    if m != s["last_m"]:
        s["last_m"] = m
        log("   boss montage -> %s (poise %s, hp %.0f, at %.0f,%.0f, staggered %s)" % (m, attr(boss, "Attribute.Poise"), hp, boss.get_actor_location().x, boss.get_actor_location().y, stag.is_staggered()))
        if s["stage"] == "after" and m and m.startswith("GS_"):
            s["attacks_after"] += 1
    d = boss.get_actor_location() - pawn.get_actor_location()
    flat = unreal.Vector(d.x, d.y, 0)
    if s["phase"] == "wait":
        if s["t"] > 8.0:
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            s.update(phase="fight", t=0.0, next_press=1.0)
        return
    if flat.length() > 190.0 and not stag.is_staggered():
        pawn.add_movement_input(flat.normal(), 1.0, False)
    if flat.length() <= 260.0:
        pawn.set_actor_rotation(unreal.Rotator(0, 0, unreal.MathLibrary.make_rot_from_x(flat).yaw), False)

    staggered = stag.is_staggered()
    if s["stage"] == "break" and staggered:
        s.update(stage="window", t_break=s["t"], next_press=s["t"] + 0.5, window_presses=0)
        log("== stance break started (stagger count %d)" % stag.get_stagger_count())
    if s["stage"] == "after" and staggered and not s.get("second_logged"):
        s["second_logged"] = True
        log("== second stance break started %.2f s after the first ended (stagger count %d)" % (s["t"] - s["t_down_end"], stag.get_stagger_count()))
    if s["stage"] == "window" and not staggered:
        s["stage"] = "after"
        s["t_down_end"] = s["t"]
        log("== stance break over after %.2f s (critical hits %d), poise now %s" % (s["t"] - s["t_break"], stag.get_critical_hit_count(), attr(boss, "Attribute.Poise")))
    if s["stage"] == "after" and not s.get("healed"):
        s["healed"] = True
        t = unreal.GameplayTag()
        t.import_text('(TagName="Attribute.Health")')
        comp(boss, "BP_AttributesComponent_C").call_method("Set Current Attribute Value", args=(t, 500.0))  # so the cooldown check is not cut short by a death
        s["last_hp"] = 500.0
    if s["stage"] == "after" and s["t"] - s["t_down_end"] > 16.0:
        finish("done: boss attacks after the stance break: %d, stance breaks in total: %d (the cooldown is 5 s)" % (s["attacks_after"], stag.get_stagger_count()))
        return

    # presses
    if s["press"] is None and s["t"] >= s["next_press"] and flat.length() <= 260.0:
        if s["stage"] in ("break", "after"):
            s["press"], s["next_press"] = "IA_StrongAttack", s["t"] + 1.3
        elif s["stage"] == "window" and s["window_presses"] < 2:
            s["press"] = "IA_NormalAttack" if s["window_presses"] == 0 else "IA_StrongAttack"
            s["window_presses"] += 1
            s["next_press"] = s["t"] + 0.9
        if s["press"]:
            s["press_until"] = s["t"] + 0.2
            log("press %s (stage %s)" % (s["press"], s["stage"]))
    if s["press"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(ACTIONS + s["press"]), unreal.Vector(1, 0, 0))
        if s["t"] >= s["press_until"]:
            s["press"] = None


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
