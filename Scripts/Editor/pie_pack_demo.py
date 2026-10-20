"""
Opens the Advanced ARPG pack's test level inside this project, plays it, and logs what exists (pawn, game mode, enemies,
attribute components). Window frames come from Scripts/CaptureLoop.ps1 while Saved/m7_flag.txt exists. Prefix [PackDemo].
  powershell -File Scripts/RunEditorScript.ps1 -Script Scripts/Editor/pie_pack_demo.py -Tag PackDemo -StopPattern "PackDemo\] finished"
"""
import os

import unreal

LEVEL = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Maps/GreyboxLevels/CombatSystemTestLevel"
SAVED = unreal.Paths.project_saved_dir()
FLAG = os.path.join(SAVED, "m7_flag.txt")
state = {"phase": "load", "t": 0.0}
handle = None


def log(msg):
    unreal.log("[PackDemo] " + msg)
    with open(os.path.join(SAVED, "pack_demo_trace.txt"), "a") as f:
        f.write(msg + chr(10))


def flag(tag):
    if tag is None:
        if os.path.exists(FLAG):
            os.remove(FLAG)
    else:
        with open(FLAG, "w") as f:
            f.write(tag)


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    global handle
    flag(None)
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception:
        pass
    q = {"n": 0, "h": None}

    def quit_tick(_dt):
        q["n"] += 1
        if q["n"] > 120:
            unreal.unregister_slate_post_tick_callback(q["h"])
            unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")

    q["h"] = unreal.register_slate_post_tick_callback(quit_tick)


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
    if s["phase"] == "load":
        s.update(phase="begin", t=0.0)
        return
    if s["phase"] == "begin":
        if s["t"] > 1.0:
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
        if s["t"] > 40.0:
            finish("no pawn after 40 s")
        return
    if s["phase"] == "wait":
        if s["t"] > 20.0:  # shader warm-up
            gm = unreal.GameplayStatics.get_game_mode(w)
            log("game mode: %s, pawn: %s, controller: %s" % (gm.get_class().get_name(), pawn.get_class().get_name(), pc.get_class().get_name()))
            actors = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)
            names = {}
            for a in actors:
                n = a.get_class().get_name()
                names[n] = names.get(n, 0) + 1
            log("actors by class: " + ", ".join("%s x%d" % (k, v) for k, v in sorted(names.items()) if not k.startswith(("StaticMesh", "Light", "Sky", "Atmos", "Exponential", "PostProcess", "Navigation", "Recast", "Brush", "World", "Default", "Player", "Sphere", "Lumen"))))
            flag("pack_demo")
            s.update(phase="hold", t=0.0)
        return
    if s["phase"] == "hold":
        if s["t"] > 3.0:
            flag(None)
            finish("captured")


# Loading a level from inside a tick crashes (async loading flush); do it in the startup script.
unreal.EditorLevelLibrary.load_level(LEVEL)
log("level loaded")
handle = unreal.register_slate_post_tick_callback(tick)
log("registered")
