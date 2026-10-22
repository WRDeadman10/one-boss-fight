"""Probe (log prefix [StaminaTrace]): samples the player's stamina every frame around one swing, with and without a cost override, to see when the pack's own cost and the swing tracker's extra land.
Scenario list: (label, kind override or None, cost, action). Run after the warm-up. Not a regression driver."""
import math
import unreal

log = lambda m: unreal.log("[StaminaTrace] " + m)
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
KIND = unreal.RPGAttackKind
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "press_until": 0.0, "action": "IA_StrongAttack", "samples": None}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return c.call_method("Get Current Attribute Value", args=(t,))
    except Exception:
        return None


def attr_max(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return c.call_method("GetMaxAttributeValue", args=(t,))
    except Exception:
        return None


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
    return {"pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"), "swing": comp(pawn, "RPGSwingTracker")}


def place(p, dist=110.0):
    boss, pawn = p["boss"], p["pawn"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = unreal.MathLibrary.find_look_at_rotation(q, bl).yaw
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    p["pc"].set_control_rotation(unreal.Rotator(0, 0, look))


def script():
    p = P()
    p["enc"].reset_for_test()
    yield 0.8
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["tr"].enter_combat()
    comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
    yield 2.5
    for label, override, action in (("strong, no override", None, "IA_StrongAttack"), ("strong, 35 override", 35.0, "IA_StrongAttack"), ("light, 10 override", 10.0, "IA_NormalAttack")):
        p = P()
        p["swing"].clear_cost_overrides()
        if override is not None:
            p["swing"].set_cost_override_for_test(KIND.STRONG if "strong" in label else KIND.LIGHT, override)
        place(p)
        p["dbg"].debug_refill_player()
        yield 1.0
        S["samples"] = []
        S["action"] = action
        S["press_until"] = S["now"] + 0.12
        yield 1.6
        smp = S["samples"]
        S["samples"] = None
        log("== %s: swings %d, extra total %.1f, stamina max now %s" % (label, P()["swing"].get_attack_swing_count(), P()["swing"].get_stamina_extra_total(), attr_max(P()["pawn"], "Attribute.Stamina")))
        last = None
        for t, v, m in smp:
            if v != last:
                log("   t=%.3f stamina %.2f montage %s" % (t - smp[0][0], v if v is not None else -1, m))
                last = v
        yield 2.0


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("done")
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
    if pawn is None or boss is None:
        return
    if s["now"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA + s["action"]), unreal.Vector(1, 0, 0))
    if s["samples"] is not None:
        mesh = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0]
        inst = mesh.get_anim_instance()
        m = inst.get_current_active_montage() if inst else None
        s["samples"].append((s["now"], attr(pawn, "Attribute.Stamina"), m.get_name() if m else None))
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
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
