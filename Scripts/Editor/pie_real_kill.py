"""
Gate 2 death priority (Freeze 18.2, L08): the boss is killed by a REAL player hit while its stand-in A2 attack is running (windup, hit due at 2.0 s). Checks: the boss dies, the attack instance ends in the tracker,
the player takes no damage from the cancelled attack in the following 3 s, nothing restarts. One trial per PIE run (the boss does not come back); the hit time comes from Saved/a2_kill_time.txt (seconds
after the attack start at which the player presses Light Attack, default 0.3). Log prefix [Kill].
"""
import os
import unreal

log = lambda m: unreal.log("[Kill] " + m)
IA_NORMAL = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack"
_kf = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "a2_kill_time.txt")
PRESS_AT = float(open(_kf).read().strip()) if os.path.exists(_kf) else 0.3
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0, "c": {}}
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


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("done")


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
        return
    enc, dbg, tr = comp(boss, "RPGBossEncounter"), comp(boss, "RPGCombatDebug"), comp(boss, "RPGAttackTracker")
    mc = boss.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    c = s["c"]
    bl = boss.get_actor_location()
    if s["phase"] == "wake":
        if s["t"] > 9.0 and "woke" not in s:
            s["woke"] = s["t"]
            pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + 700, bl.y, bl.z), unreal.Rotator(0, 180, 0), False, True)
        if "woke" in s:
            dbg.debug_refill_player()
            if (not enc.is_dormant()) and mc.get_anim_instance().get_current_active_montage() is None and s["t"] - s["woke"] > 4.0:
                enc.hold_for_test(True)
                comp(pawn, "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
                s.update(phase="run", t=0.0, wait=2.5)
                log("boss held, attack press at %.2f s after the start" % PRESS_AT)
        return
    if "press_until" in c:
        if s["t"] < c["press_until"]:
            unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(IA_NORMAL), unreal.Vector(1, 0, 0))
        else:
            del c["press_until"]
    if s["t"] < s["wait"]:
        return
    n = s["step"]
    if n == 0:
        dbg.debug_set_boss_health_fraction(0.05)
        dbg.debug_refill_player()
        pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + 110, bl.y, bl.z), unreal.Rotator(0, 180, 0), False, True)
        pc.set_control_rotation(unreal.Rotator(0, 180, 0))
        s["step"] = 1
        s["wait"] = s["t"] + 0.6
    elif n == 1:
        c["hp0"] = attr(pawn, "Attribute.Health")
        c["boss0"] = attr(boss, "Attribute.Health")
        log("start: boss health %s, player health %s, start_move %s" % (c["boss0"], c["hp0"], tr.start_move("A2")))
        c["t0"] = s["t"]
        s["step"] = 2
    elif n == 2:
        el = s["t"] - c["t0"]
        if el >= PRESS_AT and "pressed" not in c:
            c["pressed"] = True
            c["press_until"] = s["t"] + 0.12
        if int(el * 4) != c.get("last", -1):
            c["last"] = int(el * 4)
            inst = mc.get_anim_instance()
            m = inst.get_current_active_montage()
            log("t=%.2f boss health %s phase %s montage %s ragdoll %s player health %s" % (el, attr(boss, "Attribute.Health"), tr.get_phase_name(), m.get_name() if m else None, mc.is_simulating_physics(), attr(pawn, "Attribute.Health")))
        if el > 5.5:
            dead = (attr(boss, "Attribute.Health") or 0) <= 0
            hp = attr(pawn, "Attribute.Health")
            ok = dead and tr.get_phase_name() == "None" and hp >= c["hp0"] - 0.01
            log("%s: boss dead %s, tracker %s, player health %s -> %s (a live attack would have cost 36 at 2.0 s)" % ("PASS" if ok else "FAIL", dead, tr.get_phase_name(), c["hp0"], hp))
            finish()
            s["step"] = 99


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
