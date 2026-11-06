# Fresh-process wrapper (lead, Claude, 2026-11-06): loads L_SevarogArena, applies the usual driver preconditions, runs Scripts/Editor/pie_er_inputs.py, quits.
import importlib.util
import os
import unreal

ROOT = unreal.Paths.project_dir()
SCRIPTS = os.path.join(ROOT, "Scripts", "Editor")
log = lambda m: unreal.log("[ERInputsRunner] " + m)
state = {"phase": "load", "t": 0.0, "module": None, "after": 0}
handle = None


def load(name):
    spec = importlib.util.spec_from_file_location("onebossfight_" + name, os.path.join(SCRIPTS, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def quit_editor(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log(reason + "; quitting editor")
    unreal.SystemLibrary.quit_editor()


unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level("/Game/OneBossFight/Levels/L_SevarogArena")
load("no_throttle")
load("wake_clip_off")
load("legend_off")
load("build_off")


def tick(dt):
    state["t"] += dt
    if state["phase"] == "load":
        if state["t"] > 20.0:
            state["module"] = load("pie_er_block_probe")
            state.update(phase="driver", t=0.0)
            log("driver started")
        return
    if state["phase"] == "driver":
        if state["module"].handle is None:
            state.update(phase="after", t=0.0)
        elif state["t"] > 120.0:
            quit_editor("driver timeout")
        return
    if state["t"] > 5.0:
        quit_editor("driver finished")


handle = unreal.register_slate_post_tick_callback(tick)
