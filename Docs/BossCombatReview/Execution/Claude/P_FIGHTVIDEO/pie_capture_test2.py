"""Lead capture test 2: PIE, then a HighResShot console command every tick for 3 s of game time. Log prefix [CapTest]."""
import unreal

S = {"t": 0.0, "phase": "start", "n": 0}
HANDLE = None
OUT = "D:/FightVideo/test/f_%05d.png"


def tick(dt):
    S["t"] += dt
    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if S["phase"] == "start" and S["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="play", t=0.0)
        elif S["phase"] == "play" and world and S["t"] > 8.0:
            unreal.SystemLibrary.execute_console_command(world, "HighResShot 960x540 filename=%s" % (OUT % S["n"]))
            S["n"] += 1
            if S["t"] > 11.0:
                S.update(phase="end", t=0.0)
                unreal.log("[CapTest] requested %d frames, dt=%.4f" % (S["n"], dt))
        elif S["phase"] == "end" and S["t"] > 3.0:
            unreal.unregister_slate_post_tick_callback(HANDLE)
            unreal.log("[CapTest] finished: frames")
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception as exc:
        unreal.log("[CapTest] error %s" % exc)
        unreal.unregister_slate_post_tick_callback(HANDLE)
        unreal.log("[CapTest] finished: error")


HANDLE = unreal.register_slate_post_tick_callback(tick)
