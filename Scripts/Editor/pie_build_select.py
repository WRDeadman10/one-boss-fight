"""Gate 3, G3-5: the pre-fight build selector (URPGBuildSelect, B key; log prefix [BuildSelect]). Drives it through its test hooks (the key and mouse paths call the same functions):
  S1 the selector exists on the player and starts closed
  S2 it opens while the boss sleeps, the three rows name the three builds
  S3 a pick applies the build through the loadout (rpg.Build, weapon, HUD line) and closes the panel
  S4 a pick while closed does nothing; an invalid name keeps the panel open; picking the active build says Same
  S5 the boss awake: the panel refuses to open, an open panel closes when the boss wakes
  S6 close is idempotent (the Escape binding is on all the time)
Needs the warm-up of RunDrivers.ps1. Ends with RESULT n/m passed; rpg.Build is cleared at the end."""
import unreal

log = lambda m: unreal.log("[BuildSelect] " + m)
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0}
handle = None


def check(name, ok, detail=""):
    results.append(bool(ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    if actor is None:
        return None
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def P():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return {"pawn": pawn, "boss": boss, "sel": comp(pawn, "RPGBuildSelect"), "ld": comp(pawn, "RPGBuildLoadout"), "enc": comp(boss, "RPGBossEncounter")}


def console(cmd):
    try:
        unreal.SystemLibrary.execute_console_command(world(), cmd)
    except Exception as e:
        log("console command '%s' failed: %s" % (cmd, e))


def until(cond, timeout, step=0.0):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield step
    return True


def scenario():
    yield 3.0  # a short settle after the start (the encounter, the loadout and the selector are created in the first frames)
    p = P()
    sel, ld, enc = p["sel"], p["ld"], p["enc"]
    check("S1 the selector component exists", sel is not None)
    check("S1 the loadout component exists", ld is not None)
    if sel is None or ld is None or enc is None:
        return
    check("S1 the boss sleeps", enc.is_dormant())
    check("S1 the selector starts closed", not sel.is_open())
    check("S1 no build chosen at the start", not ld.has_choice(), ld.get_chosen_build_name())
    # S2
    opened = sel.open_for_test()
    check("S2 the selector opens while the boss sleeps", opened and sel.is_open(), sel.get_last_pick_result())
    texts = [str(sel.get_row_text(i)) for i in range(3)]
    check("S2 the rows name Starter, Strength and Dex", "Starter" in texts[0] and "Strength" in texts[1] and "Dex" in texts[2], str(texts))
    check("S2 a fourth row has no text", str(sel.get_row_text(3)) == "")
    # S4 first part: an invalid name keeps the panel open
    r = str(sel.pick_for_test("mace"))
    check("S4 an invalid build name is refused and the panel stays open", sel.is_open() and r == "invalid build", r)
    # S3
    r = str(sel.pick_for_test("Strength"))
    check("S3 picking Strength closes the panel", not sel.is_open(), r)
    ok = yield from until(lambda: "Claymore" in str(P()["ld"].get_build_line()) and P()["ld"].get_chosen_build_name() == "Strength", 6.0, 0.2)
    ld = P()["ld"]
    check("S3 the loadout applied the Strength build (claymore, HUD line)", ok, "%s | %s | %s" % (ld.get_chosen_build_name(), ld.get_build_line(), ld.get_actual_style_name()))
    # S4 rest
    r = str(sel.pick_for_test("Dex"))
    check("S4 a pick while the panel is closed does nothing", r == "not open" and P()["ld"].get_chosen_build_name() == "Strength", r)
    sel.open_for_test()
    r = str(sel.pick_for_test("strength"))
    check("S4 picking the active build (any case) says Same and closes", r == "Same" and not sel.is_open(), r)
    sel.open_for_test()
    r = str(sel.pick_for_test("Dex"))
    ok = yield from until(lambda: "Dual" in str(P()["ld"].get_build_line()) and P()["ld"].get_chosen_build_name() == "Dex", 6.0, 0.2)
    check("S4 a second pick switches to Dex", ok and not sel.is_open(), "%s | %s" % (P()["ld"].get_chosen_build_name(), P()["ld"].get_build_line()))
    # S6
    sel.close_for_test()
    sel.close_for_test()
    check("S6 close on a closed panel is harmless", not sel.is_open())
    # S5
    sel.open_for_test()
    check("S5 reopened for the wake test", sel.is_open())
    enc.wake()
    ok = yield from until(lambda: not P()["sel"].is_open(), 3.0, 0.1)
    check("S5 an open panel closes when the boss wakes", ok, str(P()["sel"].get_last_pick_result()))
    opened = P()["sel"].open_for_test()
    check("S5 the panel refuses to open while the boss is awake", (not opened) and (not P()["sel"].is_open()) and "awake" in str(P()["sel"].get_last_pick_result()), str(P()["sel"].get_last_pick_result()))
    console('rpg.Build ""')


def _tick(dt):
    global handle, gen
    s = S
    s["now"] += dt
    if s["phase"] == "start":
        s["t"] += dt
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s["phase"] = "wait"
            s["t"] = 0.0
        return
    p = P()
    if s["phase"] == "wait":
        if p["pawn"] is None or p["boss"] is None:
            return
        s["phase"] = "run"
        s["wake"] = s["now"]
        return
    if s["phase"] == "run":
        if s["now"] < s["wake"]:
            return
        try:
            w = next(gen)
            s["wake"] = s["now"] + (float(w) if w else 0.0)
        except StopIteration:
            s["phase"] = "end"
            s["wake"] = s["now"] + 0.5
        except Exception:
            import traceback
            check("scenario raised", False, traceback.format_exc())
            s["phase"] = "end"
            s["wake"] = s["now"] + 0.5
        return
    if s["phase"] == "end" and s["now"] >= s["wake"]:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
        console('rpg.Build ""')
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())


gen = scenario()
handle = unreal.register_slate_post_tick_callback(tick)
