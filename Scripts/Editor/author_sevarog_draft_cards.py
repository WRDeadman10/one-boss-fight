"""Fail-closed authoring entry point for C-1251a Sevarog draft cards.

Values are provisional, tune after PIE. The Lead runs this only in UE 5.5
after the offline preflight and C++ validation bridge are available.
"""
import json
import math
import os
from pathlib import Path
import sys


PACKAGE_DIR = "/Game/OneBossFight/Data/Sevarog"
DEFINITION_NAME = "DA_Boss_Sevarog_Draft"
PROFILE_NAME = "DA_Boss_Sevarog_FrameworkProfile_Draft"
CARD_NAMES = (
    "DA_Move_Sevarog_Swing1_Medium_C1247",
    "DA_Move_Sevarog_Swing2_Medium_C1247",
    "DA_Move_Sevarog_Swing3_Slow_C1247",
    "DA_Move_Sevarog_Speedburst_C1247",
    "DA_Move_Sevarog_Swing1_FAST_v2_C1247",
)
F5_SOURCE = "Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json"
CONTACT_SOURCE = "Documentation/Boss/C1242_SEVAROG_CONTACT_MARKING.md"
SEVAROG_ROOT = "/Game/ParagonSevarog/Characters/Heroes/Sevarog"
SKELETON_PATH = SEVAROG_ROOT + "/Meshes/Sevarog_Skeleton.Sevarog_Skeleton"
SEQUENCE_PATHS = (
    SEVAROG_ROOT + "/Animations/Swing1_Medium.Swing1_Medium",
    SEVAROG_ROOT + "/Animations/Swing2_Medium.Swing2_Medium",
    SEVAROG_ROOT + "/Animations/Swing3_Slow.Swing3_Slow",
    SEVAROG_ROOT + "/Animations/Speedburst.Speedburst",
    SEVAROG_ROOT + "/Animations/Swing1_FAST_v2.Swing1_FAST_v2",
)
# Definition identity/skeleton are the only authored definition fields; every
# other member retains its declared C++ default. bUseMontageNotifyTimings is
# explicitly false. Sources: C-1248 and RPGEncounterBinding.h declarations.
DRAFT_DEFINITION_FIELDS = {
    "schema": 1,
    "definition_id": "Boss_Sevarog_Draft",
    "presentation_id": "Sevarog",
    "skeleton": {"$soft_object": SKELETON_PATH},
    "use_montage_notify_timings": False,
}

# Complete minimum F5 profile. Numerical proof fixture values are copied from
# the cited F5 authoring/readback; optional fields retain native C++ defaults.
FRAMEWORK_PROFILE_FIELDS = {
    "fixture_label": "F5 fixture",
    "mesh": {"$soft_object": SEVAROG_ROOT + "/Meshes/Sevarog.Sevarog"},
    "anim_class": {"$soft_class": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C"},
    "target_pawn_class": {"$soft_class": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C"},
    "band_min_cm": 110.0, "band_max_cm": 140.0,
    "walk_speed_cm_per_second": 180.0, "acceptance_cm": 5.0,
    "walk_timeout_seconds": 10.0, "blend_in_seconds": 0.1, "blend_out_seconds": 0.03,
    "capsule_radius_cm": 60.0, "capsule_half_height_cm": 165.0,
    "target_health": 800.0, "damage_enabled": True,
    "hit_step_cm": 15.0, "hit_max_substeps": 8,
    "repeat_penalty": 0.2, "repeat_memory": 2, "attack_count": 3,
    "range_band_partition": True,
    "boss_max_health": 250.0, "player_hit_damage": 100.0,
    "alignment_authored": True,
    # Existing F5 fixture transform copied from the COMBO proof authoring.
    "mesh_relative_transform": {"$runtime_transform": True},
    "combo_root": "S4", "combo_max_depth": 2,
    "combo_nodes": {"$runtime_combo": "S4_WHiff_S5_MEDIUM"},
    # BOSS-PAC-005 default is 0.3 s; pack montages and 150 cm design reach
    # are the same explicitly documented C-637/PAC003 inputs.
    "punish_margin_seconds": 0.3,
    "player_light_montage": {"$soft_object": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage.Attack_PrimaryA_Montage"},
    "player_heavy_montage": {"$soft_object": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/ChargedAttack_Montage.ChargedAttack_Montage"},
    "player_reach_cm": 150.0,
}

FIELD_SOURCES = {
    "definition identity/skeleton/notify": "C-1248 rig readback; RPGEncounterBinding.h declared defaults",
    "framework base geometry, capsule, health, attack budgets": "Docs/BossCombatReview/Execution/Claude/B_COMBO2/create_combo_content.py:21-22,78-79",
    "framework dependency classes": "Docs/BossCombatReview/Execution/Claude/B_COMBO2/create_combo_content.py:72",
    "framework punish values": "C-637 witness in Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json; B_PAC003/create_punish_content.py:109-112",
    "S3/S4 card overrides": "C-1250",
    "combo S4 whiff to S5": "C-1251; RPGBossFrameworkProfile.h declared combo defaults",
    "untouched optional properties": "their declared defaults in RPGBossFrameworkProfile.h / RPGEncounterBinding.h",
}
PROFILE_FIELD_SOURCES = {
    key: ("C-1250" if key in {"combo_root", "combo_max_depth", "combo_nodes"} else
          "C-1250 selector has per-card ranges; RPGBossFrameworkProfile.cpp:52,200" if key == "range_band_partition" else
          FIELD_SOURCES["framework punish values"] if key.startswith(("punish_", "player_")) else
          FIELD_SOURCES["framework dependency classes"] if key in {"mesh", "anim_class", "target_pawn_class"} else
          FIELD_SOURCES["framework base geometry, capsule, health, attack budgets"])
    for key in FRAMEWORK_PROFILE_FIELDS
}
DEFINITION_FIELD_SOURCES = {key: FIELD_SOURCES["definition identity/skeleton/notify"]
                            for key in DRAFT_DEFINITION_FIELDS}
CARD_FIELD_SOURCES = {
    "asset_name": "C-1247 named draft allowlist",
    "move_id": "C-1247 named MoveId table",
    "family_id": F5_SOURCE + "; C-1250 S4 gap-closer family",
    "phase_id": F5_SOURCE + " Phase_1",
    "skeleton": "C-1248 Sevarog rig readback",
    "sequence": "C-1248 Sevarog rig readback",
    "montage": F5_SOURCE + " Montage=null",
    "slot_name": F5_SOURCE + " FullBody",
    "section_name": F5_SOURCE + " SectionName=None",
    "play_rate": "C++ FRPGBossMoveCardSpec default 1.0; RPGBossMoveCard.h",
    "commit_seconds": CONTACT_SOURCE + "; C-1242 approved timing marks",
    "active_start_seconds": CONTACT_SOURCE + "; C-1242 approved timing marks",
    "active_end_seconds": CONTACT_SOURCE + "; C-1242 approved timing marks",
    "recovery_end_seconds": CONTACT_SOURCE + "; C-1242 approved timing marks",
    "track_degrees_per_second": F5_SOURCE + " (or C++ source default for S4)",
    "min_range_cm": F5_SOURCE + " (S4 override: C-1250)",
    "max_range_cm": F5_SOURCE + " (S4 override: C-1250)",
    "front_cone_degrees": F5_SOURCE + " (S4 override: C-1250)",
    "max_vertical_delta_cm": "C++ FRPGBossMoveCardSpec declared default; S4 explicit C-1250",
    "hp_damage": F5_SOURCE + " (S4 non-damaging defensive card: C++ validator contract)",
    "cooldown_seconds": F5_SOURCE + " (S4 override: C-1250)",
    "candidate_weight": F5_SOURCE + " (S4 uses FRPGBossProfileCard declared default 1.0)",
    "warp_start_seconds": "C-1242 timing / C-1250 S3/S4",
    "warp_end_seconds": "C-1242 timing / C-1250 S3/S4",
    "warp_max_distance_cm": "C-1250",
    "warp_max_angle_degrees": "C-1250",
    "warp_standoff_cm": "C-1250",
    "warp_ease_in_out": "C-1250 for S4; C++ declared default for other cards",
    "defensive": "C-1250 S4 gap closer with zero damage; F5 analog source for remaining cards",
    "warp_away": "C-1250 (false, toward target)",
    "hold_at_seconds": "FRPGBossMoveCardSpec declared C++ default",
    "hold_min_seconds": "FRPGBossMoveCardSpec declared C++ default",
    "hold_max_seconds": "FRPGBossMoveCardSpec declared C++ default",
    "hold_seed": "FRPGBossMoveCardSpec declared C++ default",
    "cues": "FRPGBossMoveCardSpec declared C++ default",
    "uses_root_motion": F5_SOURCE + " bUsesRootMotion=false",
    "windows": F5_SOURCE + " socket/group/radius; C-1242 supplies revised contact interval",
    "source_analog": F5_SOURCE + " MoveId map; S4 has no analogue per C-1250",
    "source_status": "C-1248 approval requires provisional, tune after PIE",
}


def validate_source_coverage(rows):
    require(set(DEFINITION_FIELD_SOURCES) == set(DRAFT_DEFINITION_FIELDS),
            "Definition values have missing or extra source citations")
    require(set(PROFILE_FIELD_SOURCES) == set(FRAMEWORK_PROFILE_FIELDS),
            "FrameworkProfile values have missing or extra source citations")
    for row in rows:
        require(set(row) == set(CARD_FIELD_SOURCES),
                "card row values have missing or extra source citations")
        for key in CARD_FIELD_SOURCES:
            require(CARD_FIELD_SOURCES[key], "card field has no source: " + key)

# These are the Lead-approved C1242 visual timing candidates. Every other
# copied numerical field is pulled from the corresponding cited Sevarog F5
# proof card. Do not fill either None warp/range value from an arbitrary guess.
TIMING = (
    (0.200, 0.267, 0.400, 1.133),
    (0.133, 0.200, 0.400, 1.133),
    (0.467, 0.533, 0.667, 1.700),
    (0.200, 0.267, 1.133, 1.267),
    (0.200, 0.267, 0.333, 0.533),
)
F5_ANALOG_IDS = (
    "Move_Sevarog_SwingMedium_F5",
    "Move_Sevarog_SwingMedium_F5",
    "Move_Sevarog_HeavySlam_F5",
    None,
    "Move_Sevarog_AntiGreed_F5",
)
FAMILY_IDS = (
    "Family_08_ComboSweep",
    "Family_08_ComboSweep",
    "Family_06_HeavySlam",
    "Family_05_GapCloser",
    "Family_02_AntiGreed",
)
REQUIRED_CARD_NUMBERS = (
    "play_rate", "commit_seconds", "active_start_seconds", "active_end_seconds",
    "recovery_end_seconds", "track_degrees_per_second", "min_range_cm", "max_range_cm",
    "front_cone_degrees", "max_vertical_delta_cm", "hp_damage", "cooldown_seconds", "candidate_weight",
)


class Refusal(RuntimeError):
    """A preflight refusal; the script must not partially author assets."""


REFLECTED_TYPE_ALIASES = {
    "RPGBossComboEdgeData": ("RpgBossComboEdgeData",),
    "RPGBossComboNodeData": ("RpgBossComboNodeData",),
    "RPGBossComboOutcome": ("RpgBossComboOutcome",),
    "RPGBossMoveCardSpec": ("RpgBossMoveCardSpec",),
    "RPGBossMoveWindow": ("RpgBossMoveWindow",),
    "RPGBossProfileCard": ("RpgBossProfileCard",),
    "RPGBossCardValidationLibrary": ("RpgBossCardValidationLibrary",),
}
PREFLIGHT_FAILURES = None


def require(condition, message):
    if not condition:
        raise Refusal("[SevarogDraft] REFUSED: " + message)


def reflected_type(unreal_module, exact_name):
    """Resolve the U/E/F-stripped UE name exactly first, then old aliases."""
    for name in (exact_name,) + REFLECTED_TYPE_ALIASES.get(exact_name, ()):
        value = getattr(unreal_module, name, None)
        if value is not None:
            return value
    return None


def is_finite_nonnegative(value, field):
    require(type(value) in (int, float) and math.isfinite(float(value)) and value >= 0,
            field + " must be a finite nonnegative number")


def validate_write_path(path):
    """Allow writes only below the project-owned data folder; never pack paths."""
    require(isinstance(path, str) and path.startswith(PACKAGE_DIR + "/"),
            "write target is outside the Sevarog draft allowlist: " + repr(path))
    require(not path.startswith(SEVAROG_ROOT + "/") and "/Paragon" not in path,
            "pack path is never a write target: " + path)
    require(".." not in path.split("/"), "path traversal in write target")
    return path


def read_f5_cards(project_root):
    source = (project_root / F5_SOURCE).resolve()
    require(source.is_file(), "F5 proof source is missing: " + str(source))
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Refusal("[SevarogDraft] REFUSED: invalid F5 proof JSON: " + str(exc))
    require(isinstance(payload, dict) and isinstance(payload.get("cards"), list),
            "F5 proof source has an unexpected schema")
    require("design value, proposed" in str(payload.get("damage_specification", "")).lower(),
            "F5 damage values lost their proposed-design provenance")
    cards = {}
    for card in payload["cards"]:
        require(isinstance(card, dict), "F5 card row must be an object")
        move_id = card.get("MoveId")
        require(isinstance(move_id, str) and move_id not in cards,
                "F5 MoveId is missing or duplicated")
        cards[move_id] = card
    return cards


def build_candidate_specs(f5_cards):
    """Build values; None is a deliberate gate and is never silently defaulted."""
    rows = []
    for index, asset_name in enumerate(CARD_NAMES):
        analog_id = F5_ANALOG_IDS[index]
        analog = f5_cards.get(analog_id) if analog_id else None
        if analog_id:
            require(analog is not None, "required F5 analogue is missing: " + analog_id)
            require(analog.get("DamageStatus") == "design value, proposed" and
                    analog.get("CooldownStatus") == "design value, proposed",
                    analog_id + " damage/cooldown is no longer marked proposed")

        commit, active_start, active_end, recovery_end = TIMING[index]
        row = {
            "asset_name": asset_name,
            "move_id": asset_name.removeprefix("DA_").replace("_C1247", ""),
            "family_id": FAMILY_IDS[index],
            "phase_id": "Phase_1",
            "skeleton": SKELETON_PATH,
            "sequence": SEQUENCE_PATHS[index],
            "montage": "",
            "slot_name": "FullBody",
            "section_name": "None",
            "play_rate": 1.0,
            "commit_seconds": commit,
            "active_start_seconds": active_start,
            "active_end_seconds": active_end,
            "recovery_end_seconds": recovery_end,
            # Speedburst's zero tracking value comes from the earlier F5
            # candidate table; it is not inferred from the new frame capture.
            "track_degrees_per_second": analog.get("TrackDegreesPerSecond") if analog else (0.0 if index == 3 else None),
            "warp_start_seconds": 0.0,
            "warp_end_seconds": 0.0,
            "warp_max_distance_cm": 0.0,
            "warp_max_angle_degrees": 0.0,
            "warp_standoff_cm": 0.0,
            "warp_ease_in_out": False,
            "defensive": index == 3,
            "warp_away": False,
            "hold_at_seconds": 0.0,
            "hold_min_seconds": 0.0,
            "hold_max_seconds": 0.0,
            "hold_seed": 0,
            "cues": [],
            "min_range_cm": analog.get("MinRangeCm") if analog else None,
            "max_range_cm": analog.get("MaxRangeCm") if analog else None,
            "front_cone_degrees": analog.get("FrontConeDegrees") if analog else None,
            "max_vertical_delta_cm": 0.0,
            "hp_damage": 0.0 if index == 3 else analog.get("HPDamage"),
            "uses_root_motion": False,
            "windows": [],
            "cooldown_seconds": analog.get("CooldownSeconds") if analog else None,
            "candidate_weight": analog.get("BaseUtility") if analog else None,
            "source_analog": analog_id,
            "source_status": "provisional, tune after PIE",
        }

        # The S3 displacement is explicitly unresolved. Keep zero budgets here
        # only as the validator-safe "warp off" encoding; the gate below refuses
        # to author it as the requested step-in until approved values are supplied.
        if index == 2:
            row.update({
                "warp_start_seconds": 0.467,
                "warp_end_seconds": 0.533,
                "warp_max_distance_cm": 50.0,
                "warp_max_angle_degrees": 45.0,
                "warp_standoff_cm": 100.0,
            })
        # C-1250: Speedburst is a non-damaging gap closer, then S5 follows only
        # on whiff. It remains defensive for the existing zero-damage contract.
        if index == 3:
            row.update({
                "warp_start_seconds": 0.267,
                "warp_end_seconds": 0.800,
                "warp_max_distance_cm": 450.0,
                "warp_max_angle_degrees": 45.0,
                "warp_standoff_cm": 120.0,
                "warp_ease_in_out": True,
                "defensive": True,
                "warp_away": False,
                "min_range_cm": 300.0,
                "max_range_cm": 650.0,
                "front_cone_degrees": 120.0,
                "max_vertical_delta_cm": 0.0,
                "cooldown_seconds": 4.0,
                "candidate_weight": 1.0,
            })

        if index != 3:
            start, end = active_start, active_end
            radius = 25.0 if index == 2 else 15.0
            row["windows"] = [{
                "window_id": "Window_" + row["move_id"],
                "hit_group": "HitGroup_ScytheBlade",
                "start_seconds": start,
                "end_seconds": end,
                "socket_a": "weapon_r",
                "socket_b": "root_weapon_end_r",
                "radius_cm": radius,
                "secondary": False,
                "ring": False,
                "grab": False,
                "baked_samples": [],
            }]
        rows.append(row)
    return rows


def build_combo(unreal_module, report=False):
    """C-1250 combo graph: Speedburst whiff advances to S5 fast swing."""
    edge_class = reflected_type(unreal_module, "RPGBossComboEdgeData")
    node_class = reflected_type(unreal_module, "RPGBossComboNodeData")
    outcome_enum = reflected_type(unreal_module, "RPGBossComboOutcome")
    require(edge_class is not None and node_class is not None and outcome_enum is not None,
            "reflected combo edge/node/outcome types unavailable")
    edge = edge_class()
    for name, value in {
        "to_node": "S5", "min_range_cm": 0.0, "max_range_cm": 1.0e6,
        "max_abs_yaw_degrees": 180.0, "any_outcome": False,
        "outcome": getattr(outcome_enum, "WHIFF", None),
    }.items():
        require(value is not None, "combo outcome enum WHIFF unavailable")
        set_property(edge, name, value, ("FRPGBossComboEdgeData." + name) if report else None)
    first, second = node_class(), node_class()
    for node, name, move, edges in (
        (first, "S4", "Move_Sevarog_Speedburst", ue_array(unreal_module, edge_class, [edge])),
        (second, "S5", "Move_Sevarog_Swing1_Medium", ue_array(unreal_module, edge_class, [])),
    ):
        for field, value in {"node_id": name, "move_id": move, "edges": edges}.items():
            set_property(node, field, value, ("FRPGBossComboNodeData." + field) if report else None)
    return ue_array(unreal_module, node_class, [first, second])


def ue_array(unreal_module, element_type, values):
    """Build a reflected Unreal array; plain Python lists do not nativize for struct arrays."""
    array_type = getattr(unreal_module, "Array", None)
    require(callable(array_type), "unreal.Array unavailable for reflected struct array")
    result = array_type(element_type)
    for value in values:
        result.append(value)
    return result


def log_punish_estimates(rows):
    """Print source-based estimate for the Lead's S4 fail-closed decision."""
    # C-637 witness: light startup 0.3503 s, run speed 600 cm/s;
    # PAC003 design reach 150 cm. These are estimates, C++ remains authority.
    reach, run_speed, startup, required = 150.0, 600.0, 0.3503, 0.3
    for row in rows:
        if row["defensive"]:
            recovery = (row["recovery_end_seconds"] - row["warp_end_seconds"]) / row["play_rate"]
            end_distance = (row["max_range_cm"] + row["warp_max_distance_cm"]
                            if row["warp_away"] else row["warp_standoff_cm"])
            travel = max(0.0, end_distance - reach) / run_speed
            required_for_row = 0.0
            mode = "DEFENSE_COUNTERPLAY"
        else:
            recovery = (row["recovery_end_seconds"] - row["active_end_seconds"]) / row["play_rate"]
            travel = max(0.0, row["max_range_cm"] - reach) / run_speed
            required_for_row = required
            mode = "LIGHT_PUNISH"
        margin = recovery - startup - travel
        print("[SevarogDraft] PUNISH_ESTIMATE move=%s mode=%s endDistance=%.4f recovery=%.4f startup=%.4f travel=%.4f margin=%.4f required=%.4f" %
              (row["move_id"], mode, end_distance if row["defensive"] else row["max_range_cm"], recovery, startup, travel, margin, required_for_row))


def unresolved_gates(rows):
    errors = []
    if DRAFT_DEFINITION_FIELDS is None:
        errors.append("complete approved URPGBossDefinition fields await Lead input")
    if FRAMEWORK_PROFILE_FIELDS is None:
        errors.append("complete approved URPGBossFrameworkProfile fields await Lead input")
    for row in rows:
        for name in REQUIRED_CARD_NUMBERS:
            if row.get(name) is None:
                errors.append(row["move_id"] + "." + name + " is not approved")
        if row["source_analog"] is None and row["move_id"].endswith("Speedburst"):
            for name in ("warp_max_distance_cm", "warp_max_angle_degrees", "warp_standoff_cm",
                         "min_range_cm", "max_range_cm", "front_cone_degrees", "cooldown_seconds"):
                if row[name] is None:
                    errors.append(row["move_id"] + "." + name + " awaits Lead approval")
        if row["move_id"].endswith("Swing3_Slow") and row["warp_max_distance_cm"] is None:
            errors.append(row["move_id"] + ".warp budget awaits Lead approval")
        for name, value in row.items():
            if name.endswith("_seconds") or name.endswith("_cm") or name.endswith("_degrees"):
                if value is not None:
                    is_finite_nonnegative(value, row["move_id"] + "." + name)
    return errors


def require_editor_module(unreal_module):
    require(unreal_module is not None, "UE Python module unavailable")
    for name in ("Paths", "EditorAssetLibrary", "AssetToolsHelpers", "DataAssetFactory", "SoftObjectPath"):
        require(getattr(unreal_module, name, None) is not None,
                "required UE Python API is unavailable: unreal." + name)
    return unreal_module


def get_cpp_validation_bridge(unreal_module):
    """Require the Editor-only reflected wrapper around production C++ validation."""
    # C-1251 Lead fix: UE exposes URPGBossCardValidationLibrary to Python as unreal.RPGBossCardValidationLibrary
    # (the U prefix is dropped, the case is kept); the first run refused because it only tried the camel-cased name.
    library = reflected_type(unreal_module, "RPGBossCardValidationLibrary")
    require(library is not None,
            "Editor-only C++ validation bridge is missing; refusing asset creation")
    validate_card = getattr(library, "validate_move_card_report", None)
    validate_profile = getattr(library, "validate_framework_profile_report", None)
    require(callable(validate_card) and callable(validate_profile),
            "validation bridge must expose validate_move_card_report and validate_framework_profile_report")
    return validate_card, validate_profile


def unpack_validation_result(raw, label):
    """Accept only the guarded Python projection of (bool, out diagnostics)."""
    if isinstance(raw, str):
        if raw == "PASS":
            return True, []
        if raw.startswith("FAIL|"):
            return False, raw[5:].split(";")
        raise Refusal(label + " bridge returned an unknown verdict: " + raw)
    if isinstance(raw, tuple) and len(raw) == 2:
        valid, diagnostics = raw
        require(type(valid) is bool, label + " bridge returned a non-boolean verdict")
        try:
            diagnostics = list(diagnostics)
        except TypeError as exc:
            raise Refusal(label + " bridge diagnostics are not iterable: " + str(exc))
        return valid, [str(item) for item in diagnostics]
    # Compatibility for the original bool/out-array UFUNCTION projection.
    if type(raw).__name__ == "Array":
        diagnostics = [str(item) for item in raw]
        return not diagnostics, diagnostics
    raise Refusal(label + " bridge result has unsupported shape: " +
                  type(raw).__name__ + " " + repr(raw))


def set_property(obj, field_name, value, report_label=None):
    """Set a reflected property with guarded UE Python name variants."""
    names = [field_name]
    if field_name.startswith("b_"):
        names.append(field_name[2:])
    if field_name and field_name[0].isupper():
        names.append("".join(("_" + c.lower()) if c.isupper() else c for c in field_name).lstrip("_"))
    last_error = None
    for name in names:
        try:
            obj.set_editor_property(name, value)
            if report_label:
                print("[SevarogDraft] PREFLIGHT OK property=" + report_label)
            return
        except Exception as exc:
            last_error = exc
    if report_label:
        print("[SevarogDraft] PREFLIGHT MISSING property=" + report_label + ": " + str(last_error))
        if PREFLIGHT_FAILURES is not None:
            PREFLIGHT_FAILURES.append("property=" + report_label)
        return False
    raise Refusal("[SevarogDraft] REFUSED: property write failed for " + field_name + ": " + str(last_error))


def materialize_approved_value(unreal_module, value, created_cards, report=False):
    """Materialize only explicit typed values; unknown/reflected types refuse."""
    if isinstance(value, list):
        return [materialize_approved_value(unreal_module, item, created_cards, report) for item in value]
    if isinstance(value, dict):
        require(len(value) == 1, "tagged value must have exactly one type key")
        if "$soft_object" in value:
            object_path = value["$soft_object"]
            require(isinstance(object_path, str) and object_path, "soft-object path missing")
            package_path = object_path.split(".", 1)[0]
            require(package_path.startswith(SEVAROG_ROOT + "/") or
                    package_path.startswith("/Game/OneBossFight/") or
                    package_path.startswith("/Game/AdvancedARPGCombat/"),
                    "non-project/non-Sevarog reference refused: " + package_path)
            asset = unreal_module.EditorAssetLibrary.load_asset(package_path)
            require(asset is not None and str(asset.get_path_name()) == object_path,
                    "soft-object did not resolve exactly: " + object_path)
            if report:
                print("[SevarogDraft] PREFLIGHT OK asset=" + object_path)
            return asset
        if "$soft_class" in value:
            class_path = value["$soft_class"]
            require(isinstance(class_path, str) and (
                    class_path.startswith("/Script/OneBossFight.") or
                    class_path.startswith("/Game/ParagonSevarog/") or
                    class_path.startswith("/Game/AdvancedARPGCombat/")),
                    "soft class is outside the project or explicitly allowed read-only packs")
            klass = unreal_module.load_class(None, class_path)
            require(klass is not None, "soft class did not resolve: " + class_path)
            if report:
                print("[SevarogDraft] PREFLIGHT OK class=" + class_path)
            return klass
        if "$struct" in value:
            descriptor = value["$struct"]
            require(isinstance(descriptor, dict) and set(descriptor) == {"type", "fields"},
                    "struct encoding requires type and fields")
            struct_type = reflected_type(unreal_module, descriptor["type"])
            if struct_type is None and descriptor["type"] not in REFLECTED_TYPE_ALIASES:
                struct_type = getattr(unreal_module, descriptor["type"], None)
            require(struct_type is not None and isinstance(descriptor["fields"], dict),
                    "reflected struct type or fields are unavailable")
            result = struct_type()
            for name, item in descriptor["fields"].items():
                set_property(result, name, materialize_approved_value(unreal_module, item, created_cards, report),
                             (descriptor["type"] + "." + name) if report else None)
            return result
        if "$enum" in value:
            descriptor = value["$enum"]
            require(isinstance(descriptor, dict) and set(descriptor) == {"type", "value"},
                    "enum encoding requires type and value")
            enum_type = reflected_type(unreal_module, descriptor["type"])
            if enum_type is None and descriptor["type"] not in REFLECTED_TYPE_ALIASES:
                enum_type = getattr(unreal_module, descriptor["type"], None)
            enum_value = getattr(enum_type, descriptor["value"], None) if enum_type is not None else None
            require(enum_value is not None, "reflected enum value is unavailable")
            return enum_value
        if "$runtime_transform" in value:
            require(value["$runtime_transform"] is True, "unsupported transform marker")
            return unreal_module.Transform(
                location=[0.0, 0.0, -165.0],
                rotation=unreal_module.Rotator(roll=0.0, pitch=0.0, yaw=-90.0),
                scale=[1.0, 1.0, 1.0])
        if "$runtime_combo" in value:
            require(value["$runtime_combo"] == "S4_WHiff_S5_MEDIUM", "unsupported combo marker")
            return build_combo(unreal_module)
        if "$card_ref" in value:
            move_id = value["$card_ref"]
            require(move_id in created_cards, "profile card reference is not allowlisted: " + str(move_id))
            asset = created_cards[move_id]
            return asset
        raise Refusal("[SevarogDraft] REFUSED: unsupported approved value tag")
    if isinstance(value, float):
        require(math.isfinite(value), "approved value is non-finite")
    require(value is None or type(value) in (str, int, float, bool), "approved value is not a scalar/list/typed object")
    return value


def make_window(unreal_module, values, report=False):
    window_class = reflected_type(unreal_module, "RPGBossMoveWindow")
    require(window_class is not None, "reflected FRPGBossMoveWindow Python type unavailable")
    window = window_class()
    for name, value in values.items():
        set_property(window, name, value, ("FRPGBossMoveWindow." + name) if report else None)
    return window


def make_card_spec(unreal_module, row, loaded_assets, report=False):
    spec_class = reflected_type(unreal_module, "RPGBossMoveCardSpec")
    require(spec_class is not None, "reflected FRPGBossMoveCardSpec Python type unavailable")
    spec = spec_class()
    field_map = {
        "schema": 1, "move_id": row["move_id"], "family_id": row["family_id"],
        "phase_id": row["phase_id"], "skeleton": loaded_assets["skeleton"],
        "sequence": loaded_assets[row["sequence"]],
        "montage": None, "slot_name": row["slot_name"], "section_name": row["section_name"],
        "play_rate": row["play_rate"], "commit_seconds": row["commit_seconds"],
        "active_start_seconds": row["active_start_seconds"], "active_end_seconds": row["active_end_seconds"],
        "recovery_end_seconds": row["recovery_end_seconds"], "track_degrees_per_second": row["track_degrees_per_second"],
        "warp_start_seconds": row["warp_start_seconds"], "warp_end_seconds": row["warp_end_seconds"],
        "warp_max_distance_cm": row["warp_max_distance_cm"], "warp_max_angle_degrees": row["warp_max_angle_degrees"],
        "warp_standoff_cm": row["warp_standoff_cm"], "warp_ease_in_out": row["warp_ease_in_out"],
        "defensive": row["defensive"], "warp_away": row["warp_away"],
        "hold_at_seconds": row["hold_at_seconds"], "hold_min_seconds": row["hold_min_seconds"],
        "hold_max_seconds": row["hold_max_seconds"], "hold_seed": row["hold_seed"], "cues": [],
        "min_range_cm": row["min_range_cm"], "max_range_cm": row["max_range_cm"],
        "front_cone_degrees": row["front_cone_degrees"], "max_vertical_delta_cm": row["max_vertical_delta_cm"],
        "hp_damage": row["hp_damage"], "uses_root_motion": row["uses_root_motion"],
        "windows": [make_window(unreal_module, window, report) for window in row["windows"]],
    }
    for name, value in field_map.items():
        set_property(spec, name, value, ("FRPGBossMoveCardSpec." + name) if report else None)
    return spec


def clamp_marked_recovery_to_clip(rows, loaded_assets):
    """Fit rounded frame-marked recovery ends inside the resolved clip and profile blend tail."""
    blend_out = float(FRAMEWORK_PROFILE_FIELDS.get("blend_out_seconds", 0.0))
    for row in rows:
        clip_seconds = float(loaded_assets[row["sequence"]].get_play_length())
        allowed_seconds = clip_seconds - blend_out
        marked_seconds = float(row["recovery_end_seconds"])
        if marked_seconds > allowed_seconds:
            require(marked_seconds - allowed_seconds <= (1.0 / 15.0),
                    row["move_id"] + " recovery plus profile blend-out exceeds clip by more than one 15 Hz sample")
            row["recovery_end_seconds"] = allowed_seconds
            print("[SevarogDraft] TIMING_CLAMP move=%s markedRecovery=%.9f resolvedClip=%.9f blendOut=%.9f appliedRecovery=%.9f" %
                  (row["move_id"], marked_seconds, clip_seconds, blend_out, allowed_seconds))


def create_and_validate_assets(unreal_module, rows, loaded_assets, bridge):
    """Create allowlisted unsaved assets, validate them in C++, then save."""
    require(isinstance(DRAFT_DEFINITION_FIELDS, dict) and DRAFT_DEFINITION_FIELDS,
            "approved Definition property payload is missing")
    require(isinstance(FRAMEWORK_PROFILE_FIELDS, dict) and FRAMEWORK_PROFILE_FIELDS,
            "approved FrameworkProfile property payload is missing")
    require(DRAFT_DEFINITION_FIELDS.get("use_montage_notify_timings") is False,
            "draft must keep bUseMontageNotifyTimings=false")
    require("cards" not in FRAMEWORK_PROFILE_FIELDS and "Cards" not in FRAMEWORK_PROFILE_FIELDS,
            "profile card list is built from the allowlisted generated card assets")

    # Resolve every non-card property value and reflected struct before creating
    # packages, so missing fields/classes/references cannot leave partial assets.
    profile_values = {name: materialize_approved_value(unreal_module, value, {})
                      for name, value in FRAMEWORK_PROFILE_FIELDS.items()}
    definition_values = {name: materialize_approved_value(unreal_module, value, {})
                         for name, value in DRAFT_DEFINITION_FIELDS.items()}
    asset_tools = unreal_module.AssetToolsHelpers.get_asset_tools()
    require(asset_tools is not None, "AssetTools API unavailable")
    factory = unreal_module.DataAssetFactory()
    card_class = unreal_module.load_class(None, "/Script/OneBossFight.RPGBossMoveCard")
    profile_class = unreal_module.load_class(None, "/Script/OneBossFight.RPGBossFrameworkProfile")
    definition_class = unreal_module.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    require(card_class is not None and profile_class is not None and definition_class is not None,
            "one or more required project DataAsset classes are unavailable")

    # Construct all reflected values before AssetTools creates a package. A
    # missing Python wrapper/property therefore refuses with no partial assets.
    specs = [make_card_spec(unreal_module, row, loaded_assets) for row in rows]
    candidate_class = reflected_type(unreal_module, "RPGBossProfileCard")
    require(candidate_class is not None, "reflected FRPGBossProfileCard Python type unavailable")
    created = {}
    for index, row in enumerate(rows):
        path = validate_write_path(PACKAGE_DIR + "/" + row["asset_name"])
        asset = asset_tools.create_asset(row["asset_name"], PACKAGE_DIR, card_class, unreal_module.DataAssetFactory())
        require(asset is not None, "card asset creation failed: " + path)
        set_property(asset, "spec", specs[index])
        created[row["move_id"]] = asset

    candidates = []
    # C-1251 removes the punish-failing fast swing from the active profile.
    # Its allowlisted standalone card is still validated and saved as source data.
    profile_rows = rows[:4]
    for row in profile_rows:
        candidate = candidate_class()
        fields = {
            "card": created[row["move_id"]],
            "cooldown_seconds": row["cooldown_seconds"], "weight": row["candidate_weight"],
            "hyper_armor": False, "kite_weight_multiplier": 1.0, "hug_weight_multiplier": 1.0,
            "back_dodge_weight_multiplier": 1.0, "greed_weight_multiplier": 1.0,
            "heavy_finisher": False,
        }
        for name, value in fields.items():
            set_property(candidate, name, value)
        candidates.append(candidate)

    profile = asset_tools.create_asset(PROFILE_NAME, PACKAGE_DIR, profile_class, unreal_module.DataAssetFactory())
    definition = asset_tools.create_asset(DEFINITION_NAME, PACKAGE_DIR, definition_class, unreal_module.DataAssetFactory())
    require(profile is not None and definition is not None, "profile/definition asset creation failed")
    for name, value in profile_values.items():
        set_property(profile, name, value)
    set_property(profile, "cards", ue_array(unreal_module, candidate_class, candidates))
    for name, value in definition_values.items():
        set_property(definition, name, value)
    set_property(definition, "use_montage_notify_timings", False)

    validate_card, validate_profile = bridge
    # Native CompileResolved checks the actual sequence/skeleton/mesh/slot and
    # trace endpoints. The profile bridge then runs ValidateProfile/ResolveProfile.
    for row in rows:
        card = created[row["move_id"]]
        raw = validate_card(card, loaded_assets["mesh"])
        valid, diagnostics = unpack_validation_result(raw, row["move_id"])
        for diagnostic in diagnostics:
            print("[SevarogDraft] VALIDATION " + row["move_id"] + ": " + diagnostic)
        require(valid and not diagnostics,
                row["move_id"] + " failed C++ validation; no assets were saved")

    raw = validate_profile(profile)
    valid, diagnostics = unpack_validation_result(raw, "framework profile")
    for diagnostic in diagnostics:
        print("[SevarogDraft] VALIDATION framework profile: " + diagnostic)
    require(valid and not diagnostics,
            "framework profile failed C++ validation; no assets were saved")

    # Save only after every card and the complete profile pass production C++.
    for asset in list(created.values()) + [profile, definition]:
        require(asset.get_path_name().startswith("/Game/OneBossFight/Data/Sevarog/"),
                "created package escaped allowlist")
        require(unreal_module.EditorAssetLibrary.save_loaded_asset(asset),
                "save failed for " + str(asset.get_path_name()))
        unreal_module.log("[SevarogDraft] SAVED " + str(asset.get_path_name()))


def dry_run(unreal_module, rows, bridge):
    """Run the production authoring path on transient objects; never create packages or save."""
    target_paths = [PACKAGE_DIR + "/" + DEFINITION_NAME, PACKAGE_DIR + "/" + PROFILE_NAME]
    target_paths.extend(PACKAGE_DIR + "/" + name for name in CARD_NAMES)
    for path in target_paths:
        require(not unreal_module.EditorAssetLibrary.does_asset_exist(path),
                "dry-run refuses because write target exists: " + path)

    loaded_assets = {}
    for path in (SKELETON_PATH,) + SEQUENCE_PATHS + (SEVAROG_ROOT + "/Meshes/Sevarog.Sevarog",):
        asset = unreal_module.EditorAssetLibrary.load_asset(path.split(".", 1)[0])
        require(asset is not None and str(asset.get_path_name()) == path,
                "dry-run read dependency did not resolve exactly: " + path)
        key = "skeleton" if path == SKELETON_PATH else (
            "mesh" if path.endswith("/Meshes/Sevarog.Sevarog") else path)
        loaded_assets[key] = asset
    clamp_marked_recovery_to_clip(rows, loaded_assets)

    card_class = unreal_module.load_class(None, "/Script/OneBossFight.RPGBossMoveCard")
    profile_class = unreal_module.load_class(None, "/Script/OneBossFight.RPGBossFrameworkProfile")
    definition_class = unreal_module.load_class(None, "/Script/OneBossFight.RPGBossDefinition")
    require(card_class is not None and profile_class is not None and definition_class is not None,
            "dry-run required DataAsset class unavailable")
    new_object = getattr(unreal_module, "new_object", None)
    require(callable(new_object), "unreal.new_object unavailable; cannot guarantee transient dry-run")

    created = {}
    for row in rows:
        card = new_object(card_class)
        require(card is not None and not str(card.get_path_name()).startswith("/Game/"),
                "card was not created in transient package")
        set_property(card, "spec", make_card_spec(unreal_module, row, loaded_assets))
        created[row["move_id"]] = card

    profile = new_object(profile_class)
    definition = new_object(definition_class)
    require(profile is not None and definition is not None and
            not str(profile.get_path_name()).startswith("/Game/") and
            not str(definition.get_path_name()).startswith("/Game/"),
            "profile/definition was not created in transient package")
    for name, value in FRAMEWORK_PROFILE_FIELDS.items():
        set_property(profile, name, materialize_approved_value(unreal_module, value, created))
    profile_cards = []
    candidate_class = reflected_type(unreal_module, "RPGBossProfileCard")
    for row in rows[:4]:
        candidate = candidate_class()
        fields = {
            "card": created[row["move_id"]], "cooldown_seconds": row["cooldown_seconds"],
            "weight": row["candidate_weight"], "hyper_armor": False,
            "kite_weight_multiplier": 1.0, "hug_weight_multiplier": 1.0,
            "back_dodge_weight_multiplier": 1.0, "greed_weight_multiplier": 1.0,
            "heavy_finisher": False,
        }
        for name, value in fields.items():
            set_property(candidate, name, value)
        profile_cards.append(candidate)
    set_property(profile, "cards", ue_array(unreal_module, candidate_class, profile_cards))
    for name, value in DRAFT_DEFINITION_FIELDS.items():
        set_property(definition, name, materialize_approved_value(unreal_module, value, created))
    set_property(definition, "use_montage_notify_timings", False)

    validate_card, validate_profile = bridge
    for row in rows:
        raw = validate_card(created[row["move_id"]], loaded_assets["mesh"])
        valid, diagnostics = unpack_validation_result(raw, row["move_id"])
        print("[SevarogDraft] VALIDATOR move=%s verdict=%s diagnostics=%s" %
              (row["move_id"], "PASS" if valid and not diagnostics else "FAIL", diagnostics))
        require(valid and not diagnostics,
                row["move_id"] + " failed C++ validation; dry-run saved nothing")
    valid, diagnostics = unpack_validation_result(validate_profile(profile), "framework profile")
    print("[SevarogDraft] VALIDATOR framework_profile verdict=%s diagnostics=%s" %
          ("PASS" if valid and not diagnostics else "FAIL", diagnostics))
    require(valid and not diagnostics, "framework profile failed C++ validation; dry-run saved nothing")

    # ValidateProfile emits authoritative punish_check and defense_check numbers
    # from the production formulas into the UE log. Also print every authored input.
    for row in rows[:4]:
        print("[SevarogDraft] DRY_RUN_CARD move=%s activeEnd=%.6f recoveryEnd=%.6f playRate=%.6f maxRangeCm=%.3f defensive=%d warpAway=%d warpDistanceCm=%.3f warpStandoffCm=%.3f" %
              (row["move_id"], row["active_end_seconds"], row["recovery_end_seconds"], row["play_rate"],
               row["max_range_cm"], int(row["defensive"]), int(row["warp_away"]),
               row["warp_max_distance_cm"], row["warp_standoff_cm"]))
    for path in target_paths:
        require(not unreal_module.EditorAssetLibrary.does_asset_exist(path),
                "dry-run unexpectedly created a target package: " + path)
    print("[SevarogDraft] DRY-RUN COMPLETE all validators passed, 0 saved")


def main(unreal_module=None, dry_run_mode=False):
    if unreal_module is None:
        try:
            import unreal as unreal_module
        except ImportError as exc:
            raise Refusal("[SevarogDraft] REFUSED: run this script from UE Editor Python: " + str(exc))
    unreal_module = require_editor_module(unreal_module)

    project_root = Path(unreal_module.Paths.project_dir()).resolve()
    require(project_root.name.lower() == "onebossfight", "unexpected project root: " + str(project_root))
    require((project_root / "OneBossFight.uproject").is_file(), "expected .uproject not found under project root")
    require((project_root / CONTACT_SOURCE).is_file(), "contact marking source is missing")
    f5_cards = read_f5_cards(project_root)
    rows = build_candidate_specs(f5_cards)
    validate_source_coverage(rows)
    gates = unresolved_gates(rows)
    require(not gates, "unapproved values remain:\n - " + "\n - ".join(gates))
    log_punish_estimates(rows[:4])

    if dry_run_mode:
        bridge = get_cpp_validation_bridge(unreal_module)
        dry_run(unreal_module, rows, bridge)
        return

    bridge = get_cpp_validation_bridge(unreal_module)
    target_paths = [PACKAGE_DIR + "/" + DEFINITION_NAME, PACKAGE_DIR + "/" + PROFILE_NAME]
    target_paths.extend(PACKAGE_DIR + "/" + name for name in CARD_NAMES)
    for path in target_paths:
        validate_write_path(path)
        require(not unreal_module.EditorAssetLibrary.does_asset_exist(path),
                "target already exists; never overwrite or recreate: " + path)

    # Load dependencies read-only and verify exact identities before creating
    # project-owned unsaved assets. The native bridge performs resolved checks.
    loaded_assets = {}
    for path in (SKELETON_PATH,) + SEQUENCE_PATHS:
        package_path = path.split(".", 1)[0]
        require(package_path.startswith(SEVAROG_ROOT + "/"), "non-Sevarog read dependency refused: " + path)
        asset = unreal_module.EditorAssetLibrary.load_asset(package_path)
        require(asset is not None and str(asset.get_path_name()) == path,
                "Sevarog read-only dependency did not resolve exactly: " + path)
        loaded_assets["skeleton" if path == SKELETON_PATH else path] = asset
    loaded_assets["mesh"] = unreal_module.EditorAssetLibrary.load_asset(
        SEVAROG_ROOT + "/Meshes/Sevarog.Sevarog")
    require(loaded_assets["mesh"] is not None and
            str(loaded_assets["mesh"].get_path_name()) == SEVAROG_ROOT + "/Meshes/Sevarog.Sevarog",
            "Sevarog mesh did not resolve exactly")
    clamp_marked_recovery_to_clip(rows, loaded_assets)
    create_and_validate_assets(unreal_module, rows, loaded_assets, bridge)


if __name__ == "__main__":
    main(dry_run_mode=("--dry-run" in sys.argv or os.environ.get("SEVAROG_DRY_RUN") == "1"))
