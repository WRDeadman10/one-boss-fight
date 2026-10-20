"""Starts PIE, wakes the boss, lists every UserWidget alive (class name, visibility) and takes a screenshot of the player view. Log prefix [HudProbe]."""
import unreal

log = lambda m: unreal.log("[HudProbe] " + m)
state = {"phase": "start", "t": 0.0, "step": 0, "wait": 0.0}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0, wait=9.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if pawn is None or boss is None or s["t"] < s["wait"]:
        return
    if s["step"] == 0:
        log("widgets before wake:")
        for wd in unreal.WidgetLibrary.get_all_widgets_of_class(w, unreal.UserWidget, False):
            log("  %s vis=%s" % (wd.get_class().get_name(), wd.get_editor_property("visibility")))
        comp(boss, "RPGBossEncounter").wake()
        bl = boss.get_actor_location()
        pawn.set_actor_location_and_rotation(unreal.Vector(bl.x + 650, bl.y, bl.z + 20), unreal.Rotator(0, 0, 180), False, True)
        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-6, yaw=180))
        s["step"] = 1
        s["wait"] = s["t"] + 2.5
        return
    if s["step"] == 1:
        log("widgets after wake:")
        for wd in unreal.WidgetLibrary.get_all_widgets_of_class(w, unreal.UserWidget, False):
            log("  %s vis=%s" % (wd.get_class().get_name(), wd.get_editor_property("visibility")))
        comp(boss, "RPGBossEncounter").hold_for_test(True)
        comp(boss, "RPGCombatDebug").debug_set_boss_health_fraction(0.9)
        s["step"] = 2
        s["wait"] = s["t"] + 2.0
        return
    if s["step"] == 2:
        log("widgets after damage:")
        for wd in unreal.WidgetLibrary.get_all_widgets_of_class(w, unreal.UserWidget, False):
            log("  %s vis=%s" % (wd.get_class().get_name(), wd.get_editor_property("visibility")))
        s["step"] = 3
        s["wait"] = s["t"] + 0.5
        return
    if s["step"] == 3:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("done")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
