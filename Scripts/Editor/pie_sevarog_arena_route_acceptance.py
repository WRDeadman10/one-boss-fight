"""C-1619/C-1637: passive production-route PIE acceptance for L_SevarogArena.

The driver never spawns or damages a boss and never calls selector test-start APIs.
Smoke mode observes startup evidence for up to 180 seconds and does not exercise
boss death. Full mode waits without a time limit for the player to defeat Sevarog.
"""
import json
import os
import re
import time
import traceback
from pathlib import Path

import unreal

MAP_PATH = "/Game/OneBossFight/Maps/L_SevarogArena"
DEFINITION_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter.DA_Sevarog_Framework_Encounter"
MODE = os.environ.get("SEVAROG_ARENA_ROUTE_MODE", "Smoke").strip().capitalize()
if MODE not in ("Smoke", "Full"):
    raise RuntimeError("SEVAROG_ARENA_ROUTE_MODE must be Smoke or Full")
LOG_PREFIX = "[SevarogArenaRoute] "
STATE = {
    "phase": "begin_play",
    "started_at": None,
    "last_log_read": 0.0,
    "log_offset": 0,
    "log_tail": "",
    "checks": {},
    "failure": "",
    "done": False,
    "keep_python_alive": False,
    "pie_world_observed": False,
    "pie_world_lost_at": None,
}
HANDLE = None


def log(message):
    unreal.log(LOG_PREFIX + str(message))


def output_path(name):
    raw = os.environ.get(name, "").strip()
    if not raw:
        raise RuntimeError(name + " must be set by run_sevarog_arena_route_acceptance.ps1")
    return Path(raw)


def definition_preflight():
    definition = unreal.load_asset(DEFINITION_PATH)
    if definition is None:
        raise RuntimeError("framework encounter definition did not load: " + DEFINITION_PATH)
    if not bool(definition.get_editor_property("use_framework_boss")):
        raise RuntimeError("framework encounter definition has use_framework_boss=false")
    profile = definition.get_editor_property("framework_boss_profile")
    if profile is None:
        raise RuntimeError("framework encounter definition has no framework profile")
    validator = getattr(getattr(unreal, "RPGBossCardValidationLibrary", None), "validate_framework_profile_report", None)
    if not callable(validator):
        raise RuntimeError("production framework-profile validator is not exposed to Editor Python")
    result = str(validator(profile)).strip()
    if result != "PASS":
        raise RuntimeError("framework profile validation refused: " + result)
    return definition, profile


def read_new_log_text():
    path = output_path("SEVAROG_ARENA_ROUTE_LOG")
    try:
        with path.open("rb") as stream:
            stream.seek(STATE["log_offset"])
            chunk = stream.read()
            STATE["log_offset"] = stream.tell()
    except (OSError, PermissionError):
        return ""
    if not chunk:
        return ""
    text = chunk.decode("utf-8", errors="replace")
    STATE["log_tail"] = (STATE["log_tail"] + text)[-1_000_000:]
    return text


def parse_route_markers():
    text = STATE["log_tail"]
    suppressed = re.search(r"arena_pack_boss_suppressed actor=(\S+) began_play=(\d) montage_active=(\d)", text)
    binding = re.search(r"arena_binding framework=(\d+) pack=(\d+) generation=(\d+)", text)
    hud = re.search(r"arena_pack_boss_hud stage=replacement_complete viewport_count=(\d+)", text)
    health = re.search(r"\[FrameworkProof\] boss_health max=([0-9.eE+-]+)", text)
    player_health = re.search(
        r"route=SevarogFrameworkArena outcome=PlayerHealthReady hp=([0-9.eE+-]+) max_hp=([0-9.eE+-]+)(?:\s|$)",
        text,
    )
    decision = re.search(r"\[CARD_DECISION\].*?card=([^ ]+)", text)
    defeated = re.search(r"\[FrameworkProof\] RESULT outcome=BossDefeated\b", text)
    refused = re.search(r"arena_route_refused reason=([A-Za-z0-9_]+)", text)
    build_marker = re.search(r"started, rpg\.Build is '([^']*)'", text)
    suppression_record = None
    if suppressed:
        suppression_record = {
            "actor": suppressed.group(1),
            "began_play": int(suppressed.group(2)),
            "montage_active": int(suppressed.group(3)),
        }
    STATE["checks"].update({
        "suppression": suppression_record,
        "binding": ({"framework": int(binding.group(1)), "pack": int(binding.group(2)),
                     "generation": int(binding.group(3))} if binding else None),
        "pack_bosshud_viewport_count": int(hud.group(1)) if hud else None,
        "sevarog_max_health": float(health.group(1)) if health else None,
        "player_health_current": float(player_health.group(1)) if player_health else None,
        "player_health_max": float(player_health.group(2)) if player_health else None,
        "tick_selected_card": decision.group(1) if decision else None,
        "boss_defeated": bool(defeated),
        "route_refusal": refused.group(1) if refused else None,
        "rpg_build_observed": build_marker.group(1) if build_marker else None,
    })


def live_world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def live_actor_census(world):
    pawns = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Pawn)
    framework = [actor for actor in pawns if actor.get_class().get_name() == "RPGFrameworkBossCharacter"]
    pack = [actor for actor in pawns if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"]
    return len(framework), len(pack)


def fail(reason):
    STATE["failure"] = str(reason)
    finish("FAILED")


def write_receipt(result):
    checks = STATE["checks"]
    suppression = checks.get("suppression")
    bt_ticks = suppression.get("bt_attack_ticks") if suppression else None
    bt_ticks_verified_zero = (bt_ticks is not None and bt_ticks == 0)
    if MODE == "Smoke":
        checks["boss_death"] = "NOT_EXERCISED_SMOKE"
    criteria = {
        "suppressed_pack_actor_observed": suppression is not None,
        "no_pack_montage_at_suppression": suppression is not None and suppression["montage_active"] == 0,
        "binding_framework_one_pack_zero": checks.get("binding") == {"framework": 1, "pack": 0,
            "generation": checks.get("binding", {}).get("generation", -1)} if checks.get("binding") else False,
        "no_pack_bosshud_widget": checks.get("pack_bosshud_viewport_count") == 0,
        "sevarog_health_1500": checks.get("sevarog_max_health") == 1500.0,
        "production_player_health_800_800": (
            checks.get("player_health_current") == 800.0
            and checks.get("player_health_max") == 800.0
        ),
        "production_tick_selected_card": bool(checks.get("tick_selected_card")),
        "boss_death_completed_encounter": checks.get("boss_defeated") is True if MODE == "Full" else "NOT_EXERCISED_SMOKE",
        "live_actor_census_framework_one_pack_zero": checks.get("live_framework_actor_count") == 1 and checks.get("live_pack_actor_count") == 0,
        "raw_behavior_tree_tick_count": True if bt_ticks_verified_zero else "BLOCKED_NOT_INSTRUMENTED",
        "smoke_starter_loadout_observed": checks.get("rpg_build_observed") == "Starter" if MODE == "Smoke" else True,
    }
    evidence_text = (
        "Suppression occurred prior to BeginPlay; raw BehaviorTree attack-task ticks verified zero (count=0)."
        if bt_ticks_verified_zero
        else "No tick counter exists in the current runtime telemetry; montage/began_play observations are retained as a proxy only."
    )
    receipt = {
        "task": "C-1619 route PIE acceptance",
        "mode": MODE,
        "result": result,
        "map": MAP_PATH,
        "definition": DEFINITION_PATH,
        "criteria": criteria,
        "observations": checks,
        "failure": STATE["failure"],
        "raw_behavior_tree_tick_evidence": evidence_text,
        "editor_log": os.environ.get("SEVAROG_ARENA_ROUTE_LOG", ""),
        "utc_epoch": time.time(),
    }
    receipt["accepted"] = result == "PASS" and all(value is True for value in criteria.values())
    blockers = []
    if MODE == "Smoke":
        blockers.append("BOSS_DEATH_NOT_EXERCISED_SMOKE")
    if not bt_ticks_verified_zero:
        blockers.append("RAW_BEHAVIOR_TREE_TICK_COUNTER_NOT_INSTRUMENTED")
    receipt["blockers"] = blockers if not receipt["accepted"] else []
    receipt["runtime_acceptance_status"] = "PASS" if receipt["accepted"] else ("SMOKE_PASS_LIFECYCLE_UNTESTED" if MODE == "Smoke" and result == "PASS" else "BLOCKED")
    output = output_path("SEVAROG_ARENA_ROUTE_RECEIPT")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)
    log("RECEIPT result=%s accepted=%s path=%s" % (result, receipt["accepted"], output))


def finish(result):
    global HANDLE
    if STATE["done"]:
        return
    STATE["done"] = True
    if MODE == "Smoke":
        try:
            unreal.SystemLibrary.execute_console_command(None, 'rpg.Build ""')
        except Exception as reset_cvar_error:
            log("BUILD_CVAR_RESET_FAILED %s" % reset_cvar_error)
    try:
        parse_route_markers()
        write_receipt(result)
    except Exception as error:
        log("RECEIPT_WRITE_FAILED %s" % error)
    if HANDLE:
        try:
            unreal.unregister_slate_post_tick_callback(HANDLE)
        except Exception:
            pass
        HANDLE = None
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception as error:
        log("END_PIE_REQUEST_FAILED %s" % error)
    if STATE["keep_python_alive"]:
        try:
            unreal.EditorPythonScripting.set_keep_python_script_alive(False)
            STATE["keep_python_alive"] = False
        except Exception as error:
            log("PYTHON_KEEPALIVE_RESET_FAILED %s" % error)
    log("FINISHED result=%s failure=%s" % (result, STATE["failure"] or "none"))


def tick(delta_seconds):
    try:
        now = time.monotonic()
        if now - STATE["last_log_read"] >= 0.5:
            read_new_log_text()
            parse_route_markers()
            STATE["last_log_read"] = now
        if STATE["phase"] == "begin_play":
            if now - STATE["started_at"] >= 2.0:
                if MODE == "Smoke":
                    try:
                        unreal.SystemLibrary.execute_console_command(None, "rpg.Build Starter")
                    except Exception as set_cvar_error:
                        log("BUILD_CVAR_SET_FAILED %s" % set_cvar_error)
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                log("PIE_REQUESTED map=%s" % MAP_PATH)
                STATE["phase"] = "observe"
                STATE["started_at"] = now
            return
        if STATE["phase"] != "observe":
            return
        if STATE["checks"].get("route_refusal"):
            fail("arena route refused: " + STATE["checks"]["route_refusal"])
            return
        if MODE == "Full" and STATE["checks"].get("boss_defeated"):
            required = ("suppression", "binding", "pack_bosshud_viewport_count", "sevarog_max_health", "tick_selected_card")
            missing = [name for name in required if not STATE["checks"].get(name)]
            if missing:
                fail("boss death observed but required evidence missing: " + ",".join(missing))
            else:
                finish("PASS")
            return
        world = live_world()
        if world:
            STATE["pie_world_observed"] = True
            STATE["pie_world_lost_at"] = None
            world_name = world.get_name()
            if "L_SevarogArena" not in world_name:
                fail("unexpected PIE world: " + str(world_name))
                return
            if STATE["checks"].get("binding"):
                framework_count, pack_count = live_actor_census(world)
                STATE["checks"]["live_framework_actor_count"] = framework_count
                STATE["checks"]["live_pack_actor_count"] = pack_count
                if framework_count != 1 or pack_count != 0:
                    fail("live actor census mismatch framework=%d pack=%d" % (framework_count, pack_count))
                    return
        else:
            if STATE["pie_world_observed"]:
                if STATE["pie_world_lost_at"] is None:
                    STATE["pie_world_lost_at"] = now
                elif now - STATE["pie_world_lost_at"] >= 2.0:
                    fail("PIE session ended prematurely without boss defeat (Escape or manual PIE stop observed)")
                    return
            elif now - STATE["started_at"] >= 60.0:
                fail("PIE world not observed within 60 seconds of begin_play request")
                return
        if STATE["checks"].get("suppression") and STATE["checks"]["suppression"]["montage_active"] != 0:
            fail("pack boss montage was active at suppression")
            return
        if MODE == "Smoke":
            binding = STATE["checks"].get("binding") or {}
            smoke_ready = (
                STATE["checks"].get("suppression") is not None
                and STATE["checks"]["suppression"]["montage_active"] == 0
                and binding.get("framework") == 1
                and binding.get("pack") == 0
                and STATE["checks"].get("pack_bosshud_viewport_count") == 0
                and STATE["checks"].get("sevarog_max_health") == 1500.0
                and STATE["checks"].get("player_health_current") == 800.0
                and STATE["checks"].get("player_health_max") == 800.0
                and bool(STATE["checks"].get("tick_selected_card"))
                and STATE["checks"].get("rpg_build_observed") == "Starter"
            )
            if smoke_ready:
                finish("PASS")
                return
            if now - STATE["started_at"] >= 180.0:
                fail("smoke evidence incomplete after 180 seconds")
                return
            return
    except Exception as error:
        log("DRIVER_EXCEPTION %s\n%s" % (error, traceback.format_exc()))
        fail(str(error))


try:
    output_path("SEVAROG_ARENA_ROUTE_LOG")
    output_path("SEVAROG_ARENA_ROUTE_RECEIPT")
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    STATE["keep_python_alive"] = True
    definition_preflight()
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    STATE["started_at"] = time.monotonic()
    HANDLE = unreal.register_slate_post_tick_callback(tick)
    if not HANDLE:
        raise RuntimeError("could not register Slate post-tick callback")
    log("PREFLIGHT_PASS map=%s definition=%s route_switch_temporarily_enabled=1; player must defeat boss through normal combat" % (MAP_PATH, DEFINITION_PATH))
except Exception as error:
    log("STARTUP_REFUSED %s\n%s" % (error, traceback.format_exc()))
    if STATE["keep_python_alive"]:
        try:
            unreal.EditorPythonScripting.set_keep_python_script_alive(False)
            STATE["keep_python_alive"] = False
        except Exception as reset_error:
            log("PYTHON_KEEPALIVE_RESET_FAILED %s" % reset_error)
    raise
