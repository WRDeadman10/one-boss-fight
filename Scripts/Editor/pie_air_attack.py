"""
PIE check of the jump attacks: the pack player enters combat, jumps, and while airborne triggers the melee ability (what the input buffer does on a light
attack press). Logs the player's montage and whether the character is falling every 0.1 s. Flags: HEAVY triggers Ability.Melee.StrongAttack input instead
(not implemented yet). Open L_SevarogArena first; run with Scripts/run_in_editor.py. Log prefix [AirPie].
"""
import unreal

log = lambda m: unreal.log("[AirPie] " + m)
HEAVY = True
JUMP = True
MANUAL_ACTIVATE = False  # False: only the injected input action starts the attack, as for a player  # False: the same press on the ground (checks the test itself)
ATTACK_DELAY = 0.12  # seconds after the jump press (the pack jump is short: back on the ground by about 0.3 s)
state = {"phase": "start", "t": 0.0, "log_t": 0.0, "jumped": False, "attacked": False}
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
    return "%s@%.2f" % (m.get_name(), inst.montage_get_position(m)) if m else None


def inject(pc, action_name):
    action = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/" + action_name)
    ok = unreal.RPGInputTestUtils.inject_action(pc, action, unreal.Vector(1, 0, 0))
    if not state.get("inject_logged"):
        state["inject_logged"] = True
        pawn = pc.get_controlled_pawn()
        buf = comp(pawn, "BP_InputBufferComponent_C")
        log("inject %s -> %s; action=%s; buffered tag now=%s" % (action_name, ok, action, buf.call_method("Get Buffered Input Tag") if buf else None))


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
    asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
    move = pawn.get_components_by_class(unreal.CharacterMovementComponent)[0]
    # keep the boss away: this test is about the player's own moves
    if s["phase"] == "wait":
        if s["t"] > 6.0:
            asc.call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
            s.update(phase="jump", t=0.0)
        return
    if s["phase"] == "jump":
        if s["t"] > 2.0 and not s["jumped"]:
            if JUMP:
                pawn.jump()
            s["jumped"] = True
            s["t"] = 0.0
            log("jump pressed")
        if s["jumped"] and s["t"] > ATTACK_DELAY and not s["attacked"]:
            s["attacked"] = True
            s["inject_until"] = s["t"] + 0.25  # the real input action is injected for a quarter second (press and release)
            ok = asc.call_method("Try Activate Abilities By Tag", args=(tags("Ability.Melee"),)) if MANUAL_ACTIVATE else None
            log("attack input while falling=%s (manual activation: %s)" % (move.is_falling(), ok))
            s["t"] = 0.0
        if s["attacked"] and s["t"] < s.get("inject_until", 0.0):
            inject(pc, "IA_StrongAttack" if HEAVY else "IA_NormalAttack")
        s["log_t"] += dt
        if s["jumped"] and s["log_t"] >= 0.1:
            s["log_t"] = 0.0
            log("t=%.1f falling=%s z=%.0f montage=%s" % (s["t"], move.is_falling(), pawn.get_actor_location().z, montage_of(pawn)))
        if s["attacked"] and s["t"] > 4.0:
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
