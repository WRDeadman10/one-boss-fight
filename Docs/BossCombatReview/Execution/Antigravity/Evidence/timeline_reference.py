"""
timeline_reference.py - Offline Reference Implementation of the Timeline Compiler (Rev 04)

Computes independent expected compiled timelines, crossing evaluations, section graphs,
and loop handling from parsed montage notifies and movesheets.

Author: Antigravity (Visual & Technical Animation Investigator)
Work Order: ANTIGRAVITY_WORK_ORDER_04 (AG-16 / AG-20 / AG-24 Rev 04)
Location: Docs/BossCombatReview/Execution/Antigravity/Evidence/timeline_reference.py
"""

import os
import re
import json
import math
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
NOTIFIES_TXT = REPO_ROOT / "Docs" / "BossCombatReview" / "Execution" / "Claude" / "Evidence" / "exports" / "montage_notifies_2026-10-25.txt"
MOVESHEETS_DIR = REPO_ROOT / "Docs" / "BossCombatReview" / "Execution" / "Antigravity" / "Evidence" / "movesheets"
OUTPUT_JSON = REPO_ROOT / "Docs" / "BossCombatReview" / "Execution" / "Antigravity" / "Evidence" / "timeline_expected.json"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_dict(d):
    serialized = json.dumps(d, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class TimelineCompilerReference:
    def __init__(self):
        self.input_hashes = {}
        self.parsed_movesheets = {}
        self.timelines = {}

    def load_inputs(self):
        if not NOTIFIES_TXT.exists():
            raise FileNotFoundError(f"Missing {NOTIFIES_TXT}")
        self.input_hashes["montage_notifies_2026-10-25.txt"] = sha256_file(NOTIFIES_TXT)

        # Hash AND PARSE all 26 movesheets
        movesheet_files = sorted(MOVESHEETS_DIR.glob("*.json"))
        if len(movesheet_files) != 26:
            raise ValueError(f"Expected 26 movesheets, found {len(movesheet_files)}")
        for mf in movesheet_files:
            rel_name = f"movesheets/{mf.name}"
            self.input_hashes[rel_name] = sha256_file(mf)
            with open(mf, "r", encoding="utf-8") as f:
                data = json.load(f)
                move_id = data.get("move_id") or mf.stem
                self.parsed_movesheets[move_id] = data

    def parse_montage_notifies_txt(self):
        with open(NOTIFIES_TXT, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_montage = None
        parsed = {}

        header_re = re.compile(r"^\[P0Notify\] == ([\w]+) \(([\w]+)\) length=([\d\.]+) rate_scale=([\d\.]+)")
        meta_re = re.compile(r"^\[P0Notify\]\s+length ([\d\.]+) s, rate scale ([\d\.]+), sections (\d+), blend in ([\d\.]+) out ([\d\.]+)")
        state_re = re.compile(r"^\[P0Notify\]\s+\[state\] ([\w]+) at (-?[\d\.]+) s for ([\d\.]+) s")
        instant_re = re.compile(r"^\[P0Notify\]\s+([\w]+) at (-?[\d\.]+) s")

        for line in lines:
            line_str = line.strip()
            hm = header_re.match(line_str)
            if hm:
                m_name = hm.group(1)
                m_type = hm.group(2)
                m_len = float(hm.group(3))
                m_rate = float(hm.group(4))
                current_montage = {
                    "name": m_name,
                    "type": m_type,
                    "length_s": m_len,
                    "rate_scale": m_rate,
                    "sections_count": 1,
                    "blend_in": 0.25,
                    "blend_out": 0.25,
                    "windows": [],
                    "markers": []
                }
                parsed[m_name] = current_montage
                continue

            if not current_montage:
                continue

            mm = meta_re.match(line_str)
            if mm:
                current_montage["sections_count"] = int(mm.group(3))
                current_montage["blend_in"] = float(mm.group(4))
                current_montage["blend_out"] = float(mm.group(5))
                continue

            sm = state_re.match(line_str)
            if sm:
                w_class = sm.group(1)
                start_s = max(0.0, float(sm.group(2)))
                dur_s = float(sm.group(3))
                end_s = start_s + dur_s
                current_montage["windows"].append({
                    "id": f"W_{len(current_montage['windows']):02d}_{w_class}",
                    "semantic": self.map_semantic(w_class),
                    "source_class": w_class,
                    "begin_s": round(start_s, 5),
                    "end_s": round(end_s, 5),
                    "full_payload": {
                        "class": w_class,
                        "declared_begin_s": start_s,
                        "declared_duration_s": dur_s,
                        "raw_end_s": end_s
                    }
                })
                continue

            im = instant_re.match(line_str)
            if im:
                m_class = im.group(1)
                pos_s = max(0.0, float(im.group(2)))
                current_montage["markers"].append({
                    "id": f"M_{len(current_montage['markers']):02d}_{m_class}",
                    "semantic": self.map_semantic(m_class),
                    "source_class": m_class,
                    "position_s": round(pos_s, 5),
                    "full_payload": {
                        "class": m_class,
                        "declared_position_s": pos_s
                    }
                })
                continue

        return parsed

    def map_semantic(self, class_name):
        c = class_name.lower()
        if "collisiontrace" in c:
            return "ActiveDamage"
        if "disablemovement" in c:
            return "MovementLock"
        if "setdesiredrotation" in c:
            return "RotationTracking"
        if "hitstunimmune" in c:
            return "Hyperarmor"
        if "trail" in c:
            return "WeaponVisualTrail"
        if "playsound" in c or "sound" in c:
            return "AcousticCue"
        if "performfollowup" in c:
            return "ComboBranchMarker"
        if "endanimatingability" in c:
            return "AbilityEndMarker"
        return "GenericNotify"

    def compile_montage(self, m_dict):
        length = m_dict["length_s"]
        if length <= 0.0 or not math.isfinite(length):
            raise ValueError(f"Invalid montage length: {length}")

        compiled_windows = []
        ids_seen = set()

        for w in m_dict["windows"]:
            wid = w["id"]
            if wid in ids_seen:
                raise ValueError(f"Duplicate ID in windows: {wid}")
            ids_seen.add(wid)

            b = w["begin_s"]
            e = w["end_s"]
            if not (math.isfinite(b) and math.isfinite(e)):
                raise ValueError(f"Non-finite window bounds: {b}, {e}")
            if b < 0.0:
                raise ValueError(f"Negative window begin: {b}")

            # REJECTION: Begin must be strictly inside sequence
            if b >= length:
                raise ValueError(f"Window Begin ({b}s) >= Sequence Length ({length}s); invalid window")

            if e <= b:
                raise ValueError(f"Malformed window bounds: [{b}, {e}] (End <= Begin)")

            # Clamping policy: RawEnd preserved; End clamped to length
            raw_e = e
            clamped_e = min(length, e)
            if clamped_e <= b:
                raise ValueError(f"Window clamped End ({clamped_e}s) <= Begin ({b}s); reversed interval rejected")

            norm_b = b / length
            norm_e = clamped_e / length

            # FULL PAYLOAD HASH (Text export class and interval scope)
            payload_dict = w.get("full_payload", {"class": w["source_class"], "b": b, "e": e})
            payload_hash = sha256_dict(payload_dict)

            compiled_windows.append({
                "id": wid,
                "semantic": w["semantic"],
                "source_class": w["source_class"],
                "begin_s": b,
                "end_s": clamped_e,
                "raw_end_s": raw_e,
                "is_clipped_at_end": raw_e > length,
                "normalised_begin": round(norm_b, 6),
                "normalised_end": round(norm_e, 6),
                "payload_scope": "TEXT_EXPORT_CLASS_AND_INTERVAL_ONLY",
                "payload_scope_note": "Hash covers exported notify class, begin_s, and duration_s from montage_notifies_2026-10-25.txt; binary UObject properties and state pointers unexported",
                "payload_hash": payload_hash
            })

        compiled_markers = []
        for m in m_dict["markers"]:
            mid = m["id"]
            if mid in ids_seen:
                raise ValueError(f"Duplicate ID in markers: {mid}")
            ids_seen.add(mid)

            pos = m["position_s"]
            if not math.isfinite(pos) or pos < 0.0 or pos > length:
                raise ValueError(f"Malformed marker position: {pos} (length={length})")

            norm_pos = pos / length
            payload_dict = m.get("full_payload", {"class": m["source_class"], "pos": pos})
            payload_hash = sha256_dict(payload_dict)

            compiled_markers.append({
                "id": mid,
                "semantic": m["semantic"],
                "source_class": m["source_class"],
                "position_s": pos,
                "normalised_position": round(norm_pos, 6),
                "payload_scope": "TEXT_EXPORT_CLASS_AND_INTERVAL_ONLY",
                "payload_scope_note": "Hash covers exported notify class and position_s from montage_notifies_2026-10-25.txt; binary UObject properties unexported",
                "payload_hash": payload_hash,
                "provenance": "montage_notifies_export"
            })

        # SECTION GRAPH: Honest representation (unverified section names/topology in text export)
        sec_count = m_dict.get("sections_count", 1)
        if sec_count == 1:
            section_graph = {
                "declared_sections_count": 1,
                "topology": "UNVERIFIED_IN_TEXT_EXPORT",
                "sections": [{
                    "inferred_name": "Default",
                    "start_s": 0.0,
                    "end_s": length,
                    "next_section": None,
                    "note": "Section name 'Default' inferred; section track boundaries and linkages unexported in montage_notifies_2026-10-25.txt"
                }],
                "note": "Single section declared in export; full montage section track layout unexported"
            }
        else:
            section_graph = {
                "declared_sections_count": sec_count,
                "topology": "NOT_AVAILABLE_IN_TEXT_EXPORT",
                "sections": [],
                "note": "Section boundaries cannot be inferred by equal division; requires editor montage asset export"
            }

        # Correlate with parsed movesheet if available
        base_name = m_dict["name"].replace("_Montage", "").replace("_Anim", "")
        associated_movesheet = self.parsed_movesheets.get(base_name) or self.parsed_movesheets.get(m_dict["name"])

        montage_obj = {
            "name": m_dict["name"],
            "length_s": length,
            "rate_scale": m_dict.get("rate_scale", 1.0),
            "blend_in": m_dict.get("blend_in", 0.25),
            "blend_out": m_dict.get("blend_out", 0.25),
            "section_graph": section_graph,
            "has_associated_movesheet": associated_movesheet is not None,
            "movesheet_declared_intent": associated_movesheet.get("declared_intent") if associated_movesheet else None,
            "windows": compiled_windows,
            "markers": compiled_markers
        }
        # Whole-montage payload SHA256 (resolves Codex X-125 critique #3)
        montage_obj["payload_sha256"] = sha256_dict(montage_obj)
        return montage_obj

    @staticmethod
    def evaluate_crossing(compiled, prev_s, curr_s, is_initial=False, traversal="Forward", loop_ordinal=0, prev_loop_ordinal=0):
        """
        Evaluates crossed windows and markers in forward interval (prev_s, curr_s].
        Strictly guards against:
          1. Out of bounds positions: prev_s, curr_s not in [0.0, length] -> INCONCLUSIVE
          2. Non-forward traversals: Reverse, SectionJump, Teleport, Gap -> INCONCLUSIVE
          3. Unverified loop increments or retrograde motion -> INCONCLUSIVE
        Supports honest forward loop traversal when loop_ordinal increments:
          Crosses (prev_s, Length] on loop N, and [0.0, curr_s] on loop N+1.
        """
        length = compiled["length_s"]

        # 0. Finite position check (resolves Codex X-136 critique #1: NaN / Inf guard)
        if not math.isfinite(prev_s) or not math.isfinite(curr_s):
            return {
                "status": "INCONCLUSIVE",
                "reason": f"Non-finite position detected (NaN or Inf): prev={prev_s}, curr={curr_s}",
                "crossings": []
            }

        # 1. Bounds check (resolves Codex X-125 critique #2)
        if prev_s < 0.0 or curr_s < 0.0 or prev_s > length or curr_s > length:
            return {
                "status": "INCONCLUSIVE",
                "reason": f"Position out of bounds: prev={prev_s}, curr={curr_s}, length={length}",
                "crossings": []
            }

        # 2. Traversal validation: only "Forward" and "ForwardLoop" supported on monotone sequence (resolves Codex X-125 critique #1)
        if traversal not in ("Forward", "ForwardLoop"):
            return {
                "status": "INCONCLUSIVE",
                "reason": f"Unsupported traversal '{traversal}' (non-forward traversal cannot be evaluated on flat timeline without section graph)",
                "crossings": []
            }

        # 3. Monotonicity validation within same loop ordinal
        if loop_ordinal == prev_loop_ordinal and curr_s < prev_s:
            return {
                "status": "INCONCLUSIVE",
                "reason": f"Reverse traversal detected (prev={prev_s}, curr={curr_s}, loop={loop_ordinal})",
                "crossings": []
            }

        # 4. Traversal type vs loop ordinal consistency
        if traversal == "ForwardLoop":
            if loop_ordinal != prev_loop_ordinal + 1:
                return {
                    "status": "INCONCLUSIVE",
                    "reason": f"ForwardLoop requires loop_ordinal increment of exactly 1 (prev={prev_loop_ordinal}, curr={loop_ordinal})",
                    "crossings": []
                }
        elif traversal == "Forward":
            if loop_ordinal != prev_loop_ordinal:
                return {
                    "status": "INCONCLUSIVE",
                    "reason": f"Forward traversal across loop boundary requires traversal='ForwardLoop' (prev_loop={prev_loop_ordinal}, curr_loop={loop_ordinal})",
                    "crossings": []
                }

        starts_at_zero = is_initial and prev_s == 0.0
        crossings = []

        # 5. Forward loop wrap traversal (resolves Codex X-136 critique #2: full declared-wrap handling)
        if traversal == "ForwardLoop" or loop_ordinal == prev_loop_ordinal + 1:
            # Sub-interval A: (prev_s, length]
            for w in compiled["windows"]:
                if w["begin_s"] > prev_s and w["begin_s"] <= length:
                    crossings.append({"id": w["id"], "edge": "Begin", "time_s": w["begin_s"], "loop": prev_loop_ordinal})
                if w["end_s"] > prev_s and w["end_s"] <= length:
                    crossings.append({"id": w["id"], "edge": "End", "time_s": w["end_s"], "loop": prev_loop_ordinal})
            for m in compiled["markers"]:
                if m["position_s"] > prev_s and m["position_s"] <= length:
                    crossings.append({"id": m["id"], "edge": "Marker", "time_s": m["position_s"], "loop": prev_loop_ordinal})

            # Sub-interval B: [0.0, curr_s]
            for w in compiled["windows"]:
                if (w["begin_s"] >= 0.0 and w["begin_s"] <= curr_s):
                    crossings.append({"id": w["id"], "edge": "Begin", "time_s": w["begin_s"], "loop": loop_ordinal})
                if (w["end_s"] > 0.0 and w["end_s"] <= curr_s):
                    crossings.append({"id": w["id"], "edge": "End", "time_s": w["end_s"], "loop": loop_ordinal})
            for m in compiled["markers"]:
                if (m["position_s"] >= 0.0 and m["position_s"] <= curr_s):
                    crossings.append({"id": m["id"], "edge": "Marker", "time_s": m["position_s"], "loop": loop_ordinal})

            edge_order = {"Begin": 0, "End": 1, "Marker": 2}
            crossings.sort(key=lambda c: (c["loop"], c["time_s"], edge_order.get(c["edge"], 99), c["id"]))

            return {
                "status": "MATCH",
                "traversal": "ForwardLoop",
                "intervals": [[prev_s, length], [0.0, curr_s]],
                "crossings_count": len(crossings),
                "crossings": crossings
            }

        # 6. Standard forward monotone advance
        def crossed(t):
            return (t > prev_s and t <= curr_s) or (starts_at_zero and t == 0.0)

        for w in compiled["windows"]:
            if crossed(w["begin_s"]):
                crossings.append({"id": w["id"], "edge": "Begin", "time_s": w["begin_s"], "loop": loop_ordinal})
            if crossed(w["end_s"]):
                crossings.append({"id": w["id"], "edge": "End", "time_s": w["end_s"], "loop": loop_ordinal})

        for m in compiled["markers"]:
            if crossed(m["position_s"]):
                crossings.append({"id": m["id"], "edge": "Marker", "time_s": m["position_s"], "loop": loop_ordinal})

        edge_order = {"Begin": 0, "End": 1, "Marker": 2}
        crossings.sort(key=lambda c: (c["time_s"], edge_order.get(c["edge"], 99), c["id"]))

        return {
            "status": "MATCH",
            "traversal": "Forward",
            "interval": [prev_s, curr_s],
            "crossings_count": len(crossings),
            "crossings": crossings
        }


def run_self_tests(compiler):
    print("[SelfTest] Running 11 deliberate rejection and boundary verification tests...")
    tests_passed = 0

    # 1. Malformed notify: End <= Begin
    try:
        compiler.compile_montage({
            "name": "TEST_Malformed_EndBeforeBegin",
            "length_s": 2.0,
            "windows": [{"id": "W0", "semantic": "ActiveDamage", "source_class": "ANS", "begin_s": 0.5, "end_s": 0.4}],
            "markers": []
        })
        print("FAIL: Did not reject End <= Begin")
    except ValueError as e:
        assert "End <= Begin" in str(e)
        tests_passed += 1
        print("  Test 1 PASSED: Rejected window End <= Begin")

    # 2. Overlapping duplicate ID
    try:
        compiler.compile_montage({
            "name": "TEST_Duplicate_ID",
            "length_s": 2.0,
            "windows": [
                {"id": "W_DUP", "semantic": "ActiveDamage", "source_class": "ANS", "begin_s": 0.1, "end_s": 0.3},
                {"id": "W_DUP", "semantic": "MovementLock", "source_class": "ANS", "begin_s": 0.4, "end_s": 0.6}
            ],
            "markers": []
        })
        print("FAIL: Did not reject duplicate ID")
    except ValueError as e:
        assert "Duplicate ID" in str(e)
        tests_passed += 1
        print("  Test 2 PASSED: Rejected duplicate asset ID across windows")

    # 3. Negative length
    try:
        compiler.compile_montage({
            "name": "TEST_Negative_Length",
            "length_s": -1.5,
            "windows": [],
            "markers": []
        })
        print("FAIL: Did not reject negative length")
    except ValueError as e:
        assert "Invalid montage length" in str(e)
        tests_passed += 1
        print("  Test 3 PASSED: Rejected negative montage length")

    # 4. Marker position beyond length
    try:
        compiler.compile_montage({
            "name": "TEST_Marker_Beyond_Length",
            "length_s": 1.2,
            "windows": [],
            "markers": [{"id": "M0", "semantic": "AcousticCue", "source_class": "AN", "position_s": 1.5}]
        })
        print("FAIL: Did not reject marker beyond length")
    except ValueError as e:
        assert "Malformed marker position" in str(e)
        tests_passed += 1
        print("  Test 4 PASSED: Rejected marker placed beyond montage sequence length")

    # 5. Non-forward traversal rejection in crossing evaluation
    compiled_mock = {
        "name": "TEST_Reverse",
        "length_s": 2.0,
        "windows": [{"id": "W0", "semantic": "Damage", "source_class": "ANS", "begin_s": 0.5, "end_s": 1.0}],
        "markers": []
    }
    res = compiler.evaluate_crossing(compiled_mock, prev_s=1.2, curr_s=0.8, is_initial=False, traversal="Reverse")
    assert res["status"] == "INCONCLUSIVE" and "Unsupported traversal" in res["reason"]
    tests_passed += 1
    print("  Test 5 PASSED: Detected non-forward traversal ('Reverse') as INCONCLUSIVE")

    # 6. CODEX COUNTEREXAMPLE: Window Begin >= Length (Begin 1.2, End 1.5 on Length 1.0)
    try:
        compiler.compile_montage({
            "name": "TEST_Codex_ClampCounterExample",
            "length_s": 1.0,
            "windows": [{"id": "W_REVERSED", "semantic": "Damage", "source_class": "ANS", "begin_s": 1.2, "end_s": 1.5}],
            "markers": []
        })
        print("FAIL: Did not reject Begin >= Length")
    except ValueError as e:
        assert "Begin" in str(e) and ">= Sequence Length" in str(e)
        tests_passed += 1
        print("  Test 6 PASSED (Codex Counterexample): Rejected window with Begin (1.2s) >= Length (1.0s)")

    # 7. CODEX X-125 CRITIQUE 1: SectionJump Traversal Guard
    res_jump = compiler.evaluate_crossing(compiled_mock, prev_s=0.0, curr_s=0.9, is_initial=False, traversal="SectionJump")
    assert res_jump["status"] == "INCONCLUSIVE" and "SectionJump" in res_jump["reason"]
    tests_passed += 1
    print("  Test 7 PASSED (Codex X-125 Critique 1): Reclassified SectionJump traversal as INCONCLUSIVE")

    # 8. CODEX X-125 CRITIQUE 2: Out of Bounds Position Guard (curr 2.5 / length 2.0)
    res_oob = compiler.evaluate_crossing(compiled_mock, prev_s=0.0, curr_s=2.5, is_initial=False, traversal="Forward")
    assert res_oob["status"] == "INCONCLUSIVE" and "out of bounds" in res_oob["reason"]
    tests_passed += 1
    print("  Test 8 PASSED (Codex X-125 Critique 2): Reclassified out-of-bounds evaluation position as INCONCLUSIVE")

    # 9. CODEX X-125 CRITIQUE 3: Whole-Montage payload_sha256 Present
    compiled_test = compiler.compile_montage(compiled_mock)
    assert "payload_sha256" in compiled_test and len(compiled_test["payload_sha256"]) == 64
    tests_passed += 1
    print("  Test 9 PASSED (Codex X-125 Critique 3): Verified whole-montage payload_sha256 generation (64-char hex)")

    # 10. CODEX X-136 REPRODUCER 1: Non-finite position (NaN/Inf) -> INCONCLUSIVE
    res_nan = compiler.evaluate_crossing(compiled_mock, float('nan'), 0.5)
    assert res_nan["status"] == "INCONCLUSIVE" and "Non-finite" in res_nan["reason"]
    tests_passed += 1
    print("  Test 10 PASSED (Codex X-136 Reproducer 1): NaN position rejected as INCONCLUSIVE")

    # 11. CODEX X-136 REPRODUCER 2: ForwardLoop wrap evaluation when curr_s >= prev_s
    res_loop = compiler.evaluate_crossing(compiled_mock, prev_s=0.1, curr_s=0.2, traversal="ForwardLoop", prev_loop_ordinal=0, loop_ordinal=1)
    assert res_loop["status"] == "MATCH" and res_loop["traversal"] == "ForwardLoop"
    # compiled_mock length 2.0, window (0.5, 1.0) is in interval A (0.1, 2.0], crossings count == 2 (Begin and End)
    assert len(res_loop["crossings"]) == 2
    tests_passed += 1
    print("  Test 11 PASSED (Codex X-136 Reproducer 2): ForwardLoop with curr >= prev evaluated as MATCH with crossings")

    print(f"[SelfTest] All {tests_passed}/11 deliberate verification tests PASSED successfully!\n")


def main():
    compiler = TimelineCompilerReference()
    compiler.load_inputs()
    print(f"[TimelineRef] Loaded inputs. 1 export + {len(compiler.parsed_movesheets)} movesheets parsed.")

    run_self_tests(compiler)

    parsed_montages = compiler.parse_montage_notifies_txt()
    print(f"[TimelineRef] Parsed {len(parsed_montages)} montages from montage_notifies_2026-10-25.txt.")

    compiled_database = {
        "schema_version": "4.0",
        "provenance": {
            "compiler": "Antigravity Timeline Reference Compiler (AG-24 Rev 04)",
            "description": "Offline reference implementation with verified traversal guards, NaN/finite check, out-of-bounds rejection, full ForwardLoop wrap handling, transparent text export scope, and whole-montage payload SHA-256 hashes.",
            "input_hashes": compiler.input_hashes
        },
        "montages": {},
        "interval_crossing_samples": {}
    }

    for m_name, m_data in parsed_montages.items():
        compiled = compiler.compile_montage(m_data)
        compiled_database["montages"][m_name] = compiled

        # Sample standard 100ms interval advance test
        dt = 0.1
        sample_results = []
        t = 0.0
        is_init = True
        while t < min(1.0, compiled["length_s"]):
            next_t = round(t + dt, 3)
            cr = compiler.evaluate_crossing(compiled, t, next_t, is_initial=is_init, traversal="Forward")
            sample_results.append(cr)
            t = next_t
            is_init = False

        compiled_database["interval_crossing_samples"][m_name] = sample_results

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(compiled_database, f, indent=2)

    print(f"[TimelineRef] Successfully compiled {len(compiled_database['montages'])} timelines to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
