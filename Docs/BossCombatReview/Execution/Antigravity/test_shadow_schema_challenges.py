"""Independent adversarial shadow schema & semantic challenge harness (Task AG07-2).

Extracts validate_records from staged pie_timeline_shadow.py via AST.
Executes pure offline test probes using safe fake buffers. Zero Unreal import.
Demonstrates concrete accepted malformed cases, valid diagnostic edge cases
(such as zero crossings on MATCH and same-world reset generation advance),
and separates transport wire schema validation from semantic parity contracts.
"""
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
DRAFT_PATH = ROOT / "Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_timeline_shadow.py"

# AST-only extraction of validate_records
source_bytes = DRAFT_PATH.read_bytes()
draft_sha = hashlib.sha256(source_bytes).hexdigest()
tree = ast.parse(source_bytes, filename=str(DRAFT_PATH))
function_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "validate_records")
namespace = {"json": json, "math": math, "re": re}
exec(compile(ast.Module(body=[function_node], type_ignores=[]), str(DRAFT_PATH), "exec"), namespace)
validate_records = namespace["validate_records"]

BASE_ROW = {
    "world_session": "SyntheticWorld-01",
    "encounter_instance": "SyntheticEncounter-01",
    "participant_slot": "Boss",
    "source_asset": "/Game/SyntheticFixture",
    "variant": "Fixture",
    "coverage_scope": "SYNTHETIC_ONLY",
    "asset_sha256": "a" * 64,
    "adapter_sha256": "b" * 64,
    "previous": 0.0,
    "current": 0.1,
    "game_time": 1.0,
    "actual_rate": 1.0,
    "observation_ordinal": "1",
    "generation": 1,
    "authoritative_action": None,
    "compiled_crossings": [],
    "legacy_snapshot": {
        "tracked": True,
        "move": "A1",
        "phase": "Active",
        "instance": 1,
        "illegal_starts": 0,
        "double_launches": 0
    },
    "comparison_status": "MATCH"
}

class FakeBuffer:
    def __init__(self, rows, count=None):
        self.rows = rows
        self.count = len(rows) if count is None else count

    def get_record_count(self):
        return self.count

    def get_record_json_for_test(self, index):
        return json.dumps(self.rows[index])

def run_adversarial_challenges():
    results = []

    # Probe 0: Baseline Valid Synthetic Row
    p0 = validate_records(FakeBuffer([BASE_ROW]))
    results.append({
        "probe_id": "PROBE-00-BASELINE",
        "title": "Baseline Valid Row",
        "description": "Standard synthetic row conforming to 31 Codex schema checks",
        "accepted_by_validator": p0,
        "classification": "VALID_BASELINE"
    })

    # Probe 1: Valid MATCH Row with ZERO Crossings (Valid Diagnostic State)
    # When sample is mid-window, no boundary is crossed during interval -> compiled_crossings is naturally []
    r_zero_cross = copy.deepcopy(BASE_ROW)
    r_zero_cross["compiled_crossings"] = []
    p1 = validate_records(FakeBuffer([r_zero_cross]))
    results.append({
        "probe_id": "PROBE-01-VALID-ZERO-CROSSINGS",
        "title": "Valid MATCH with Zero Crossings",
        "description": "Mid-window active sample has no edge events; compiled_crossings == [] is legitimate engine behavior",
        "accepted_by_validator": p1,
        "classification": "VALID_ENGINE_BEHAVIOR"
    })

    # Probe 2: Valid Same-World Reset Generation Advancement (Valid Diagnostic State)
    # Producer OnSnapshot (RPGShadowCompare.cpp:124) retains record buffer across encounter resets
    r_gen1 = copy.deepcopy(BASE_ROW)
    r_gen1["observation_ordinal"] = "1"
    r_gen1["generation"] = 1
    r_gen2 = copy.deepcopy(BASE_ROW)
    r_gen2["observation_ordinal"] = "2"
    r_gen2["generation"] = 2
    p2 = validate_records(FakeBuffer([r_gen1, r_gen2]))
    results.append({
        "probe_id": "PROBE-02-VALID-RESET-GENERATION",
        "title": "Valid Reset Generation Advancement",
        "description": "Encounter reset advances generation monotonically within same world/encounter; legitimate multi-duel trace",
        "accepted_by_validator": p2,
        "classification": "VALID_ENGINE_BEHAVIOR"
    })

    # Probe 3: Cross-Row Identity Drift (Material Gap)
    # Subsequent row switches to completely different world_session and unrelated encounter_instance
    r_drift1 = copy.deepcopy(BASE_ROW)
    r_drift2 = copy.deepcopy(BASE_ROW)
    r_drift2["observation_ordinal"] = "2"
    r_drift2["world_session"] = "DifferentWorldSession"
    r_drift2["encounter_instance"] = "UnrelatedEncounter"
    p3 = validate_records(FakeBuffer([r_drift1, r_drift2]))
    results.append({
        "probe_id": "PROBE-03-SESSION-DRIFT",
        "title": "Cross-Row World/Encounter Identity Drift",
        "description": "Buffer accepts disjoint world sessions and unrelated encounters without trace demarcation",
        "accepted_by_validator": p3,
        "classification": "MATERIAL_TRACE_GAP"
    })

    # Probe 4: Non-Monotonic / Backwards Game Time (Material Gap)
    r_time1 = copy.deepcopy(BASE_ROW)
    r_time1["game_time"] = 100.0
    r_time2 = copy.deepcopy(BASE_ROW)
    r_time2["observation_ordinal"] = "2"
    r_time2["game_time"] = 2.5
    p4 = validate_records(FakeBuffer([r_time1, r_time2]))
    results.append({
        "probe_id": "PROBE-04-BACKWARDS-TIME",
        "title": "Backwards Game Time Sequence",
        "description": "Later observation ordinal carries game_time earlier than prior record (100.0s -> 2.5s) in same session",
        "accepted_by_validator": p4,
        "classification": "MATERIAL_TRACE_GAP"
    })

    # Probe 5: Traversal Inconsistency / Unverified Discontinuity
    r_play1 = copy.deepcopy(BASE_ROW)
    r_play1["previous"] = 0.0
    r_play1["current"] = 0.1
    r_play1["game_time"] = 1.000
    r_play2 = copy.deepcopy(BASE_ROW)
    r_play2["observation_ordinal"] = "2"
    r_play2["previous"] = 120.0
    r_play2["current"] = 150.0
    r_play2["game_time"] = 1.016
    p5 = validate_records(FakeBuffer([r_play1, r_play2]))
    results.append({
        "probe_id": "PROBE-05-UNVERIFIED-TRAVERSAL-JUMP",
        "title": "Unverified Montage Traversal Jump",
        "description": "Playhead jumps 150.0s in 16ms without section/instance metadata; unclassified traversal discontinuity",
        "accepted_by_validator": p5,
        "classification": "INCONCLUSIVE_TRAVERSAL_GAP"
    })

    # Probe 6: Diagnostic Acceptance of REGRESSION_CANDIDATE
    # Wire validator correctly accepts diagnostic rows, but caller must not treat as parity success
    r_regress = copy.deepcopy(BASE_ROW)
    r_regress["comparison_status"] = "REGRESSION_CANDIDATE"
    p6 = validate_records(FakeBuffer([r_regress]))
    results.append({
        "probe_id": "PROBE-06-REGRESSION-STATUS-TRANSPORT",
        "title": "Diagnostic Acceptance of Regression Rows",
        "description": "Validator accepts REGRESSION_CANDIDATE as valid diagnostic shape; flaw exists only if caller equates with parity gate",
        "accepted_by_validator": p6,
        "classification": "DEFENSIBLE_DIAGNOSTIC_SHAPE"
    })

    # Probe 7: Unvalidated Garbage in compiled_crossings
    r_cross_garbage = copy.deepcopy(BASE_ROW)
    r_cross_garbage["compiled_crossings"] = ["not_a_struct", 99999, None, {"bogus_field": True}]
    p7 = validate_records(FakeBuffer([r_cross_garbage]))
    results.append({
        "probe_id": "PROBE-07-UNVALIDATED-CROSSINGS-ELEMENTS",
        "title": "Unvalidated Nested Crossing Elements",
        "description": "isinstance(list) accepts arbitrary heterogeneous corrupted objects inside compiled_crossings",
        "accepted_by_validator": p7,
        "classification": "MATERIAL_SCHEMA_GAP"
    })

    # Probe 8: Missing Required Fields in legacy_snapshot
    # Real C++ producer always emits tracked, move, phase, instance, illegal_starts, double_launches
    r_legacy_empty = copy.deepcopy(BASE_ROW)
    r_legacy_empty["legacy_snapshot"] = {}  # Empty dict lacks all 6 producer fields
    p8 = validate_records(FakeBuffer([r_legacy_empty]))
    results.append({
        "probe_id": "PROBE-08-EMPTY-LEGACY-SNAPSHOT",
        "title": "Empty Legacy Snapshot Missing Required Fields",
        "description": "Validator accepts {} for legacy_snapshot, omitting required tracked/move/phase/instance/illegal/double fields",
        "accepted_by_validator": p8,
        "classification": "MATERIAL_SCHEMA_GAP"
    })

    # Probe 9: Positive Fixture for EEdge::Marker (edge = 2)
    # Staged compiler emits Marker crossings for instantaneous animation sync markers
    r_marker = copy.deepcopy(BASE_ROW)
    r_marker["compiled_crossings"] = [{
        "id": "SyncMarker_Footstep",
        "semantic": "Marker",
        "position": 0.35,
        "edge": 2,  # EEdge::Marker
        "loop_ordinal": 0
    }]
    p9 = validate_records(FakeBuffer([r_marker]))
    results.append({
        "probe_id": "PROBE-09-POSITIVE-MARKER-CROSSING",
        "title": "Positive Fixture for EEdge::Marker Crossing",
        "description": "Valid crossing with EEdge::Marker (edge = 2) representing discrete timeline marker",
        "accepted_by_validator": p9,
        "classification": "VALID_ENGINE_BEHAVIOR"
    })

    # Probe 10: Positive Fixture for EEdge::Closed (edge = 3)
    # Staged compiler FCursor::Close emits Closed crossing where id is legitimately None/empty
    r_closed = copy.deepcopy(BASE_ROW)
    r_closed["compiled_crossings"] = [{
        "id": "None",
        "semantic": "Closed",
        "position": 1.20,
        "edge": 3,  # EEdge::Closed
        "loop_ordinal": 0
    }]
    p10 = validate_records(FakeBuffer([r_closed]))
    results.append({
        "probe_id": "PROBE-10-POSITIVE-CLOSED-CROSSING",
        "title": "Positive Fixture for EEdge::Closed Crossing",
        "description": "Valid closure crossing with EEdge::Closed (edge = 3) where id is None with closure-reason semantic",
        "accepted_by_validator": p10,
        "classification": "VALID_ENGINE_BEHAVIOR"
    })

    # Probe 11: Explicit Null-Valued Required Wire Keys
    # C++ producer always emits authoritative_action and engine_instance (null when unset)
    r_null_keys = copy.deepcopy(BASE_ROW)
    r_null_keys["authoritative_action"] = None
    r_null_keys["engine_instance"] = None
    p11 = validate_records(FakeBuffer([r_null_keys]))
    results.append({
        "probe_id": "PROBE-11-NULL-REQUIRED-KEYS",
        "title": "Explicit Null-Valued Required Wire Keys",
        "description": "authoritative_action and engine_instance are always emitted on wire as explicit JSON null when unset",
        "accepted_by_validator": p11,
        "classification": "VALID_ENGINE_BEHAVIOR"
    })

    # Probe 12: Encounter Reset World Clock Continuity Inversion (Material Gap)
    # Encounter reset advances generation, but UWorld::GetTimeSeconds is continuous within the same session.
    # Generation advance cannot excuse a backward world clock (100.0s -> 2.5s) in same world_session!
    r_reset_t1 = copy.deepcopy(BASE_ROW)
    r_reset_t1["observation_ordinal"] = "1"
    r_reset_t1["generation"] = 1
    r_reset_t1["game_time"] = 100.0
    r_reset_t2 = copy.deepcopy(BASE_ROW)
    r_reset_t2["observation_ordinal"] = "2"
    r_reset_t2["generation"] = 2
    r_reset_t2["game_time"] = 2.5  # Inverted backward world time across reset
    p12 = validate_records(FakeBuffer([r_reset_t1, r_reset_t2]))
    results.append({
        "probe_id": "PROBE-12-RESET-TIME-INVERSION",
        "title": "Reset Generation Backward World Time Inversion",
        "description": "Later generation in same world_session carries backwards game_time (100.0s -> 2.5s); UWorld clock continuity violated",
        "accepted_by_validator": p12,
        "classification": "MATERIAL_TRACE_GAP"
    })

    # Probe 13: Unvalidated / Malformed window_projections Objects
    r_proj_malformed = copy.deepcopy(BASE_ROW)
    r_proj_malformed["window_projections"] = [{"unrecognized_garbage": 123}]  # Missing window_id, ClampedFrom, effective_end
    p13 = validate_records(FakeBuffer([r_proj_malformed]))
    results.append({
        "probe_id": "PROBE-13-MALFORMED-PROJECTION-OBJECT",
        "title": "Malformed Window Projections Array Elements",
        "description": "Validator accepts arbitrary unvalidated dictionaries inside window_projections missing required C++ fields",
        "accepted_by_validator": p13,
        "classification": "MATERIAL_SCHEMA_GAP"
    })

    return results

if __name__ == "__main__":
    results = run_adversarial_challenges()
    summary = {
        "harness": "test_shadow_schema_challenges.py",
        "target_draft": str(DRAFT_PATH.relative_to(ROOT)),
        "draft_sha256": draft_sha,
        "total_probes": len(results),
        "accepted_count": sum(1 for r in results if r["accepted_by_validator"]),
        "results": results
    }
    print(json.dumps(summary, indent=2))
