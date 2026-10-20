"""PIE: logs the Blueprint functions of the player pawn and its components ([RPGDebug] FUNCTION lines). Needs a warm-up PIE first."""
import unreal
state = {"t": 0.0, "phase": "start"}
handle = None


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    if boss is None or s["t"] < 9.0:
        return
    next(c for c in boss.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == "RPGCombatDebug").dump_player_functions()
    unreal.unregister_slate_post_tick_callback(handle)
    handle = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        unreal.log("[DumpFn] " + traceback.format_exc())


handle = unreal.register_slate_post_tick_callback(tick)
