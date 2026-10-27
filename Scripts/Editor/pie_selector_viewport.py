"""DD-1 step 1 condition 3 (measurement driver, Codex lead work order 02, C-L2 part 2): records what the build selector does in the REAL PIE viewport.
Run it with the editor window at a large and at a constrained size (Scripts/SetEditorWindow.ps1). With the fourth-build test fixture on (rpg.CatalogTestFourth 1, data
source) it opens the selector and logs the actual viewport size, the selector's layout height, the visible-row verdict of every row for that height and the row texts.
No component property writes; UFUNCTION hooks only; restores the cvars. Log prefix [SelectorViewport]; RESULT n/m counts the checks (each asserts a recorded fact, not a formula)."""
import unreal

log = lambda msg: unreal.log("[SelectorViewport] " + msg)
results = []
S = {"time": 0.0, "next": 0.0, "heartbeat": 0.0, "done": False}
handle = None


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def console(command):
    unreal.SystemLibrary.execute_console_command(world(), command)


def check(name, ok, detail=""):
    results.append(bool(ok))
    log(("PASS " if ok else "FAIL ") + name + " " + str(detail))


def component(actor, cls):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent)
                 if c.get_class().get_name() == cls), None) if actor else None


def parts():
    w = world()
    pawn = unreal.GameplayStatics.get_player_pawn(w, 0) if w else None
    return pawn, component(pawn, "RPGBuildLoadout"), component(pawn, "RPGBuildSelect"), unreal.GameplayStatics.get_player_controller(w, 0) if w else None


def wait_until(predicate, timeout):
    deadline = S["time"] + timeout
    while S["time"] < deadline:
        if predicate():
            return True
        yield 0.2
    return False


ORIGINAL = {name: unreal.SystemLibrary.get_console_variable_string_value(name) for name in ("rpg.CatalogSource", "rpg.CatalogTestFourth", "rpg.CatalogTestInvalid")}


def script():
    console("rpg.CatalogSource data")
    console("rpg.CatalogTestFourth 1")
    console("rpg.CatalogTestInvalid 0")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
    ok = yield from wait_until(lambda: parts()[2] is not None, 60.0)
    check("selector component exists", ok)
    if not ok:
        return
    yield 10.0  # the player must be alive and grounded and the boss dormant for the selector to open (CanOpen)
    pawn, ld, sel, pc = parts()
    log("epoch: " + str(ld.get_catalog_diagnostic()))
    check("fourth fixture row present (4 rows, data epoch)", sel.get_row_count() == 4 and str(ld.get_catalog_diagnostic()).startswith("data:"), sel.get_row_count())
    # A fresh session starts with the player's health attribute at 0 ("the player is dead" refuses the selector): refill through the existing debug hook of the boss.
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world(), unreal.Character)
                 if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
    debug = component(boss, "RPGCombatDebug")
    check("debug hook for the refill exists", debug is not None)
    if debug is not None:
        debug.debug_refill_player()
        yield 1.0
    # The selector needs a few seconds after the session start (loadout idle, epoch bound): retry the open for up to 20 s.
    opened = yield from wait_until(lambda: sel.is_open() or (sel.open_for_test() and sel.is_open()), 20.0)
    check("selector opens", opened, "reason when refused: " + str(sel.get_last_pick_result()))
    yield 1.0  # a frame or two so the widget has a real geometry
    # LayoutHeight() is not exposed to Python: use the same fallback the selector uses when its widget has no geometry yet (viewport height / viewport scale).
    viewport = unreal.WidgetLayoutLibrary.get_viewport_size(world())
    scale = float(unreal.WidgetLayoutLibrary.get_viewport_scale(world()))
    log("viewport size (px): %.0f x %.0f, viewport scale %.3f" % (viewport.x, viewport.y, scale))
    height = float(viewport.y) / max(scale, 0.01)
    log("selector layout height (slate units, viewport height / scale): %.1f" % height)
    check("layout height is a real positive number", height > 50.0, height)
    verdicts = [bool(sel.is_row_visible(i, height)) for i in range(4)]
    log("row visibility at that height (rows 0 to 3): %s" % verdicts)
    log("row texts: %s" % [str(sel.get_row_text(i)) for i in range(4)])
    check("the first three rows are always visible", all(verdicts[:3]), verdicts)
    log("RECORD fourth row visible=%s at layout height %.1f" % (verdicts[3], height))
    # The same question for a deliberately constrained height, as the formula (unit view), next to the measured one.
    for probe in (200.0, 400.0, 600.0, 800.0):
        log("formula view: height %.0f -> visible rows %s" % (probe, [bool(sel.is_row_visible(i, probe)) for i in range(4)]))
    # A pick of a hidden row must be refused by the same geometry (programmatic path).
    if not verdicts[3]:
        result = str(sel.pick_for_test("CatalogFourth"))
        check("a hidden fourth row cannot be picked", result in ("row not visible", "invalid build"), result)
    else:
        result = str(sel.pick_for_test("CatalogFourth"))
        check("a visible fourth row can be picked", result in ("Accepted", "Same"), result)
    sel.close_for_test()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    yield 2.0


def finish():
    global handle
    if S["done"]:
        return
    S["done"] = True
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    for name, value in ORIGINAL.items():
        try:
            console(name + ' "' + str(value).replace('"', '') + '"')
        except Exception as error:
            log("restore %s failed: %s" % (name, error))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("RESULT %d/%d passed" % (sum(results), len(results)))


def tick(delta):
    try:
        S["time"] += delta
        if S["time"] - S["heartbeat"] > 10.0:
            S["heartbeat"] = S["time"]
            log("heartbeat %.1fs checks=%d" % (S["time"], len(results)))
        if S["time"] > 150.0:
            raise TimeoutError("selector viewport driver deadline")
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
