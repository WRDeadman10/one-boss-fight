"""C-1622/BT-79: Opt-in PIE visual smoke driver for Greystone player test route.

Per Lead directives [X-2581], [X-2583], [X-2584], and [X-2585], this driver enforces:
1. Exact BP_GreystoneERPlayer_C possession via exact class path (fail closed
   if mannequin or another pawn remains possessed).
2. Exact asset and class path validation on components:
   - CharacterMesh0 (source mesh): hidden in game, exact canonical mannequin mesh
     path, exact ABP_CombatCharacter_C anim class path, AlwaysTickPoseAndRefreshBones.
   - GreystoneRuntimeVisual (visible mesh): visible in game, exact Greystone mesh
     path, exact ABP_Greystone_RuntimeRetarget_C anim class path, attached to
     CharacterMesh0, AlwaysTickPoseAndRefreshBones, NoCollision.
3. Exact normalized PIE world map identity check against 'L_SevarogArena' (no substring).
4. Continuous Editor log monitoring: fails closed if Editor log is missing,
   unreadable, or 0 bytes are read across observation ticks.
5. Zero GetMainAnimBP Accessed None errors (KI-052 regression detector).
6. Mandatory environment run token and source hashes binding (runner, driver, C++).
7. Verified CVar restoration: real readback of rpg.GreystonePlayerTestPawn must equal 0,
   failing closed if unverified or mismatched.
8. Strict separation of machine-readable evidence from owner visual-art evaluation.

No assets, maps, or configuration files are saved by this driver.
"""
import json
import os
import re
import time
import traceback
from pathlib import Path

import unreal

MAP_PATH = "/Game/OneBossFight/Maps/L_SevarogArena"
EXPECTED_NORMALIZED_MAP_NAME = "L_SevarogArena"
EXPECTED_PAWN_CLASS_PATH = "/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer.BP_GreystoneERPlayer_C"
SOURCE_MESH_NAME = "CharacterMesh0"
VISIBLE_COMPONENT_NAME = "GreystoneRuntimeVisual"

ALLOWED_SOURCE_MESH_PATHS = (
    "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple.SKM_CombatMannequin_Simple",
    "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin.SKM_CombatMannequin",
)
EXPECTED_SOURCE_ANIM_CLASS_PATH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.ABP_CombatCharacter_C"
EXPECTED_VISIBLE_MESH_PATH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.Greystone"
EXPECTED_VISIBLE_ANIM_CLASS_PATH = "/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget.ABP_Greystone_RuntimeRetarget_C"

LOG_PREFIX = "[GreystoneVisualSmoke] "

STATE = {
    "phase": "preflight",
    "started_at": 0.0,
    "last_log_check": 0.0,
    "log_offset": 0,
    "log_tail": "",
    "total_bytes_read": 0,
    "log_read_count": 0,
    "get_main_anim_bp_errors": 0,
    "pc": None,
    "pawn": None,
    "source_hashes": {},
    "observation_settle_start": 0.0,
    "criteria": {
        "exact_pawn_possessed": False,
        "source_mesh_hidden": False,
        "runtime_visual_visible": False,
        "log_monitored_continuous": False,
        "zero_get_main_anim_bp_errors": False,
        "cvar_restored_zero": False,
    },
    "observations": {},
    "failure": "",
    "done": False,
    "cleaned_up": False,
    "keep_python_alive": False,
}

HANDLE = None


def log(message):
    unreal.log(LOG_PREFIX + str(message))


def log_warning(message):
    unreal.log_warning(LOG_PREFIX + str(message))


def log_error(message):
    unreal.log_error(LOG_PREFIX + str(message))


def get_run_token():
    # Per [X-2584]: remove standalone token fallback. Run token must be explicitly bound.
    token = os.environ.get("GREYSTONE_SMOKE_RUN_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GREYSTONE_SMOKE_RUN_TOKEN environment variable is required; standalone token generation is prohibited")
    return token


def get_log_path():
    raw = os.environ.get("GREYSTONE_SMOKE_LOG", "").strip()
    if not raw:
        raise RuntimeError("GREYSTONE_SMOKE_LOG environment variable is required; explicit Editor log path mandatory")
    return Path(raw)


def get_receipt_path():
    raw = os.environ.get("GREYSTONE_SMOKE_RECEIPT", "").strip()
    if not raw:
        raise RuntimeError("GREYSTONE_SMOKE_RECEIPT environment variable is required; explicit receipt path mandatory")
    return Path(raw)


def get_source_hashes():
    raw = os.environ.get("GREYSTONE_SMOKE_SOURCE_HASHES", "").strip()
    if not raw:
        raise RuntimeError("GREYSTONE_SMOKE_SOURCE_HASHES environment variable is required; source hash binding mandatory")
    try:
        hashes = json.loads(raw)
        required_keys = ("runner", "driver", "retarget_cpp", "moves_cpp")
        missing = [k for k in required_keys if not hashes.get(k)]
        if missing:
            raise RuntimeError("GREYSTONE_SMOKE_SOURCE_HASHES missing required keys: " + ", ".join(missing))
        return hashes
    except Exception as exc:
        raise RuntimeError("failed to parse GREYSTONE_SMOKE_SOURCE_HASHES: " + str(exc))


def normalize_world_name(raw_name):
    # Normalize PIE world name: e.g. 'UEDPIE_0_L_SevarogArena' -> 'L_SevarogArena'
    return re.sub(r"^UEDPIE_\d+_", "", raw_name)


def read_and_scan_log():
    log_file = get_log_path()
    if not log_file.is_file():
        # Log file not yet written by engine; non-fatal on early ticks
        return

    try:
        with open(str(log_file), "rb") as stream:
            stream.seek(STATE["log_offset"])
            chunk = stream.read()
            STATE["log_offset"] = stream.tell()
    except (OSError, PermissionError) as exc:
        log_error("failed to read log file: %s" % exc)
        fail("Editor log unreadable: " + str(exc))
        return

    if not chunk:
        return

    STATE["total_bytes_read"] += len(chunk)
    STATE["log_read_count"] += 1
    text = chunk.decode("utf-8", errors="replace")
    STATE["log_tail"] = (STATE["log_tail"] + text)[-500_000:]

    # Scan for GetMainAnimBP errors / warnings (KI-052 regression detector)
    lines = text.splitlines()
    for line in lines:
        if "GetMainAnimBP" in line:
            if "Accessed None" in line or "Error" in line or "Warning" in line:
                STATE["get_main_anim_bp_errors"] += 1
                log_error("DETECTED_GET_MAIN_ANIM_BP_ERROR: %s" % line.strip())


def restore_cvar():
    # Per [X-2585]: Execute restore AND read back real value; fail closed if not 0
    try:
        unreal.SystemLibrary.execute_console_command(None, "rpg.GreystonePlayerTestPawn 0")
        log("CVAR_RESTORE_COMMAND_EXECUTED cvar=rpg.GreystonePlayerTestPawn value=0")
    except Exception as exc:
        log_error("FAILED_CVAR_RESTORE_COMMAND error=%s" % exc)

    try:
        readback_str = unreal.SystemLibrary.get_console_variable_string_value("rpg.GreystonePlayerTestPawn").strip()
        STATE["observations"]["cvar_readback_value"] = readback_str
        if readback_str == "0":
            STATE["criteria"]["cvar_restored_zero"] = True
            log("CVAR_READBACK_VERIFIED cvar=rpg.GreystonePlayerTestPawn value=0")
        else:
            STATE["criteria"]["cvar_restored_zero"] = False
            log_error("CVAR_READBACK_MISMATCH expected='0' actual='%s'" % readback_str)
            fail("cvar rpg.GreystonePlayerTestPawn readback mismatch: expected '0', got '%s'" % readback_str)
    except Exception as exc:
        STATE["criteria"]["cvar_restored_zero"] = False
        STATE["observations"]["cvar_readback_error"] = str(exc)
        log_error("CVAR_READBACK_FAILED error=%s" % exc)
        fail("cvar rpg.GreystonePlayerTestPawn readback failed: %s" % exc)


def cleanup():
    if STATE["cleaned_up"]:
        return
    STATE["cleaned_up"] = True
    log("CLEANUP_INITIATED")
    restore_cvar()

    global HANDLE
    if HANDLE is not None:
        try:
            unreal.unregister_slate_post_tick_callback(HANDLE)
        except Exception:
            pass
        HANDLE = None

    if STATE["keep_python_alive"]:
        try:
            unreal.EditorPythonScripting.set_keep_python_script_alive(False)
            STATE["keep_python_alive"] = False
        except Exception:
            pass


def fail(reason):
    if not STATE["failure"]:
        STATE["failure"] = str(reason)
    log_error("SMOKE_FAILED reason=%s" % reason)
    finish("FAIL")


def finish(result):
    if STATE["done"]:
        return
    STATE["done"] = True

    # Final log sweep
    read_and_scan_log()

    # Per [X-2584]: fail closed if Editor log was missing, unreadable, or unmonitored
    log_file = get_log_path()
    if not log_file.is_file() or STATE["total_bytes_read"] == 0 or STATE["log_read_count"] == 0:
        if not STATE["failure"]:
            STATE["failure"] = "Editor log is missing or unmonitored: file_exists=%s bytes_read=%d reads=%d" % (
                log_file.is_file(), STATE["total_bytes_read"], STATE["log_read_count"]
            )
        result = "FAIL"
        STATE["criteria"]["log_monitored_continuous"] = False
        STATE["criteria"]["zero_get_main_anim_bp_errors"] = False
    else:
        STATE["criteria"]["log_monitored_continuous"] = True
        STATE["criteria"]["zero_get_main_anim_bp_errors"] = (STATE["get_main_anim_bp_errors"] == 0)

    # Perform mandatory cleanup (including CVar real-readback verification) before writing receipt
    cleanup()

    # Determine overall acceptance
    all_criteria_met = all(bool(val) for val in STATE["criteria"].values())
    overall_passed = (result == "PASS" and all_criteria_met)

    # Compile observations
    observations = STATE["observations"]
    observations.update({
        "requested_cvar": "rpg.GreystonePlayerTestPawn=1",
        "log_monitored": {
            "path": str(get_log_path()),
            "total_bytes_read": STATE["total_bytes_read"],
            "read_count": STATE["log_read_count"],
        },
        "get_main_anim_bp_errors": STATE["get_main_anim_bp_errors"],
        "cleanup": {
            "cvar_restored_to_zero": STATE["criteria"]["cvar_restored_zero"],
            "cvar_readback_value": observations.get("cvar_readback_value", "UNVERIFIED"),
        },
    })

    receipt = {
        "task": "BT-79: Greystone opt-in PIE visual smoke driver",
        "run_token": get_run_token(),
        "result": "PASS" if overall_passed else "FAIL",
        "accepted": overall_passed,
        "map": MAP_PATH,
        "source_hashes": STATE["source_hashes"],
        "criteria": STATE["criteria"],
        "observations": observations,
        "visual_art_judgment": {
            "status": "PENDING_OWNER_INSPECTION",
            "scope": "Owner visual art inspection only",
            "note": (
                "Automated smoke verifies runtime retarget attachment, hidden source mannequin, "
                "continuous log monitoring, zero GetMainAnimBP errors, and CVar restoration. Visual "
                "aesthetics, cape/shoulder mesh deformation, clipping, and animation blending require "
                "direct Owner inspection in PIE."
            ),
        },
        "failure": STATE["failure"],
        "timestamp_utc": time.time(),
    }

    try:
        receipt_path = get_receipt_path()
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        temp_receipt = receipt_path.with_suffix(receipt_path.suffix + ".tmp")
        temp_receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp_receipt.replace(receipt_path)
        log("RECEIPT_WRITTEN path=%s accepted=%s" % (receipt_path, overall_passed))
    except Exception as exc:
        log_error("RECEIPT_WRITE_FAILED error=%s" % exc)

    # Structured log output
    log("RUN_TOKEN=%s" % get_run_token())
    log("MAP=%s" % MAP_PATH)
    pawn_obs = observations.get("possessed_pawn", {})
    log("POSSESSED_PAWN class=%s path=%s" % (pawn_obs.get("class", "None"), pawn_obs.get("path", "None")))
    src_obs = observations.get("source_mesh", {})
    log("SOURCE_MESH component=%s hidden=%s mesh=%s anim=%s tick=%s" % (
        src_obs.get("component_name", "None"),
        1 if src_obs.get("hidden_in_game") else 0,
        src_obs.get("mesh_asset_path", "None"),
        src_obs.get("anim_class_path", "None"),
        src_obs.get("tick_option", "None"),
    ))
    vis_obs = observations.get("visible_mesh", {})
    log("VISIBLE_MESH component=%s visible=%s mesh=%s anim=%s parent=%s" % (
        vis_obs.get("component_name", "None"),
        1 if vis_obs.get("visible") else 0,
        vis_obs.get("mesh_asset_path", "None"),
        vis_obs.get("anim_class_path", "None"),
        vis_obs.get("parent_component", "None"),
    ))
    log("LOG_MONITORED bytes=%d reads=%d continuous=%d" % (
        STATE["total_bytes_read"],
        STATE["log_read_count"],
        1 if STATE["criteria"]["log_monitored_continuous"] else 0,
    ))
    log("GET_MAIN_ANIM_BP_ERRORS count=%d" % STATE["get_main_anim_bp_errors"])
    log("CLEANUP cvar_restored=%d readback_value=%s" % (
        1 if STATE["criteria"]["cvar_restored_zero"] else 0,
        observations.get("cvar_readback_value", "UNVERIFIED"),
    ))
    log("VISUAL_ART_JUDGMENT status=PENDING_OWNER_INSPECTION owner_only=1")
    log("RESULT=%s reason=%s" % ("PASS" if overall_passed else "FAIL", STATE["failure"] or "all_smoke_criteria_verified"))

    # End PIE session safely
    try:
        editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        if editor_subsystem:
            editor_subsystem.editor_request_end_play()
    except Exception as exc:
        log_error("END_PIE_REQUEST_FAILED error=%s" % exc)


def verify_components(pawn):
    log("VERIFYING_COMPONENTS pawn=%s" % pawn.get_path_name())
    mesh_components = pawn.get_components_by_class(unreal.SkeletalMeshComponent)
    source_comp = None
    visual_comp = None

    for comp in mesh_components:
        comp_name = comp.get_name()
        if comp_name == SOURCE_MESH_NAME:
            source_comp = comp
        elif comp_name == VISIBLE_COMPONENT_NAME:
            visual_comp = comp

    # Fallback for source mesh: character's primary mesh
    if source_comp is None:
        try:
            primary_mesh = pawn.get_editor_property("mesh")
            if primary_mesh:
                source_comp = primary_mesh
        except Exception:
            pass

    if source_comp is None:
        fail("source mesh component CharacterMesh0 not found on pawn")
        return False

    if visual_comp is None:
        fail("visible component GreystoneRuntimeVisual not found on pawn")
        return False

    # 1. Verify Source Mesh (CharacterMesh0)
    # Must be hidden in game, exact canonical mannequin mesh path, exact ABP_CombatCharacter_C anim class path, AlwaysTickPoseAndRefreshBones
    src_hidden = bool(source_comp.get_editor_property("hidden_in_game"))
    src_mesh_obj = source_comp.get_editor_property("skeletal_mesh_asset")
    src_mesh_path = src_mesh_obj.get_path_name() if src_mesh_obj else ""
    src_anim_inst = source_comp.get_anim_instance()
    src_anim_class_path = src_anim_inst.get_class().get_path_name() if src_anim_inst else ""
    src_tick_opt = str(source_comp.get_editor_property("visibility_based_anim_tick_option"))
    src_tick_normalized = src_tick_opt.upper().replace("_", "")

    STATE["observations"]["source_mesh"] = {
        "component_name": source_comp.get_name(),
        "hidden_in_game": src_hidden,
        "mesh_asset_path": src_mesh_path,
        "anim_class_path": src_anim_class_path,
        "tick_option": src_tick_opt,
    }

    if not src_hidden:
        fail("CharacterMesh0 is not hidden in game (bHiddenInGame=false)")
        return False

    if src_mesh_path not in ALLOWED_SOURCE_MESH_PATHS:
        fail("CharacterMesh0 skeletal mesh exact path mismatch: %s not in %s" % (src_mesh_path, ALLOWED_SOURCE_MESH_PATHS))
        return False

    if src_anim_class_path != EXPECTED_SOURCE_ANIM_CLASS_PATH:
        fail("CharacterMesh0 anim class exact path mismatch: %s != %s" % (src_anim_class_path, EXPECTED_SOURCE_ANIM_CLASS_PATH))
        return False

    if "ALWAYSTICKPOSEANDREFRESHBONES" not in src_tick_normalized:
        fail("CharacterMesh0 tick option is not AlwaysTickPoseAndRefreshBones: %s" % src_tick_opt)
        return False

    STATE["criteria"]["source_mesh_hidden"] = True

    # 2. Verify Visible Component (GreystoneRuntimeVisual)
    # Must be visible, not hidden in game, attached to CharacterMesh0, exact Greystone mesh path, exact ABP_Greystone_RuntimeRetarget_C anim class path
    vis_hidden = bool(visual_comp.get_editor_property("hidden_in_game"))
    vis_visible = bool(visual_comp.get_editor_property("visible"))
    vis_mesh_obj = visual_comp.get_editor_property("skeletal_mesh_asset")
    vis_mesh_path = vis_mesh_obj.get_path_name() if vis_mesh_obj else ""
    vis_anim_inst = visual_comp.get_anim_instance()
    vis_anim_class_path = vis_anim_inst.get_class().get_path_name() if vis_anim_inst else ""
    attach_parent = visual_comp.get_attach_parent()
    parent_name = attach_parent.get_name() if attach_parent else ""

    STATE["observations"]["visible_mesh"] = {
        "component_name": visual_comp.get_name(),
        "hidden_in_game": vis_hidden,
        "visible": vis_visible,
        "mesh_asset_path": vis_mesh_path,
        "anim_class_path": vis_anim_class_path,
        "parent_component": parent_name,
    }

    if vis_hidden or not vis_visible:
        fail("GreystoneRuntimeVisual is not visible (hidden_in_game=%s visible=%s)" % (vis_hidden, vis_visible))
        return False

    if vis_mesh_path != EXPECTED_VISIBLE_MESH_PATH:
        fail("GreystoneRuntimeVisual mesh exact path mismatch: %s != %s" % (vis_mesh_path, EXPECTED_VISIBLE_MESH_PATH))
        return False

    if vis_anim_class_path != EXPECTED_VISIBLE_ANIM_CLASS_PATH:
        fail("GreystoneRuntimeVisual anim class exact path mismatch: %s != %s" % (vis_anim_class_path, EXPECTED_VISIBLE_ANIM_CLASS_PATH))
        return False

    if parent_name != source_comp.get_name():
        fail("GreystoneRuntimeVisual is not attached to CharacterMesh0 (parent=%s)" % parent_name)
        return False

    STATE["criteria"]["runtime_visual_visible"] = True
    log("COMPONENTS_VERIFIED source_hidden=1 visual_visible=1")
    return True


def tick(delta_seconds):
    try:
        now = time.monotonic()

        # Periodically scan log stream
        if now - STATE["last_log_check"] >= 0.25:
            read_and_scan_log()
            STATE["last_log_check"] = now

        phase = STATE["phase"]

        # Phase: waiting for PIE game world
        if phase == "waiting_for_pie":
            world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
            if world:
                raw_world_name = world.get_name()
                normalized_name = normalize_world_name(raw_world_name)
                # Per [X-2585]: exact normalized identity match against 'L_SevarogArena' (no substring)
                if normalized_name != EXPECTED_NORMALIZED_MAP_NAME:
                    fail("unexpected PIE world (normalized '%s' != '%s', raw '%s')" % (
                        normalized_name, EXPECTED_NORMALIZED_MAP_NAME, raw_world_name
                    ))
                    return
                log("PIE_WORLD_FOUND raw=%s normalized=%s" % (raw_world_name, normalized_name))
                STATE["phase"] = "waiting_for_possession"
                STATE["started_at"] = now
            elif now - STATE["started_at"] >= 15.0:
                fail("timeout waiting for PIE world to start (15s)")
            return

        # Phase: waiting for player possession of BP_GreystoneERPlayer_C
        if phase == "waiting_for_possession":
            world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
            if not world:
                fail("PIE game world lost while waiting for possession")
                return

            raw_world_name = world.get_name()
            normalized_name = normalize_world_name(raw_world_name)
            if normalized_name != EXPECTED_NORMALIZED_MAP_NAME:
                fail("PIE world identity mismatch during possession: normalized '%s' != '%s'" % (
                    normalized_name, EXPECTED_NORMALIZED_MAP_NAME
                ))
                return

            pc = unreal.GameplayStatics.get_player_controller(world, 0)
            if not pc:
                if now - STATE["started_at"] >= 15.0:
                    fail("timeout waiting for PlayerController 0")
                return

            pawn = pc.get_controlled_pawn() if hasattr(pc, "get_controlled_pawn") else (pc.get_pawn() if hasattr(pc, "get_pawn") else None)
            if not pawn:
                if now - STATE["started_at"] >= 15.0:
                    fail("timeout waiting for pawn possession")
                return

            pawn_class_path = pawn.get_class().get_path_name()
            # Replacement happens on next tick after initial spawn.
            if pawn_class_path == EXPECTED_PAWN_CLASS_PATH:
                log("POSSESSED_EXPECTED_PAWN path=%s" % pawn_class_path)
                STATE["pc"] = pc
                STATE["pawn"] = pawn
                STATE["criteria"]["exact_pawn_possessed"] = True
                STATE["observations"]["possessed_pawn"] = {
                    "class": pawn.get_class().get_name(),
                    "path": pawn_class_path,
                }

                # Verify components immediately with exact paths
                if not verify_components(pawn):
                    return

                # Check for any early GetMainAnimBP errors
                read_and_scan_log()
                if STATE["get_main_anim_bp_errors"] > 0:
                    fail("GetMainAnimBP error detected (count=%d)" % STATE["get_main_anim_bp_errors"])
                    return

                # Settle for 1.5 seconds to observe continuous animation ticks and log streams
                STATE["phase"] = "observation_settle"
                STATE["observation_settle_start"] = now
            elif now - STATE["started_at"] >= 15.0:
                fail("fail closed: possessed pawn path is %s, expected %s" % (pawn_class_path, EXPECTED_PAWN_CLASS_PATH))
            return

        # Phase: observation settle (~1.5 second to observe continuous ticks)
        if phase == "observation_settle":
            elapsed = now - STATE["observation_settle_start"]
            read_and_scan_log()
            if STATE["get_main_anim_bp_errors"] > 0:
                fail("GetMainAnimBP error detected during animation observation (count=%d)" % STATE["get_main_anim_bp_errors"])
                return

            if elapsed >= 1.5:
                finish("PASS")
            return

    except Exception as exc:
        log_error("UNHANDLED_DRIVER_EXCEPTION error=%s\n%s" % (exc, traceback.format_exc()))
        fail("unhandled driver exception: " + str(exc))


# Entry point when executed via -ExecutePythonScript
try:
    log("INITIALIZING_GREYSTONE_VISUAL_SMOKE_DRIVER token=%s" % get_run_token())

    # Pre-validate mandatory environment variables per [X-2584] and [X-2585]
    get_run_token()
    get_log_path()
    get_receipt_path()
    STATE["source_hashes"] = get_source_hashes()

    # Keep Python alive during PIE
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    STATE["keep_python_alive"] = True

    # 1. Enable opt-in CVar for test route
    unreal.SystemLibrary.execute_console_command(None, "rpg.GreystonePlayerTestPawn 1")
    log("CVAR_OPT_IN_SET rpg.GreystonePlayerTestPawn=1")

    # 2. Ensure L_SevarogArena is loaded
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    log("LEVEL_LOADED map=%s" % MAP_PATH)

    # 3. Register Slate post-tick callback
    STATE["started_at"] = time.monotonic()
    STATE["last_log_check"] = time.monotonic()
    STATE["phase"] = "waiting_for_pie"
    HANDLE = unreal.register_slate_post_tick_callback(tick)
    if not HANDLE:
        raise RuntimeError("failed to register Slate post-tick callback")

    # 4. Request PIE
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
    log("PIE_REQUEST_BEGIN_PLAY requested")

except Exception as start_exc:
    log_error("STARTUP_FAILED error=%s\n%s" % (start_exc, traceback.format_exc()))
    cleanup()
    raise
