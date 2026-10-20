"""Starts PIE, asks the boss's debug component to log all ability variables (LogRPGDebug "ABILITY" lines), stops PIE. Log prefix [DumpAb]."""
import unreal

log = lambda m: unreal.log("[DumpAb] " + m)
state = {"t": 0.0, "phase": "start", "done": False}
handle = None


def _tick(dt):
    global handle
    s = state
    s["t"] += dt
    if s["phase"] == "start" and s["t"] > 0.5:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        s.update(phase="play", t=0.0)
        return
    if s["phase"] != "play":
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if w is None:
        return
    if not s["done"] and s["t"] > 9.0:
        for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character):
            if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C":
                for c in a.get_components_by_class(unreal.ActorComponent):
                    if c.get_class().get_name() == "RPGCombatDebug":
                        c.dump_abilities(); c.dump_player_abilities(); c.dump_attributes()
                        log("dumped")
        s["done"] = True
    if s["t"] > 12.0:
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
