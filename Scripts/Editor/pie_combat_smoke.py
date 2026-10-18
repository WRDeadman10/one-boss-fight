"""
Play-in-editor smoke test for M3 combat. Run inside the open editor (L_Greybox loaded):
starts PIE, puts the player next to a dummy, swings the light combo, a heavy attack and a dodge,
and logs state / health transitions with the prefix [M3Drive]. Read the result in the Output Log.
"""

import unreal

LOG = "[M3Drive] "
state = {"phase": "start", "t": 0.0, "pawn": None, "dummy": None, "log_t": 0.0}
handle = None


def log(msg):
    unreal.log(LOG + msg)


def pie_world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def find(world, cls_name):
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.load_class(None, cls_name)):
        return a
    return None


def dump(tag):
    pawn, dummy = state["pawn"], state["dummy"]
    combat = pawn.get_components_by_class(unreal.RPGCombatComponent)[0]
    attr = pawn.get_components_by_class(unreal.RPGAttributeComponent)[0]
    dcombat = dummy.get_components_by_class(unreal.RPGCombatComponent)[0]
    dattr = dummy.get_components_by_class(unreal.RPGAttributeComponent)[0]
    log("%s | player state=%s idx=%s stamina=%.0f hitwin=%s | dummy state=%s hp=%.0f poise=%.0f" % (
        tag, combat.get_state(), combat.get_combo_index(), attr.get_stamina(), combat.is_hit_window_open(),
        dcombat.get_state(), dattr.get_health(), dattr.get_poise()))
    if combat.is_hit_window_open():
        mesh = pawn.get_editor_property("mesh")
        log("   sword base=%s tip=%s | pawn=%s dummy=%s" % (
            mesh.get_socket_location("sword_bottom"), mesh.get_socket_location("sword_top"),
            pawn.get_actor_location(), dummy.get_actor_location()))
    return combat


def tick(dt):
    try:
        _tick(dt)
    except Exception as exc:
        import traceback
        log('tick error: %s' % traceback.format_exc())
        finish()


def _tick(dt):
    global handle
    state['hb'] = state.get('hb', 0.0) + dt
    if state['hb'] > 2.0:
        state['hb'] = 0.0
        log('heartbeat phase=%s t=%.1f' % (state['phase'], state['t']))
    state["t"] += dt
    phase = state["phase"]

    if phase == "start":
        if state["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            state.update(phase="wait_pie", t=0.0)
        return

    world = pie_world()
    if phase == "wait_pie":
        if world is None or state["t"] < 3.0:
            return
        pawn = find(world, "/Script/OneBossFight.RPGPlayerCharacter")
        dummy = find(world, "/Script/OneBossFight.RPGTrainingDummy")
        if pawn is None or dummy is None:
            if state["t"] > 15.0:
                log("FAIL: pawn or dummy not found")
                finish()
            return
        state.update(pawn=pawn, dummy=dummy, phase="swing1", t=0.0)
        # Stand 170 cm in front of the dummy, facing it (dummy at x=-1100 faces -X).
        pawn.set_actor_location_and_rotation(unreal.Vector(-1270.0, 0.0, 110.0), unreal.Rotator(0.0, 0.0, 0.0), False, True)
        log("PIE up; pawn mesh anim class = %s" % pawn.get_editor_property("mesh").get_editor_property("anim_class"))
        dump("initial")
        try:
            hits = unreal.SystemLibrary.sphere_trace_multi_for_objects(
                world, unreal.Vector(-1270.0, 0.0, 110.0), unreal.Vector(-1100.0, 0.0, 110.0), 18.0,
                [unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY3], False, [pawn], unreal.DrawDebugTrace.NONE, False)
            log("object trace (Pawn) hits: %s" % [h.to_tuple()[9].get_name() if h.to_tuple()[9] else None for h in (hits[1] if isinstance(hits, tuple) else hits)])
        except Exception as exc:
            log("object trace failed: %s" % exc)
        dcombat = dummy.get_components_by_class(unreal.RPGCombatComponent)[0]
        pcombat = pawn.get_components_by_class(unreal.RPGCombatComponent)[0]
        log("teams player=%s dummy=%s ; capsule collision dummy=%s" % (
            pcombat.get_editor_property("team_id"), dcombat.get_editor_property("team_id"),
            dummy.get_editor_property("capsule_component").get_collision_enabled()))
        return

    if world is None:
        log("PIE ended")
        finish()
        return

    pawn = state["pawn"]
    combat = pawn.get_components_by_class(unreal.RPGCombatComponent)[0]

    # Sample every 0.1 s while anything is happening.
    state["log_t"] += dt
    if state["log_t"] > 0.1 and phase not in ("start", "wait_pie"):
        state["log_t"] = 0.0
        dump("t=%.1f %s" % (state["t"], phase))

    if phase == "swing1" and state["t"] > 1.0:
        log("request light 1 -> %s" % combat.request_light_attack())
        state.update(phase="combo", t=0.0)
    elif phase == "combo":
        # Keep pressing: the buffered press must chain 4 swings.
        if int(state["t"] * 10) % 4 == 0:
            combat.request_light_attack()
        if state["t"] > 5.0:
            state.update(phase="heavy", t=0.0)
    elif phase == "heavy" and state["t"] > 1.0:
        log("request heavy -> %s" % combat.request_heavy_attack())
        state.update(phase="dodge", t=0.0)
    elif phase == "dodge" and state["t"] > 6.0:
        log("request dodge -> %s" % combat.request_dodge(unreal.Vector(0.0, 1.0, 0.0)))
        state.update(phase="done", t=0.0)
    elif phase == "done" and state["t"] > 2.0:
        finish()


def finish():
    global handle
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        pass
    log("finished")


handle = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
