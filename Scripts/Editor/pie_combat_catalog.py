"""DD-1 catalog integration driver, NOT RUN by Codex. Fresh PIE per source mode.
No component property writes. RESULT counts every assertion, heartbeat and bounded waits.
Requires reviewed catalog assets authored by Claude for strict-data phase; missing assets FAIL.
Restores changed process cvars and unregisters callback even on failure. [CombatCatalog]"""
import unreal

log = lambda msg: unreal.log("[CombatCatalog] " + msg)
results = []
S = {"time": 0.0, "wait": 0.0, "next": 0.0, "heartbeat": 0.0, "done": False}
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


def actors():
    w = world()
    pawn = unreal.GameplayStatics.get_player_pawn(w, 0) if w else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
                 if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return pawn, component(pawn, "RPGBuildLoadout"), component(pawn, "RPGBuildSelect"), component(boss, "RPGBossEncounter")


def wait_until(predicate, timeout):
    deadline = S["time"] + timeout
    while S["time"] < deadline:
        if predicate():
            return True
        yield 0.1
    return False


def script():
    epochs = []
    for mode, fourth in (("legacy", 0), ("data", 0), ("data", 1)):
        console("rpg.CatalogSource " + mode)
        console("rpg.CatalogTestFourth %d" % fourth)
        console("rpg.CatalogTestInvalid 0")
        console('rpg.Build ""')
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        yield 10.0
        pawn, ld, sel, enc = actors()
        check(mode + " components", bool(pawn and ld and sel and enc))
        if not all((ld, sel, enc)):
            raise RuntimeError("missing catalog consumers")
        diagnostic = str(ld.get_catalog_diagnostic())
        check(mode + " actual source", diagnostic.startswith(mode + ":"), diagnostic)
        if mode == "data":
            check(mode + " coverage routes recorded", any("Starter/Light=exact" in str(line) for line in ld.get_catalog_coverage_lines()))
        check(mode + " independent epoch", diagnostic not in epochs, diagnostic)
        epochs.append(diagnostic)
        check(mode + " row count", sel.get_row_count() == (4 if fourth else 3))
        check(mode + " no initial choice", not ld.has_choice())
        for i, name in enumerate(("Starter", "Strength", "Dex")):
            check(mode + " legacy row " + name, name in str(sel.get_row_text(i)))
        check(mode + " fourth fits1080", sel.is_row_visible(3, 1080.0) == bool(fourth))
        check(mode + " hidden fourth400", not sel.is_row_visible(3, 200.0))
        check(mode + " open", sel.open_for_test())
        # Same-tick pick: regression witness C107 F1, no Slate layout/yield allowed here.
        immediate = str(sel.pick_for_test("Starter"))
        check(mode + " immediate legacy pick independent of layout", immediate in ("Accepted", "Same"), immediate)
        check(mode + " reopen after immediate pick", sel.open_for_test())
        before = str(ld.get_chosen_build_name())
        check(mode + " invalid selector", str(sel.pick_for_test("InvalidCatalogId")) == "invalid build" and sel.is_open())
        check(mode + " invalid unchanged", str(ld.get_chosen_build_name()) == before)
        target = "CatalogFourth" if fourth else "Strength"
        if fourth:
            log("INFO fourth fixture shares the existing Sword WeaponId: identity proof only, NOT new-weapon proof")
        check(mode + " select accepted", str(sel.pick_for_test(target)) in ("Accepted", "Same"))
        ok = yield from wait_until(lambda: str(actors()[1].get_state_name()) == "Idle" and str(actors()[1].get_chosen_build_name()) == target, 12.0)
        check(mode + " selected identity through equip", ok, ld.get_build_line())
        check(mode + " actual item", ("ToughSword" if fourth else "KwangSword") in str(ld.get_weapon_slot_report()))
        check(mode + " actual actor", str(ld.get_equipped_actor_class_name()) == ("BP_ToughSword_C" if fourth else "BP_KwangSword_C"))
        check(mode + " actual ability", ld.has_weapon_ability_for_test("GA_Sword_Melee_C" if fourth else "GA_Claymore_Melee_C"))
        check(mode + " actual style", str(ld.get_actual_style_name()) == ("SwordCombatStyle" if fourth else "ClaymoreCombatStyle"))
        before = str(ld.get_chosen_build_name())
        check(mode + " invalid loadout", str(ld.set_build_for_test("InvalidCatalogId")) == "Invalid" and str(ld.get_chosen_build_name()) == before)
        # Exercise the same deferred request through real loadout gates, not a resolver-only test.
        ld.set_build_for_test("Dex")
        ok = yield from wait_until(lambda: str(ld.get_actual_style_name()) == "DualSwordCombatStyle" and str(ld.get_state_name()) == "Idle", 12.0)
        check(mode + " prep different equipment", ok)
        enc.wake()
        yield 2.0
        enc.hold_for_test(True)
        calls = ld.get_apply_attempt_count()
        reply = str(ld.set_build_for_test(target))
        yield 0.3
        check(mode + " choice deferred while awake", reply == "Deferred" and ld.get_apply_attempt_count() == calls, reply)
        enc.reset_for_test()
        enc.hold_for_test(False)
        ok = yield from wait_until(lambda: str(ld.get_chosen_build_name()) == target and str(ld.get_state_name()) == "Idle" and str(ld.get_actual_style_name()) == ("SwordCombatStyle" if fourth else "ClaymoreCombatStyle"), 14.0)
        check(mode + " deferred apply after reset", ok, ld.get_build_line())
        check(mode + " deferred apply actual pack call", ld.get_apply_attempt_count() > calls)
        if fourth:
            # Existing debug hook already used by pie_builds B10; no new gameplay start hook.
            debug = component(enc.get_owner(), "RPGCombatDebug")
            old_name = pawn.get_name()
            check("fourth respawn debug hook available", debug is not None)
            if debug is not None:
                debug.debug_set_player_health(0.0)
                ok = yield from wait_until(lambda: actors()[0] is not None and actors()[0].get_name() != old_name, 30.0)
                check("fourth new pawn respawn", ok)
                ok = yield from wait_until(lambda: actors()[1] is not None and str(actors()[1].get_chosen_build_name()) == target and str(actors()[1].get_state_name()) == "Idle", 16.0)
                check("fourth reapply after respawn", ok)
                ld = actors()[1]
                check("fourth respawn actual style", str(ld.get_actual_style_name()) == "SwordCombatStyle")
        console("rpg.CatalogSource legacy" if mode == "data" else "rpg.CatalogSource data")
        yield 0.2
        check(mode + " late cvar cannot mutate epoch", str(ld.get_catalog_diagnostic()) == diagnostic)
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        yield 2.0
    # Isolated malformed startup fixture: no asset rename, property mutation or global epoch stack.
    console("rpg.CatalogSource data")
    console("rpg.CatalogTestFourth 0")
    console("rpg.CatalogTestInvalid 1")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
    yield 10.0
    pawn, ld, sel, enc = actors()
    check("strict fixture has consumers", ld is not None and sel is not None)
    if ld is not None and sel is not None:
        check("strict failure no epoch", str(ld.get_catalog_diagnostic()).startswith("unavailable:"))
        check("strict failure selector unavailable", sel.get_row_count() == 0 and not sel.open_for_test())
        check("strict failure invalid request", str(ld.set_build_for_test("Starter")) == "Invalid")


def finish():
    global handle
    if S["done"]:
        return
    S["done"] = True
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    # Each restore independent: one error must not skip the other settings.
    for name, value in ORIGINAL.items():
        try:
            console(name + ' "' + str(value).replace('"', '') + '"')
        except Exception as error:
            check("restore " + name, False, error)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    log("RESULT %d/%d passed" % (sum(results), len(results)))


def tick(delta):
    try:
        S["time"] += delta
        if S["time"] - S["heartbeat"] > 10.0:
            S["heartbeat"] = S["time"]
            log("heartbeat %.1fs checks=%d" % (S["time"], len(results)))
        if S["time"] > 280.0:
            raise TimeoutError("catalog driver deadline")
        if S["time"] < S["next"]:
            return
        S["next"] = S["time"] + float(next(GEN))
    except StopIteration:
        finish()
    except Exception:
        import traceback
        check("driver exception", False, traceback.format_exc())
        finish()


ORIGINAL = {name: unreal.SystemLibrary.get_console_variable_string_value(name)
            for name in ("rpg.CatalogSource", "rpg.CatalogTestFourth", "rpg.CatalogTestInvalid", "rpg.Build")}
GEN = script()
handle = unreal.register_slate_post_tick_callback(tick)
