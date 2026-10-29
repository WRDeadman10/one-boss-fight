"""Reference Wire Contract Oracle & Comprehensive Mutation Test Suite (AG09 Rev 3).

Pure-offline reference contract validator, synthetic producer-shaped fixtures,
and isolated one-defect mutation matrix for the Phase 1 P1 shadow wire contract.

Pinned Enforced Source Inputs:
  - pie_timeline_shadow.py:   c0af0dc6066b73bbbd248981244fc231d653cfc9fbd58cfde4c054958caad99c
  - RPGShadowCompare.cpp:     f6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924
  - RPGShadowCompare.h:       95da9c0c6a72a302ed16cc1d9c3b0d5f7fd8e758f573dd65bda0bc4b13ca00ab
  - RPGTimelineCompiler.h:    5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e
  - RPGEncounterBinding.h:    4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80

Governing Reviews:
  - Docs/BossCombatReview/Execution/Codex/AG09_A127_REVIEW.md (anchor: a46ee521900ff30d5447df72ad5c52d7a353e70fb6919ce06ef7469975e7ad95)
  - Docs/BossCombatReview/Execution/Codex/AG09_A128_REVIEW.md (anchor: 1e1601024a385bb7e12b28afad4045a4b46acb567af80aa3ced6dd941ac5a8f5)
"""

import ast
import copy
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

# Locate staged driver and draft producer files
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]
DRAFT_DRIVER_PATH = PROJECT_ROOT / "Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_timeline_shadow.py"
PRODUCER_CPP_PATH = PROJECT_ROOT / "Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp"
PRODUCER_H_PATH = PROJECT_ROOT / "Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h"
COMPILER_H_PATH = PROJECT_ROOT / "Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h"
BINDING_H_PATH = PROJECT_ROOT / "Source/OneBossFight/Player/RPGEncounterBinding.h"

EXPECTED_FROZEN_PINS = {
    "pie_timeline_shadow.py": "c0af0dc6066b73bbbd248981244fc231d653cfc9fbd58cfde4c054958caad99c",
    "RPGShadowCompare.cpp": "f6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924",
    "RPGShadowCompare.h": "95da9c0c6a72a302ed16cc1d9c3b0d5f7fd8e758f573dd65bda0bc4b13ca00ab",
    "RPGTimelineCompiler.h": "5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e",
    "RPGEncounterBinding.h": "4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80"
}

def get_sha256(path: Path) -> str:
    if not path.exists():
        return "FILE_NOT_FOUND"
    return hashlib.sha256(path.read_bytes()).hexdigest()

OBSERVED_PINS = {
    "pie_timeline_shadow.py": get_sha256(DRAFT_DRIVER_PATH),
    "RPGShadowCompare.cpp": get_sha256(PRODUCER_CPP_PATH),
    "RPGShadowCompare.h": get_sha256(PRODUCER_H_PATH),
    "RPGTimelineCompiler.h": get_sha256(COMPILER_H_PATH),
    "RPGEncounterBinding.h": get_sha256(BINDING_H_PATH)
}

# Enforce fail-on-drift pin check
for name, exp_hash in EXPECTED_FROZEN_PINS.items():
    obs_hash = OBSERVED_PINS.get(name)
    if obs_hash != exp_hash:
        raise RuntimeError(f"Frozen source pin drift detected for {name}! Expected {exp_hash}, got {obs_hash}")

# AST extraction of staged validate_records from pie_timeline_shadow.py
source_bytes = DRAFT_DRIVER_PATH.read_bytes()
tree = ast.parse(source_bytes, filename=str(DRAFT_DRIVER_PATH))
func_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "validate_records")
ns = {"json": json, "math": math, "re": re}
exec(compile(ast.Module(body=[func_node], type_ignores=[]), str(DRAFT_DRIVER_PATH), "exec"), ns)
staged_validate_records = ns["validate_records"]


# ==============================================================================
# 1. INDEPENDENT PRODUCER-SHAPED 31-KEY SCHEMA DEFINITION
# ==============================================================================

# Derived directly and independently from C++ URPGCombatTimelineShadow::ObserveAfterTracker
# (RPGShadowCompare.cpp:139-223). Immutable frozenset to prevent self-weakening.
INDEPENDENT_PRODUCER_31_KEYS = frozenset({
    "world_session",
    "encounter_instance",
    "participant_slot",
    "generation",
    "observation_ordinal",
    "playback_ordinal",
    "authoritative_action",
    "source_asset",
    "observed_source_asset",
    "observed_segment_asset",
    "asset_sha256",
    "adapter_sha256",
    "synthetic_fixture",
    "projection_policy",
    "move",
    "variant",
    "section",
    "coverage_scope",
    "previous",
    "current",
    "game_time",
    "actual_rate",
    "traversal",
    "loop",
    "engine_instance",
    "legacy_snapshot",
    "compiled_crossings",
    "window_projections",
    "comparison_status",
    "limitation",
    "possible_explanations_not_acceptance"
})


# ==============================================================================
# 2. COMPLETE 31-TOP-LEVEL-FIELD PRODUCER-SHAPED BASELINE FIXTURE
# ==============================================================================

COMPLETE_31_FIELD_BASELINE_ROW = {
    # 1. Invariant session & identity headers (Lines 140-142)
    # FGuid::ToString(EGuidFormats::Digits) produces 32 hex uppercase/lowercase digits
    "world_session": "8A32D1844DF2474AA03870678D4E1122",
    "encounter_instance": "C1F7201B94C647B7B08878A7605D3344",
    "participant_slot": "Boss",
    # 2. Monotonic counters & sequence ordinals (Lines 143-146)
    # FRPGParticipantKey::Generation is uint32 (RPGEncounterBinding.h:76) starting at 1
    # LexToString(Sequence) and LexToString(PlaybackOrdinal) start at 1
    "generation": 1,
    "observation_ordinal": "1",
    "playback_ordinal": "1",
    # 3. Optional action string or explicit JSON null (Lines 147-148)
    "authoritative_action": None,
    # 4. Source & observed asset identifiers (Lines 149-153)
    "source_asset": "/Game/OneBossFight/Boss/Anims/AM_Boss_Attack_01",
    "observed_source_asset": "/Game/OneBossFight/Boss/Anims/AM_Boss_Attack_01",
    "observed_segment_asset": "/Game/OneBossFight/Boss/Anims/AS_Boss_Attack_01",
    "asset_sha256": "4a5e3f1082d491c9b2075f1a30f36f9c87b1c4112e52b2b1a8d01f8e12489110",
    "adapter_sha256": "81c03bf8449c256722ad95a62d088921e649e1a182479e39b972cf61a38bb921",
    # 5. Compile metadata & section scope (Lines 154-158)
    "synthetic_fixture": True,
    "projection_policy": 0,  # EOverhangPolicy::Reject = 0
    "move": "A1",
    "variant": "Default",
    "section": "Default",
    "coverage_scope": "GetCurrentActiveMontage result; first slot track/current segment only; other slots, additive sequences, inactive blend-outs UNCOVERED",
    # 6. Timeline playhead, world time & rate (Lines 159-160)
    "previous": 0.0,
    "current": 0.016,
    "game_time": 10.016,
    "actual_rate": 1.0,
    # 7. Traversal, loop & internal engine instance (Lines 161-163)
    "traversal": 0,  # ETraversal::Forward = 0
    "loop": 0,       # uint32
    "engine_instance": None,
    # 8. Nested legacy attack tracker snapshot (Lines 164-168)
    "legacy_snapshot": {
        "tracked": True,
        "move": "A1",
        "phase": "Active",
        "instance": 1,
        "illegal_starts": 0,
        "double_launches": 0
    },
    # 9. Nested compiled crossings array (Lines 169-177)
    "compiled_crossings": [
        {
            "id": "DamageWindow_01",
            "semantic": "ActiveDamage",
            "position": 0.016,
            "edge": 0,  # EEdge::Begin = 0
            "loop_ordinal": 0
        }
    ],
    # 10. Nested window overhang projections array (Lines 178-187)
    "window_projections": [],
    # 11. Comparison diagnostic status & limitations (Lines 188-211)
    "comparison_status": "MATCH",
    "limitation": "MATCH covers sampled active state only, not hit/geometry/cause parity",
    # 12. Nested candidate difference registry annotations (Lines 213-220)
    "possible_explanations_not_acceptance": []
}

# Verify baseline fixture satisfies independent schema equality
assert frozenset(COMPLETE_31_FIELD_BASELINE_ROW.keys()) == INDEPENDENT_PRODUCER_31_KEYS, \
    "Baseline fixture key set drifted from independent producer schema definition!"


# ==============================================================================
# 3. INDEPENDENT REFERENCE WIRE CONTRACT ORACLE
# ==============================================================================

class ReferenceWireContractOracle:
    """Independent reference validator enforcing C++ producer wire contract and trace continuity.
    
    Evaluates wire transport syntax, value boundaries, type integrity, and trace continuity.
    Intentionally separate from gameplay parity verdict.
    """

    # FGuid::ToString(EGuidFormats::Digits) emits 32 hex digits
    GUID_32HEX_REGEX = re.compile(r'^[0-9a-fA-F]{32}$', re.ASCII)
    SHA256_REGEX = re.compile(r'^[0-9a-fA-F]{64}$', re.ASCII)
    # Canonical positive uint64 decimal string: ASCII, no leading zero, 1..20 chars, <= 2^64-1
    UINT64_STRICT_REGEX = re.compile(r'^[1-9][0-9]{0,19}$', re.ASCII)
    UINT64_MAX = 18446744073709551615

    INT32_MIN = -2147483648
    INT32_MAX = 2147483647
    UINT32_MAX = 4294967295

    KNOWN_COMPARISON_STATUSES = frozenset({
        "MATCH",
        "REGRESSION_CANDIDATE",
        "UNTRACKED_PACK_PATH",
        "MISSING_METADATA",
        "INCONCLUSIVE_SAMPLING",
        "INVALID_RUN"
    })

    @staticmethod
    def is_strict_int(val) -> bool:
        return isinstance(val, int) and not isinstance(val, bool)

    @staticmethod
    def is_safe_finite_float(val) -> bool:
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            return False
        try:
            return math.isfinite(val)
        except (TypeError, OverflowError):
            return False

    @classmethod
    def validate_row(cls, row):
        """Validates schema conformance of an isolated serialized shadow row without raising exceptions."""
        if not isinstance(row, dict):
            return False, "Row is not a dictionary"

        # 1. Enforce exact 31-field presence against independent schema
        missing_keys = INDEPENDENT_PRODUCER_31_KEYS - set(row.keys())
        if missing_keys:
            return False, f"Missing required top-level keys: {sorted(list(missing_keys))}"

        # 2. Key-by-key type and value domain checks
        # GUID string headers (32 hex digits, non-zero)
        for g_key in ("world_session", "encounter_instance"):
            g_val = row[g_key]
            if not isinstance(g_val, str) or not cls.GUID_32HEX_REGEX.fullmatch(g_val) or g_val == "0" * 32:
                return False, f"{g_key} must be valid non-zero 32-hex GUID string"

        if not isinstance(row["participant_slot"], str) or not row["participant_slot"].strip():
            return False, "participant_slot must be non-empty string"

        # generation: positive uint32 (Source/OneBossFight/Player/RPGEncounterBinding.h:76)
        gen = row["generation"]
        if not cls.is_strict_int(gen) or gen < 1 or gen > cls.UINT32_MAX:
            return False, f"generation must be positive uint32 (1..{cls.UINT32_MAX})"

        # Canonical decimal string uint64 ordinals
        for ord_key in ("observation_ordinal", "playback_ordinal"):
            val = row[ord_key]
            if not isinstance(val, str) or not cls.UINT64_STRICT_REGEX.fullmatch(val):
                return False, f"{ord_key} must be canonical decimal string representing uint64 without leading zeros or whitespace"
            try:
                n = int(val, 10)
            except (ValueError, TypeError):
                return False, f"{ord_key} cannot be parsed as integer"
            if n > cls.UINT64_MAX:
                return False, f"{ord_key} exceeds uint64 max value ({cls.UINT64_MAX})"

        # Nullable string authoritative_action
        if row["authoritative_action"] is not None:
            if not isinstance(row["authoritative_action"], str) or not row["authoritative_action"].strip():
                return False, "authoritative_action must be non-empty string or None"

        # Source asset object paths
        for p_key in ("source_asset", "observed_source_asset"):
            p_val = row[p_key]
            if not isinstance(p_val, str) or not p_val.startswith("/"):
                return False, f"{p_key} must be valid asset object path starting with '/'"

        # observed_segment_asset: can legitimately be empty string "" if segment clip absent
        seg_val = row["observed_segment_asset"]
        if not isinstance(seg_val, str):
            return False, "observed_segment_asset must be string"
        if seg_val != "" and not seg_val.startswith("/"):
            return False, "observed_segment_asset must be empty or start with '/'"

        # SHA256 hashes
        for h_key in ("asset_sha256", "adapter_sha256"):
            h_val = row[h_key]
            if not isinstance(h_val, str) or not cls.SHA256_REGEX.fullmatch(h_val):
                return False, f"{h_key} must be 64-hex SHA256 string"

        # Boolean synthetic_fixture (strictly bool, no int 1/0)
        if type(row["synthetic_fixture"]) is not bool:
            return False, "synthetic_fixture must be strict boolean"

        # EOverhangPolicy projection_policy: Reject=0, ClipDiagnosticToPlaybackEnd=1
        proj_pol = row["projection_policy"]
        if not cls.is_strict_int(proj_pol) or proj_pol not in (0, 1):
            return False, "projection_policy out of EOverhangPolicy domain (0, 1)"

        # Section, move, variant FNames
        for n_key in ("move", "variant", "section"):
            if not isinstance(row[n_key], str) or not row[n_key].strip():
                return False, f"{n_key} must be non-empty FName string"

        if not isinstance(row["coverage_scope"], str) or "UNCOVERED" not in row["coverage_scope"]:
            return False, "coverage_scope disclaimer missing or malformed"

        # Finite playhead floats
        for f_key in ("previous", "current", "game_time", "actual_rate"):
            v = row[f_key]
            if not cls.is_safe_finite_float(v):
                return False, f"{f_key} must be finite number"

        if row["game_time"] < 0.0:
            return False, "game_time must be non-negative"

        # ETraversal: Forward=0, Reverse=1, Loop=2, SectionJump=3, Unknown=4
        trav = row["traversal"]
        if not cls.is_strict_int(trav) or trav not in (0, 1, 2, 3, 4):
            return False, "traversal out of ETraversal domain (0..4)"

        # uint32 loop ordinal
        loop = row["loop"]
        if not cls.is_strict_int(loop) or loop < 0 or loop > cls.UINT32_MAX:
            return False, f"loop must be unsigned 32-bit int (0..{cls.UINT32_MAX})"

        # Nullable int32 engine_instance (in PIE non-negative int32)
        eng_inst = row["engine_instance"]
        if eng_inst is not None:
            if not cls.is_strict_int(eng_inst) or eng_inst < 0 or eng_inst > cls.INT32_MAX:
                return False, f"engine_instance must be non-negative int32 (0..{cls.INT32_MAX}) or None"

        # Nested legacy_snapshot
        legacy = row["legacy_snapshot"]
        if not isinstance(legacy, dict):
            return False, "legacy_snapshot must be dictionary"
        req_legacy = ("tracked", "move", "phase", "instance", "illegal_starts", "double_launches")
        for lk in req_legacy:
            if lk not in legacy:
                return False, f"legacy_snapshot missing required key '{lk}'"
        if type(legacy["tracked"]) is not bool:
            return False, "legacy_snapshot field 'tracked' must be bool"
        if not isinstance(legacy["move"], str) or not isinstance(legacy["phase"], str):
            return False, "legacy_snapshot move/phase must be string"
        if not cls.is_strict_int(legacy["instance"]) or legacy["instance"] < cls.INT32_MIN or legacy["instance"] > cls.INT32_MAX:
            return False, "legacy_snapshot field 'instance' must be int32"
        for counter_key in ("illegal_starts", "double_launches"):
            cv = legacy[counter_key]
            if not cls.is_strict_int(cv) or cv < 0 or cv > cls.INT32_MAX:
                return False, f"legacy_snapshot field '{counter_key}' must be non-negative int32"

        # Nested compiled_crossings array
        crossings = row["compiled_crossings"]
        if not isinstance(crossings, list):
            return False, "compiled_crossings must be list"
        for i, c in enumerate(crossings):
            if not isinstance(c, dict):
                return False, f"compiled_crossings[{i}] must be dictionary"
            for ck in ("id", "semantic", "position", "edge", "loop_ordinal"):
                if ck not in c:
                    return False, f"compiled_crossings[{i}] missing key '{ck}'"
            if not isinstance(c["id"], str) or not isinstance(c["semantic"], str):
                return False, f"compiled_crossings[{i}] id/semantic must be str"
            if not cls.is_safe_finite_float(c["position"]):
                return False, f"compiled_crossings[{i}] position must be finite number"
            # EEdge: Begin=0, End=1, Marker=2, Closed=3
            edge_val = c["edge"]
            if not cls.is_strict_int(edge_val) or edge_val not in (0, 1, 2, 3):
                return False, f"compiled_crossings[{i}] edge out of EEdge domain (0..3)"
            c_loop = c["loop_ordinal"]
            if not cls.is_strict_int(c_loop) or c_loop < 0 or c_loop > cls.UINT32_MAX:
                return False, f"compiled_crossings[{i}] loop_ordinal must be uint32 (0..{cls.UINT32_MAX})"

        # Nested window_projections array
        projections = row["window_projections"]
        if not isinstance(projections, list):
            return False, "window_projections must be list"
        for i, p in enumerate(projections):
            if not isinstance(p, dict):
                return False, f"window_projections[{i}] must be dictionary"
            for pk in ("window_id", "ClampedFrom", "effective_end", "provenance_flag"):
                if pk not in p:
                    return False, f"window_projections[{i}] missing key '{pk}'"
            if not isinstance(p["window_id"], str) or not isinstance(p["provenance_flag"], str):
                return False, f"window_projections[{i}] string fields malformed"
            if not cls.is_safe_finite_float(p["ClampedFrom"]):
                return False, f"window_projections[{i}] ClampedFrom must be finite number"
            if not cls.is_safe_finite_float(p["effective_end"]):
                return False, f"window_projections[{i}] effective_end must be finite number"

        # Comparison status: safely reject non-string without raising TypeError
        c_status = row.get("comparison_status")
        if not isinstance(c_status, str) or c_status not in cls.KNOWN_COMPARISON_STATUSES:
            return False, f"comparison_status must be a recognized string in {sorted(list(cls.KNOWN_COMPARISON_STATUSES))}"

        if not isinstance(row["limitation"], str) or not row["limitation"].strip():
            return False, "limitation must be non-empty string"

        # Nested possible_explanations_not_acceptance array
        explanations = row["possible_explanations_not_acceptance"]
        if not isinstance(explanations, list):
            return False, "possible_explanations_not_acceptance must be list"
        for i, e in enumerate(explanations):
            if not isinstance(e, dict):
                return False, f"possible_explanations_not_acceptance[{i}] must be dictionary"
            for ek in ("id", "boundary", "evidence"):
                if ek not in e or not isinstance(e[ek], str):
                    return False, f"possible_explanations_not_acceptance[{i}] field '{ek}' must be str"

        return True, "Row structurally valid"

    @classmethod
    def validate_buffer(cls, rows):
        """Validates an entire continuous trace segment across all records."""
        if not isinstance(rows, list) or len(rows) == 0:
            return False, "Buffer must contain at least 1 record"

        first = rows[0]
        v_ok, v_err = cls.validate_row(first)
        if not v_ok:
            return False, f"Row 0 malformed: {v_err}"

        session_id = first["world_session"]
        encounter_id = first["encounter_instance"]
        slot_id = first["participant_slot"]
        prev_obs_ord = int(first["observation_ordinal"], 10)
        prev_gen = first["generation"]
        prev_time = first["game_time"]

        for i in range(1, len(rows)):
            r = rows[i]
            r_ok, r_err = cls.validate_row(r)
            if not r_ok:
                return False, f"Row {i} malformed: {r_err}"

            # Invariant session identity across continuous trace
            if r["world_session"] != session_id:
                return False, f"Row {i} world_session drifted from initial session"
            if r["encounter_instance"] != encounter_id:
                return False, f"Row {i} encounter_instance drifted from initial encounter"
            if r["participant_slot"] != slot_id:
                return False, f"Row {i} participant_slot drifted within single-observer trace"

            # Strictly monotonic observation ordinal
            curr_obs_ord = int(r["observation_ordinal"], 10)
            if curr_obs_ord <= prev_obs_ord:
                return False, f"Row {i} observation_ordinal not strictly increasing ({curr_obs_ord} <= {prev_obs_ord})"

            # Monotonic generation advance across encounter resets
            if r["generation"] < prev_gen:
                return False, f"Row {i} generation regressed ({r['generation']} < {prev_gen})"

            # Continuous non-decreasing world simulation time (UWorld::GetTimeSeconds does NOT regress on reset)
            if r["game_time"] < prev_time:
                return False, f"Row {i} game_time backwards ({r['game_time']} < {prev_time}); world clock continuity violated"

            prev_obs_ord = curr_obs_ord
            prev_gen = r["generation"]
            prev_time = r["game_time"]

        return True, f"Trace valid across all {len(rows)} records"


class FakeBufferAdapter:
    """Implements C++ URPGCombatTimelineShadow test interface for staged validate_records."""
    def __init__(self, rows):
        self.rows = rows

    def get_record_count(self):
        return len(self.rows)

    def get_record_json_for_test(self, index):
        return json.dumps(self.rows[index])


# ==============================================================================
# 4. POSITIVE FIXTURES & ISOLATED ONE-DEFECT MUTATION MATRIX
# ==============================================================================

def build_test_cases():
    cases = []

    # --------------------------------------------------------------------------
    # POSITIVE VALID PROBES (Reference Oracle: ACCEPT)
    # --------------------------------------------------------------------------
    cases.append({
        "id": "POS-01-COMPLETE-BASELINE",
        "title": "Complete 31-Field Synthetic Baseline",
        "category": "POSITIVE",
        "payload": [copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)],
        "oracle_expected": True,
        "oracle_reason": "Satisfies all 31 top-level field types and nested contracts"
    })

    # POS-02: Valid Zero-Crossing MATCH (Mid-window interior tick)
    r_pos02 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos02["compiled_crossings"] = []
    cases.append({
        "id": "POS-02-ZERO-CROSSINGS-MATCH",
        "title": "Valid Mid-Window MATCH with Zero Crossings",
        "category": "POSITIVE",
        "payload": [r_pos02],
        "oracle_expected": True,
        "oracle_reason": "Interior window ticks legitimately cross 0 boundaries while MATCH is true"
    })

    # POS-03: Positive Fixture for EEdge::Marker (edge = 2)
    r_pos03 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos03["compiled_crossings"] = [{
        "id": "FootstepSync", "semantic": "Marker", "position": 0.35, "edge": 2, "loop_ordinal": 0
    }]
    cases.append({
        "id": "POS-03-MARKER-CROSSING",
        "title": "Positive Fixture for EEdge::Marker (edge = 2)",
        "category": "POSITIVE",
        "payload": [r_pos03],
        "oracle_expected": True,
        "oracle_reason": "Discrete timeline marker crossings valid within EEdge domain"
    })

    # POS-04: Positive Fixture for EEdge::Closed (edge = 3)
    r_pos04 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos04["compiled_crossings"] = [{
        "id": "None", "semantic": "Closed", "position": 1.20, "edge": 3, "loop_ordinal": 0
    }]
    cases.append({
        "id": "POS-04-CLOSED-CROSSING",
        "title": "Positive Fixture for EEdge::Closed (edge = 3)",
        "category": "POSITIVE",
        "payload": [r_pos04],
        "oracle_expected": True,
        "oracle_reason": "Cursor closure event carries EEdge::Closed with closure reason semantic"
    })

    # POS-05: Explicit Null-Valued Required Wire Keys
    r_pos05 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos05["authoritative_action"] = None
    r_pos05["engine_instance"] = None
    cases.append({
        "id": "POS-05-NULLABLE-WIRE-KEYS",
        "title": "Explicit Null-Valued Required Wire Keys",
        "category": "POSITIVE",
        "payload": [r_pos05],
        "oracle_expected": True,
        "oracle_reason": "Keys always emitted on wire; null values represent unset C++ optionals"
    })

    # POS-06: Same-World Monotonic Reset Generation Advance
    r_pos06_a = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos06_a["generation"] = 1
    r_pos06_a["observation_ordinal"] = "1"
    r_pos06_a["game_time"] = 10.0
    r_pos06_b = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos06_b["generation"] = 2
    r_pos06_b["observation_ordinal"] = "2"
    r_pos06_b["game_time"] = 10.5
    cases.append({
        "id": "POS-06-RESET-GENERATION-FORWARD",
        "title": "Monotonic Reset Generation Advancement with Continuous Time",
        "category": "POSITIVE",
        "payload": [r_pos06_a, r_pos06_b],
        "oracle_expected": True,
        "oracle_reason": "Generation advance is valid multi-duel telemetry when game_time advances"
    })

    # POS-07: Source-Permitted Empty Observed Segment Asset
    r_pos07 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos07["observed_segment_asset"] = ""
    cases.append({
        "id": "POS-07-EMPTY-SEGMENT-ASSET",
        "title": "Source-Permitted Empty Observed Segment Asset",
        "category": "POSITIVE",
        "payload": [r_pos07],
        "oracle_expected": True,
        "oracle_reason": "CaptureAfterTracker leaves segment empty when current segment absent; wire accepts empty string"
    })

    # POS-08: Valid Diagnostic Status Transport (REGRESSION_CANDIDATE)
    r_pos08 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos08["comparison_status"] = "REGRESSION_CANDIDATE"
    cases.append({
        "id": "POS-08-REGRESSION-CANDIDATE-TRANSPORT",
        "title": "Valid Transport of Diagnostic Status (REGRESSION_CANDIDATE)",
        "category": "POSITIVE",
        "payload": [r_pos08],
        "oracle_expected": True,
        "oracle_reason": "REGRESSION_CANDIDATE is a valid producer-emitted diagnostic wire status"
    })

    # POS-09: Large uint64 Ordinal Above 2^53 JavaScript Safe Integer Limit
    r_pos09 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos09["observation_ordinal"] = "9007199254740993"  # 2^53 + 1
    r_pos09["playback_ordinal"] = "9007199254740993"
    cases.append({
        "id": "POS-09-UINT64-ABOVE-2POW53",
        "title": "Large uint64 Ordinal Above 2^53 (Decimal String Preservation)",
        "category": "POSITIVE",
        "payload": [r_pos09],
        "oracle_expected": True,
        "oracle_reason": "64-bit precision preserved losslessly via decimal string transport"
    })

    # POS-10: Maximum uint64 Value Boundary (2^64 - 1)
    r_pos10 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos10["observation_ordinal"] = "18446744073709551615"
    r_pos10["playback_ordinal"] = "18446744073709551615"
    cases.append({
        "id": "POS-10-UINT64-MAX-BOUNDARY",
        "title": "Maximum uint64 Value Boundary (18446744073709551615)",
        "category": "POSITIVE",
        "payload": [r_pos10],
        "oracle_expected": True,
        "oracle_reason": "Exact uint64 maximum decimal string accepted"
    })

    # POS-11: Valid Traversal Enum Variants
    r_pos11 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos11["traversal"] = 1  # ETraversal::Reverse
    cases.append({
        "id": "POS-11-TRAVERSAL-REVERSE",
        "title": "Valid Traversal Variant (Reverse = 1)",
        "category": "POSITIVE",
        "payload": [r_pos11],
        "oracle_expected": True,
        "oracle_reason": "Negative play rate serializes valid ETraversal::Reverse"
    })

    # POS-12: Engine Instance Boundary (int32 max)
    r_pos12 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos12["engine_instance"] = 2147483647
    cases.append({
        "id": "POS-12-ENGINE-INSTANCE-INT32-MAX",
        "title": "Engine Instance Boundary (int32 max = 2147483647)",
        "category": "POSITIVE",
        "payload": [r_pos12],
        "oracle_expected": True,
        "oracle_reason": "int32 maximum value representable for engine instance"
    })

    # POS-13: Positive uint32 Generation Upper-Range (2^31)
    r_pos13 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos13["generation"] = 2147483648  # 2^31
    cases.append({
        "id": "POS-13-GENERATION-2POW31",
        "title": "Positive uint32 Generation (2^31 = 2147483648)",
        "category": "POSITIVE",
        "payload": [r_pos13],
        "oracle_expected": True,
        "oracle_reason": "FRPGParticipantKey::Generation is uint32 (RPGEncounterBinding.h:76); 2^31 valid"
    })

    # POS-14: Maximum uint32 Generation Boundary (2^32 - 1)
    r_pos14 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos14["generation"] = 4294967295  # 2^32 - 1
    cases.append({
        "id": "POS-14-GENERATION-UINT32-MAX",
        "title": "Maximum uint32 Generation Boundary (4294967295)",
        "category": "POSITIVE",
        "payload": [r_pos14],
        "oracle_expected": True,
        "oracle_reason": "Exact uint32 maximum boundary accepted for participant generation"
    })

    # POS-15: Cross-Row Upper-Range Monotonic Generation Advance
    r_pos15_a = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos15_a["generation"] = 2147483648
    r_pos15_a["observation_ordinal"] = "1"
    r_pos15_a["game_time"] = 100.0
    r_pos15_b = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_pos15_b["generation"] = 2147483649
    r_pos15_b["observation_ordinal"] = "2"
    r_pos15_b["game_time"] = 100.5
    cases.append({
        "id": "POS-15-GENERATION-UPPER-RANGE-FORWARD",
        "title": "Cross-Row Upper-Range Generation Advance (2^31 -> 2^31 + 1)",
        "category": "POSITIVE",
        "payload": [r_pos15_a, r_pos15_b],
        "oracle_expected": True,
        "oracle_reason": "Upper-range uint32 generation advance is valid multi-duel telemetry"
    })

    # --------------------------------------------------------------------------
    # ISOLATED ONE-DEFECT MUTATIONS (Reference Oracle: REJECT)
    # --------------------------------------------------------------------------

    # MUT-01: Missing required top-level key (playback_ordinal omitted)
    r_m01 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    del r_m01["playback_ordinal"]
    cases.append({
        "id": "MUT-01-OMITTED-TOP-LEVEL-KEY",
        "title": "Missing Required Top-Level Key (playback_ordinal)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m01],
        "oracle_expected": False,
        "oracle_reason": "Top-level producer key omitted"
    })

    # MUT-02: Missing nullable key entirely (authoritative_action omitted vs null)
    r_m02 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    del r_m02["authoritative_action"]
    cases.append({
        "id": "MUT-02-OMITTED-NULLABLE-KEY",
        "title": "Missing Nullable Wire Key (authoritative_action omitted)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m02],
        "oracle_expected": False,
        "oracle_reason": "Nullable wire keys must always be present on wire"
    })

    # MUT-03: Missing nullable engine_instance entirely
    r_m03 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    del r_m03["engine_instance"]
    cases.append({
        "id": "MUT-03-OMITTED-ENGINE-INSTANCE",
        "title": "Missing Nullable Wire Key (engine_instance omitted)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m03],
        "oracle_expected": False,
        "oracle_reason": "engine_instance must always be present on wire"
    })

    # MUT-04: Missing observed_segment_asset key entirely
    r_m04 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    del r_m04["observed_segment_asset"]
    cases.append({
        "id": "MUT-04-OMITTED-SEGMENT-ASSET-KEY",
        "title": "Missing observed_segment_asset Key (Omission vs Empty String)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m04],
        "oracle_expected": False,
        "oracle_reason": "observed_segment_asset key must be present even when empty"
    })

    # MUT-05: Ordinal serialized as JSON number (precision loss)
    r_m05 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m05["observation_ordinal"] = 1
    cases.append({
        "id": "MUT-05-ORDINAL-AS-JSON-NUMBER",
        "title": "Uint64 Ordinal Serialized as JSON Number (lossy)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m05],
        "oracle_expected": False,
        "oracle_reason": "Ordinals must be decimal strings to prevent JS float precision loss"
    })

    # MUT-06: Non-decimal observation ordinal string
    r_m06 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m06["observation_ordinal"] = "1.5"
    cases.append({
        "id": "MUT-06-NON-DECIMAL-ORDINAL-STRING",
        "title": "Non-Decimal Ordinal String ('1.5')",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m06],
        "oracle_expected": False,
        "oracle_reason": "Observation ordinal must strictly parse as integer uint64"
    })

    # MUT-07: First observation ordinal zero ('0' rejected; producer starts at 1)
    r_m07 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m07["observation_ordinal"] = "0"
    cases.append({
        "id": "MUT-07-ZERO-OBSERVATION-ORDINAL",
        "title": "Zero Observation Ordinal ('0' Rejected; Sequence starts >= 1)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m07],
        "oracle_expected": False,
        "oracle_reason": "Producer increments Sequence before emitting observation; sample is strictly positive"
    })

    # MUT-08: Leading zero in ordinal string ('01')
    r_m08 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m08["observation_ordinal"] = "01"
    cases.append({
        "id": "MUT-08-LEADING-ZERO-ORDINAL",
        "title": "Non-Canonical Leading Zero in Ordinal ('01')",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m08],
        "oracle_expected": False,
        "oracle_reason": "LexToString produces canonical decimal without leading zeros"
    })

    # MUT-09: Trailing newline in ordinal string ('1\\n')
    r_m09 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m09["observation_ordinal"] = "1\n"
    cases.append({
        "id": "MUT-09-NEWLINE-IN-ORDINAL",
        "title": "Newline-Terminated Ordinal String ('1\\n')",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m09],
        "oracle_expected": False,
        "oracle_reason": "Ordinal string must not contain trailing whitespace or newlines"
    })

    # MUT-10: Non-ASCII digit in ordinal string (Arabic digit '١')
    r_m10 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m10["observation_ordinal"] = "\u0661"
    cases.append({
        "id": "MUT-10-NON-ASCII-ORDINAL",
        "title": "Non-ASCII Digit in Ordinal (Arabic Digit)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m10],
        "oracle_expected": False,
        "oracle_reason": "Ordinal must strictly match ASCII digits [1-9][0-9]*"
    })

    # MUT-11: uint64 overflow (2^64)
    r_m11 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m11["observation_ordinal"] = "18446744073709551616"
    cases.append({
        "id": "MUT-11-UINT64-OVERFLOW",
        "title": "uint64 Overflow Boundary (18446744073709551616)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m11],
        "oracle_expected": False,
        "oracle_reason": "Value exceeds uint64 maximum representable in C++"
    })

    # MUT-12: Bool-as-number type confusion (synthetic_fixture = 1)
    r_m12 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m12["synthetic_fixture"] = 1
    cases.append({
        "id": "MUT-12-BOOL-AS-INT-TYPE-CONFUSION",
        "title": "Bool-as-Number Type Confusion (synthetic_fixture = 1)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m12],
        "oracle_expected": False,
        "oracle_reason": "Boolean fields must be strict bool type"
    })

    # MUT-13: int32 overflow for engine_instance (2^31)
    r_m13 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m13["engine_instance"] = 2147483648  # 2^31
    cases.append({
        "id": "MUT-13-ENGINE-INSTANCE-INT32-OVERFLOW",
        "title": "Engine Instance int32 Overflow (2^31)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m13],
        "oracle_expected": False,
        "oracle_reason": "engine_instance exceeds signed 32-bit int maximum"
    })

    # MUT-14: uint32 overflow for row-level loop (2^32)
    r_m14 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m14["loop"] = 4294967296  # 2^32
    cases.append({
        "id": "MUT-14-LOOP-UINT32-OVERFLOW",
        "title": "Loop Ordinal uint32 Overflow (2^32)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m14],
        "oracle_expected": False,
        "oracle_reason": "Loop ordinal must fit within uint32"
    })

    # MUT-15: Negative loop ordinal (-1)
    r_m15 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m15["loop"] = -1
    cases.append({
        "id": "MUT-15-NEGATIVE-LOOP-ORDINAL",
        "title": "Negative Loop Ordinal (-1)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m15],
        "oracle_expected": False,
        "oracle_reason": "Loop ordinal is unsigned and cannot be negative"
    })

    # MUT-16: uint32 overflow for crossing loop_ordinal (2^32)
    r_m16 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m16["compiled_crossings"] = [{
        "id": "W1", "semantic": "ActiveDamage", "position": 0.016, "edge": 0, "loop_ordinal": 4294967296
    }]
    cases.append({
        "id": "MUT-16-CROSSING-LOOP-UINT32-OVERFLOW",
        "title": "Crossing loop_ordinal uint32 Overflow (2^32)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m16],
        "oracle_expected": False,
        "oracle_reason": "FCrossing::LoopOrdinal must fit within uint32"
    })

    # MUT-17: int32 overflow in legacy_snapshot instance (2^31)
    r_m17 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m17["legacy_snapshot"]["instance"] = 2147483648
    cases.append({
        "id": "MUT-17-LEGACY-INSTANCE-INT32-OVERFLOW",
        "title": "Legacy Snapshot instance int32 Overflow (2^31)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m17],
        "oracle_expected": False,
        "oracle_reason": "legacy_snapshot instance must be valid int32"
    })

    # MUT-18: Traversal out of ETraversal domain (99)
    r_m18 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m18["traversal"] = 99
    cases.append({
        "id": "MUT-18-TRAVERSAL-OUT-OF-DOMAIN",
        "title": "ETraversal Out of Domain (99)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m18],
        "oracle_expected": False,
        "oracle_reason": "Traversal must be within ETraversal domain (0..4)"
    })

    # MUT-19: Projection policy out of EOverhangPolicy domain (5)
    r_m19 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m19["projection_policy"] = 5
    cases.append({
        "id": "MUT-19-PROJECTION-POLICY-OUT-OF-DOMAIN",
        "title": "Projection Policy Out of Domain (5)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m19],
        "oracle_expected": False,
        "oracle_reason": "Projection policy must be within EOverhangPolicy domain (0, 1)"
    })

    # MUT-20: Crossing edge out of EEdge domain (4)
    r_m20 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m20["compiled_crossings"] = [{
        "id": "WindowA", "semantic": "Damage", "position": 0.1, "edge": 4, "loop_ordinal": 0
    }]
    cases.append({
        "id": "MUT-20-EDGE-OUT-OF-DOMAIN",
        "title": "Crossing edge Out of EEdge Domain (4)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m20],
        "oracle_expected": False,
        "oracle_reason": "Edge must be within EEdge domain (0..3)"
    })

    # MUT-21: Hyphenated GUID rejected (UE5.5 Digits format requires 32 hex)
    r_m21 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m21["world_session"] = "8A32D184-4DF2-474A-A038-70678D4E1122"
    cases.append({
        "id": "MUT-21-GUID-HYPHEN-REJECTED",
        "title": "Hyphenated GUID Rejected (FGuid::ToString default is 32-hex Digits)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m21],
        "oracle_expected": False,
        "oracle_reason": "Producer calls FGuid::ToString without format arg, emitting 32 hex digits"
    })

    # MUT-22: Non-hex characters in GUID
    r_m22 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m22["world_session"] = "Z" * 32
    cases.append({
        "id": "MUT-22-GUID-NON-HEX-CHARACTERS",
        "title": "Non-Hex Characters in GUID Header",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m22],
        "oracle_expected": False,
        "oracle_reason": "GUID must be valid hexadecimal characters"
    })

    # MUT-23: Malformed comparison_status as list (must reject safely without raising TypeError)
    r_m23 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m23["comparison_status"] = []
    cases.append({
        "id": "MUT-23-STATUS-NON-STRING-LIST",
        "title": "Non-String comparison_status as List (Safe Rejection vs TypeError)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m23],
        "oracle_expected": False,
        "oracle_reason": "Non-string status must reject safely rather than raising TypeError"
    })

    # MUT-24: Huge integer in float field (must reject safely without raising OverflowError)
    r_m24 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m24["current"] = 10 ** 400
    cases.append({
        "id": "MUT-24-HUGE-INT-OVERFLOW-CURRENT",
        "title": "Huge Int Overflow in Float Position (Safe Rejection vs OverflowError)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m24],
        "oracle_expected": False,
        "oracle_reason": "10**400 must reject safely rather than raising OverflowError in math.isfinite"
    })

    # MUT-25: Non-finite float (NaN in playhead current)
    r_m25 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m25["current"] = float("nan")
    cases.append({
        "id": "MUT-25-NON-FINITE-FLOAT-NAN",
        "title": "Non-Finite Float (current = NaN)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m25],
        "oracle_expected": False,
        "oracle_reason": "Playhead numbers must be finite"
    })

    # MUT-26: Non-finite float in crossing position (Inf)
    r_m26 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m26["compiled_crossings"] = [{
        "id": "WindowA", "semantic": "Damage", "position": float("inf"), "edge": 0, "loop_ordinal": 0
    }]
    cases.append({
        "id": "MUT-26-CROSSING-NON-FINITE-POSITION",
        "title": "Non-Finite Crossing Position (Inf)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m26],
        "oracle_expected": False,
        "oracle_reason": "Crossing position must be finite number"
    })

    # MUT-27: Empty legacy_snapshot dictionary {}
    r_m27 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m27["legacy_snapshot"] = {}
    cases.append({
        "id": "MUT-27-EMPTY-LEGACY-SNAPSHOT",
        "title": "Empty legacy_snapshot Missing Required Fields",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m27],
        "oracle_expected": False,
        "oracle_reason": "Producer unconditionally serializes 6 legacy fields"
    })

    # MUT-28: Malformed legacy_snapshot field type
    r_m28 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m28["legacy_snapshot"]["tracked"] = "TrueString"
    cases.append({
        "id": "MUT-28-LEGACY-SNAPSHOT-TYPE-ERROR",
        "title": "Malformed legacy_snapshot Field Type (tracked = string)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m28],
        "oracle_expected": False,
        "oracle_reason": "tracked field must be strict bool"
    })

    # MUT-29: Malformed compiled_crossings element missing edge
    r_m29 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m29["compiled_crossings"] = [{"id": "WindowA", "semantic": "Damage", "position": 0.1, "loop_ordinal": 0}]
    cases.append({
        "id": "MUT-29-CROSSING-MISSING-EDGE",
        "title": "Crossing Element Missing edge Field",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m29],
        "oracle_expected": False,
        "oracle_reason": "Crossing elements must contain exact 5 producer fields"
    })

    # MUT-30: Malformed window_projections element missing ClampedFrom
    r_m30 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m30["window_projections"] = [{"window_id": "W1", "effective_end": 1.0, "provenance_flag": "FLAG"}]
    cases.append({
        "id": "MUT-30-PROJECTION-MISSING-CLAMPEDFROM",
        "title": "Projection Element Missing ClampedFrom Field",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m30],
        "oracle_expected": False,
        "oracle_reason": "Projection elements must contain ClampedFrom"
    })

    # MUT-31: Malformed possible_explanations element missing evidence
    r_m31 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m31["possible_explanations_not_acceptance"] = [{"id": "DiffA", "boundary": "Attack"}]
    cases.append({
        "id": "MUT-31-EXPLANATION-MISSING-EVIDENCE",
        "title": "Explanation Element Missing evidence Field",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m31],
        "oracle_expected": False,
        "oracle_reason": "Explanation elements must contain evidence"
    })

    # MUT-32: Cross-row trace identity leak (world_session switches)
    r_m32_a = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m32_b = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m32_b["observation_ordinal"] = "2"
    r_m32_b["world_session"] = "99999999999999999999999999999999"
    cases.append({
        "id": "MUT-32-SESSION-IDENTITY-LEAK",
        "title": "Cross-Row World Session Identity Leak",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m32_a, r_m32_b],
        "oracle_expected": False,
        "oracle_reason": "Single-observer trace cannot switch world sessions"
    })

    # MUT-33: Non-monotonic observation ordinal sequence (2 followed by 1)
    r_m33_a = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m33_a["observation_ordinal"] = "2"
    r_m33_b = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m33_b["observation_ordinal"] = "1"
    cases.append({
        "id": "MUT-33-ORDINAL-SEQUENCE-INVERSION",
        "title": "Observation Ordinal Sequence Inversion ('2' -> '1')",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m33_a, r_m33_b],
        "oracle_expected": False,
        "oracle_reason": "Observation ordinals must be strictly increasing"
    })

    # MUT-34: Backward generation advance (gen 2 followed by gen 1)
    r_m34_a = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m34_a["generation"] = 2
    r_m34_a["observation_ordinal"] = "1"
    r_m34_b = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m34_b["generation"] = 1
    r_m34_b["observation_ordinal"] = "2"
    cases.append({
        "id": "MUT-34-GENERATION-REGRESSION",
        "title": "Generation Advance Regression (gen 2 -> gen 1)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m34_a, r_m34_b],
        "oracle_expected": False,
        "oracle_reason": "Generation advance must be monotonically non-decreasing"
    })

    # MUT-35: Backward game time within same generation (100.0s -> 2.5s)
    r_m35_a = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m35_a["observation_ordinal"] = "1"
    r_m35_a["game_time"] = 100.0
    r_m35_b = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m35_b["observation_ordinal"] = "2"
    r_m35_b["game_time"] = 2.5
    cases.append({
        "id": "MUT-35-BACKWARD-GAME-TIME-SAME-GEN",
        "title": "Backward Game Time within Same Generation (100.0s -> 2.5s)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m35_a, r_m35_b],
        "oracle_expected": False,
        "oracle_reason": "Simulation time cannot regress within continuous session"
    })

    # MUT-36: Backward game time across encounter reset (100.0s -> 2.5s across gen 1 -> gen 2)
    r_m36_a = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m36_a["observation_ordinal"] = "1"
    r_m36_a["generation"] = 1
    r_m36_a["game_time"] = 100.0
    r_m36_b = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m36_b["observation_ordinal"] = "2"
    r_m36_b["generation"] = 2
    r_m36_b["game_time"] = 2.5
    cases.append({
        "id": "MUT-36-RESET-TIME-CONTINUITY-INVERSION",
        "title": "Reset World Clock Continuity Inversion (100.0s -> 2.5s across reset)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m36_a, r_m36_b],
        "oracle_expected": False,
        "oracle_reason": "UWorld clock does not reset on duel reset; time cannot regress"
    })

    # MUT-37: Generation Zero Rejected ('0' rejected; bound generation starts >= 1)
    r_m37 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m37["generation"] = 0
    cases.append({
        "id": "MUT-37-GENERATION-ZERO",
        "title": "Zero Generation Rejected (Bound generation initialized >= 1)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m37],
        "oracle_expected": False,
        "oracle_reason": "Active bound participant generation is positive uint32 (1..UINT32_MAX)"
    })

    # MUT-38: Generation uint32 Overflow (2^32)
    r_m38 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m38["generation"] = 4294967296  # 2^32
    cases.append({
        "id": "MUT-38-GENERATION-UINT32-OVERFLOW",
        "title": "Generation uint32 Overflow Boundary (2^32 = 4294967296)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m38],
        "oracle_expected": False,
        "oracle_reason": "Participant generation cannot exceed uint32 max"
    })

    # MUT-39: Negative Generation (-1)
    r_m39 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m39["generation"] = -1
    cases.append({
        "id": "MUT-39-GENERATION-NEGATIVE",
        "title": "Negative Generation (-1)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m39],
        "oracle_expected": False,
        "oracle_reason": "Participant generation is unsigned uint32 and cannot be negative"
    })

    # MUT-40: Generation Bool-as-Int (True)
    r_m40 = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
    r_m40["generation"] = True
    cases.append({
        "id": "MUT-40-GENERATION-BOOL-AS-INT",
        "title": "Generation Bool-as-Int (True)",
        "category": "ONE_DEFECT_MUTATION",
        "payload": [r_m40],
        "oracle_expected": False,
        "oracle_reason": "generation must be strict integer, not boolean"
    })

    # --------------------------------------------------------------------------
    # INDIVIDUAL KEY DELETIONS (Proves all 31 keys are individually required)
    # --------------------------------------------------------------------------
    for idx, key in enumerate(sorted(list(INDEPENDENT_PRODUCER_31_KEYS)), start=1):
        r_del = copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)
        del r_del[key]
        cases.append({
            "id": f"MUT-KEY-DEL-{idx:02d}-{key.upper()}",
            "title": f"Individual Key Deletion: '{key}' omitted",
            "category": "KEY_DELETION_MUTATION",
            "payload": [r_del],
            "oracle_expected": False,
            "oracle_reason": f"Required top-level key '{key}' omitted from row dictionary"
        })

    return cases


# ==============================================================================
# 5. EXECUTION HARNESS WITH HARD ASSERTIONS & RUNNER SELF-TEST
# ==============================================================================

def execute_harness(test_cases=None):
    cases = test_cases if test_cases is not None else build_test_cases()
    results = []
    assertion_failures = []

    pos_count = sum(1 for c in cases if c["category"] == "POSITIVE")
    mut_count = sum(1 for c in cases if c["category"] != "POSITIVE")

    print("================================================================================")
    print("AG09 Reference Wire Contract Oracle & Mutation Suite (Rev 3)")
    print("================================================================================")
    print(f"Target Staged Driver: pie_timeline_shadow.py ({OBSERVED_PINS['pie_timeline_shadow.py'][:16]}...) [ENFORCED]")
    print(f"C++ Shadow Producer:  RPGShadowCompare.cpp   ({OBSERVED_PINS['RPGShadowCompare.cpp'][:16]}...) [ENFORCED]")
    print(f"Producer Header:      RPGShadowCompare.h     ({OBSERVED_PINS['RPGShadowCompare.h'][:16]}...) [ENFORCED]")
    print(f"Staged Compiler:      RPGTimelineCompiler.h ({OBSERVED_PINS['RPGTimelineCompiler.h'][:16]}...) [ENFORCED]")
    print(f"Encounter Binding:    RPGEncounterBinding.h  ({OBSERVED_PINS['RPGEncounterBinding.h'][:16]}...) [ENFORCED]")
    print(f"Total Test Cases:     {len(cases)} ({pos_count} Positive Fixtures, {mut_count} One-Defect Mutations)")
    print("--------------------------------------------------------------------------------\n")

    for tc in cases:
        case_id = tc["id"]
        payload = tc["payload"]
        exp_oracle = tc["oracle_expected"]

        # Run independent reference oracle
        oracle_actual, oracle_msg = ReferenceWireContractOracle.validate_buffer(payload)

        # Run dormant staged driver via AST-extracted function
        try:
            staged_actual = staged_validate_records(FakeBufferAdapter(payload))
        except Exception as e:
            staged_actual = f"EXCEPTION: {type(e).__name__}: {e}"

        # Evaluate assertion against reference contract
        passed_assertion = (oracle_actual == exp_oracle)
        if not passed_assertion:
            assertion_failures.append({
                "case_id": case_id,
                "expected": exp_oracle,
                "actual": oracle_actual,
                "message": oracle_msg
            })

        # Classify gap against dormant validator
        gap_status = "DORMANT_VALIDATOR_PERMISSIVE_GAP" if (not oracle_actual and staged_actual is True) else "CONCORDANT"

        status_icon = "[PASS]" if passed_assertion else "[FAIL]"
        print(f"{status_icon} [{case_id}] {tc['title']}")
        print(f"   Oracle: Expected={exp_oracle}, Actual={oracle_actual} ({oracle_msg})")
        print(f"   Staged Dormant Driver: {staged_actual} | Gap: {gap_status}\n")

        results.append({
            "id": case_id,
            "title": tc["title"],
            "category": tc["category"],
            "oracle_expected": exp_oracle,
            "oracle_actual": oracle_actual,
            "oracle_message": oracle_msg,
            "staged_driver_actual": staged_actual,
            "gap_classification": gap_status,
            "assertion_passed": passed_assertion
        })

    # Summary counts
    total_cases = len(cases)
    total_passed = sum(1 for r in results if r["assertion_passed"])
    dormant_gaps = sum(1 for r in results if r["gap_classification"] == "DORMANT_VALIDATOR_PERMISSIVE_GAP")

    print("--------------------------------------------------------------------------------")
    print(f"Results: {total_passed}/{total_cases} assertions passed.")
    print(f"Detected Gaps in Staged pie_timeline_shadow.py: {dormant_gaps} defects accepted by dormant driver.")
    print("--------------------------------------------------------------------------------\n")

    if assertion_failures:
        print(f"[FAIL] {len(assertion_failures)} assertion failures encountered!")
        for f in assertion_failures:
            print(f"   - {f['case_id']}: Expected {f['expected']}, got {f['actual']} ({f['message']})")
        sys.exit(1)

    print("[PASS] All reference contract assertions PASSED (Exit Code 0).")
    return results


# ==============================================================================
# 6. RUNNER SELF-TEST
# ==============================================================================

def run_self_test():
    """In-memory self-test proving that an assertion failure causes execute_harness to exit 1."""
    print("Executing In-Memory Runner Failure-Path Self-Test...")
    fake_contradictory_cases = [{
        "id": "SELFTEST-CONTRADICTION",
        "title": "Intentional Inverted Expectation",
        "category": "SELFTEST",
        "payload": [copy.deepcopy(COMPLETE_31_FIELD_BASELINE_ROW)],
        "oracle_expected": False,  # Baseline is valid, so this will fail assertion
        "oracle_reason": "Contradictory expectation to test failure branch"
    }]
    # Run in sub-context and verify SystemExit with code 1
    caught_exit_code = None
    try:
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            execute_harness(fake_contradictory_cases)
    except SystemExit as exc:
        caught_exit_code = exc.code

    if caught_exit_code != 1:
        print(f"[CRITICAL] Self-test failed: expected exit code 1, got {caught_exit_code}!")
        sys.exit(2)

    print("[PASS] Runner Failure-Path Self-Test Verified: contradiction correctly exited with code 1.\n")


if __name__ == "__main__":
    run_self_test()
    execute_harness()
