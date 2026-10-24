"""
PIE edge cases of the boss stance break (URPGBossStagger). MODE "boss_dies": during the stance break the boss is put at 3 percent of its runtime maximum health and hit with a light attack (a critical,
x2.5, kills it); logs what the component and the boss do afterwards. MODE "player_dies": one second into the stance break the player's health is set to 0 (the pack's
death task respawns the player); logs the respawn, the stagger state and what the boss does for 12 s afterwards. Log prefix [EdgePie]. Open L_SevarogArena first; run
with Scripts/run_in_editor.py (editor throttling off). MODE "boss_resets": one second into the stance break the boss health is set back to its maximum (what the pack does on a player respawn); the stance break must end at once and the boss must get up. Set MODE below.
"""
import unreal

MODE = "boss_resets"
LETHAL_HEALTH_FRACTION = 0.03
log = lambda m: unreal.log("[EdgePie] " + m)
ACTIONS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
state = {"phase": "start", "t": 0.0, "press": None, "press_until": -1.0, "next_press": 0.0, "stage": "break", "last_m": None, "t_event": None, "heal_t": 0.0, "pawn_id": None,
         "act_done": False, "last_stag": None}
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


def has_tag(actor, tag):
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag)
    try:
        return actor.call_method("HasMatchingGameplayTag", args=(t,))
    except Exception:
        return None


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
    if s["t"] > 170.0:
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
    if boss is None:
        if s["stage"] in ("after", "window"):
            log("boss actor is gone (destroyed)")
            finish("boss destroyed")
        return
    stag = comp(boss, "RPGBossStagger")
    if pawn is None:
        if s["pawn_id"] is not None:
            log("   (no pawn this tick)")
        return
    if s["pawn_id"] is None:
        s["pawn_id"] = pawn.get_name()
    elif pawn.get_name() != s["pawn_id"]:
        log("== player respawned as %s (was %s), %.2f s after the event; boss: staggered=%s hp %.0f poise %s montage %s" % (pawn.get_name(), s["pawn_id"], s["t"] - s["t_event"], stag.is_staggered(), attr(boss, "Attribute.Health"), attr(boss, "Attribute.Poise"), montage_of(boss)))
        s["pawn_id"] = pawn.get_name()
        s["respawned"] = s["t"]
    stagg = stag.is_staggered()
    if stagg != s["last_stag"]:
        s["last_stag"] = stagg
        log("   component staggered -> %s (boss hp %.0f, poise %s)" % (stagg, attr(boss, "Attribute.Health"), attr(boss, "Attribute.Poise")))
    m = montage_of(boss)
    if m != s["last_m"]:
        s["last_m"] = m
        log("   boss montage -> %s (hp %.0f, at %.0f,%.0f, Dead tag %s, immune tag %s)" % (m, attr(boss, "Attribute.Health"), boss.get_actor_location().x, boss.get_actor_location().y, has_tag(boss, "Status.Dead"), has_tag(boss, "Status.HitStunImmune")))
    s["heal_t"] += dt
    if s["heal_t"] > 0.4 and not (MODE == "player_dies" and s["stage"] != "break"):
        s["heal_t"] = 0.0
        set_attr(pawn, "Attribute.Health", 100.0)
    d = boss.get_actor_location() - pawn.get_actor_location()
    flat = unreal.Vector(d.x, d.y, 0)
    if s["phase"] == "wait":
        if s["t"] > 8.0:
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            s.update(phase="fight", t=0.0, next_press=1.0)
        return
    if flat.length() > 190.0 and not stagg:
        pawn.add_movement_input(flat.normal(), 1.0, False)
    if flat.length() <= 260.0:
        pawn.set_actor_rotation(unreal.Rotator(0, 0, unreal.MathLibrary.make_rot_from_x(flat).yaw), False)

    if s["stage"] == "break" and stagg:
        s.update(stage="window", t_event=s["t"], next_press=s["t"] + 0.8)
        log("== stance break started")
    if s["stage"] == "window" and MODE == "player_dies" and s["t"] - s["t_event"] > 1.0 and not s["act_done"]:
        s["act_done"] = True
        s["t_event"] = s["t"]
        log("== killing the player now (health %s)" % attr(pawn, "Attribute.Health"))
        set_attr(pawn, "Attribute.Health", 0.0)
        s["stage"] = "after"
    if s["stage"] == "window" and MODE == "boss_resets" and s["t"] - s["t_event"] > 1.0 and not s["act_done"]:
        s["act_done"] = True
        s["t_event"] = s["t"]
        maximum = max_attr(boss, "Attribute.Health")
        log("== resetting the boss health to its maximum now (it is down): %s" % maximum)
        if maximum is not None:
            set_attr(boss, "Attribute.Health", maximum)
        s["stage"] = "after"
    if s["stage"] == "window" and MODE == "boss_dies" and not s["act_done"] and s["t"] >= s["next_press"] and not s["press"]:
        s["act_done"] = True
        maximum = max_attr(boss, "Attribute.Health")
        if maximum is not None:
            set_attr(boss, "Attribute.Health", maximum * LETHAL_HEALTH_FRACTION)
        s["press"], s["press_until"] = "IA_NormalAttack", s["t"] + 0.2
        s["t_event"] = s["t"]
        s["stage"] = "after"
        log("== boss set to 3 percent of maximum health (%s), striking it while it is down" % maximum)
    if s["stage"] == "break" and not s["press"] and s["t"] >= s["next_press"] and flat.length() <= 260.0:
        s["press"], s["press_until"], s["next_press"] = "IA_StrongAttack", s["t"] + 0.2, s["t"] + 1.3
        log("press heavy")
    if s["press"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(ACTIONS + s["press"]), unreal.Vector(1, 0, 0))
        if s["t"] >= s["press_until"]:
            s["press"] = None
    if s["stage"] == "after" and s["t"] - s["t_event"] > (8.0 if MODE in ("boss_dies", "boss_resets") else 14.0):
        log("final: boss hp %.0f, staggered %s, stagger count %d, crit hits %d, Dead tag %s, immune tag %s, poise %s" % (attr(boss, "Attribute.Health"), stag.is_staggered(), stag.get_stagger_count(), stag.get_critical_hit_count(), has_tag(boss, "Status.Dead"), has_tag(boss, "Status.HitStunImmune"), attr(boss, "Attribute.Poise")))
        finish("done")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
