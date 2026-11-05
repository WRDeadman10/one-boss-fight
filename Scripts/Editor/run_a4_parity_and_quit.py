"""Fresh-process A4 parity runner: apply RunDrivers preconditions, run A4, then quit."""
import importlib.util
import os
import unreal

ROOT = unreal.Paths.project_dir()
SCRIPTS = os.path.join(ROOT, "Scripts", "Editor")
log = lambda message: unreal.log("[A4ParityRunner] " + message)
state = {"phase": "warmup", "elapsed": 0.0, "ticks": 0, "after": 0, "module": None, "done": False}


def load(name):
    path = os.path.join(SCRIPTS, name + ".py")
    spec = importlib.util.spec_from_file_location("onebossfight_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Match the RunDrivers.ps1 session preconditions before the first driver run.
load("no_throttle")
load("wake_clip_off")
load("legend_off")
load("build_off")
warmup = load("pie_debug_overlay")
handle = None


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    if not state["done"]:
        state["done"] = True
        log("runner timeout/failure; quitting editor")
        unreal.SystemLibrary.quit_editor()


def tick(delta):
    global handle
    state["ticks"] += 1
    state["elapsed"] += delta
    if state["phase"] == "warmup":
        if warmup.handle is not None:
            if state["elapsed"] > 90.0:
                finish()
            return
        state["phase"] = "settle"
        state["elapsed"] = 0.0
        log("first-PIE debug-overlay warm-up completed; settling for 40 seconds")
        return
    if state["phase"] == "settle":
        if state["elapsed"] < 40.0:
            return
        state["module"] = load("pie_a4_low_sweep")
        state["phase"] = "driver"
        state["elapsed"] = 0.0
        log("A4 driver started")
        return
    if state["phase"] == "driver":
        if state["module"].handle is not None:
            if state["elapsed"] > 420.0:
                finish()
            return
        state["phase"] = "shutdown_settle"
        state["elapsed"] = 0.0
        return
    if state["phase"] == "shutdown_settle":
        state["after"] += 1
        if state["after"] < 60:
            return
        state["done"] = True
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        log("run complete; quitting editor")
        unreal.SystemLibrary.quit_editor()


handle = unreal.register_slate_post_tick_callback(tick)
