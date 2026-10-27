"""DD-1 step 1, live equip of the DISTINCT fourth weapon through the isolated test catalog (Codex lead decision C170, X-156 2026-10-26).
Needs Scripts/Editor/make_typed_abi_fixtures.py and make_abi_test_catalog.py done and the editor built with rpg.CatalogPath. Snapshots and restores rpg.CatalogSource,
rpg.CatalogPath, rpg.CatalogTestFourth, rpg.CatalogTestInvalid and rpg.Build in every exit path; the shipped catalog and the map are never touched. A fresh PIE session starts with the
test catalog latched, the loadout equips build ABIFourth (own item, style, actor class, granted ability) and every identity is read back from the live pawn. Grant membership is
NOT claimed as ability execution. UFUNCTION hooks only, no component property writes. Log prefix [ABIFourthEquip]; RESULT n/m counts the checks."""
import unreal

log = lambda msg: unreal.log("[ABIFourthEquip] " + msg)
results = []
S = {"time": 0.0, "next": 0.0, "heartbeat": 0.0, "done": False}
handle = None
TEST_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/DA_ABITest_Catalog.DA_ABITest_Catalog"
CVARS = ("rpg.CatalogSource", "rpg.CatalogPath", "rpg.CatalogTestFourth", "rpg.CatalogTestInvalid", "rpg.Build")
ORIGINAL = {name: unreal.SystemLibrary.get_console_variable_string_value(name) for name in CVARS}


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
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
                 if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return pawn, component(pawn, "RPGBuildLoadout"), boss, component(boss, "RPGBossEncounter"), component(boss, "RPGCombatDebug")


def wait_until(predicate, timeout):
    deadline = S["time"] + timeout
    while S["time"] < deadline:
        if predicate():
            return True
        yield 0.2
    return False


def equipped(ld):
    return "style=%s actor=%s state=%s last=%s" % (ld.get_actual_style_name(), ld.get_equipped_actor_class_name(), ld.get_state_name(), ld.get_last_result())


def script():
    console("rpg.CatalogSource data")
    console('rpg.CatalogPath "%s"' % TEST_PATH)
    console("rpg.CatalogTestFourth 0")
    console("rpg.CatalogTestInvalid 0")
    console('rpg.Build ""')
    check("cvars read back as set", unreal.SystemLibrary.get_console_variable_string_value("rpg.CatalogPath") == TEST_PATH
          and unreal.SystemLibrary.get_console_variable_string_value("rpg.CatalogSource") == "data")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
    ok = yield from wait_until(lambda: parts()[1] is not None and parts()[3] is not None and parts()[4] is not None, 60.0)
    check("the pawn, the loadout, the boss encounter and the debug hook exist in a fresh PIE", ok)
    if not ok:
        return
    yield 8.0  # loadout idle, epoch bound, player grounded
    pawn, ld, boss, enc, dbg = parts()
    # Python has no game-instance-subsystem accessor in this editor build (probed 2026-10-26: no SubsystemBlueprintLibrary), so the latch is proven by its EFFECT here (the epoch
    # lists the fourth weapon, which exists only in the isolated test catalog) and by the editor log line "latched source=data path=<TEST_PATH>" that the analysis reads.
    diag = str(ld.get_catalog_diagnostic())
    coverage = [str(line) for line in ld.get_catalog_coverage_lines()]
    log("epoch: " + diag)
    log("coverage lines: %d, fourth weapon lines: %d" % (len(coverage), len([c for c in coverage if c.startswith("ABIFourthWeapon/")])))
    check("the epoch is data and lists the fourth weapon of the isolated test catalog (six action rows)", diag.startswith("data:") and len([c for c in coverage if c.startswith("ABIFourthWeapon/")]) == 6, diag)
    sel = component(pawn, "RPGBuildSelect")
    check("the selector lists four rows", sel is not None and sel.get_row_count() == 4, sel.get_row_count() if sel is not None else "no selector")
    # The pack answers the first style read some seconds after the session start (run 2 of 2026-10-26 read "None" at 8 s and answered at 17.5 s): wait for it, then record the state before the choice.
    answered = yield from wait_until(lambda: parts()[1].get_actual_style_name() != "None", 40.0)
    check("the pack has answered the first style read", answered)
    ld = parts()[1]
    before = equipped(ld)
    log("before: " + before)
    check("before the choice the player holds the pack sword", ld.get_actual_style_name() == "SwordCombatStyle" and ld.get_equipped_actor_class_name() == "BP_ToughSword_C", before)
    enc.reset_for_test()
    yield 1.0
    dbg.debug_refill_player()
    yield 1.5
    ld.reset_counters_for_test()
    answer = str(ld.set_build_for_test("ABIFourth"))
    log("set_build_for_test(ABIFourth) -> " + answer)
    check("the choice of the fourth build is accepted", answer == "Accepted", answer)
    ok = yield from wait_until(lambda: parts()[1].get_actual_style_name() == "DA_ABI_FourthCombatStyle" and parts()[1].get_state_name() == "Idle", 40.0)
    yield 1.0
    pawn, ld, boss, enc, dbg = parts()
    after = equipped(ld)
    log("after: " + after)
    for line in ld.get_event_lines():
        log("loadout event: " + str(line)[:300])
    check("the player holds the FIXTURE combat style (own asset name) and the loadout is idle", ok and ld.get_actual_style_name() == "DA_ABI_FourthCombatStyle", after)
    check("the weapon actor in the slot is the FIXTURE actor class, not the shipped sword", ld.get_equipped_actor_class_name() == "BP_ABI_FourthWeaponActor_C", ld.get_equipped_actor_class_name())
    slot = str(ld.get_weapon_slot_report())
    log("weapon slot: " + slot[:600])
    check("the weapon slot holds the fixture item asset", "DA_ABI_FourthWeaponItem" in slot, slot[:300])
    check("the chosen BuildId is the fourth build and the verified held build is its catalog display name", ld.has_choice() and ld.get_chosen_build_name() == "ABIFourth" and ld.get_build_name() == "ABI Fourth",
          "chosen=%s held=%s" % (ld.get_chosen_build_name(), ld.get_build_name()))
    check("the HUD line names the fourth build from the catalog", "ABI Fourth" in str(ld.get_build_line()), ld.get_build_line())
    check("one equip call succeeded and none failed", ld.get_apply_success_count() >= 1 and ld.get_apply_failure_count() == 0,
          "calls=%d success=%d failure=%d" % (ld.get_apply_attempt_count(), ld.get_apply_success_count(), ld.get_apply_failure_count()))
    grant = bool(ld.has_weapon_ability_for_test("GA_ABI_FourthMelee_C"))
    log("RECORD grant membership of GA_ABI_FourthMelee_C on the pawn: %s (membership only: no ability execution is claimed)" % grant)
    check("the fixture ability is a member of the pawn's granted abilities", grant)
    # Back to the shipped sword: the equip is reversible and the fixture does not stick.
    answer = str(ld.set_build_for_test("Starter"))
    ok = yield from wait_until(lambda: parts()[1].get_actual_style_name() == "SwordCombatStyle" and parts()[1].get_state_name() == "Idle", 40.0)
    yield 1.0
    ld = parts()[1]
    back = equipped(ld)
    log("back to Starter (%s): %s" % (answer, back))
    check("choosing Starter again restores the shipped sword style and actor", ok and ld.get_equipped_actor_class_name() == "BP_ToughSword_C", back)
    log("RECORD fixture ability still granted after the switch back: %s" % bool(ld.has_weapon_ability_for_test("GA_ABI_FourthMelee_C")))
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
    log("RESTORED " + str({name: unreal.SystemLibrary.get_console_variable_string_value(name) for name in CVARS}))
    log("RESULT %d/%d passed" % (sum(results), len(results)))


def tick(delta):
    try:
        S["time"] += delta
        if S["time"] - S["heartbeat"] > 10.0:
            S["heartbeat"] = S["time"]
            log("heartbeat %.1fs checks=%d" % (S["time"], len(results)))
        if S["time"] > 240.0:
            raise TimeoutError("abi fourth equip driver deadline")
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
