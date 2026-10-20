"""
PIE gallery: spawns each candidate Niagara system a few metres in front of the player (arena start, boss idle) and
writes Saved/m7_flag.txt with its name while it plays, so Scripts/CaptureLoop.ps1 grabs frames of it. Prefix [VfxGallery].
Systems come from Saved/vfx_gallery.txt (one /Game path per line, optional "path scale" pairs); defaults below.
"""
import os

import unreal

LOG = "[VfxGallery] "
SAVED = unreal.Paths.project_saved_dir()
FLAG = os.path.join(SAVED, "m7_flag.txt")
DEFAULTS = [
    ("/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Circle", 1.0),
    ("/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Buff_Lightning", 2.0),
    ("/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Aura_Lightning", 2.0),
    ("/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Explosion", 1.0),
    ("/Game/BeamPack/Niagara/LaserBeam/NS_Thunder_Beam7", 1.0),
    ("/Game/BeamPack/Niagara/LaserBeam/NS_Thunder_BeamUpgrade", 1.0),
    ("/Game/BeamPack/Niagara/LaserBeam/NS_LightingBeamV3", 1.0),
    ("/Game/BeamPack/Niagara/LaserBeam/NS_Proj_00_B_S_Lightning", 1.0),
    ("/Game/BeamPack/Niagara/LaserBeam/NS_Proj_00_B_S_Lightning4", 1.0),
    ("/Game/BeamPack/Niagara/LaserBeam/NS_Proj_00_B_S_Lightning5", 1.0),
    ("/Game/BloodPack/Slash/Niagara/NS_Slash_Med", 1.0),
    ("/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med", 1.0),
]
WARMUP_SECONDS = 20.0
SLOWMO = 0.1
HOLD_SECONDS = 4.0
state = {"phase": "start", "t": 0.0, "i": 0, "live": None}
handle = None


def log(msg):
    unreal.log(LOG + msg)
    with open(os.path.join(SAVED, "m7_trace.txt"), "a") as f:
        f.write(msg + chr(10))


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def entries():
    path = os.path.join(SAVED, "vfx_gallery.txt")
    if not os.path.exists(path):
        return DEFAULTS
    result = []
    for line in open(path).read().split(chr(10)):
        parts = line.split()
        if parts:
            result.append((parts[0], float(parts[1]) if len(parts) > 1 else 1.0))
    return result


def set_flag(tag):
    if tag is None:
        if os.path.exists(FLAG):
            os.remove(FLAG)
    else:
        with open(FLAG, "w") as f:
            f.write(tag)


def finish(reason):
    global handle
    set_flag(None)
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
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
    pawn.get_components_by_class(unreal.RPGAttributeComponent)[0].heal(1000.0)
    systems = entries()

    if s["phase"] == "wait":
        if s["t"] > 4.0:
            # Warm-up: every system once, so their shaders compile (and land in the local DDC) before the photos.
            forward = pawn.get_actor_forward_vector()
            for path, scale in systems:
                system = unreal.load_asset(path)
                if system is not None:
                    unreal.NiagaraFunctionLibrary.spawn_system_at_location(
                        w, system, pawn.get_actor_location() + forward * 380.0 - unreal.Vector(0.0, 0.0, 90.0),
                        unreal.Rotator(0.0, 0.0, 0.0), unreal.Vector(scale, scale, scale), True, True)
            log("warm-up spawned %d systems" % len(systems))
            s.update(phase="warm", t=0.0)
        return
    if s["phase"] == "warm":
        if s["t"] > WARMUP_SECONDS:
            s.update(phase="spawn", t=0.0)
        return
    if s["phase"] == "spawn":
        if s["i"] >= len(systems):
            finish("all shown")
            return
        path, scale = systems[s["i"]]
        system = unreal.load_asset(path)
        name = path.split("/")[-1]
        if system is None:
            log("missing " + path)
            s["i"] += 1
            return
        # In front of the player, on the floor, facing the player.
        forward = pawn.get_actor_forward_vector()
        where = pawn.get_actor_location() + forward * 380.0 - unreal.Vector(0.0, 0.0, 90.0)
        rot = unreal.Rotator(0.0, pawn.get_actor_rotation().yaw, 0.0)
        s["live"] = unreal.NiagaraFunctionLibrary.spawn_system_at_location(
            w, system, where, rot, unreal.Vector(scale, scale, scale), True, True)
        log("spawned %s scale %.1f -> %s" % (name, scale, s["live"]))
        set_flag(name)
        unreal.GameplayStatics.set_global_time_dilation(w, SLOWMO)  # short bursts need slow motion to photograph
        s.update(phase="hold", t=0.0)
        return
    if s["phase"] == "hold":
        if s["t"] > HOLD_SECONDS:
            unreal.GameplayStatics.set_global_time_dilation(w, 1.0)
            set_flag(None)
            if s["live"] is not None:
                s["live"].deactivate()
                s["live"].destroy_component(s["live"])
            s["i"] += 1
            s.update(phase="spawn", t=0.0)


handle = unreal.register_slate_post_tick_callback(tick)
log("gallery registered")
