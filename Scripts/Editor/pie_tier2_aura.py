"""Lead-only two-route Tier 2 aura lifecycle witness; run through RunLeadPie.ps1."""
import os
import sys
import time
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[Tier2Aura] "
S = {"phase": "start", "elapsed": 0.0, "gen": None, "wake": 0.0, "done": False, "checks": []}
HANDLE = None


def log(message):
    unreal.log(LOG + str(message))


def wait(seconds):
    deadline = time.perf_counter() + seconds
    while time.perf_counter() < deadline:
        yield 0.0


def attribute(actor, method, value=None):
    comp = plc.component(actor, "BP_AttributesComponent_C")
    if comp is None:
        raise RuntimeError("boss AttributesComponent missing")
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="Attribute.Health")')
    args = (tag,) if value is None else (tag, float(value))
    return float(comp.call_method(method, args=args)) if value is None else comp.call_method(method, args=args)


def aura_rows(boss):
    rows = []
    for item in boss.get_components_by_class(unreal.NiagaraComponent):
        asset = item.get_asset()
        if asset and asset.get_name() == "NS_Boss_PhaseTwoAura":
            rows.append((item.get_name(), bool(item.is_active())))
    return rows


def check(label, boss, expected):
    rows = aura_rows(boss)
    ok = len(rows) == expected and (not rows or rows[0][1])
    S["checks"].append(ok)
    log("CHECK %s pass=%s aura=%s expected_count=%d" % (label, ok, rows, expected))
    return ok


def witness():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    boss = plc.boss_actor(world)
    encounter = plc.component(boss, "RPGBossEncounter")
    presentation = plc.component(boss, "RPGTier2BossPresentation")
    if not all((world, boss, encounter, presentation)):
        raise RuntimeError("boss/encounter/Tier2 presentation missing")
    encounter.reset_for_test()
    yield from wait(1.0)
    encounter.wake()
    encounter.hold_for_test(True)
    yield from wait(2.2)
    maximum = attribute(boss, "GetMaxAttributeValue")
    log("ROUTE %s max_health=%.1f" % ("data" if os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip() else "legacy", maximum))
    if maximum <= 0:
        raise RuntimeError("boss max health unavailable")
    attribute(boss, "Set Current Attribute Value", maximum * 0.501)
    yield from wait(1.0)
    log("HEALTH threshold=%.1f actual=%.1f" % (maximum * 0.501, attribute(boss, "Get Current Attribute Value")))
    check("above_threshold", boss, 0)
    attribute(boss, "Set Current Attribute Value", maximum)
    yield from wait(0.5)
    check("full_health", boss, 0)
    attribute(boss, "Set Current Attribute Value", maximum * 0.5)
    yield from wait(1.0)
    log("HEALTH threshold=%.1f actual=%.1f" % (maximum * 0.5, attribute(boss, "Get Current Attribute Value")))
    check("half_health", boss, 1)
    unreal.SystemLibrary.execute_console_command(world, "rpg.Art.Tier2 0")
    yield from wait(0.5)
    check("tier2_off", boss, 0)
    unreal.SystemLibrary.execute_console_command(world, "rpg.Art.Tier2 1")
    yield from wait(1.0)
    check("tier2_on_again", boss, 1)
    encounter.reset_for_test()
    yield from wait(1.0)
    log("HEALTH after_reset=%.1f" % attribute(boss, "Get Current Attribute Value"))
    check("encounter_reset", boss, 0)
    encounter.wake()
    encounter.hold_for_test(True)
    yield from wait(2.2)
    attribute(boss, "Set Current Attribute Value", maximum * 0.5)
    yield from wait(1.0)
    check("next_phase", boss, 1)
    encounter.hold_for_test(False)


def finish(reason):
    global HANDLE
    if S["done"]:
        return
    S["done"] = True
    unreal.SystemLibrary.execute_console_command(None, "rpg.Art.Tier2 0")
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None
    log("SUMMARY pass=%s checks=%d reason=%s" %
        (len(S["checks"]) == 7 and all(S["checks"]), len(S["checks"]), reason))
    plc.end_play()


def tick(dt):
    try:
        S["elapsed"] += dt
        if S["elapsed"] > 45.0:
            finish("timeout")
            return
        if S["phase"] == "start":
            if S["elapsed"] > 0.5:
                selection = os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()
                if selection:
                    unreal.SystemLibrary.execute_console_command(None, "rpg.EncounterDefinition " + selection)
                unreal.SystemLibrary.execute_console_command(None, "rpg.Art.Tier2 1")
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                S.update(phase="wait", elapsed=0.0)
            return
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if S["phase"] == "wait":
            if world and plc.boss_actor(world) and S["elapsed"] > 6.0:
                S.update(phase="run", gen=witness())
            elif S["elapsed"] > 25.0:
                finish("boss missing")
            return
        if world and plc.game_time(world) >= S["wake"]:
            try:
                S["wake"] = plc.game_time(world) + float(next(S["gen"]))
            except StopIteration:
                finish("witness complete")
    except Exception:
        import traceback
        log("ERROR " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
