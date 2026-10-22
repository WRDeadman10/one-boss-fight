"""
Gate 3, M13: the build line of the HUD (URPGBossHudWidget::BuildTextBlock, filled by URPGBossHud from the player's URPGBuildLoadout; log prefix [BuildHud]).
  U1 no build chosen: the widget exists and shows no build line (a default run is unchanged).
  U2 a build chosen while the boss sleeps: the line shows "Build: Strength (Claymore)" (the weapon really held) once the loadout has equipped it.
  U3 the boss awake: the line stays, the text is the loadout's own line.
  U4 a choice made in the fight: the line still names the weapon really held and says the new build comes next fight.
  U5 after the reset the new build is applied and the line says it ("Build: Dex (Dual Swords)").
  U6 the choice cleared (rpg.Build ""): the line is gone.
Screenshots with the UI (Shot ShowUI) of the dormant and the fighting state are taken for the owner's eye (the overlap with the pack's top left widget, plan R10): Saved/Screenshots/WindowsEditor, log lines "screenshot".
Needs the warm-up of RunDrivers.ps1. Ends with RESULT n/m passed; rpg.Build is cleared at the end.
"""
import unreal

log = lambda m: unreal.log("[BuildHud] " + m)
results = []
S = {"phase": "start", "t": 0.0, "now": 0.0, "wait": 0.0, "gen": None, "nopawn": 0.0}
handle = None
STYLE = {"Starter": "SwordCombatStyle", "Strength": "ClaymoreCombatStyle", "Dex": "DualSwordCombatStyle"}
LINE = {"Starter": "Build: Starter (Sword)", "Strength": "Build: Strength (Claymore)", "Dex": "Build: Dex (Dual Swords)"}


def check(name, ok, detail=""):
    results.append(bool(ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def comp(actor, name):
    if actor is None:
        return None
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def actors():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def P():
    w, pc, pawn, boss = actors()
    return {"w": w, "pc": pc, "pawn": pawn, "boss": boss, "enc": comp(boss, "RPGBossEncounter"), "tr": comp(boss, "RPGAttackTracker"), "dbg": comp(boss, "RPGCombatDebug"),
            "ld": comp(pawn, "RPGBuildLoadout"), "hud": comp(boss, "RPGBossHud")}


def console(cmd):
    try:
        w = world()
        if w is None:
            w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        unreal.SystemLibrary.execute_console_command(w, cmd)
    except Exception as e:
        log("console command '%s' failed: %s" % (cmd, e))


def until(cond, timeout, step=0.0):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield step
    return True


def shot(name):
    unreal.SystemLibrary.execute_console_command(world(), "Shot ShowUI")
    log("screenshot (ShowUI) " + name)


def widget():
    hud = P()["hud"]
    return hud.get_widget() if hud else None


def shown_text():
    wd = widget()
    return (wd.is_build_line_shown(), str(wd.get_build_line_text())) if wd else (None, None)


def equip(build, timeout=10.0):
    ld = P()["ld"]
    answer = ld.set_build_for_test(build)
    ok = yield from until(lambda: P()["ld"].get_actual_style_name() == STYLE[build] and P()["ld"].get_state_name() == "Idle", timeout)
    yield 0.6
    return answer, ok


def script():
    # U1 no choice
    P()["enc"].reset_for_test()
    yield 1.0
    p = P()
    check("U1 the boss HUD component and its widget exist", p["hud"] is not None and widget() is not None)
    shown, text = shown_text()
    check("U1 no build chosen: no build line (shown %s, text '%s')" % (shown, text), shown is False and not p["ld"].has_choice())
    # U2 Strength while the boss sleeps
    answer, ok = yield from equip("Strength")
    shown_ok = yield from until(lambda: shown_text()[0] is True, 3.0)
    shown, text = shown_text()
    check("U2 Strength chosen (%s, equipped %s): the line is shown and says '%s' (text '%s')" % (answer, ok, LINE["Strength"], text), ok and shown_ok and text == LINE["Strength"])
    check("U2 the text is the loadout's own line (%s)" % P()["ld"].get_build_line(), text == P()["ld"].get_build_line())
    shot("dormant, Strength")
    yield 0.8
    # U3 the boss awake
    p = P()
    p["enc"].wake()
    p["enc"].hold_for_test(True)
    p["dbg"].debug_refill_player()
    yield 3.0
    shown, text = shown_text()
    check("U3 the boss is awake (%s): the line stays '%s' (shown %s)" % (p["hud"].get_state_name(), text, shown), p["hud"].get_state_name() == "Fighting" and shown is True and text == LINE["Strength"])
    shot("fighting, Strength")
    yield 0.8
    # U4 a choice in the fight
    answer = P()["ld"].set_build_for_test("Dex")
    yield 1.5
    shown, text = shown_text()
    check("U4 a choice made in the fight (%s): the line names the weapon held and the next fight (text '%s')" % (answer, text), answer == "Deferred" and shown is True and text == LINE["Strength"] + " - next fight")
    # U5 the reset applies it
    P()["enc"].reset_for_test()
    ok = yield from until(lambda: P()["ld"].get_actual_style_name() == STYLE["Dex"] and P()["ld"].get_state_name() == "Idle", 12.0)
    yield 1.0
    shown, text = shown_text()
    check("U5 after the reset Dex is applied (%s) and the line says '%s' (text '%s')" % (ok, LINE["Dex"], text), ok and shown is True and text == LINE["Dex"])
    shot("dormant, Dex")
    # U6 cleared
    P()["ld"].set_build_for_test("")
    yield 1.0
    shown, text = shown_text()
    check("U6 the choice cleared: the line is gone (shown %s, has choice %s)" % (shown, P()["ld"].has_choice()), shown is False and not P()["ld"].has_choice())


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    try:
        console('rpg.Build ""')
    except Exception:
        pass
    log("RESULT %d/%d passed" % (sum(1 for r in results if r), len(results)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    s = S
    s["t"] += dt
    s["now"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            console('rpg.Build ""')
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    w, pc, pawn, boss = actors()
    if s["now"] - s.get("hb", 0.0) > 15.0:
        s["hb"] = s["now"]
        log("heartbeat: %.0f s, pawn %s, boss %s, wait %.2f" % (s["now"], pawn.get_name() if pawn else None, boss.get_name() if boss else None, s["wait"]))
    if pawn is None or boss is None:
        s["nopawn"] += dt
        if s["nopawn"] > 40.0 and s["gen"] is not None:
            check("the player and the boss exist (missing for 40 s)", False)
            finish()
        return
    s["nopawn"] = 0.0
    if s["wait"] > 0:
        s["wait"] -= dt
        return
    if s["gen"] is None:
        if s["t"] < 9.0:
            return
        s["gen"] = script()
    try:
        s["wait"] = float(next(s["gen"]))
    except StopIteration:
        finish()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        check("tick raised", False)
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
