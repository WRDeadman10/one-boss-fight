"""DRAFT diagnostics, not a map authoring/setup script. [EncounterBinding]
Requires promoted step2 and an explicitly reviewed two-encounter fixture map already open.
No component property writes, map loads or game-state hooks. Missing fixture FAILS.
Fresh PIE recreation is tested; seamless/in-game world travel remains a separate witness.
"""
import time
import traceback
import unreal

TAG = "[EncounterBinding] "
RESULTS = []
HANDLE = None
START = time.monotonic()
NEXT = 0.0
HEARTBEAT = 0.0
DONE = False
ORIGINAL = {name: unreal.SystemLibrary.get_console_variable_string_value(name)
            for name in ("rpg.CatalogSource", "rpg.CatalogTestInvalid")}


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def command(text):
    unreal.SystemLibrary.execute_console_command(world(), text)


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    unreal.log(TAG + ("PASS " if ok else "FAIL ") + name + " " + str(detail))


def script():
    previous_sessions = set()
    for mode, invalid in (("legacy", 0), ("auto", 0), ("data", 0), ("data", 1)):
        command("rpg.CatalogSource " + mode)
        command("rpg.CatalogTestInvalid " + str(invalid))
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        yield 8.0
        w = world()
        check(mode + " PIE world", w is not None)
        if w is None:
            raise RuntimeError("PIE did not begin")
        ctx = unreal.SubsystemBlueprintLibrary.get_world_subsystem(w, unreal.RPGCombatContextSubsystem)
        check(mode + " context available", ctx is not None)
        if ctx is None:
            raise RuntimeError("step2 not promoted or subsystem absent")
        session = str(ctx.get_session_id())
        check(mode + " fresh world session", bool(session) and session not in previous_sessions)
        previous_sessions.add(session)
        actors = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)
        participants = [c for a in actors for c in a.get_components_by_class(unreal.RPGCombatParticipant)]
        if invalid:
            check("strict invalid publishes no ready stack", ctx.get_ready_count() == 0)
            check("strict invalid no participant fallback", not any(c.is_ready() for c in participants))
        else:
            check(mode + " explicit two-encounter fixture present", ctx.get_bound_count() >= 4)
            check(mode + " every bound participant ready", ctx.get_ready_count() == ctx.get_bound_count() and ctx.get_ready_count() >= 4)
            check(mode + " participant component count", len(participants) == ctx.get_bound_count())
            keys = [str(c.get_key_diagnostic()) for c in participants]
            check(mode + " keys unique", len(keys) >= 4 and len(keys) == len(set(keys)))
            check(mode + " every participant ready", bool(participants) and all(c.is_ready() for c in participants))
            unreal.SystemLibrary.collect_garbage()
            yield 0.5
            check(mode + " ready after real GC", ctx.get_ready_count() >= 4 and all(c.is_ready() for c in participants))
        # Release Python UObject proxies before teardown; new PIE must have a new session.
        participants = actors = ctx = w = None
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        yield 2.0
        check(mode + " teardown world gone", world() is None)


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
    for name, value in ORIGINAL.items():
        try:
            command(name + ' "' + str(value).replace('"', '') + '"')
        except Exception as error:
            check("restore " + name, False, error)
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
        if elapsed > 100.0:
            raise TimeoutError("binding driver wall-clock deadline")
        if elapsed >= NEXT:
            NEXT = elapsed + float(next(GEN))
    except StopIteration:
        finish()
    except Exception:
        check("driver exception", False, traceback.format_exc())
        finish()


GEN = script()
HANDLE = unreal.register_slate_post_tick_callback(tick)
