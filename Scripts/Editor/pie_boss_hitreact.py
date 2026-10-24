"""
PIE probe of the boss's hit reaction: the player walks up and lands real light attacks (IA_NormalAttack) and then heavy attacks (IA_StrongAttack) on the pack's
great-sword boss. After every hit it logs the boss's hit stun ability state: its "Hit Data" variable (set by the damage cue just before it tries to activate the
ability, so non-empty means the activation was attempted), whether the ability is active, the result of its own "Can Activate Ability?", boss poise, health and
montage. Log prefix [HitReact]. Open L_SevarogArena first; run with Scripts/run_in_editor.py (editor throttling off).
"""
import unreal

log = lambda m: unreal.log("[HitReact] " + m)
ACTIONS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
# (label, input action, seconds to wait after this press): heavies to break the poise, light and heavy presses inside the stagger window, then a pause for the get-up
PLAN = [("heavy", "IA_StrongAttack", 1.4), ("heavy", "IA_StrongAttack", 1.4), ("heavy", "IA_StrongAttack", 1.0), ("light", "IA_NormalAttack", 0.7), ("light", "IA_NormalAttack", 0.7),
        ("heavy", "IA_StrongAttack", 0.7), ("light", "IA_NormalAttack", 6.0), ("light", "IA_NormalAttack", 2.0), ("heavy", "IA_StrongAttack", 2.0)]
state = {"phase": "start", "t": 0.0, "step": 0, "press_until": -1.0, "wait_until": 0.0, "last_hp": None, "label": "-", "heal_t": 0.0}
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


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def montage_of(actor):
    mc = actor.get_components_by_class(unreal.SkeletalMeshComponent)
    inst = mc[0].get_anim_instance() if mc else None
    m = inst.get_current_active_montage() if inst else None
    return m.get_name() if m else None


def hit_stun(boss):
    asc = comp(boss, "BP_AdvancedAbilitySystemComponent_C")
    for a in asc.get_editor_property("CreatedAbilities"):
        if a is not None and a.get_class().get_name() == "GA_GS_Boss_HitStun_C":
            return a
    return None


def probe(boss, label):
    hs = hit_stun(boss)
    hd = None
    can = None
    active = None
    try:
        hd = hs.get_editor_property("Hit Data")
    except Exception as e:
        hd = "ERR " + str(e)[:50]
    try:
        can = hs.call_method("Can Activate Ability?")
    except Exception as e:
        can = "ERR " + str(e)[:80]
    try:
        active = hs.call_method("IsAbilityActive?")
    except Exception as e:
        active = "ERR"
    log("%s: hitstun HitData=%s CanActivate=%s active=%s | poise %s hp %s boss montage %s" % (label, hd.get_name() if hasattr(hd, "get_name") else hd, can, active,
        attr(boss, "Attribute.Poise"), attr(boss, "Attribute.Health"), montage_of(boss)))


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
    if s["t"] > 160.0:
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
    s["heal_t"] += dt
    if s["heal_t"] > 0.4:
        s["heal_t"] = 0.0
        t = unreal.GameplayTag()
        t.import_text('(TagName="Attribute.Health")')
        comp(pawn, "BP_AttributesComponent_C").call_method("Set Current Attribute Value", args=(t, 100.0))
        # keep the boss alive for the whole probe
        maximum = max_attr(boss, "Attribute.Health")
        comp(boss, "BP_AttributesComponent_C").call_method("Set Current Attribute Value", args=(t, maximum)) if maximum is not None and (attr(boss, "Attribute.Health") or 0) < maximum * 0.3 else None
    hs_now = hit_stun(boss)
    try:
        act_now = hs_now.call_method("IsAbilityActive?")
    except Exception:
        act_now = None
    if act_now != s.get("last_act"):
        s["last_act"] = act_now
        log("   boss hit stun ability active -> %s (poise %s)" % (act_now, attr(boss, "Attribute.Poise")))
    bm = montage_of(boss)
    if bm != s.get("last_bm"):
        s["last_bm"] = bm
        log("   boss montage -> %s (poise %s, hp %.0f, at %.0f,%.0f)" % (bm, attr(boss, "Attribute.Poise"), attr(boss, "Attribute.Health"), boss.get_actor_location().x, boss.get_actor_location().y))
    hp = attr(boss, "Attribute.Health")
    if s["last_hp"] is not None and hp < s["last_hp"]:
        probe(boss, "HIT (%s step, hp %.0f -> %.0f)" % (s["label"], s["last_hp"], hp))
    s["last_hp"] = hp
    d = boss.get_actor_location() - pawn.get_actor_location()
    flat = unreal.Vector(d.x, d.y, 0)
    if s["phase"] == "wait":
        if s["t"] > 8.0:
            comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            probe(boss, "before any hit")
            for tag in ("Status.HitStunImmune", "Status.Invulnerable", "Status.ActionCommitted", "Status.CancelFramesActive", "Character.State.Attacking", "Status.Dead"):
                t = unreal.GameplayTag()
                t.import_text('(TagName="%s")' % tag)
                try:
                    log("   boss has %s: %s" % (tag, boss.call_method("HasMatchingGameplayTag", args=(t,))))
                except Exception as e:
                    log("   boss has %s: ERR %s" % (tag, str(e)[:90]))
            s.update(phase="fight", t=0.0, wait_until=1.0)
        return
    if flat.length() > 200.0:
        pawn.add_movement_input(flat.normal(), 1.0, False)
    elif s["t"] > s["wait_until"] and s["press_until"] < s["t"] and s["step"] < len(PLAN):
        pawn.set_actor_rotation(unreal.Rotator(0, 0, unreal.MathLibrary.make_rot_from_x(flat).yaw), False)
        s["label"], _, delay = PLAN[s["step"]]
        s["press_until"] = s["t"] + 0.2
        s["wait_until"] = s["t"] + delay
        s["step"] += 1
        log("press %s" % s["label"])
    if s["t"] < s["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(ACTIONS + PLAN[s["step"] - 1][1]), unreal.Vector(1, 0, 0))
    if s["step"] >= len(PLAN) and s["t"] > s["wait_until"] + 1.0:
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
