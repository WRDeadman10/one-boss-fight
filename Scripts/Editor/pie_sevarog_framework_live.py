"""C-1254a/C-1258a: Sevarog framework driver with bounded transient self-test and Lead full-run mode."""
import os
import sys
import time
import uuid
import traceback
import math
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(unreal.Paths.project_dir()) / "Scripts" / "Editor"))
import pie_lead_common as plc

LOG = "[SevarogLive] "
PROFILE_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Draft"
ENCOUNTER_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter.DA_Sevarog_Framework_Encounter"
DEFAULT_EXPECTED_CARDS = (
    "Move_Sevarog_Swing1_Medium",
    "Move_Sevarog_Swing2_Medium",
    "Move_Sevarog_Swing3_Slow",
    "Move_Sevarog_Speedburst",
)


def expected_cards_from_environment(environ=None):
    """Allow Lead to run a bounded explicit card list without editing this driver."""
    environ = os.environ if environ is None else environ
    raw = environ.get("SEVAROG_LIVE_CARDS", "").strip()
    if not raw:
        return DEFAULT_EXPECTED_CARDS
    cards = tuple(part.strip() for part in raw.replace("+", ",").split(",") if part.strip())
    if not cards or len(set(cards)) != len(cards):
        raise ValueError("SEVAROG_LIVE_CARDS must contain unique comma- or +-separated move IDs")
    allowed = set(DEFAULT_EXPECTED_CARDS) | {
        "Move_Sevarog_Ultimate_Swing_120fps_C1277",
        "Move_Sevarog_Subjugation_C1277",
        "Move_Sevarog_Soul_Siphon_C1277",
    }
    unknown = [card for card in cards if card not in allowed]
    if unknown:
        raise ValueError("SEVAROG_LIVE_CARDS contains unsupported IDs: " + ",".join(unknown))
    return cards


EXPECTED_CARDS = expected_cards_from_environment()
COMBO_SOURCE = "Move_Sevarog_Speedburst"
COMBO_FOLLOWUP = None
OUT_ROOT = "D:/FightVideo/sevarog_live"
SHOT_WIDTH, SHOT_HEIGHT = 960, 540
STATE = {"done": False, "world_requested": False, "started_at": 0.0, "next_index": 0,
         "active_id": None, "wait_started": 0.0, "pawn_wait": 0.0, "next_due": 0.0, "final_due": 0.0, "last_missing": 0.0,
         "combo_seen": False, "reason": "not_started", "shots": 0, "attempt_due": 0.0, "capture": None,
         "ambient_encounter_isolated": False, "trace_geometry_enabled": False,
         "clip_trace_frame": 0, "clip_trace_state": None, "clip_trace_done": set(),
         "viewport_prewarm_started": False, "viewport_prewarm_complete": False, "viewport_prewarm_failed": False}
STATE.update({"autonomous_selected": None, "autonomous_started_at": None, "autonomous_polls": 0})
STATE.update({"deferred_started_at": None, "deferred_polls": 0})
STATE.update({"probe_index": 0, "probe_attempt_due": 0.0, "probe_wait_started": None, "probe_starts": 0})
# X26-IMPL-B1 T4 (X-1965/X-1967): post-phase-transition selector probes. S6 and S8 live in disjoint range bands,
# so after the Phase_2 latch the driver places the player in each band and requests one selector decision per band;
# every decision logs its full candidate/refusal traces natively (StartSelectedCardForTest).
PHASE2_PROBES = (("s6_band", 115.0), ("s8_band", 400.0))
STATE.update({"dodge_out_due": None, "dodge_out_started_at": None, "dodge_out_done": False})
STATE.update({"s7_started_at": None, "s7_release_sample_due": None, "s7_release_sample_done": False})
STATE.update({"spawn_ready": False, "nav_pending_since": None, "nav_pending_log_at": 0.0})
STATE.update({"pack_style_wait_started": None, "pack_style_wait_log_at": 0.0, "pack_style_ready": False})
HANDLE = None


def log(message):
    unreal.log(LOG + str(message))


def read_property(obj, *names):
    last_error = None
    for name in names:
        try:
            return obj.get_editor_property(name)
        except Exception as error:
            last_error = error
    raise RuntimeError("cannot read reflected property %s: %s" % (names, last_error))


def pack_style_status(pawn):
    """Read the pack's combat-style initialization witness before the test changes target health."""
    try:
        components = pawn.get_components_by_class(unreal.ActorComponent)
    except Exception as error:
        return False, "components_unreadable:%s" % str(error)[:120]
    combat = next((component for component in components
                   if component.get_class().get_name() == "BP_CombatComponent_C"), None)
    if combat is None:
        return False, "BP_CombatComponent_C_missing"
    try:
        style = read_property(combat, "current_combat_style", "CurrentCombatStyle")
    except Exception as error:
        return False, "CurrentCombatStyle_unreadable:%s" % str(error)[:120]
    if style is None:
        return False, "CurrentCombatStyle_None"
    try:
        style_name = style.get_name()
    except Exception:
        style_name = str(style)
    return True, str(style_name)


def wait_for_pack_style(pawn):
    """Wait boundedly for the pack's delayed equipment/style setup to finish."""
    ready, detail = pack_style_status(pawn)
    if ready:
        STATE["pack_style_ready"] = True
        log("PACK_STYLE_READY component=BP_CombatComponent_C style=%s targetHealthWrite=after_style" % detail)
        return True
    now = time.perf_counter()
    if STATE["pack_style_wait_started"] is None:
        STATE["pack_style_wait_started"] = now
        STATE["pack_style_wait_log_at"] = now
    elapsed = now - STATE["pack_style_wait_started"]
    if elapsed >= 30.0:
        raise RuntimeError("pack combat style did not initialize within 30 seconds: " + detail)
    if now >= STATE["pack_style_wait_log_at"]:
        log("PACK_STYLE_WAIT elapsed=%.1f detail=%s" % (elapsed, detail))
        STATE["pack_style_wait_log_at"] = now + 2.0
    return False


def profile_report():
    profile = unreal.load_asset(PROFILE_PATH)
    if profile is None:
        raise RuntimeError("authored framework profile did not load: " + PROFILE_PATH)
    library = getattr(unreal, "RPGBossCardValidationLibrary", None)
    validate = getattr(library, "validate_framework_profile_report", None) if library else None
    if not callable(validate):
        raise RuntimeError("production ValidateFrameworkProfileReport bridge is unavailable")
    report = str(validate(profile))
    if report != "PASS":
        raise RuntimeError("production profile resolution refused: " + report)
    cards = profile.get_editor_property("cards")
    if not cards:
        raise RuntimeError("resolved profile has no candidate cards")
    move_ids = []
    for candidate in cards:
        card = read_property(candidate, "card", "Card")
        if card is None:
            raise RuntimeError("profile contains a null candidate card")
        spec = read_property(card, "spec", "Spec")
        move_id = str(read_property(spec, "move_id", "MoveId"))
        move_ids.append(move_id)
    missing = [move_id for move_id in EXPECTED_CARDS if move_id not in move_ids]
    if missing:
        raise RuntimeError("profile is missing expected combo cards: " + ",".join(missing))
    log("PROFILE PASS path=%s candidates=%d move_ids=%s" %
        (PROFILE_PATH, len(move_ids), ",".join(move_ids)))
    nodes = read_property(profile, "combo_nodes", "ComboNodes")
    node_moves = {}
    for node in nodes:
        node_id = str(read_property(node, "node_id", "NodeId"))
        node_moves[node_id] = str(read_property(node, "move_id", "MoveId"))
    source_nodes = [node for node in nodes if str(read_property(node, "move_id", "MoveId")) == COMBO_SOURCE]
    if not source_nodes:
        raise RuntimeError("profile combo graph has no node for " + COMBO_SOURCE)
    edges = read_property(source_nodes[0], "edges", "Edges")
    if not edges:
        raise RuntimeError("profile combo node has no follow-up edge for " + COMBO_SOURCE)
    target_node = str(read_property(edges[0], "to_node", "ToNode"))
    followup = node_moves.get(target_node)
    if not followup:
        raise RuntimeError("profile combo edge points to missing node " + target_node)
    if followup not in move_ids:
        raise RuntimeError("combo follow-up card is missing from profile candidates: " + followup)
    log("PROFILE COMBO_NODES count=%d source=%s followup=%s target_node=%s" %
        (len(nodes), COMBO_SOURCE, followup, target_node))
    return profile, followup


def check_bridge_reflection():
    deferred_selection = os.environ.get("SEVAROG_LIVE_DEFERRED_SELECTION") == "1"
    cls = getattr(unreal, "RPGFrameworkBossCharacter", None)
    if cls is None:
        raise RuntimeError("RPGFrameworkBossCharacter Python class is unavailable")
    init_name = "initialize_selected_encounter_for_test" if deferred_selection else "initialize_with_profile_for_test"
    init = getattr(cls, init_name, None)
    spawn = getattr(cls, "spawn_framework_boss_for_test", None)
    if not callable(init) or not callable(spawn):
        raise RuntimeError("test bridge UFUNCTIONs are not exposed to Python")
    if not deferred_selection:
        start = getattr(cls, "start_card_for_test", None)
        combo_start = getattr(cls, "start_combo_for_test", None)
        if not callable(start) or not callable(combo_start):
            raise RuntimeError("standalone test-start UFUNCTIONs are not exposed to Python")
    if deferred_selection:
        moves_cls = getattr(unreal, "RPGPlayerMovesSubsystem", None)
        selection_cls = getattr(unreal, "RPGEncounterSelectionSubsystem", None)
        if not callable(getattr(moves_cls, "get_for_world", None)) or not callable(getattr(selection_cls, "get_for_world", None)):
            raise RuntimeError("deferred selection subsystem accessors are not exposed to Python")
        if not callable(getattr(moves_cls, "activate_deferred_selection_for_test", None)):
            raise RuntimeError("deferred selection activation hook is not exposed to Python")
        if not callable(getattr(cls, "get_outcome_for_test", None)) or not callable(getattr(cls, "get_current_phase_for_test", None)):
            raise RuntimeError("deferred passive outcome/phase readback UFUNCTIONs are not exposed to Python")
    if os.environ.get("SEVAROG_LIVE_AUTONOMOUS") == "1" and not deferred_selection:
        if not callable(getattr(cls, "start_selected_card_for_test", None)) or not callable(getattr(cls, "get_outcome_for_test", None)):
            raise RuntimeError("autonomous selector bridge UFUNCTIONs are not exposed to Python")
    if os.environ.get("SEVAROG_LIVE_PHASE2_PROBES") == "1":
        if deferred_selection:
            raise RuntimeError("SEVAROG_LIVE_PHASE2_PROBES cannot run in deferred production-Tick mode")
        if os.environ.get("SEVAROG_LIVE_AUTONOMOUS") != "1":
            raise RuntimeError("SEVAROG_LIVE_PHASE2_PROBES=1 requires SEVAROG_LIVE_AUTONOMOUS=1")
        if not callable(getattr(cls, "get_current_phase_for_test", None)):
            raise RuntimeError("phase2 probe bridge UFUNCTION get_current_phase_for_test is not exposed to Python")
    if not callable(getattr(cls, "get_navigation_result_for_test", None)):
        raise RuntimeError("navigation-result summary UFUNCTION is not exposed to Python")
    log("LIVE_API PASS mode=%s init=%s test_start_apis=%d spawn_framework_boss_for_test=1" %
        ("deferred_selection" if deferred_selection else "standalone_profile", init_name,
         0 if deferred_selection else 1))


def autonomous_time_cap():
    try:
        requested = int(os.environ.get("SEVAROG_LIVE_AUTONOMOUS_SECONDS", "45"))
    except (TypeError, ValueError):
        requested = 45
    return max(5, min(90, requested))


def validate_navigation_identity(summary, expected_route, expected_generation):
    text = str(summary).strip()
    route_marker = "route="
    generation_marker = " generation="
    route_start = text.find(route_marker)
    generation_start = text.find(generation_marker, route_start + len(route_marker)) if route_start >= 0 else -1
    if route_start < 0 or generation_start < 0:
        raise RuntimeError("navigation summary lacks route/generation identity: " + (text or "empty"))
    route = text[route_start + len(route_marker):generation_start].strip()
    generation_text = text[generation_start + len(generation_marker):].split(" ", 1)[0]
    try:
        generation = int(generation_text)
    except (TypeError, ValueError):
        raise RuntimeError("navigation summary has invalid generation: " + generation_text)
    if route != str(expected_route).strip() or generation != int(expected_generation):
        raise RuntimeError("navigation identity mismatch expected_route=%s expected_generation=%s actual_route=%s actual_generation=%s" %
                           (expected_route, expected_generation, route, generation))
    return route, generation


def validate_spawn_navigation(boss, profile, pawn, now):
    summary = str(boss.get_navigation_result_for_test()).strip()
    if not summary or summary in ("PENDING", "Unavailable", "None"):
        if STATE["nav_pending_since"] is None:
            STATE["nav_pending_since"] = time.perf_counter()
        elapsed = time.perf_counter() - STATE["nav_pending_since"]
        if elapsed > 15.0:
            raise RuntimeError("navigation result did not resolve within 15 seconds: " + (summary or "empty"))
        if now >= STATE["nav_pending_log_at"]:
            log("NAV_WAIT state=pending elapsed=%.2f summary=%s" % (elapsed, summary or "empty"))
            STATE["nav_pending_log_at"] = now + 2.0
        return False
    validate_navigation_identity(summary, read_property(profile, "fixture_label", "FixtureLabel"), 1)
    STATE["nav_summary"] = summary
    log("NAV_RESULT " + summary)
    controller = boss.get_controller()
    controller_match = "UNEXPOSED" if controller else "NO_CONTROLLER"
    if controller:
        try:
            get_pawn = getattr(controller, "get_pawn", None)
            if callable(get_pawn):
                controller_match = str(int(get_pawn() == boss))
        except Exception:
            controller_match = "GETTER_FAILED"
    nav_class = getattr(unreal, "RecastNavMesh", None)
    nav_actors = unreal.GameplayStatics.get_all_actors_of_class(live_world(), nav_class) if nav_class else []
    log("NAV_DIAG after_init controller=%s controller_pawn_match=%s recast_navmesh_class=%s recast_actor_count=%d; "
        "inspect [FrameworkProof] test_nav_probe, test_walk_skipped, nav request/fullPath and MoveFailed" %
        (controller.get_class().get_name() if controller else "NONE", controller_match,
         int(nav_class is not None), len(nav_actors)))
    if controller is None or controller_match == "0":
        raise RuntimeError("navigation diagnosis: spawned boss controller does not possess the selected boss (match=%s)" % controller_match)
    STATE["spawn_ready"] = True
    log("SPAWN PASS actor=%s initialPlayerDistanceCm=%.1f" %
        (boss.get_name(), (pawn.get_actor_location() - boss.get_actor_location()).length()))
    return True


def place_player_at_distance(pawn, boss, distance_cm, label):
    forward = boss.get_actor_forward_vector()
    boss_loc = boss.get_actor_location()
    pawn_loc = pawn.get_actor_location()
    target = boss_loc + forward * float(distance_cm)
    pawn.set_actor_location(unreal.Vector(target.x, target.y, pawn_loc.z), False, True)
    actual = (pawn.get_actor_location() - boss_loc).length()
    log("PHASE2_PROBE_PLACE band=%s requestedCm=%.1f actualCm=%.1f" % (label, distance_cm, actual))
    return actual


def tick_phase2_probes(boss, pawn, now):
    """After the first selected card, request one selector decision per disjoint band (115 cm, 400 cm).

    StartSelectedCardForTest returns NAME_None while the executor is busy or the selector refuses, and
    each accepted request logs the full candidate/refusal trace rows the X26-P2 verifier reads. Bounded:
    35 s per probe, then the run fails loudly."""
    if STATE["probe_index"] >= len(PHASE2_PROBES):
        log("AUTONOMOUS_RESULT route=framework-proof-selector selected=%s outcome=Phase2ProbesComplete starts=%d polls=%d elapsed=%.3f saves=0" %
            (STATE["autonomous_selected"], 1 + STATE["probe_starts"], STATE["autonomous_polls"], now - STATE["autonomous_started_at"]))
        finish("phase2 selector probes complete: S6-band and S8-band decisions traced")
        return
    if now < STATE["probe_attempt_due"]:
        return
    STATE["probe_attempt_due"] = now + 0.5
    label, distance = PHASE2_PROBES[STATE["probe_index"]]
    if STATE["probe_wait_started"] is None:
        STATE["probe_wait_started"] = now
    # Probe only after the Phase_2 latch: a pre-latch decision would be a Phase_1 sample, not P2 evidence.
    phase = str(boss.get_current_phase_for_test()).strip()
    if phase != "Phase_2":
        if now - STATE["probe_wait_started"] > 35.0:
            raise RuntimeError("phase2 probe waited 35 s without the Phase_2 latch (phase=%s)" % phase)
        return
    place_player_at_distance(pawn, boss, distance, label)
    selected = str(boss.start_selected_card_for_test()).strip()
    if selected and selected not in ("None", "NAME_None"):
        STATE["probe_starts"] += 1
        log("PHASE2_PROBE index=%d band=%s distanceCm=%.1f selected=%s" % (STATE["probe_index"], label, distance, selected))
        STATE["probe_index"] += 1
        STATE["probe_wait_started"] = None
        STATE["probe_attempt_due"] = now + 3.0  # one card window before the next band probe
        return
    if now - STATE["probe_wait_started"] > 35.0:
        raise RuntimeError("phase2 probe timed out band=%s distanceCm=%.1f" % (label, distance))


def tick_autonomous_selector(world, boss, now):
    if STATE["autonomous_started_at"] is None:
        selected = boss.start_selected_card_for_test()
        selected_name = str(selected).strip()
        if not selected_name or selected_name in ("None", "NAME_None"):
            outcome = str(boss.get_outcome_for_test()).strip()
            log("AUTONOMOUS_RESULT route=framework-proof-selector selected=0 refusal=NoSelectionOrStart outcome=%s starts=0 saves=0" % outcome)
            finish("autonomous selector did not start a card")
            return
        STATE["autonomous_selected"] = selected_name
        STATE["autonomous_started_at"] = now
        STATE["active_id"] = selected_name
        log("AUTONOMOUS_START route=framework-proof-selector selected=%s phase_generation=see_native_selection_receipt card_cap=1 time_cap_seconds=%d saves=0" %
            (selected_name, autonomous_time_cap()))
    STATE["autonomous_polls"] += 1
    outcome = str(boss.get_outcome_for_test()).strip()
    if os.environ.get("SEVAROG_LIVE_PHASE2_PROBES") == "1" and outcome == "Active":
        pawn = unreal.GameplayStatics.get_player_controller(world, 0).get_controlled_pawn()
        tick_phase2_probes(boss, pawn, now)
        if STATE["done"]:
            return
    if outcome in ("BossDefeated", "Succeeded", "Failed"):
        log("AUTONOMOUS_RESULT route=framework-proof-selector selected=%s outcome=%s starts=1 polls=%d elapsed=%.3f saves=0" %
            (STATE["autonomous_selected"], outcome, STATE["autonomous_polls"], now - STATE["autonomous_started_at"]))
        finish("autonomous selector reached terminal outcome: " + outcome)
        return
    elapsed = now - STATE["autonomous_started_at"]
    if elapsed >= autonomous_time_cap():
        log("AUTONOMOUS_RESULT route=framework-proof-selector selected=%s outcome=TimeCap activeState=%s starts=1 polls=%d elapsed=%.3f saves=0" %
            (STATE["autonomous_selected"], outcome, STATE["autonomous_polls"], elapsed))
        finish("autonomous selector bounded time cap reached without terminal outcome")


def tick_deferred_selector(world, boss, now):
    """Passively observe the actual production Tick selector in deferred mode.

    This path intentionally does not call any test-start API. Native
    `[CARD_DECISION]` / `decision` diagnostics are the selection evidence.
    """
    if STATE["deferred_started_at"] is None:
        STATE["deferred_started_at"] = now
        log("DEFERRED_TICK_MONITOR route=selected-framework-production-tick selector_trigger=none test_start_calls=0 saves=0 time_cap_seconds=%d" %
            autonomous_time_cap())
    STATE["deferred_polls"] += 1
    outcome = str(boss.get_outcome_for_test()).strip()
    phase_api = getattr(boss, "get_current_phase_for_test", None)
    phase = str(phase_api()).strip() if callable(phase_api) else "unavailable"
    if STATE["deferred_polls"] == 1 or STATE["deferred_polls"] % 20 == 0:
        log("DEFERRED_TICK_POLL polls=%d outcome=%s phase=%s" % (STATE["deferred_polls"], outcome, phase))
    if outcome in ("BossDefeated", "Succeeded", "Failed"):
        log("DEFERRED_TICK_RESULT route=selected-framework-production-tick outcome=%s phase=%s polls=%d elapsed=%.3f saves=0" %
            (outcome, phase, STATE["deferred_polls"], now - STATE["deferred_started_at"]))
        finish("deferred production Tick reached terminal outcome: " + outcome)
        return
    elapsed = now - STATE["deferred_started_at"]
    if elapsed >= autonomous_time_cap():
        log("DEFERRED_TICK_RESULT route=selected-framework-production-tick outcome=TimeCap activeState=%s phase=%s polls=%d elapsed=%.3f saves=0" %
            (outcome, phase, STATE["deferred_polls"], elapsed))
        finish("deferred production Tick bounded time cap reached")


def live_world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def finish(reason):
    global HANDLE
    if STATE["done"]:
        return
    STATE["done"] = True
    STATE["reason"] = str(reason)
    if HANDLE:
        try:
            unreal.unregister_slate_post_tick_callback(HANDLE)
        except Exception:
            pass
        HANDLE = None
    log("finished: %s shots=%d" % (STATE["reason"], STATE["shots"]))
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception as error:
        log("END_PIE request_failed=%s" % error)


def spawn_live_boss(world, pawn, profile):
    style_ready, style_detail = pack_style_status(pawn)
    if not style_ready:
        raise RuntimeError("refusing test boss initialization before pack combat style: " + style_detail)
    cls = getattr(unreal, "RPGFrameworkBossCharacter", None)
    spawn = getattr(cls, "spawn_framework_boss_for_test", None) if cls else None
    if cls is None or not callable(spawn):
        raise RuntimeError("SpawnFrameworkBossForTest bridge is unavailable")
    player_loc = pawn.get_actor_location()
    player_forward = pawn.get_actor_forward_vector()
    spawn_loc = player_loc + player_forward * 160.0
    spawn_rot = unreal.Rotator(0.0, pawn.get_actor_rotation().yaw + 180.0, 0.0)
    boss = spawn(world, cls, spawn_loc, spawn_rot)
    if boss is None:
        raise RuntimeError("SpawnFrameworkBossForTest refused transient Sevarog spawn")
    unreal.SystemLibrary.execute_console_command(world, "rpg.BossProofSkipInitialWalk 1")
    log("TEST_HOOK skip_initial_walk=1 scope=standalone_test_authorized_target_in_profile_band")
    place_player_for_card(profile, pawn, boss, EXPECTED_CARDS[0], "before_initialize")
    if os.environ.get("SEVAROG_LIVE_DEFERRED_SELECTION") == "1":
        # Selection is an explicit opt-in so existing profile/X26 arms do not
        # depend on the separate BK-3 authored asset being present.
        definition = unreal.load_asset(ENCOUNTER_PATH)
        if definition is None:
            boss.destroy_actor()
            raise RuntimeError("framework encounter definition did not load: " + ENCOUNTER_PATH)
        selection_cls = getattr(unreal, "RPGEncounterSelectionSubsystem", None)
        selection = selection_cls.get_for_world(world) if selection_cls and callable(getattr(selection_cls, "get_for_world", None)) else None
        clear_selection = getattr(selection, "clear_selected_definition", None) if selection else None
        if not callable(clear_selection):
            boss.destroy_actor()
            raise RuntimeError("selection subsystem clear bridge is unavailable")
        clear_selection()
        unreal.SystemLibrary.execute_console_command(world, "rpg.EncounterDefinition %s" % ENCOUNTER_PATH)
        unreal.SystemLibrary.execute_console_command(world, "rpg.FrameworkEncounterSelection 1")
        moves_cls = getattr(unreal, "RPGPlayerMovesSubsystem", None)
        moves = moves_cls.get_for_world(world) if moves_cls and callable(getattr(moves_cls, "get_for_world", None)) else None
        activate = getattr(moves, "activate_deferred_selection_for_test", None) if moves else None
        if not callable(activate):
            boss.destroy_actor()
            raise RuntimeError("ActivateDeferredSelectionForTest bridge is unavailable")
        try:
            activated = activate()
        except Exception as error:
            boss.destroy_actor()
            raise RuntimeError("deferred selected-route activation raised: %s" % error)
        ok = activated[0] if isinstance(activated, tuple) and activated else activated
        if not ok:
            diagnostic_api = getattr(selection, "get_selection_diagnostic", None)
            diagnostic = str(diagnostic_api()) if callable(diagnostic_api) else "unavailable"
            snapshot_api = getattr(moves, "build_encounter_parity_snapshot", None)
            snapshot = str(snapshot_api()) if callable(snapshot_api) else "unavailable"
            boss.destroy_actor()
            reason = "activation_refused:%r selection_diagnostic=%s snapshot=%s" % (activated, diagnostic, snapshot)
            log("DEFERRED_TICK_RESULT route=selected-framework-production-tick outcome=ActivationRefused reason=%s test_start_calls=0 saves=0" % reason.replace(" ", "_"))
            # Avoid raising through/unregistering this editor callback: Unreal's
            # Python plugin can fault during callback teardown. The bounded runner
            # records the result marker, then closes the editor normally.
            STATE["done"] = True
            STATE["reason"] = reason
            return None
        definition_hash = str(definition.get_editor_property("stable_manifest_hash"))
        log("DEFERRED_SELECTION route=framework definition=%s hash=%s pack_isolated_before_spawn=1 framework_spawn_before_selection=1 selector_flag=1 test_start_calls=0" %
            (ENCOUNTER_PATH, definition_hash))
    else:
        # This reflected UFUNCTION is an instance method. Resolve it on the
        # spawned actor so Python binds `self` before passing the profile/pawn.
        init = getattr(boss, "initialize_with_profile_for_test", None)
        if not callable(init):
            boss.destroy_actor()
            raise RuntimeError("InitializeWithProfileForTest bridge is unavailable")
        try:
            initialized = init(profile, pawn)
        except Exception as error:
            boss.destroy_actor()
            raise RuntimeError("InitializeWithProfileForTest call failed: %s" % error)
        error_text = str(initialized[1]) if isinstance(initialized, tuple) and len(initialized) > 1 else ""
        ok = initialized[0] if isinstance(initialized, tuple) and initialized else initialized
        if isinstance(ok, str):
            error_text, ok = ok, not ok
        if not ok:
            boss.destroy_actor()
            raise RuntimeError("profile initialization refused: %s" % error_text)
    apply_test_health_fraction(boss, world)
    STATE["nav_pending_since"] = time.perf_counter()
    STATE["nav_pending_log_at"] = plc.game_time(world)
    STATE["spawn_ready"] = False
    STATE["started_at"] = plc.game_time(world)
    log("NAV_WAIT state=initializing summary=%s" % boss.get_navigation_result_for_test())
    return boss


def place_player_for_card(profile, pawn, boss, move_id, stage="before_request"):
    card_spec = None
    for candidate in read_property(profile, "cards", "Cards"):
        card = read_property(candidate, "card", "Card")
        spec = read_property(card, "spec", "Spec") if card else None
        if spec and str(read_property(spec, "move_id", "MoveId")) == move_id:
            card_spec = spec
            break
    if card_spec is None:
        raise RuntimeError("profile has no move spec for requested card " + move_id)
    minimum = float(read_property(card_spec, "min_range_cm", "MinRangeCm"))
    maximum = float(read_property(card_spec, "max_range_cm", "MaxRangeCm"))
    requested_by_card = {
        "Move_Sevarog_Speedburst": 450.0,
        "Move_Sevarog_Ultimate_Swing_120fps_C1277": 120.0,
        "Move_Sevarog_Subjugation_C1277": 600.0,
        "Move_Sevarog_Soul_Siphon_C1277": 400.0,
    }
    requested = requested_by_card.get(move_id, min(max(110.0, minimum), maximum))
    if requested < minimum or requested > maximum:
        raise RuntimeError("requested player range %.1f is outside %s card band %.1f..%.1f cm" %
                            (requested, move_id, minimum, maximum))
    forward = boss.get_actor_forward_vector()
    boss_loc = boss.get_actor_location()
    pawn_loc = pawn.get_actor_location()
    target = boss_loc + forward * requested
    target = unreal.Vector(target.x, target.y, pawn_loc.z)
    pawn.set_actor_location(target, False, True)
    actual_loc = pawn.get_actor_location()
    actual = math.hypot(actual_loc.x - boss_loc.x, actual_loc.y - boss_loc.y)
    in_band = minimum <= actual <= maximum
    relative = pawn.get_actor_location() - boss.get_actor_location()
    log("SETUP stage=%s move=%s requestedRangeCm=%.1f actualDistanceCm=%.1f cardBandCm=%.1f..%.1f inBand=%d bossYaw=%.2f targetYaw=%.2f relativeToBoss=X%.1f_Y%.1f_Z%.1f" %
        (stage, move_id, requested, actual, minimum, maximum, int(in_band),
         boss.get_actor_rotation().yaw, pawn.get_actor_rotation().yaw, relative.x, relative.y, relative.z))
    if not in_band:
        raise RuntimeError("player reposition readback is outside %s card band" % move_id)
    return actual


def apply_test_health_fraction(boss, world):
    """Set a bounded Lead-only starting fraction through the Shipping-excluded bridge."""
    raw = os.environ.get("SEVAROG_LIVE_BOSS_HEALTH_FRACTION", "").strip()
    if not raw:
        return
    if os.environ.get("SEVAROG_LIVE_DEFERRED_SELECTION") == "1":
        raise RuntimeError("test boss-health override is forbidden in deferred production-Tick mode")
    try:
        fraction = float(raw)
    except (TypeError, ValueError):
        raise RuntimeError("SEVAROG_LIVE_BOSS_HEALTH_FRACTION must be numeric")
    if not math.isfinite(fraction) or fraction <= 0.0 or fraction > 1.0:
        raise RuntimeError("SEVAROG_LIVE_BOSS_HEALTH_FRACTION must be in (0,1]")
    setter = getattr(boss, "set_boss_health_fraction_for_test", None)
    if not callable(setter):
        raise RuntimeError("Shipping-excluded boss health fraction bridge is unavailable")
    if not setter(fraction):
        raise RuntimeError("boss refused test health fraction %.6f" % fraction)
    log("TEST_HOOK boss_health_fraction=%.6f scope=standalone_test_actor" % fraction)
    if fraction <= 0.6:
        # Give the boss's own Tick the opportunity to consume the ordinary
        # phase threshold and emit its real phase_transition receipt.
        STATE["attempt_due"] = plc.game_time(world) + 0.75


def capsule_surface_distance(point, pawn, capsule):
    """3D distance from a world point to the upright player capsule surface."""
    # Use the actual capsule component center; actor location is its base/root
    # origin on character pawns and would inflate vertical clearance distances.
    center = capsule.get_world_location()
    radius = float(capsule.get_scaled_capsule_radius())
    half_height = float(capsule.get_scaled_capsule_half_height())
    dx, dy = point.x - center.x, point.y - center.y
    vertical = max(0.0, abs(point.z - center.z) - max(0.0, half_height - radius))
    return max(0.0, math.sqrt(dx * dx + dy * dy + vertical * vertical) - radius)


def trace_clip_frame(boss, pawn, world_time):
    """Opt-in test telemetry: sample both live weapon sockets every PIE frame."""
    if os.environ.get("SEVAROG_LIVE_TRACE_CLIP") != "1":
        return
    move_id = STATE.get("active_id")
    trace_state = STATE.get("clip_trace_state")
    if move_id not in ("Move_Sevarog_Swing1_Medium", "Move_Sevarog_Swing2_Medium"):
        move_id = trace_state["move"] if trace_state else None
    if move_id not in ("Move_Sevarog_Swing1_Medium", "Move_Sevarog_Swing2_Medium"):
        return
    meshes = boss.get_components_by_class(unreal.SkeletalMeshComponent)
    capsules = pawn.get_components_by_class(unreal.CapsuleComponent)
    # Framework subclasses may rename their inherited mesh; use the character's
    # first skeletal mesh just as the established PIE probes do.
    mesh = meshes[0] if meshes else None
    capsule = capsules[0] if capsules else None
    if mesh is None or capsule is None:
        raise RuntimeError("clip trace components missing: boss=%s skeletalMeshes=%s player=%s capsules=%s" %
                           (boss.get_name(), [c.get_name() for c in meshes], pawn.get_name(),
                            [c.get_name() for c in capsules]))
    anim = mesh.get_anim_instance()
    montage = anim.get_current_active_montage() if anim else None
    if montage is None:
        if trace_state and trace_state["samples"]:
            trace_state["missing_montage_ticks"] += 1
            if trace_state["missing_montage_ticks"] >= 2:
                finish_clip_trace(trace_state["move"])
        return
    if trace_state and trace_state["move"] != move_id:
        finish_clip_trace(trace_state["move"])
        trace_state = None
    position = float(anim.montage_get_position(montage))
    a = mesh.get_socket_location("weapon_r")
    b = mesh.get_socket_location("root_weapon_end_r")
    da = capsule_surface_distance(a, pawn, capsule)
    db = capsule_surface_distance(b, pawn, capsule)
    frame = STATE["clip_trace_frame"]
    STATE["clip_trace_frame"] = frame + 1
    if trace_state is None or trace_state["move"] != move_id:
        if move_id in STATE["clip_trace_done"]:
            return
        STATE["clip_trace_state"] = {"move": move_id, "samples": 0, "min_a": (float("inf"), 0.0),
                                     "min_b": (float("inf"), 0.0), "montage": montage.get_name(),
                                     "missing_montage_ticks": 0, "max_position": 0.0}
        trace_state = STATE["clip_trace_state"]
        log("CLIP_TRACE_START move=%s montage=%s requestedRangeCm=140 whole_clip=1 sample=every_PIE_frame" %
            (move_id, trace_state["montage"]))
    trace_state["samples"] += 1
    trace_state["missing_montage_ticks"] = 0
    trace_state["max_position"] = max(trace_state["max_position"], position)
    if da < trace_state["min_a"][0]:
        trace_state["min_a"] = (da, position)
    if db < trace_state["min_b"][0]:
        trace_state["min_b"] = (db, position)
    log("CLIP_TRACE_FRAME frame=%d move=%s montage=%s localSeconds=%.5f worldSeconds=%.5f "
        "weapon_r=(%.3f,%.3f,%.3f) weapon_r_capsuleSurfaceCm=%.3f "
        "root_weapon_end_r=(%.3f,%.3f,%.3f) root_weapon_end_r_capsuleSurfaceCm=%.3f "
        "capsuleCenter=(%.3f,%.3f,%.3f) capsuleRadiusCm=%.3f capsuleHalfHeightCm=%.3f" %
        (frame, move_id, montage.get_name(), position, world_time,
         a.x, a.y, a.z, da, b.x, b.y, b.z, db,
        pawn.get_actor_location().x, pawn.get_actor_location().y,
        pawn.get_actor_location().z,
        float(capsule.get_scaled_capsule_radius()),
        float(capsule.get_scaled_capsule_half_height())))


def finish_clip_trace(move_id):
    trace_state = STATE.get("clip_trace_state")
    if not trace_state or trace_state["move"] != move_id:
        return
    # Last PIE callback can land just before natural montage completion. Accept
    # the final sampled pose only when it is within two 30 Hz frames of the
    # 1.1333 s source clip; the montage must also have ended before this closes.
    full_clip = trace_state["max_position"] >= (1.1333 - 0.0600)
    log("CLIP_TRACE_END move=%s montage=%s samples=%d maxLocalSeconds=%.5f expectedClipSeconds=1.1333 endToleranceSeconds=0.0600 fullClip=%d "
        "closest_weapon_r_cm=%.3f at=%.5f closest_root_weapon_end_r_cm=%.3f at=%.5f" %
        (move_id, trace_state["montage"], trace_state["samples"], trace_state["max_position"], int(full_clip),
         trace_state["min_a"][0], trace_state["min_a"][1],
         trace_state["min_b"][0], trace_state["min_b"][1]))
    STATE["clip_trace_done"].add(move_id)
    STATE["clip_trace_state"] = None


def shot(world, boss, move_id):
    if os.environ.get("SEVAROG_LIVE_SHOTS") != "1":
        return
    os.makedirs(OUT_ROOT, exist_ok=True)
    STATE["capture"] = {"move": move_id, "stage": "warm", "streak": 0, "attempts": 0,
                         "path": None, "check_at": 0.0, "file_deadline": 0.0,
                         "ready_at": plc.game_time(world)}
    log("SHOT_WARMUP requested move=%s thresholdBytes=300000 spacingSeconds=0.15" % move_id)


def tick_capture(world):
    capture = STATE.get("capture")
    if not capture:
        return
    now = plc.game_time(world)
    if capture["path"] is not None:
        if now < capture["check_at"]:
            return
        if not os.path.exists(capture["path"]):
            if now < capture["file_deadline"]:
                return
            capture["path"] = None
            capture["attempts"] += 1
            if capture["attempts"] >= (40 if capture["stage"] == "warm" else 8):
                log("SHOT_CAPTURE_FAIL move=%s stage=%s attempts=%d reason=file_timeout" %
                    (capture["move"], capture["stage"], capture["attempts"]))
                if capture["move"] == "__viewport_prewarm__":
                    STATE["viewport_prewarm_failed"] = True
                STATE["capture"] = None
                return
            capture["ready_at"] = now + 0.15
            return
        path = capture["path"]
        size = os.path.getsize(path)
        capture["path"] = None
        if capture["stage"] == "warm":
            capture["streak"] = capture["streak"] + 1 if size > 300000 else 0
            try:
                os.remove(path)
            except OSError:
                pass
            if capture["streak"] >= 2:
                capture["stage"] = "final"
                capture["attempts"] = 0
            elif capture["attempts"] >= 40:
                log("SHOT_WARMUP_FAIL move=%s attempts=%d lastBytes=%d" %
                    (capture["move"], capture["attempts"], size))
                if capture["move"] == "__viewport_prewarm__":
                    STATE["viewport_prewarm_failed"] = True
                STATE["capture"] = None
                return
            capture["ready_at"] = now + 0.15
        else:
            if size > 300000:
                if capture["move"] == "__viewport_prewarm__":
                    try:
                        os.remove(path)
                    except OSError:
                        pass
                    STATE["viewport_prewarm_complete"] = True
                    log("VIEWPORT_PREWARM ready=1 bytes=%d warmBrightStreak=%d" % (size, capture["streak"]))
                else:
                    STATE["shots"] += 1
                    log("SHOT_READY move=%s bytes=%d path=%s warmBrightStreak=%d" %
                        (capture["move"], size, path, capture["streak"]))
                STATE["capture"] = None
                return
            try:
                os.remove(path)
            except OSError:
                pass
            capture["attempts"] += 1
            if capture["attempts"] >= 8:
                log("SHOT_FINAL_FAIL move=%s attempts=%d lastBytes=%d" %
                    (capture["move"], capture["attempts"], size))
                if capture["move"] == "__viewport_prewarm__":
                    STATE["viewport_prewarm_failed"] = True
                STATE["capture"] = None
                return
            capture["ready_at"] = now + 0.15
    if capture["path"] is None and now >= capture["ready_at"]:
        capture["attempts"] += 1
        if capture["stage"] == "warm":
            path = os.path.join(OUT_ROOT, "_warm_%s_%s.png" % (capture["move"], uuid.uuid4().hex))
        else:
            path = os.path.join(OUT_ROOT, "%s_%s.png" % (capture["move"], uuid.uuid4().hex[:8]))
        unreal.SystemLibrary.execute_console_command(
            world, "HighResShot %dx%d filename=%s" % (SHOT_WIDTH, SHOT_HEIGHT, path))
        capture["path"] = path
        capture["check_at"] = now + 0.15
        capture["file_deadline"] = now + 15.0


def isolate_ambient_encounter(world):
    if STATE["ambient_encounter_isolated"]:
        return
    ambient_boss = plc.boss_actor(world)
    if ambient_boss is None:
        return
    encounter = plc.component(ambient_boss, "RPGBossEncounter")
    if encounter is None:
        log("AMBIENT_ENCOUNTER not_isolated reason=RPGBossEncounter_missing actor=%s" % ambient_boss.get_name())
        return
    encounter.hold_for_test(True)
    ambient_boss.set_actor_hidden_in_game(True)
    STATE["ambient_encounter_isolated"] = True
    actor_name = ambient_boss.get_name()
    # hold_for_test prevents new encounter scheduling, but does not cancel an
    # ability already in flight. Destroy this map-owned actor only in the
    # transient PIE world so it cannot mutate the test target's health.
    ambient_boss.destroy_actor()
    log("AMBIENT_ENCOUNTER isolated actor=%s held=1 hidden=1 destroyed_in_pie=1" % actor_name)


def tick(delta_seconds):
    if STATE["done"]:
        return
    try:
        world = live_world()
        if world is None:
            if not STATE["world_requested"]:
                STATE["world_requested"] = True
                STATE["wait_started"] = time.perf_counter()
                log("WAITING_FOR_PIE")
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            elif time.perf_counter() - STATE["wait_started"] > 60.0:
                finish("failed: PIE world did not start")
            return
        pc = unreal.GameplayStatics.get_player_controller(world, 0)
        pawn = pc.get_controlled_pawn() if pc else None
        if pawn is None:
            if STATE["pawn_wait"] == 0.0:
                STATE["pawn_wait"] = time.perf_counter()
            if time.perf_counter() - STATE["pawn_wait"] > 30.0:
                finish("failed: player pawn missing")
            return
        isolate_ambient_encounter(world)
        if os.environ.get("SEVAROG_LIVE_TRACE_GEOMETRY") == "1" and not STATE["trace_geometry_enabled"]:
            unreal.SystemLibrary.execute_console_command(world, "rpg.BossProofTraceGeometry 1")
            STATE["trace_geometry_enabled"] = True
            log("TRACE_GEOMETRY enabled=1 scope=all_active_weapon_substeps")
        tick_capture(world)
        if os.environ.get("SEVAROG_LIVE_SHOTS") == "1" and not STATE["viewport_prewarm_complete"]:
            if STATE["viewport_prewarm_failed"]:
                raise RuntimeError("viewport prewarm did not produce a bright frame")
            if not STATE["viewport_prewarm_started"]:
                os.makedirs(OUT_ROOT, exist_ok=True)
                STATE["viewport_prewarm_started"] = True
                STATE["capture"] = {"move": "__viewport_prewarm__", "stage": "warm", "streak": 0,
                                     "attempts": 0, "path": None, "check_at": 0.0, "file_deadline": 0.0,
                                     "ready_at": plc.game_time(world)}
                log("VIEWPORT_PREWARM requested thresholdBytes=300000 spacingSeconds=0.15")
            return
        STATE["pawn_wait"] = 0.0
        profile = unreal.load_asset(PROFILE_PATH)
        if profile is None:
            raise RuntimeError("framework profile disappeared in PIE")
        cls = getattr(unreal, "RPGFrameworkBossCharacter", None)
        bosses = unreal.GameplayStatics.get_all_actors_of_class(world, cls) if cls else []
        boss = next((actor for actor in bosses if actor.get_name().startswith("RPGFrameworkBossCharacter")), None)
        if boss is None:
            now = time.perf_counter()
            if now - STATE["last_missing"] >= 2.0:
                STATE["last_missing"] = now
                log("HEARTBEAT missing_boss=1 player=1")
            if not STATE["pack_style_ready"] and not wait_for_pack_style(pawn):
                return
            boss = spawn_live_boss(world, pawn, profile)
            STATE["active_id"] = None
            return
        now = plc.game_time(world)
        if not STATE["spawn_ready"]:
            if not validate_spawn_navigation(boss, profile, pawn, now):
                return
        if os.environ.get("SEVAROG_LIVE_DEFERRED_SELECTION") == "1":
            tick_deferred_selector(world, boss, now)
            return
        if os.environ.get("SEVAROG_LIVE_AUTONOMOUS") == "1":
            tick_autonomous_selector(world, boss, now)
            return
        trace_clip_frame(boss, pawn, now)
        if STATE["active_id"] is None and STATE["next_index"] < len(EXPECTED_CARDS):
            # A capture belongs to one card. Do not replace its warmup/final
            # state with the next card's request while HighResShot is pending.
            if os.environ.get("SEVAROG_LIVE_SHOTS") == "1" and STATE["capture"] is not None:
                return
            if now < STATE["attempt_due"]:
                return
            STATE["attempt_due"] = now + 0.5
            move_id = EXPECTED_CARDS[STATE["next_index"]]
            distance = place_player_for_card(profile, pawn, boss, move_id, "before_request")
            if STATE["wait_started"] == 0.0:
                STATE["wait_started"] = now
                log("CARD request move=%s" % move_id)
            if move_id == "Move_Sevarog_Speedburst":
                result = boss.start_combo_for_test(move_id)
                if result:
                    log("COMBO_START root=%s mode=real_combo_gate" % move_id)
            else:
                result = boss.start_card_for_test(move_id)
            if result:
                STATE["active_id"] = move_id
                STATE["wait_started"] = 0.0
                STATE["next_index"] += 1
                duration = 3.0
                log("CARD accepted move=%s targetDistanceCm=%.1f inBand=1" % (move_id, distance))
                shot(world, boss, move_id)
                STATE["next_due"] = now + duration
                if move_id == "Move_Sevarog_Subjugation_C1277" and os.environ.get("SEVAROG_LIVE_S7_DODGE_OUT") == "1":
                    # S7 release is at 0.800 s; move at release + 0.300 s,
                    # before the 0.750 s resolve delay expires.
                    STATE["dodge_out_started_at"] = now
                    STATE["dodge_out_due"] = now + 1.100
                    STATE["dodge_out_done"] = False
                if move_id == "Move_Sevarog_Subjugation_C1277":
                    STATE["s7_started_at"] = now
                    STATE["s7_release_sample_due"] = now + 0.800
                    STATE["s7_release_sample_done"] = False
            elif now - STATE["wait_started"] > 35.0:
                raise RuntimeError("card start timed out move=%s" % move_id)
            return
        if (STATE["active_id"] == "Move_Sevarog_Subjugation_C1277"
                and not STATE["s7_release_sample_done"] and STATE["s7_release_sample_due"] is not None
                and now >= STATE["s7_release_sample_due"]):
            player_ground = pawn.get_actor_location()
            boss_ground = boss.get_actor_location()
            player_capsules = pawn.get_components_by_class(unreal.CapsuleComponent)
            boss_capsules = boss.get_components_by_class(unreal.CapsuleComponent)
            if player_capsules:
                player_ground.z -= float(player_capsules[0].get_scaled_capsule_half_height())
            if boss_capsules:
                boss_ground.z -= float(boss_capsules[0].get_scaled_capsule_half_height())
            log("S7_RELEASE_SAMPLE elapsedAfterStart=%.3f playerGround=(%.3f,%.3f,%.3f) bossGround=(%.3f,%.3f,%.3f)" %
                (now - STATE["s7_started_at"] if STATE["s7_started_at"] is not None else -1.0,
                 player_ground.x, player_ground.y, player_ground.z,
                 boss_ground.x, boss_ground.y, boss_ground.z))
            STATE["s7_release_sample_done"] = True
        if (STATE["active_id"] == "Move_Sevarog_Subjugation_C1277"
                and os.environ.get("SEVAROG_LIVE_S7_DODGE_OUT") == "1"
                and not STATE["dodge_out_done"] and STATE["dodge_out_due"] is not None
                and now >= STATE["dodge_out_due"]):
            away = pawn.get_actor_location() - boss.get_actor_location()
            away.z = 0.0
            if away.length() <= 1.0:
                away = boss.get_actor_forward_vector()
            away = away.normal()
            current = pawn.get_actor_location()
            destination = current + away * 500.0
            destination.z = current.z
            pawn.set_actor_location(destination, False, True)
            actual = (pawn.get_actor_location() - current).length()
            log("S7_DODGE_OUT elapsedAfterStart=%.3f requestedDisplacementCm=500 actualDisplacementCm=%.1f variant=release_plus_0.3s" %
                (now - STATE["dodge_out_started_at"], actual))
            STATE["dodge_out_done"] = True
        if STATE["active_id"] is not None and now >= STATE["next_due"]:
            completed_id = STATE["active_id"]
            finish_clip_trace(completed_id)
            if STATE["active_id"] == "Move_Sevarog_Speedburst":
                log("COMBO_EXPECTED followup=%s; require native combo_gate and combo_step receipts" % COMBO_FOLLOWUP)
            STATE["active_id"] = None
            STATE["wait_started"] = 0.0
            self_test_cards = int(os.environ.get("SEVAROG_LIVE_SELF_TEST_CARDS", "1"))
            if os.environ.get("SEVAROG_LIVE_SELF_TEST") == "1" and STATE["next_index"] >= self_test_cards:
                log("SELF_TEST CARD_WINDOW_ELAPSED count=%d last_card=%s; runner verifies every CARD_END" %
                    (self_test_cards, completed_id))
                finish("self-test completed requested card windows; runner verifies each CARD_END")
                return
            if STATE["next_index"] >= len(EXPECTED_CARDS):
                STATE["final_due"] = now + 12.0
        if STATE["next_index"] >= len(EXPECTED_CARDS) and STATE["active_id"] is None and STATE["final_due"] > 0.0 and now >= STATE["final_due"]:
            if STATE["capture"] is None:
                finish("driver complete: S1-S3 standalone and S4->S5 combo receipts are in the UE log")
    except Exception as error:
        log("ERROR " + str(error))
        log(traceback.format_exc())
        finish("failed: %s" % error)


def main():
    global COMBO_FOLLOWUP
    profile, COMBO_FOLLOWUP = profile_report()
    if os.environ.get("SEVAROG_LIVE_TRANSIENT_CHECK") == "1":
        check_bridge_reflection()
        log("finished: transient profile and bridge reflection check only; no PIE, spawn, save, or map edit")
        return
    check_bridge_reflection()
    STATE["started_at"] = time.perf_counter()
    global HANDLE
    HANDLE = unreal.register_slate_post_tick_callback(tick)
    if not HANDLE:
        raise RuntimeError("could not register live-driver tick callback")
    log("READY awaiting PIE; profile=%s optionalShots=%s" %
        (PROFILE_PATH, os.environ.get("SEVAROG_LIVE_SHOTS") == "1"))


try:
    main()
except Exception as error:
    log("ERROR " + str(error))
    log("finished: refused before PIE or driver setup")
    raise
