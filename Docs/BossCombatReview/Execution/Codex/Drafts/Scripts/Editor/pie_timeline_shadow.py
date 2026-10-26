"""DRAFT passive diagnostics. Requires fixture with hydrated/bound shadow components.
No forcing attacks, no toggling gameplay cvars, no pack writes. Does NOT prove on/off parity.
Natural run may have no observed move: zero samples explicitly FAIL, not an implicit pass.
"""
import time
import traceback
import unreal

TAG = "[TimelineShadow] "
RESULTS = []
HANDLE = None
START = time.monotonic()
NEXT = 0.0
HEARTBEAT = 0.0
DONE = False


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    unreal.log(TAG + ("PASS " if ok else "FAIL ") + name + " " + str(detail))


def script():
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
    yield 8.0
    w = world()
    if w is None:
        check("PIE world", False)
        return
    actors = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)
    shadows = [c for a in actors for c in a.get_components_by_class(unreal.RPGCombatTimelineShadow)]
    check("explicit two-instance observer fixture", len(shadows) >= 2)
    # Preserve metadata only, not actor proxies across teardown.
    initial = {str(s.get_owner().get_path_name()): s.get_record_count() for s in shadows}
    yield 25.0
    check("nonzero natural diagnostic coverage", bool(shadows) and sum(s.get_record_count() for s in shadows) > 0)
    check("record bound", all(0 <= s.get_record_count() <= 4096 for s in shadows))
    check("no dropped samples in fixture", bool(shadows) and all(s.get_dropped_records() == 0 for s in shadows))
    check("same actors, per-instance buffers", len(initial) == len(shadows))
    unreal.SystemLibrary.collect_garbage()
    yield 1.0
    check("observers live after GC", bool(shadows) and all(s.get_owner() is not None for s in shadows))
    unreal.log(TAG + "INFO diagnostic coverage only; flush provenance and observer-off/on hit/state parity require separate reviewed harness")
    shadows = actors = w = None
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    yield 2.0
    check("world teardown", world() is None)


def finish():
    global DONE, HANDLE
    if DONE:
        return
    DONE = True
    try:
        if HANDLE is not None:
            unreal.unregister_slate_post_tick_callback(HANDLE)
            HANDLE = None
    except Exception as error:
        check("unregister callback", False, error)
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception as error:
        check("end PIE", False, error)
    unreal.log(TAG + "RESULT %d/%d passed" % (sum(RESULTS), len(RESULTS)))


def tick(_delta):
    global NEXT, HEARTBEAT
    elapsed = time.monotonic() - START
    try:
        if elapsed - HEARTBEAT >= 10.0:
            HEARTBEAT = elapsed
            unreal.log(TAG + "heartbeat %.1fs checks=%d" % (elapsed, len(RESULTS)))
        if elapsed > 70.0:
            raise TimeoutError("shadow driver wall-clock deadline")
        if elapsed >= NEXT:
            NEXT = elapsed + float(next(GEN))
    except StopIteration:
        finish()
    except Exception:
        check("driver exception", False, traceback.format_exc())
        finish()


GEN = script()
HANDLE = unreal.register_slate_post_tick_callback(tick)
