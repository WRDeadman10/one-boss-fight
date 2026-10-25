"""P0 read-only observer: logs every start of a boss montage while a PIE fight runs (run it BEFORE the fight driver, it waits for PIE).
Per start: world time, montage name, distance to the player, tracker phase name and current move (empty for untracked moves), boss phase two / transition flags.
Also logs once at the start the live cvars (rpg.WakeClip, rpg.CloseTelegraph) so the sample is labelled. Changes nothing: no property set, no function that mutates, only getters.
Log prefix [P0Nat]; it stops itself ten seconds after the game world is gone and prints a per-montage count ([P0Nat] COUNT ...)."""
import unreal

log = lambda m: unreal.log("[P0Nat] " + m)
S = unreal.SystemLibrary
state = {"t": 0.0, "last": None, "no_world": 0.0, "counts": {}, "armed": False, "t0": None}
handle = None


def find_boss(world):
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
        if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C":
            return a
    return None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def _tick(dt):
    global handle
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if world is None:
        if state["armed"]:
            state["no_world"] += dt
            if state["no_world"] > 10.0:
                for k, v in sorted(state["counts"].items(), key=lambda kv: -kv[1]):
                    log("COUNT %s x%d" % (k, v))
                log("done")
                unreal.unregister_slate_post_tick_callback(handle)
                handle = None
        return
    state["no_world"] = 0.0
    boss = find_boss(world)
    if boss is None:
        return
    if not state["armed"]:
        state["armed"] = True
        log("armed: rpg.WakeClip=%s rpg.CloseTelegraph=%s rpg.Build=%r" % (S.get_console_variable_float_value("rpg.WakeClip"), S.get_console_variable_float_value("rpg.CloseTelegraph"), S.get_console_variable_string_value("rpg.Build")))
    state["fps_acc"] = state.get("fps_acc", 0.0) + dt
    state["fps_n"] = state.get("fps_n", 0) + 1
    if state["fps_acc"] >= 10.0:
        log("FPS over the last %.1f s: %.1f frames/s (tick count %d)" % (state["fps_acc"], state["fps_n"] / state["fps_acc"], state["fps_n"]))
        state["fps_acc"] = 0.0
        state["fps_n"] = 0
    anim = boss.get_editor_property("mesh").get_anim_instance()  # Character.get_mesh is not exposed to Python
    montage = anim.get_current_active_montage() if anim else None
    name = montage.get_name() if montage else None
    if name != state["last"]:
        state["last"] = name
        if name:
            pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
            dist = (pawn.get_actor_location() - boss.get_actor_location()).length() if pawn else -1.0
            tracker = comp(boss, "RPGAttackTracker")
            phases = comp(boss, "RPGBossPhases")
            log("MONTAGE %s t=%.2f dist=%.0f tracker_phase=%s tracker_move=%s phase_two=%s transition=%s" % (
                name, unreal.GameplayStatics.get_time_seconds(world), dist, tracker.get_phase_name() if tracker else "?", tracker.get_current_move() if tracker else "?",
                phases.is_phase_two() if phases else "?", phases.is_in_transition() if phases else "?"))
            state["counts"][name] = state["counts"].get(name, 0) + 1


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
log("observer registered")
