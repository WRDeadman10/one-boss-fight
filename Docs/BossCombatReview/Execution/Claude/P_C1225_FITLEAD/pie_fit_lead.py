"""Lead fit capture (C-1225), built on the proven pie_sword_closeup.py pattern.
Reads Saved/ERFit_<blind>.json (-ERFitBlindId=...), holds + hides the boss, stands the player 500 cm away, and for the
baseline (mannequin, source clips) and the candidate (target mesh, retargeted clips) captures 3 poses x 2 views per clip.
Frames: D:/FightVideo/fit_test/<blind>/{base,cand}_<clip>_<view>_<n>.png. Never logs the character name.
Log prefix [FitLead]; stop marker "[FitLead] finished:". Saves no assets."""
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[FitLead] "
S = {"gen": None, "done": False, "n": 0, "t_req": 0.0}
HANDLE = None
BRIGHT_BYTES = 300000  # a black 960x540 PNG is ~10 KB; real frames are ~800 KB


def log(m):
    unreal.log(LOG + str(m))


def actors():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return world, pc, pawn, (plc.boss_actor(world) if world else None)


def wait(seconds):
    end = plc.game_time(actors()[0]) + seconds
    while plc.game_time(actors()[0]) < end:
        yield 0.0


def shot(path):
    world = actors()[0]
    unreal.SystemLibrary.execute_console_command(world, "HighResShot 960x540 filename=%s" % path)
    deadline = time.perf_counter() + 15.0
    while not os.path.exists(path) and time.perf_counter() < deadline:
        yield 0.0
    yield from wait(0.1)  # let the file finish and a few frames render
    size = os.path.getsize(path) if os.path.exists(path) else 0
    return size


def warm(out, tag):
    streak = 0
    for i in range(40):
        p = "%s/_warm_%s_%02d.png" % (out, tag, i)
        size = yield from shot(p)
        streak = streak + 1 if size > BRIGHT_BYTES else 0
        try:
            os.remove(p)
        except OSError:
            pass
        if streak >= 2:
            log("WARM_OK tag=%s frames=%d" % (tag, i + 1))
            return True
        yield from wait(0.15)
    log("WARM_FAIL tag=%s" % tag)
    return False


def capture_clip(pc, pawn, mesh, seq, out, prefix, clip):
    duration = max(0.01, float(seq.get_play_length()))
    mesh.play_animation(seq, False)
    mesh.set_play_rate(0.0)
    for view, off in (("side", 90.0), ("34", 45.0)):
        yaw = pawn.get_actor_rotation().yaw + off
        pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=-5.0, yaw=yaw))
        yield from wait(0.4)
        ok = yield from warm(out, "%s_%s_%s" % (prefix, clip, view))
        for k, frac in enumerate((0.15, 0.5, 0.85)):
            mesh.set_position(duration * frac, False)
            yield from wait(0.15)
            path = "%s/%s_%s_%s_%d.png" % (out, prefix, clip, view, k + 1)
            for attempt in range(8):
                size = yield from shot(path)
                if size > BRIGHT_BYTES:
                    break
                os.remove(path)
                yield from wait(0.2)
            log("SHOT %s ok=%s bytes=%d" % (os.path.basename(path), size > BRIGHT_BYTES, size))
            S["n"] += 1


def witness():
    cmd = unreal.SystemLibrary.get_command_line()
    blind = re.search(r"-ERFitBlindId=(Candidate_[ABC])", cmd).group(1)
    manifest = json.load(open(str(Path(unreal.Paths.project_saved_dir()) / ("ERFit_%s.json" % blind))))
    out = "D:/FightVideo/fit_test/%s" % blind
    os.makedirs(out, exist_ok=True)
    world, pc, pawn, boss = actors()
    enc = plc.component(boss, "RPGBossEncounter")
    enc.hold_for_test(True)
    boss.set_actor_hidden_in_game(True)
    loc = boss.get_actor_location()
    plc.place_player(pc, pawn, (loc.x - 500.0, loc.y, loc.z + 20.0), 0.0)
    yield from wait(1.0)
    mesh = next(c for c in pawn.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "CharacterMesh0")
    unreal.SystemLibrary.execute_console_command(world, "slomo 0.5")
    log("started blind=%s clips=%d" % (blind, len(manifest["clips"])))
    for prefix, mesh_path, key in (("base", manifest["source_mesh"], "source"), ("cand", manifest["target_mesh"], "output")):
        sk = unreal.load_asset(mesh_path)
        mesh.set_skeletal_mesh_asset(sk)
        yield from wait(0.5)
        for row in manifest["clips"]:
            seq = unreal.load_asset(row[key])
            if not seq:
                log("MISSING %s %s" % (prefix, row["name"]))
                continue
            yield from capture_clip(pc, pawn, mesh, seq, out, prefix, row["name"])
    unreal.SystemLibrary.execute_console_command(actors()[0], "slomo 1")


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("finished: %s shots=%d" % (reason, S["n"]))
    plc.end_play()


def tick(dt):
    try:
        world = actors()[0]
        if S["gen"] is None:
            if world is None:
                if not S.get("requested"):
                    S["requested"] = True
                    sel = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
                    if sel:
                        unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + sel)
                    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                    S["t_req"] = time.perf_counter()
                return
            _, pc, pawn, boss = actors()
            if not (pawn and boss) or time.perf_counter() - S["t_req"] < 6.0:
                return
            S["gen"] = witness()
        next(S["gen"])
    except StopIteration:
        finish("complete")
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
log("driver registered")
