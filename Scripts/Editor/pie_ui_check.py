"""
PIE UI check: enters the boss fight, logs READY_HUD (capture the viewport then), opens the pause menu, logs
READY_MENU (capture again), then closes it and checks the game resumed. Prefix [UiDrive]. Needs -unattended and focus.
"""
import unreal

LOG = "[UiDrive] "
TRIGGER_POINT = unreal.Vector(-1100.0, 0.0, 120.0)
state = {"phase": "start", "t": 0.0}
handle = None


def log(msg):
    unreal.log(LOG + msg)


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    global handle
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        pass
    log("finished: " + reason)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error: " + traceback.format_exc())
        finish("error")


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    if w is None:
        if s["phase"] != "wait":
            finish("PIE ended")
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    boss = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGBossCharacter)
    if not boss:
        return
    brain = boss[0].get_components_by_class(unreal.RPGBossCombatComponent)[0]

    if s["phase"] == "wait":
        if s["t"] > 3.0:
            pawn.set_actor_location(TRIGGER_POINT, False, True)
            s.update(phase="fight", t=0.0)
            log("entered trigger; controller class %s" % pc.get_class().get_name())
        return
    if s["phase"] == "fight":
        if brain.get_boss_state() == unreal.RPGBossState.COMBAT and s["t"] > 1.0:
            # Stay near the boss so the boss bar and a hit effect show.
            pawn.set_actor_location_and_rotation(unreal.Vector(-235.0, 0.0, 120.0), unreal.Rotator(0.0, 0.0, 0.0), False, True)
            log("READY_HUD")
            s.update(phase="hud_wait", t=0.0)
        return
    if s["phase"] == "hud_wait":
        if s["t"] > 22.0:
            pc.set_menu_open(True)
            log("menu open=%s paused=%s" % (pc.is_menu_open(), unreal.GameplayStatics.is_game_paused(w)))
            log("READY_MENU")
            s.update(phase="menu_wait", t=0.0)
        return
    if s["phase"] == "menu_wait":
        if s["t"] > 14.0:
            pc.open_settings_page()
            log("READY_SETTINGS")
            s.update(phase="settings_wait", t=0.0)
        return
    if s["phase"] == "settings_wait":
        if s["t"] > 16.0:
            pc.set_menu_open(False)
            log("menu open=%s paused=%s" % (pc.is_menu_open(), unreal.GameplayStatics.is_game_paused(w)))
            s.update(phase="done", t=0.0)
        return
    if s["phase"] == "done" and s["t"] > 1.5:
        finish("checked")


handle = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
