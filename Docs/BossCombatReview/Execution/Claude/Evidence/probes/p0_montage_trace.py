"""P0 read-only tick tracer: for every boss montage start, logs the next TRACE_TICKS ticks: world time, montage position, is_playing/is_stopped, blend weight if readable, the names of the boss ability
system's ActivatedAbilities and AnimatingAbility (reflection getters). Purpose: find what ends a montage seconds before it should (E-005). Changes nothing. Log prefix [P0Trace]; ends itself 10 s after the world is gone."""
import unreal

log = lambda m: unreal.log("[P0Trace] " + m)
TRACE_TICKS = 14
LONG_TRACE_TICKS = 48  # for GS_ChargedAttack_Montage (A2): the stops were seen near 1 s of montage time
state = {"last": None, "left": 0, "no_world": 0.0, "armed": False, "name": None, "t": 0}
handle = None


def find_boss(world):
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
        if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C":
            return a
    return None


def asc_of(boss):
    return next((c for c in boss.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == "BP_AdvancedAbilitySystemComponent_C"), None)


def names(arr):
    try:
        return [x.get_class().get_name() for x in arr if x]
    except Exception as e:
        return "ERR %s" % e


def snapshot(world, boss, anim, montage, label):
    asc = asc_of(boss)
    act = names(asc.get_editor_property("ActivatedAbilities")) if asc else "no asc"
    try:
        animating = asc.get_editor_property("AnimatingAbility")
        animating = animating.get_class().get_name() if animating else None
    except Exception as e:
        animating = "ERR %s" % e
    behavior = "?"
    try:
        ctrl = boss.get_controller()
        bm = next((c for c in ctrl.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == "BP_BehaviorManagerComponent_C"), None) if ctrl else None
        cs = bm.get_editor_property("CurrentState") if bm else None
        behavior = cs.get_class().get_name() if cs else None
    except Exception as e:
        behavior = "ERR %s" % str(e)[:60]
    pos = anim.montage_get_position(montage) if montage else -1
    playing = anim.montage_is_playing(montage) if montage else None
    stopped = anim.montage_get_is_stopped(montage) if montage else None
    cur = anim.get_current_active_montage()
    log("%s t=%.3f montage=%s pos=%.3f playing=%s stopped=%s current=%s activated=%s animating=%s behavior_state=%s" % (
        label, unreal.GameplayStatics.get_time_seconds(world), montage.get_name() if montage else None, pos, playing, stopped, cur.get_name() if cur else None, act, animating, behavior))


def _tick(dt):
    global handle
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if world is None:
        if state["armed"]:
            state["no_world"] += dt
            if state["no_world"] > 10.0:
                log("done")
                unreal.unregister_slate_post_tick_callback(handle)
                handle = None
        return
    state["no_world"] = 0.0
    boss = find_boss(world)
    if boss is None:
        return
    state["armed"] = True
    anim = boss.get_editor_property("mesh").get_anim_instance()
    cur = anim.get_current_active_montage() if anim else None
    name = cur.get_name() if cur else None
    if name != state["last"]:
        state["last"] = name
        if name and not name.startswith("AnimMontage_"):
            state["left"] = LONG_TRACE_TICKS if name == "GS_ChargedAttack_Montage" else TRACE_TICKS
            state["mon"] = cur
            log("START %s" % name)
    if state["left"] > 0:
        snapshot(world, boss, anim, state.get("mon"), "tick")
        state["left"] -= 1
        if state["left"] == 0:
            log("END of trace")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
log("tracer registered")
