"""Lead capture test 3: PIE at slomo 0.1, sequential HighResShot (next request only after the previous PNG exists).
Logs frames per real second and game seconds per frame. Log prefix [CapTest]."""
import os
import time
import unreal

S = {"t": 0.0, "phase": "start", "n": 0, "pending": None, "t0": None, "g0": None}
HANDLE = None
OUT = "D:/FightVideo/test3/f_%05d.png"


def tick(dt):
    S["t"] += dt
    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if S["phase"] == "start" and S["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="play", t=0.0)
        elif S["phase"] == "play" and world and S["t"] > 8.0:
            if S["t0"] is None:
                unreal.SystemLibrary.execute_console_command(world, "slomo 0.1")
                S["t0"], S["g0"] = time.time(), unreal.GameplayStatics.get_time_seconds(world)
            if S["pending"] is None or os.path.exists(S["pending"]):
                S["pending"] = OUT % S["n"]
                unreal.SystemLibrary.execute_console_command(world, "HighResShot 960x540 filename=%s" % S["pending"])
                S["n"] += 1
            if time.time() - S["t0"] > 20.0:
                g = unreal.GameplayStatics.get_time_seconds(world) - S["g0"]
                unreal.log("[CapTest] frames=%d real_s=20 game_s=%.2f frames_per_real_s=%.2f game_s_per_frame=%.4f" % (S["n"], g, S["n"] / 20.0, g / max(S["n"], 1)))
                S.update(phase="end", t=0.0)
        elif S["phase"] == "end" and S["t"] > 3.0:
            unreal.unregister_slate_post_tick_callback(HANDLE)
            unreal.log("[CapTest] finished: frames")
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception as exc:
        unreal.log("[CapTest] error %s" % exc)
        unreal.unregister_slate_post_tick_callback(HANDLE)
        unreal.log("[CapTest] finished: error")


HANDLE = unreal.register_slate_post_tick_callback(tick)
