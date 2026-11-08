"""Lead capture test: start PIE, wait, take 3 in-engine high-res screenshots, end. Log prefix [CapTest]."""
import unreal

S = {"t": 0.0, "phase": "start", "shots": 0}
HANDLE = None
OUT = "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/captest_%d.png"


def tick(dt):
    global HANDLE
    S["t"] += dt
    try:
        if S["phase"] == "start" and S["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="play", t=0.0)
        elif S["phase"] == "play" and S["t"] > 8.0 + S["shots"] * 1.0:
            ok = unreal.AutomationLibrary.take_high_res_screenshot(1280, 720, OUT % S["shots"])
            unreal.log("[CapTest] shot %d requested ok=%s" % (S["shots"], ok))
            S["shots"] += 1
            if S["shots"] >= 3:
                S.update(phase="end", t=0.0)
        elif S["phase"] == "end" and S["t"] > 3.0:
            unreal.unregister_slate_post_tick_callback(HANDLE)
            unreal.log("[CapTest] finished: shots")
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception as exc:
        unreal.log("[CapTest] error %s" % exc)
        unreal.unregister_slate_post_tick_callback(HANDLE)
        unreal.log("[CapTest] finished: error")


HANDLE = unreal.register_slate_post_tick_callback(tick)
