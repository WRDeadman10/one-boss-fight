"""Scratch route (a) PIE proof (owner approval G-3, 2026-10-26). Spawns a SECOND boss inside PIE whose EnemyInfoRef names the scratch info
(set before BeginPlay by the C++ helper, nothing saved, the placed boss is never touched) and reads back what runs. No property writes on
components. Pack asset and map hashes are compared before and after. Log prefix [ScratchA]; RESULT n/m passed."""
import hashlib
import os
import unreal

log = lambda msg: unreal.log("[ScratchA] " + msg)
PROJECT = "C:/UnrealProject/OneBossFight/Content"
WATCH = ["/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/ExampleGreatSwordBoss.uasset",
         "/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss.uasset",
         "/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BB_Base.uasset",
         "/OneBossFight/Scratch/RouteA/BT_ScratchRouteA.uasset",
         "/OneBossFight/Scratch/RouteA/DA_ScratchRouteAInfo.uasset"]
MAP_DIR = PROJECT + "/OneBossFight/Levels"
INFO = "/Game/OneBossFight/Scratch/RouteA/DA_ScratchRouteAInfo"
BOSS_CLASS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C"
results = []
S = {"time": 0.0, "next": 0.0, "heartbeat": 0.0, "done": False}
handle = None


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else "absent"


def hashes():
    state = {p: sha(PROJECT + p) for p in WATCH}
    if os.path.isdir(MAP_DIR):
        for name in sorted(os.listdir(MAP_DIR)):
            if name.endswith(".umap"):
                state["map:" + name] = sha(MAP_DIR + "/" + name)
    return state


def check(name, ok, detail=""):
    results.append(bool(ok))
    log(("PASS " if ok else "FAIL ") + name + " " + str(detail))


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def placed_boss():
    w = world()
    return next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
                 if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C" and "ScratchBoss" not in a.get_name()), None) if w else None


def seq_of(lines, needle):
    for line in lines:
        if needle in line:
            return int(line.split()[0][1:])
    return None


def script():
    before = hashes()
    lib = unreal.RPGScratchRouteALibrary
    lib.reset_route_a_report()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
    yield 10.0
    placed = placed_boss()
    check("placed boss exists", placed is not None)
    if placed is None:
        return
    placed_before = str(lib.describe_ai(placed))
    log("placed readback: " + placed_before)
    check("placed boss uses the pack info and tree", "ExampleGreatSwordBoss." in placed_before and "BT_ExampleBoss" in placed_before, placed_before)
    check("placed boss tree is running", "running=1" in placed_before)

    info = unreal.load_asset(INFO)
    boss_class = unreal.load_class(None, BOSS_CLASS)
    check("scratch info and boss class load", info is not None and boss_class is not None)
    if info is None or boss_class is None:
        return
    location = placed.get_actor_location() + unreal.Vector(0.0, 900.0, 40.0)
    spawned = lib.spawn_boss_with_info(world(), boss_class, info, location)
    scratch, error = (spawned[0], spawned[1]) if isinstance(spawned, tuple) else (spawned, "")
    check("scratch boss spawned with the scratch info before BeginPlay", scratch is not None, error)
    if scratch is None:
        return
    yield 5.0
    scratch_read = str(lib.describe_ai(scratch))
    log("scratch readback: " + scratch_read)
    check("scratch boss EnemyInfoRef is the scratch info", "DA_ScratchRouteAInfo" in scratch_read, scratch_read)
    check("scratch boss runs the scratch tree under the pack controller", "BT_ScratchRouteA" in scratch_read and "controller=" in scratch_read and "controller=none" not in scratch_read, scratch_read)
    check("scratch boss uses the pack blackboard", "BB_Base" in scratch_read, scratch_read)

    lines = [str(x) for x in lib.get_route_a_report()]
    for line in lines:
        log("report " + line)
    entry_denied = seq_of(lines, "ENTRY") if lines else None
    check("report not empty: the project task ran", len(lines) > 0)
    denied_entry = next((l for l in lines if "ENTRY" in l and "deny=1" in l), None)
    allowed_entry = next((l for l in lines if "ENTRY" in l and "deny=0" in l), None)
    check("denied task entered under the pack controller", denied_entry is not None and "controller=" in denied_entry and "none" not in denied_entry.split("controller=")[1], denied_entry)
    reserve1 = seq_of(lines, "RESERVATION id=1")
    rejected = next((l for l in lines if "REJECTED id=1" in l), None)
    check("reservation allocated before the reject", reserve1 is not None and rejected is not None and reserve1 < seq_of(lines, "REJECTED id=1"))
    check("reject did not call the pack", rejected is not None and "pack was not called" in rejected and not any("PACK_CALL id=1" in l for l in lines))
    check("reject changed no montage", rejected is not None and "montage now=none" in rejected and any("RESERVATION id=1" in l and "montage now=none" in l for l in lines))
    check("allowed task entered after the rejection (selector fell through)", allowed_entry is not None and seq_of(lines, "ENTRY") is not None and lines.index(allowed_entry) > lines.index(denied_entry) if denied_entry and allowed_entry else False)
    reserve2 = seq_of(lines, "RESERVATION id=2")
    call2 = seq_of(lines, "PACK_CALL id=2")
    result2 = seq_of(lines, "PACK_RESULT id=2")
    check("reservation 2 allocated BEFORE the pack call", reserve2 is not None and call2 is not None and reserve2 < call2)
    check("pack call precedes its result", call2 is not None and result2 is not None and call2 < result2)
    result_line = next((l for l in lines if "PACK_RESULT id=2" in l), "")
    log("pack result line: " + result_line)
    check("pack ability route answered (activated flag recorded)", "activated=" in result_line, result_line)
    placed_after = str(lib.describe_ai(placed))
    check("placed boss readback unchanged by the scratch boss", placed_after == placed_before or placed_after.replace("running=0", "running=1") == placed_before, placed_after)

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    yield 3.0
    after = hashes()
    check("pack assets, scratch assets and maps unchanged by the test", before == after, [k for k in after if before.get(k) != after[k]])


def finish():
    global handle
    if S["done"]:
        return
    S["done"] = True
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("RESULT %d/%d passed" % (sum(results), len(results)))


def tick(delta):
    try:
        S["time"] += delta
        if S["time"] - S["heartbeat"] > 10.0:
            S["heartbeat"] = S["time"]
            log("heartbeat %.1fs checks=%d" % (S["time"], len(results)))
        if S["time"] > 120.0:
            raise TimeoutError("scratch driver deadline")
        if S["time"] < S["next"]:
            return
        S["next"] = S["time"] + float(next(GEN))
    except StopIteration:
        finish()
    except Exception:
        import traceback
        check("driver exception", False, traceback.format_exc())
        finish()


GEN = script()
handle = unreal.register_slate_post_tick_callback(tick)
