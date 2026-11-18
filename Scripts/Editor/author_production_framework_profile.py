"""Authoring script for DA_Boss_Sevarog_FrameworkProfile_Production.

Applies owner-approved O1 boss stats (Stats.MaxHealth=1500, Posture=100, Phase 2 at 60%)
to a dedicated production framework profile, preserving the F5 test fixture untouched.
TargetHealth (player health) has no owner-approved default and must be explicitly supplied.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

PACKAGE_DIR = "/Game/OneBossFight/Data/Sevarog"
PROFILE_NAME = "DA_Boss_Sevarog_FrameworkProfile_Production"
ASSET_PATH = PACKAGE_DIR + "/" + PROFILE_NAME
F5_FIXTURE_PATH = PACKAGE_DIR + "/DA_Boss_Sevarog_FrameworkProfile_Draft"
ENCOUNTER_PATH = PACKAGE_DIR + "/DA_Sevarog_Framework_Encounter"
ENCOUNTER_NAME = "DA_Sevarog_Framework_Encounter"
BOSS_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft"
PLAYER_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3"
ENCOUNTER_PHASE = "Phase_1"
SEVAROG_ROOT = "/Game/ParagonSevarog/Characters/Heroes/Sevarog"

PRODUCTION_CARD_SPECS = (
    ("DA_Move_Sevarog_Swing1_Medium_C1247", 0.0, 1.0),
    ("DA_Move_Sevarog_Swing2_Medium_C1247", 0.0, 1.0),
    ("DA_Move_Sevarog_Swing3_Slow_C1247", 0.0, 1.0),
    ("DA_Move_Sevarog_Speedburst_C1247", 4.0, 1.0),
    ("DA_Move_Sevarog_Ultimate_Swing_120fps_C1277", 6.0, 1.0),
    ("DA_Move_Sevarog_Subjugation_C1277", 8.0, 1.0),
    ("DA_Move_Sevarog_Soul_Siphon_C1277", 10.0, 1.0),
)

REFLECTED_TYPE_ALIASES = {
    "RPGBossProfileCard": ("RpgBossProfileCard",),
    "RPGBossComboEdgeData": ("RpgBossComboEdgeData",),
    "RPGBossComboNodeData": ("RpgBossComboNodeData",),
    "RPGBossComboOutcome": ("RpgBossComboOutcome", "ERpgBossComboOutcome", "ERPGBossComboOutcome"),
    "RPGBossCardValidationLibrary": ("RpgBossCardValidationLibrary",),
}


class Refusal(RuntimeError):
    pass


def require(ok, message):
    if not ok:
        raise Refusal("[ProductionProfileAuthor] REFUSED: " + message)


def approved_float_matches(actual, expected, tol=1e-4):
    """Compare reflected Unreal float32 readbacks to approved values (consistent with C-1623)."""
    try:
        actual_number = float(actual)
        expected_number = float(expected)
    except (TypeError, ValueError, OverflowError):
        return False
    return (math.isfinite(actual_number) and math.isfinite(expected_number)
            and abs(actual_number - expected_number) <= tol)


EXACT_APPROVED_TARGET_HEALTH = 800.0


def parse_target_health(argv=None, environ=None, target_health_arg=None):
    """Extract and validate mandatory TargetHealth input.

    TargetHealth has an owner-approved production value of 800.0 HP.
    It must be explicitly supplied with no implicit fallback default via
    target_health_arg, --target-health <float>, or SEVAROG_TARGET_HEALTH.
    Fails closed if missing, non-numeric, non-finite, or different from the approved 800.0 HP value.
    """
    raw_val = target_health_arg
    if raw_val is None:
        if argv is None:
            argv = sys.argv[1:]
        if environ is None:
            environ = os.environ

        for i, arg in enumerate(argv):
            if arg == "--target-health" and i + 1 < len(argv):
                raw_val = argv[i + 1]
                break
            if arg.startswith("--target-health="):
                raw_val = arg.split("=", 1)[1]
                break

        if raw_val is None:
            raw_val = environ.get("SEVAROG_TARGET_HEALTH")

    if raw_val is None or (isinstance(raw_val, str) and raw_val.strip() == ""):
        raise Refusal(
            "TargetHealth is mandatory and has no default value. "
            "Supply --target-health 800.0 or set SEVAROG_TARGET_HEALTH=800.0."
        )

    if isinstance(raw_val, bool):
        raise Refusal("TargetHealth must be numeric, got boolean")

    try:
        val = float(raw_val)
    except (TypeError, ValueError, OverflowError) as exc:
        raise Refusal("TargetHealth must be numeric: " + str(exc))

    if not math.isfinite(val) or val <= 0.0:
        raise Refusal("TargetHealth must be a positive finite float, got: %r" % raw_val)

    if val != EXACT_APPROVED_TARGET_HEALTH:
        raise Refusal(
            "TargetHealth value %g does not match owner-approved production value %g"
            % (val, EXACT_APPROVED_TARGET_HEALTH)
        )

    return val


EXACT_APPROVED_O1_VALUES = {
    "Stats.MaxHealth": 1500.0,
    "Stats.MaxPosture": 100.0,
    "Stats.PostureRegenDelay": 6.0,
    "Stats.PostureRegenRate": 13.0,
    "Phases[Phase_1].EntryHealthFraction": 0.6,
}


def load_o1_values(project_root):
    """Load and validate approved O1 boss parameters from sevarog_o1_inputs.json."""
    inputs_path = Path(project_root) / "Scripts/Editor/sevarog_o1_inputs.json"
    require(inputs_path.is_file(), "O1 inputs file missing: " + str(inputs_path))
    data = json.loads(inputs_path.read_text(encoding="utf-8"))
    values = data.get("values", {})
    for key, expected_val in EXACT_APPROVED_O1_VALUES.items():
        require(key in values, "O1 missing required key: " + key)
        val = float(values[key])
        require(math.isfinite(val) and val == expected_val,
                "O1 key %s value %g does not match exact approved value %g" % (key, val, expected_val))
    return values


def build_profile_payload(o1_values, target_health):
    """Build the canonical profile configuration dictionary."""
    return {
        "fixture_label": "Production",
        "mesh": {"$soft_object": SEVAROG_ROOT + "/Meshes/Sevarog.Sevarog"},
        "anim_class": {"$soft_class": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C"},
        "target_pawn_class": {"$soft_class": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C"},
        "band_min_cm": 110.0,
        "band_max_cm": 140.0,
        "walk_speed_cm_per_second": 180.0,
        "acceptance_cm": 5.0,
        "walk_timeout_seconds": 10.0,
        "blend_in_seconds": 0.1,
        "blend_out_seconds": 0.03,
        "capsule_radius_cm": 60.0,
        "capsule_half_height_cm": 165.0,
        "target_health": float(target_health),
        "damage_enabled": True,
        "hit_step_cm": 15.0,
        "hit_max_substeps": 8,
        "repeat_penalty": 0.2,
        "repeat_memory": 2,
        "attack_count": 3,
        "range_band_partition": True,
        "boss_max_health": float(o1_values["Stats.MaxHealth"]),
        "player_hit_damage": 100.0,
        "alignment_authored": True,
        "mesh_relative_transform": {"$runtime_transform": True},
        "combo_root": "S4",
        "combo_max_depth": 2,
        "combo_nodes": {"$runtime_combo": "S4_WHiff_S5_MEDIUM"},
        "punish_margin_seconds": 0.3,
        "player_light_montage": {"$soft_object": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage.Attack_PrimaryA_Montage"},
        "player_heavy_montage": {"$soft_object": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/ChargedAttack_Montage.ChargedAttack_Montage"},
        "player_reach_cm": 150.0,
        "phase_two_fraction": float(o1_values["Phases[Phase_1].EntryHealthFraction"]),
        "phase_two_id": "Phase_2",
        "posture_max": float(o1_values["Stats.MaxPosture"]),
        "posture_regen_delay_seconds": float(o1_values["Stats.PostureRegenDelay"]),
        "posture_regen_per_second": float(o1_values["Stats.PostureRegenRate"]),
        "player_posture_hit_amount": 60.0,
        "stagger_seconds": 2.5,
    }


def compute_manifest_hash(payload):
    """Compute deterministic SHA256 of canonical profile payload."""
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def reflected_type(unreal_module, exact_name):
    """Resolve reflected class or struct type."""
    for name in (exact_name,) + REFLECTED_TYPE_ALIASES.get(exact_name, ()):
        val = getattr(unreal_module, name, None)
        if val is not None:
            return val
    return None


def set_property(obj, field_name, value):
    """Set a reflected property; fails closed without silently ignoring errors."""
    names = [field_name]
    if field_name.startswith("b_"):
        names.append(field_name[2:])
    if field_name and field_name[0].isupper():
        names.append("".join(("_" + c.lower()) if c.isupper() else c for c in field_name).lstrip("_"))
    last_error = None
    for name in names:
        try:
            obj.set_editor_property(name, value)
            return
        except Exception as exc:
            last_error = exc
    raise Refusal("Property write failed for " + field_name + ": " + str(last_error))


def ue_array(unreal_module, element_type, values):
    """Build a reflected Unreal array."""
    array_type = getattr(unreal_module, "Array", None)
    require(callable(array_type), "unreal.Array unavailable for reflected array")
    result = array_type(element_type)
    for value in values:
        result.append(value)
    return result


def build_combo(unreal_module):
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
        set_property(edge, name, value)
    first, second = node_class(), node_class()
    for node, name, move, edges in (
        (first, "S4", "Move_Sevarog_Speedburst", ue_array(unreal_module, edge_class, [edge])),
        (second, "S5", "Move_Sevarog_Swing1_Medium", ue_array(unreal_module, edge_class, [])),
    ):
        for field, value in {"node_id": name, "move_id": move, "edges": edges}.items():
            set_property(node, field, value)
    return ue_array(unreal_module, node_class, [first, second])


def materialize_value(unreal_module, value):
    """Materialize typed descriptors into live Unreal Engine objects/structs."""
    if isinstance(value, dict):
        if "$soft_object" in value:
            obj_path = value["$soft_object"]
            package_path = obj_path.split(".", 1)[0]
            require(package_path.startswith("/Game/ParagonSevarog/") or
                    package_path.startswith("/Game/OneBossFight/") or
                    package_path.startswith("/Game/AdvancedARPGCombat/"),
                    "Disallowed reference path: " + package_path)
            asset = unreal_module.EditorAssetLibrary.load_asset(package_path)
            require(asset is not None and str(asset.get_path_name()) == obj_path,
                    "Soft object failed to resolve: " + obj_path)
            return asset
        if "$soft_class" in value:
            cls_path = value["$soft_class"]
            klass = unreal_module.load_class(None, cls_path)
            require(klass is not None, "Soft class failed to resolve: " + cls_path)
            return klass
        if "$runtime_transform" in value:
            return unreal_module.Transform(
                location=[0.0, 0.0, -165.0],
                rotation=unreal_module.Rotator(roll=0.0, pitch=0.0, yaw=-90.0),
                scale=[1.0, 1.0, 1.0],
            )
        if "$runtime_combo" in value:
            return build_combo(unreal_module)
        raise Refusal("Unsupported descriptor: " + str(value))
    return value


def get_cpp_validation_bridge(unreal_module):
    """Obtain the Editor C++ validation bridge."""
    library = reflected_type(unreal_module, "RPGBossCardValidationLibrary")
    require(library is not None, "RPGBossCardValidationLibrary bridge unavailable")
    validate_profile = getattr(library, "validate_framework_profile_report", None)
    require(callable(validate_profile), "validate_framework_profile_report bridge unavailable")
    return validate_profile


def unpack_validation_result(raw, label):
    """Unpack C++ validation report."""
    if isinstance(raw, str):
        if raw == "PASS":
            return True, []
        if raw.startswith("FAIL|"):
            return False, raw[5:].split(";")
        raise Refusal(label + " bridge returned unknown verdict: " + raw)
    if isinstance(raw, tuple) and len(raw) == 2:
        valid, diagnostics = raw
        require(type(valid) is bool, label + " bridge returned non-boolean verdict")
        return valid, [str(d) for d in list(diagnostics)]
    if type(raw).__name__ == "Array":
        diagnostics = [str(d) for d in raw]
        return not diagnostics, diagnostics
    raise Refusal(label + " bridge returned unsupported result: " + repr(raw))


def build_candidate_cards(unreal_module):
    """Build reflected FRPGBossProfileCard array from production card specs."""
    candidate_class = reflected_type(unreal_module, "RPGBossProfileCard")
    require(candidate_class is not None, "RPGBossProfileCard reflected type unavailable")
    candidates = []
    for asset_name, cooldown, weight in PRODUCTION_CARD_SPECS:
        card_path = PACKAGE_DIR + "/" + asset_name
        card_asset = unreal_module.EditorAssetLibrary.load_asset(card_path)
        require(card_asset is not None, "Required production card missing: " + card_path)
        candidate = candidate_class()
        set_property(candidate, "card", card_asset)
        set_property(candidate, "cooldown_seconds", cooldown)
        set_property(candidate, "weight", weight)
        set_property(candidate, "hyper_armor", False)
        set_property(candidate, "kite_weight_multiplier", 1.0)
        set_property(candidate, "hug_weight_multiplier", 1.0)
        set_property(candidate, "back_dodge_weight_multiplier", 1.0)
        set_property(candidate, "greed_weight_multiplier", 1.0)
        set_property(candidate, "heavy_finisher", False)
        candidates.append(candidate)
    return ue_array(unreal_module, candidate_class, candidates)


def apply_properties_to_profile(unreal_module, profile_obj, payload):
    """Apply and materialize all profile properties."""
    for key, val in payload.items():
        materialized = materialize_value(unreal_module, val)
        set_property(profile_obj, key, materialized)
    cards = build_candidate_cards(unreal_module)
    set_property(profile_obj, "cards", cards)


def verify_profile_readback(unreal_module, profile_obj, payload, validate_profile):
    """Assert exact property readback for all fields and cards, plus passing C++ validation."""
    scalar_fields = (
        ("fixture_label", str),
        ("band_min_cm", float),
        ("band_max_cm", float),
        ("walk_speed_cm_per_second", float),
        ("acceptance_cm", float),
        ("walk_timeout_seconds", float),
        ("blend_in_seconds", float),
        ("blend_out_seconds", float),
        ("capsule_radius_cm", float),
        ("capsule_half_height_cm", float),
        ("target_health", float),
        ("damage_enabled", bool),
        ("hit_step_cm", float),
        ("hit_max_substeps", int),
        ("repeat_penalty", float),
        ("repeat_memory", int),
        ("attack_count", int),
        ("range_band_partition", bool),
        ("boss_max_health", float),
        ("player_hit_damage", float),
        ("alignment_authored", bool),
        ("combo_root", str),
        ("combo_max_depth", int),
        ("punish_margin_seconds", float),
        ("player_reach_cm", float),
        ("phase_two_fraction", float),
        ("phase_two_id", str),
        ("posture_max", float),
        ("posture_regen_delay_seconds", float),
        ("posture_regen_per_second", float),
        ("player_posture_hit_amount", float),
        ("stagger_seconds", float),
    )
    for field_name, field_type in scalar_fields:
        val = profile_obj.get_editor_property(field_name)
        expected = payload[field_name]
        if field_type is float:
            require(approved_float_matches(val, expected), "%s readback mismatch: %r != %r" % (field_name, val, expected))
        elif field_type is bool:
            require(bool(val) == bool(expected), "%s readback mismatch: %r != %r" % (field_name, val, expected))
        elif field_type is int:
            require(int(val) == int(expected), "%s readback mismatch: %r != %r" % (field_name, val, expected))
        else:
            require(str(val) == str(expected), "%s readback mismatch: %r != %r" % (field_name, val, expected))

    soft_ref_fields = (
        ("mesh", "$soft_object"),
        ("anim_class", "$soft_class"),
        ("target_pawn_class", "$soft_class"),
        ("player_light_montage", "$soft_object"),
        ("player_heavy_montage", "$soft_object"),
    )
    for field_name, desc_key in soft_ref_fields:
        ref_obj = profile_obj.get_editor_property(field_name)
        expected_path = payload[field_name][desc_key]
        actual_path = str(ref_obj.get_path_name()) if hasattr(ref_obj, "get_path_name") else str(ref_obj)
        require(actual_path == expected_path,
                "%s readback exact path mismatch: %r != %r" % (field_name, actual_path, expected_path))

    cards = profile_obj.get_editor_property("cards")
    require(len(cards) == len(PRODUCTION_CARD_SPECS), "cards array length mismatch: %d != %d" % (len(cards), len(PRODUCTION_CARD_SPECS)))
    for i, (spec_name, spec_cooldown, spec_weight) in enumerate(PRODUCTION_CARD_SPECS):
        c = cards[i]
        card_asset = c.get_editor_property("card")
        expected_card_path = PACKAGE_DIR + "/" + spec_name + "." + spec_name
        card_actual_path = str(card_asset.get_path_name()) if hasattr(card_asset, "get_path_name") else str(card_asset)
        require(card_actual_path == expected_card_path,
                "card[%d] exact asset mismatch: %r != %r" % (i, card_actual_path, expected_card_path))
        require(approved_float_matches(c.get_editor_property("cooldown_seconds"), spec_cooldown),
                "card[%d] cooldown mismatch" % i)
        require(approved_float_matches(c.get_editor_property("weight"), spec_weight),
                "card[%d] weight mismatch" % i)
        require(bool(c.get_editor_property("hyper_armor")) is False,
                "card[%d] hyper_armor mismatch" % i)
        require(approved_float_matches(c.get_editor_property("kite_weight_multiplier"), 1.0),
                "card[%d] kite_weight_multiplier mismatch" % i)
        require(approved_float_matches(c.get_editor_property("hug_weight_multiplier"), 1.0),
                "card[%d] hug_weight_multiplier mismatch" % i)
        require(approved_float_matches(c.get_editor_property("back_dodge_weight_multiplier"), 1.0),
                "card[%d] back_dodge_weight_multiplier mismatch" % i)
        require(approved_float_matches(c.get_editor_property("greed_weight_multiplier"), 1.0),
                "card[%d] greed_weight_multiplier mismatch" % i)
        require(bool(c.get_editor_property("heavy_finisher")) is False,
                "card[%d] heavy_finisher mismatch" % i)

    # Exact mesh_relative_transform readback
    tf = profile_obj.get_editor_property("mesh_relative_transform")
    loc = getattr(tf, "translation", getattr(tf, "location", None))
    rot = getattr(tf, "rotation", None)
    scale = getattr(tf, "scale3d", None)
    require(loc is not None and rot is not None and scale is not None, "mesh_relative_transform missing components")
    require(approved_float_matches(loc.x, 0.0) and approved_float_matches(loc.y, 0.0) and approved_float_matches(loc.z, -165.0),
            "mesh_relative_transform location mismatch: (%g, %g, %g) != (0, 0, -165)" % (float(loc.x), float(loc.y), float(loc.z)))
    # Fail-closed rotation validation: supports Rotator or FQuat representations
    rot_obj = None
    if hasattr(rot, "rotator") and callable(rot.rotator):
        rot_obj = rot.rotator()
    elif hasattr(rot, "to_rotator") and callable(rot.to_rotator):
        rot_obj = rot.to_rotator()
    elif hasattr(rot, "yaw") and hasattr(rot, "pitch") and hasattr(rot, "roll"):
        rot_obj = rot
    elif hasattr(rot, "x") and hasattr(rot, "y") and hasattr(rot, "z") and hasattr(rot, "w"):
        # FQuat representation: roll 0, pitch 0, yaw -90 degrees -> z = -sin(pi/4), w = cos(pi/4)
        qx, qy, qz, qw = float(rot.x), float(rot.y), float(rot.z), float(rot.w)
        expected_z = -math.sin(math.pi / 4.0)
        expected_w = math.cos(math.pi / 4.0)
        match_direct = (abs(qx) < 1e-4 and abs(qy) < 1e-4 and abs(qz - expected_z) < 1e-4 and abs(qw - expected_w) < 1e-4)
        match_inverted = (abs(qx) < 1e-4 and abs(qy) < 1e-4 and abs(qz + expected_z) < 1e-4 and abs(qw + expected_w) < 1e-4)
        require(match_direct or match_inverted,
                "mesh_relative_transform quat mismatch: (x=%g, y=%g, z=%g, w=%g)" % (qx, qy, qz, qw))
    else:
        raise Refusal("mesh_relative_transform rotation has unknown/unsupported type: " + repr(rot))

    if rot_obj is not None:
        yaw_val = getattr(rot_obj, "yaw", None)
        pitch_val = getattr(rot_obj, "pitch", None)
        roll_val = getattr(rot_obj, "roll", None)
        require(yaw_val is not None and pitch_val is not None and roll_val is not None,
                "mesh_relative_transform rotator missing yaw/pitch/roll")
        require(approved_float_matches(yaw_val, -90.0) and approved_float_matches(pitch_val, 0.0) and approved_float_matches(roll_val, 0.0),
                "mesh_relative_transform rotator mismatch: roll=%g, pitch=%g, yaw=%g" % (float(roll_val), float(pitch_val), float(yaw_val)))
    require(approved_float_matches(scale.x, 1.0) and approved_float_matches(scale.y, 1.0) and approved_float_matches(scale.z, 1.0),
            "mesh_relative_transform scale mismatch: (%g, %g, %g) != (1, 1, 1)" % (float(scale.x), float(scale.y), float(scale.z)))

    # Exact combo graph readback
    require(str(profile_obj.get_editor_property("combo_root")) == "S4", "combo_root mismatch")
    require(int(profile_obj.get_editor_property("combo_max_depth")) == 2, "combo_max_depth mismatch")
    combo_nodes = profile_obj.get_editor_property("combo_nodes")
    require(len(combo_nodes) == 2, "combo_nodes length mismatch: %d != 2" % len(combo_nodes))
    node0, node1 = combo_nodes[0], combo_nodes[1]
    require(str(node0.get_editor_property("node_id")) == "S4", "combo node[0] id mismatch")
    require(str(node0.get_editor_property("move_id")) == "Move_Sevarog_Speedburst", "combo node[0] move mismatch")
    edges0 = node0.get_editor_property("edges")
    require(len(edges0) == 1, "combo node[0] edges count mismatch: %d != 1" % len(edges0))
    e0 = edges0[0]
    require(str(e0.get_editor_property("to_node")) == "S5", "combo edge[0] to_node mismatch")
    require(approved_float_matches(e0.get_editor_property("min_range_cm"), 0.0), "combo edge[0] min_range mismatch")
    require(approved_float_matches(e0.get_editor_property("max_range_cm"), 1.0e6), "combo edge[0] max_range mismatch")
    require(approved_float_matches(e0.get_editor_property("max_abs_yaw_degrees"), 180.0), "combo edge[0] max_abs_yaw mismatch")
    require(bool(e0.get_editor_property("any_outcome")) is False, "combo edge[0] any_outcome mismatch")
    outcome_str = str(e0.get_editor_property("outcome")).upper()
    require("WHIFF" in outcome_str, "combo edge[0] outcome is not WHIFF: %s" % outcome_str)

    require(str(node1.get_editor_property("node_id")) == "S5", "combo node[1] id mismatch")
    require(str(node1.get_editor_property("move_id")) == "Move_Sevarog_Swing1_Medium", "combo node[1] move mismatch")
    edges1 = node1.get_editor_property("edges")
    require(len(edges1) == 0, "combo node[1] edges count mismatch: %d != 0" % len(edges1))

    valid, diagnostics = unpack_validation_result(validate_profile(profile_obj), "persisted production profile")
    require(valid and not diagnostics, "persisted profile failed C++ validation: " + ";".join(diagnostics))


def build_encounter_payload(profile_path=ASSET_PATH):
    return {
        "schema": 1,
        "boss_slot": "Boss",
        "player_slot": "Player",
        "initial_boss_phase": ENCOUNTER_PHASE,
        "boss_definition": BOSS_PATH,
        "player_definition": PLAYER_PATH,
        "use_framework_boss": True,
        "framework_boss_profile": profile_path,
    }


def compute_encounter_manifest_hash(payload):
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def verify_encounter_readback(unreal, encounter_asset, expected_manifest_hash, expected_profile_path):
    require(encounter_asset is not None, "Encounter asset is None")
    path_str = str(encounter_asset.get_path_name())
    require(path_str.startswith(ENCOUNTER_PATH), "Encounter path mismatch: " + path_str)

    actual_hash = str(encounter_asset.get_editor_property("stable_manifest_hash"))
    require(
        actual_hash == expected_manifest_hash,
        "Encounter stable_manifest_hash mismatch: %r != %r" % (actual_hash, expected_manifest_hash),
    )
    require(str(encounter_asset.get_editor_property("boss_slot")) == "Boss", "Encounter boss_slot mismatch")
    require(str(encounter_asset.get_editor_property("player_slot")) == "Player", "Encounter player_slot mismatch")
    require(
        str(encounter_asset.get_editor_property("initial_boss_phase")) == ENCOUNTER_PHASE,
        "Encounter initial_boss_phase mismatch",
    )
    require(
        bool(encounter_asset.get_editor_property("use_framework_boss")) is True,
        "Encounter use_framework_boss is not True",
    )

    prof = encounter_asset.get_editor_property("framework_boss_profile")
    require(prof is not None, "Encounter framework_boss_profile is None")
    prof_path = str(prof.get_path_name())
    require(
        prof_path == expected_profile_path or prof_path == expected_profile_path + "." + PROFILE_NAME,
        "Encounter framework_boss_profile path mismatch: %r != %r" % (prof_path, expected_profile_path),
    )

    boss_def = encounter_asset.get_editor_property("boss_definition")
    require(boss_def is not None, "Encounter boss_definition is None")
    boss_path = str(boss_def.get_path_name())
    require(
        boss_path == BOSS_PATH or boss_path == BOSS_PATH + ".DA_Boss_Sevarog_Draft",
        "Encounter boss_definition mismatch: " + boss_path,
    )

    player_def = encounter_asset.get_editor_property("player_definition")
    require(player_def is not None, "Encounter player_definition is None")
    player_path = str(player_def.get_path_name())
    require(
        player_path == PLAYER_PATH or player_path == PLAYER_PATH + ".DA_Player_Hero_Draft_V3",
        "Encounter player_definition mismatch: " + player_path,
    )

    guid_str = str(encounter_asset.get_editor_property("encounter_instance"))
    require(guid_str not in ("", "00000000-00000000-00000000-00000000"), "Encounter instance GUID invalid")


def write_receipt_file(receipt):
    receipt_out_path = os.environ.get("SEVAROG_AUTHOR_RECEIPT_PATH")
    if not receipt_out_path:
        for i, a in enumerate(sys.argv[1:]):
            if a == "--receipt" and i + 1 < len(sys.argv[1:]):
                receipt_out_path = sys.argv[1:][i + 1]
                break
            if a.startswith("--receipt="):
                receipt_out_path = a.split("=", 1)[1]
                break

    if receipt_out_path:
        out_p = Path(receipt_out_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        tmp_p = out_p.with_suffix(".tmp")
        tmp_p.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp_p.replace(out_p)


def main(unreal_module=None, dry_run=False, write=False, readback=False, target_health_arg=None, rebind_encounter=False):
    if dry_run:
        write = False
    project_root = Path(__file__).resolve().parents[2]
    target_health = parse_target_health(target_health_arg=target_health_arg)

    o1_values = load_o1_values(project_root)
    payload = build_profile_payload(o1_values, target_health)
    manifest_hash = compute_manifest_hash(payload)

    # Safety assertions
    require(ASSET_PATH != F5_FIXTURE_PATH, "Must never overwrite F5 fixture")
    require(ASSET_PATH != ENCOUNTER_PATH, "Target path must not be encounter path")
    require(ASSET_PATH.startswith(PACKAGE_DIR + "/"), "Target path must be within " + PACKAGE_DIR)

    enc_payload = build_encounter_payload(ASSET_PATH)
    enc_manifest_hash = compute_encounter_manifest_hash(enc_payload)

    receipt = {
        "task": "author_production_framework_profile",
        "target_path": ASSET_PATH,
        "manifest_hash": manifest_hash,
        "boss_max_health": payload["boss_max_health"],
        "target_health": payload["target_health"],
        "posture_max": payload["posture_max"],
        "player_posture_hit_amount": payload["player_posture_hit_amount"],
        "stagger_seconds": payload["stagger_seconds"],
        "phase_two_fraction": payload["phase_two_fraction"],
        "fixture_label": payload["fixture_label"],
        "cards_count": len(PRODUCTION_CARD_SPECS),
        "f5_fixture_preserved": F5_FIXTURE_PATH,
        "rebind_encounter": rebind_encounter,
        "encounter_path": ENCOUNTER_PATH,
        "encounter_manifest_hash": enc_manifest_hash if rebind_encounter else None,
        "encounter_binding": ASSET_PATH if rebind_encounter else F5_FIXTURE_PATH,
        "mode": "readback" if readback else ("write" if write else "dry_run"),
    }

    if unreal_module is None:
        try:
            import unreal as unreal_module
        except ImportError:
            unreal_module = None

    if unreal_module is None:
        write_receipt_file(receipt)
        print("[ProductionProfileAuthor] OFFLINE_RECEIPT: " + json.dumps(receipt, indent=2, sort_keys=True))
        return receipt

    unreal = unreal_module
    profile_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossFrameworkProfile")
    require(profile_class is not None, "RPGBossFrameworkProfile class unavailable")
    validate_profile = get_cpp_validation_bridge(unreal)

    if readback:
        asset = unreal.EditorAssetLibrary.load_asset(ASSET_PATH)
        require(asset is not None, "Production profile asset does not exist for readback: " + ASSET_PATH)
        verify_profile_readback(unreal, asset, payload, validate_profile)
        if rebind_encounter:
            encounter = unreal.EditorAssetLibrary.load_asset(ENCOUNTER_PATH)
            require(encounter is not None, "Encounter asset does not exist for readback: " + ENCOUNTER_PATH)
            verify_encounter_readback(unreal, encounter, enc_manifest_hash, ASSET_PATH)
        write_receipt_file(receipt)
        unreal.log("[ProductionProfileAuthor] READBACK_PASS " + json.dumps(receipt, sort_keys=True))
        return receipt

    # In dry-run and write mode, validate full transient profile first
    transient_profile = unreal.new_object(profile_class)
    require(transient_profile is not None, "Transient profile object creation failed")
    apply_properties_to_profile(unreal, transient_profile, payload)

    valid, diagnostics = unpack_validation_result(validate_profile(transient_profile), "transient production profile")
    require(valid and not diagnostics, "Transient profile failed C++ validation: " + ";".join(diagnostics))

    if not write:
        if rebind_encounter:
            encounter = unreal.EditorAssetLibrary.load_asset(ENCOUNTER_PATH)
            require(encounter is not None, "Encounter asset does not exist for dry-run: " + ENCOUNTER_PATH)
            enc_class = unreal.load_class(None, "/Script/OneBossFight.RPGBossEncounterDefinition")
            require(enc_class is not None, "RPGBossEncounterDefinition class unavailable")
            require(
                encounter.get_class() == enc_class or encounter.get_class().is_child_of(enc_class),
                "Encounter class mismatch: " + str(encounter.get_class()),
            )
        write_receipt_file(receipt)
        unreal.log("[ProductionProfileAuthor] DRY_RUN_PASS " + json.dumps(receipt, sort_keys=True))
        return receipt

    # Write mode
    asset = unreal.EditorAssetLibrary.load_asset(ASSET_PATH)
    if not asset:
        asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            PROFILE_NAME, PACKAGE_DIR, profile_class, unreal.DataAssetFactory()
        )
    require(asset is not None, "Production profile asset creation failed: " + ASSET_PATH)

    apply_properties_to_profile(unreal, asset, payload)
    require(unreal.EditorAssetLibrary.save_loaded_asset(asset), "Production profile asset save failed: " + ASSET_PATH)

    # Full reload and readback assertion
    reloaded_asset = unreal.EditorAssetLibrary.load_asset(ASSET_PATH)
    require(reloaded_asset is not None, "Reloading saved production profile failed: " + ASSET_PATH)
    verify_profile_readback(unreal, reloaded_asset, payload, validate_profile)

    if rebind_encounter:
        encounter = unreal.EditorAssetLibrary.load_asset(ENCOUNTER_PATH)
        require(encounter is not None, "Encounter asset does not exist for rebind: " + ENCOUNTER_PATH)
        encounter.set_editor_property("framework_boss_profile", reloaded_asset)
        encounter.set_editor_property("stable_manifest_hash", enc_manifest_hash)
        encounter.set_editor_property("use_framework_boss", True)
        encounter.set_editor_property("boss_slot", "Boss")
        encounter.set_editor_property("player_slot", "Player")
        encounter.set_editor_property("initial_boss_phase", ENCOUNTER_PHASE)
        require(unreal.EditorAssetLibrary.save_loaded_asset(encounter), "Encounter asset save failed: " + ENCOUNTER_PATH)

        reloaded_encounter = unreal.EditorAssetLibrary.load_asset(ENCOUNTER_PATH)
        require(reloaded_encounter is not None, "Reloading saved encounter failed: " + ENCOUNTER_PATH)
        verify_encounter_readback(unreal, reloaded_encounter, enc_manifest_hash, ASSET_PATH)

    write_receipt_file(receipt)
    unreal.log("[ProductionProfileAuthor] WRITTEN_PASS " + ASSET_PATH + " hash=" + manifest_hash)
    return receipt


if __name__ == "__main__":
    is_dry_run = "--dry-run" in sys.argv or os.environ.get("PRODUCTION_PROFILE_DRY_RUN") == "1"
    is_write = ("--write" in sys.argv or os.environ.get("PRODUCTION_PROFILE_WRITE") == "1") and not is_dry_run
    is_readback = ("--readback" in sys.argv or os.environ.get("PRODUCTION_PROFILE_READBACK") == "1") and not is_dry_run
    do_rebind = "--rebind-encounter" in sys.argv or os.environ.get("PRODUCTION_PROFILE_REBIND_ENCOUNTER") == "1"
    main(write=is_write, readback=is_readback, dry_run=is_dry_run, rebind_encounter=do_rebind)
