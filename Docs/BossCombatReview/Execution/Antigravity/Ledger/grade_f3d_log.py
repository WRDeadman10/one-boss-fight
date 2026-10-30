#!/usr/bin/env python3
"""
grade_f3d_log.py
================
Antigravity F3d Proof Grader (Order A-264).
Parses live editor raw log from PIE playback of L_SevarogFrameworkProof and verifies
exact runtime proof invariants, log tokens, event sequences, and numerical tolerances.

Usage:
    python grade_f3d_log.py --log <path_to_editor_raw.log> [--card-json <path>]
    python grade_f3d_log.py <path_to_editor_raw.log>
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, List, Any, Tuple, Optional

# Default MoveCard parameters (Swing1_Slow telemetry values)
DEFAULT_CARD_SPEC = {
    "MoveId": "Move_Sevarog_SwingSlow",
    "SlotName": "FullBody",
    "ClipLengthSeconds": 1.70,
    "CommitSeconds": 0.30,
    "ActiveStartSeconds": 0.35,
    "ActiveEndSeconds": 0.4917,
    "RecoveryEndSeconds": 1.65,
    "BandMinCm": 250.0,
    "BandMaxCm": 350.0,
    "FrameToleranceSeconds": 0.025  # ~1.5 frames at 60 fps
}

def parse_framework_log(log_text: str) -> List[str]:
    """Extract all [FrameworkProof] lines from raw log."""
    lines = []
    for line in log_text.splitlines():
        if "[FrameworkProof]" in line:
            # Strip timestamp / log category prefix if present
            idx = line.find("[FrameworkProof]")
            lines.append(line[idx:].strip())
    return lines

def grade_log_lines(lines: List[str], spec: Dict[str, Any] = DEFAULT_CARD_SPEC) -> Dict[str, Any]:
    """Grades extracted [FrameworkProof] lines against F3d proof requirements."""
    report = {
        "passed": False,
        "summary": "",
        "checks": {},
        "errors": [],
        "parsed_data": {}
    }

    # 1. Negative Assertion: Check for any ERROR lines before RESULT
    # Errors occurring after RESULT outcome=CompletedTelemetryOnly during PIE teardown are ignored
    result_idx = -1
    for i, l in enumerate(lines):
        if l.startswith("[FrameworkProof] RESULT"):
            result_idx = i
            break

    pre_result_lines = lines if result_idx == -1 else lines[:result_idx]
    error_lines = [l for l in pre_result_lines if "ERROR" in l]
    if error_lines:
        report["checks"]["no_error_tokens"] = False
        for err in error_lines:
            report["errors"].append(f"Encountered error log line: {err}")
    else:
        report["checks"]["no_error_tokens"] = True

    # 2. Dependencies check
    dep_lines = [l for l in lines if l.startswith("[FrameworkProof] dependencies")]
    if not dep_lines:
        report["checks"]["dependencies_resolved"] = False
        report["errors"].append("Missing '[FrameworkProof] dependencies' line")
    else:
        dep = dep_lines[0]
        resolved = "resolved=1" in dep and "label=F3_fixture" in dep
        report["checks"]["dependencies_resolved"] = resolved
        if not resolved:
            report["errors"].append(f"Dependencies line not fully resolved: {dep}")

    # 3. Slot graph check
    slot_lines = [l for l in lines if l.startswith("[FrameworkProof] slot_graph")]
    if not slot_lines:
        report["checks"]["slot_graph_verified"] = False
        report["errors"].append("Missing '[FrameworkProof] slot_graph' line")
    else:
        s_line = slot_lines[0]
        slot_ok = f"name={spec['SlotName']}" in s_line and "nodeClass=AnimNode_Slot" in s_line and "verified=1" in s_line
        report["checks"]["slot_graph_verified"] = slot_ok
        if not slot_ok:
            report["errors"].append(f"Slot graph line verification failed: {s_line}")

    # 4. Nav Request check
    nav_lines = [l for l in lines if l.startswith("[FrameworkProof] nav request=")]
    if not nav_lines:
        report["checks"]["nav_path_valid"] = False
        report["errors"].append("Missing '[FrameworkProof] nav request' line")
    else:
        n_line = nav_lines[0]
        nav_ok = "fullPath=1" in n_line
        report["checks"]["nav_path_valid"] = nav_ok
        if not nav_ok:
            report["errors"].append(f"Nav request failed full path check: {n_line}")

    # 5. Walk Arrival and Band check
    walk_lines = [l for l in lines if l.startswith("[FrameworkProof] walk start=")]
    if not walk_lines:
        report["checks"]["walk_arrival_band"] = False
        report["errors"].append("Missing '[FrameworkProof] walk start' line")
    else:
        w_line = walk_lines[0]
        # Example: [FrameworkProof] walk start=(...) end=(...) distanceCm=200 rangeCm=300 bandMin=250 bandMax=350 ...
        range_match = re.search(r"rangeCm=([0-9.]+)", w_line)
        band_min_match = re.search(r"bandMin=([0-9.]+)", w_line)
        band_max_match = re.search(r"bandMax=([0-9.]+)", w_line)
        dist_match = re.search(r"distanceCm=([0-9.]+)", w_line)

        if range_match and band_min_match and band_max_match and dist_match:
            range_cm = float(range_match.group(1))
            band_min = float(band_min_match.group(1))
            band_max = float(band_max_match.group(1))
            dist_cm = float(dist_match.group(1))
            report["parsed_data"]["range_cm"] = range_cm
            report["parsed_data"]["band"] = [band_min, band_max]
            report["parsed_data"]["walk_distance_cm"] = dist_cm

            in_band = (band_min - 1e-2) <= range_cm <= (band_max + 1e-2)
            walked = dist_cm > 0.0
            report["checks"]["walk_arrival_band"] = in_band and walked
            if not in_band:
                report["errors"].append(f"Arrival range {range_cm} cm outside band [{band_min}, {band_max}]")
            if not walked:
                report["errors"].append(f"Walk distance was zero or negative: {dist_cm}")
        else:
            report["checks"]["walk_arrival_band"] = False
            report["errors"].append(f"Failed to parse parameters from walk line: {w_line}")

    # 6. Playback Start check
    pb_start_lines = [l for l in lines if l.startswith("[FrameworkProof] playback_start")]
    if not pb_start_lines:
        report["checks"]["playback_start"] = False
        report["errors"].append("Missing '[FrameworkProof] playback_start' line")
    else:
        pb_s = pb_start_lines[0]
        inst_match = re.search(r"instance=([0-9]+)", pb_s)
        slot_match = re.search(r"slot=([a-zA-Z0-9_]+)", pb_s)
        rate_match = re.search(r"rate=([0-9.]+)", pb_s)
        if inst_match and slot_match and rate_match:
            inst_id = int(inst_match.group(1))
            slot_name = slot_match.group(1)
            rate = float(rate_match.group(1))
            report["parsed_data"]["instance_id"] = inst_id
            start_ok = (inst_id > 0) and (slot_name == spec["SlotName"]) and (abs(rate - 1.0) < 1e-3)
            report["checks"]["playback_start"] = start_ok
            if not start_ok:
                report["errors"].append(f"Playback start parameters mismatch: {pb_s}")
        else:
            report["checks"]["playback_start"] = False
            report["errors"].append(f"Failed to parse playback_start: {pb_s}")

    # 6b. Optional montage natural end check (Cycle 4 timing fragility mitigation)
    natural_end_lines = [l for l in lines if l.startswith("[FrameworkProof] montage_natural_end")]
    if natural_end_lines:
        report["parsed_data"]["montage_natural_end"] = natural_end_lines[0]

    # 7. Playback Observation frames check
    pb_frames = [l for l in lines if l.startswith("[FrameworkProof] playback instance=")]
    report["parsed_data"]["playback_frame_count"] = len(pb_frames)
    if len(pb_frames) < 3:
        report["checks"]["playback_frames_observed"] = False
        report["errors"].append(f"Expected at least 3 playback observation frames, got {len(pb_frames)}")
    else:
        # Check node and montage weights in at least one frame
        weights_positive = any(
            re.search(r"nodeWeight=([1-9][0-9.]*|0\.[1-9][0-9]*)", l) and
            re.search(r"montageWeight=([1-9][0-9.]*|0\.[1-9][0-9]*)", l)
            for l in pb_frames
        )
        report["checks"]["playback_frames_observed"] = weights_positive
        if not weights_positive:
            report["errors"].append("Zero frames observed with positive slot and montage weights")

    # 8. Events Sequence & Timings check
    event_lines = [l for l in lines if l.startswith("[FrameworkProof] event")]
    parsed_events = []
    for el in event_lines:
        k_match = re.search(r"kind=([a-zA-Z0-9_]+)", el)
        w_match = re.search(r"window=([a-zA-Z0-9_]+)", el)
        t_match = re.search(r"localSeconds=([0-9.]+)", el)
        if k_match and t_match:
            parsed_events.append({
                "kind": k_match.group(1),
                "window": w_match.group(1) if w_match else "None",
                "localSeconds": float(t_match.group(1))
            })

    report["parsed_data"]["events"] = parsed_events
    kinds = [e["kind"] for e in parsed_events]
    
    # Must have Open, Close, Finished (Recovery is optional depending on card)
    has_open = "Open" in kinds
    has_close = "Close" in kinds
    has_finished = "Finished" in kinds

    timing_ok = True
    tol = spec["FrameToleranceSeconds"]

    for ev in parsed_events:
        if ev["kind"] == "Open":
            expected = spec["ActiveStartSeconds"]
            if abs(ev["localSeconds"] - expected) > tol:
                timing_ok = False
                report["errors"].append(f"Event Open timing {ev['localSeconds']:.4f}s exceeds tolerance from {expected:.4f}s")
        elif ev["kind"] == "Close":
            expected = spec["ActiveEndSeconds"]
            if abs(ev["localSeconds"] - expected) > tol:
                timing_ok = False
                report["errors"].append(f"Event Close timing {ev['localSeconds']:.4f}s exceeds tolerance from {expected:.4f}s")
        elif ev["kind"] == "Finished":
            # MoveModel finishes execution at RecoveryEndSeconds (returning to Idle)
            expected = spec["RecoveryEndSeconds"]
            if abs(ev["localSeconds"] - expected) > (tol * 2):
                timing_ok = False
                report["errors"].append(f"Event Finished timing {ev['localSeconds']:.4f}s exceeds tolerance from RecoveryEndSeconds ({expected:.4f}s)")

    report["checks"]["events_sequence"] = has_open and has_close and has_finished and timing_ok
    if not (has_open and has_close and has_finished):
        report["errors"].append(f"Missing required event kinds. Observed: {kinds}")

    # 9. Cleanup check: exactly one cleanup reason=Finished
    cleanup_lines = [l for l in lines if l.startswith("[FrameworkProof] cleanup")]
    report["parsed_data"]["cleanup_lines"] = cleanup_lines
    finished_cleanups = [l for l in cleanup_lines if "reason=Finished" in l and "modelIdle=1" in l and "ownedMontageStopped=1" in l]
    
    if len(finished_cleanups) == 1 and len(cleanup_lines) == 1:
        report["checks"]["cleanup_exact_once"] = True
    else:
        report["checks"]["cleanup_exact_once"] = False
        report["errors"].append(f"Expected exactly 1 clean finish cleanup line, got {len(finished_cleanups)} of {len(cleanup_lines)}")

    # 10. Invariant check: target HP unchanged & damage API calls == 0
    inv_lines = [l for l in lines if l.startswith("[FrameworkProof] invariant")]
    if not inv_lines:
        report["checks"]["invariant_zero_damage"] = False
        report["errors"].append("Missing '[FrameworkProof] invariant' line")
    else:
        inv_line = inv_lines[0]
        hp_before_m = re.search(r"targetHPBefore=([0-9.]+)", inv_line)
        hp_after_m = re.search(r"targetHPAfter=([0-9.]+)", inv_line)
        dmg_invoc_m = re.search(r"damageAPIInvocationsByThisExecutor=([0-9]+)", inv_line)

        if hp_before_m and hp_after_m and dmg_invoc_m:
            hp_b = float(hp_before_m.group(1))
            hp_a = float(hp_after_m.group(1))
            invocs = int(dmg_invoc_m.group(1))
            inv_ok = (abs(hp_b - hp_a) < 1e-4) and (invocs == 0) and (hp_b > 0.0)
            report["checks"]["invariant_zero_damage"] = inv_ok
            if not inv_ok:
                report["errors"].append(f"Target HP changed or damage invocations > 0: {inv_line}")
        else:
            report["checks"]["invariant_zero_damage"] = False
            report["errors"].append(f"Failed to parse invariant parameters: {inv_line}")

    # 11. Final Result Outcome check
    res_lines = [l for l in lines if l.startswith("[FrameworkProof] RESULT outcome=CompletedTelemetryOnly")]
    if len(res_lines) == 1:
        report["checks"]["result_outcome_telemetry"] = True
    else:
        report["checks"]["result_outcome_telemetry"] = False
        report["errors"].append(f"Expected exactly one RESULT line with outcome=CompletedTelemetryOnly, got {len(res_lines)}")

    # Overall PASS condition: all individual checks must be True
    all_passed = all(report["checks"].values()) and len(report["errors"]) == 0
    report["passed"] = all_passed
    report["summary"] = f"F3d Grader {'PASS' if all_passed else 'FAIL'}: {sum(1 for v in report['checks'].values() if v)}/{len(report['checks'])} checks passed."

    return report

def grade_log_file(file_path: str, spec: Dict[str, Any] = DEFAULT_CARD_SPEC) -> Tuple[bool, Dict[str, Any]]:
    """Grades a log file from path."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    lines = parse_framework_log(content)
    result = grade_log_lines(lines, spec)
    return result["passed"], result

def main():
    parser = argparse.ArgumentParser(description="Grade raw editor log from F3d PIE playback proof.")
    parser.add_argument("log_positional", nargs="?", help="Path to raw editor log file")
    parser.add_argument("--log", dest="log_flag", help="Explicit path to raw editor log file")
    parser.add_argument("--card-json", help="Path to MoveCard JSON for timing validation")
    parser.add_argument("--json", action="store_true", help="Output full JSON report")

    args = parser.parse_args()
    log_path = args.log_flag or args.log_positional
    if not log_path:
        print("[ERROR] No log file specified. Use --log <path> or pass as first argument.", file=sys.stderr)
        sys.exit(2)

    if not os.path.isfile(log_path):
        print(f"[ERROR] Log file not found: {log_path}", file=sys.stderr)
        sys.exit(2)

    spec = DEFAULT_CARD_SPEC
    if args.card_json and os.path.isfile(args.card_json):
        try:
            with open(args.card_json, "r", encoding="utf-8") as f:
                card_data = json.load(f)
            # Find matching card
            cards = card_data.get("cards", [])
            for c in cards:
                if c.get("MoveId") == spec["MoveId"]:
                    spec["ClipLengthSeconds"] = c.get("ClipLengthSeconds", spec["ClipLengthSeconds"])
                    spec["ActiveStartSeconds"] = c.get("ActiveStartSeconds", spec["ActiveStartSeconds"])
                    spec["ActiveEndSeconds"] = c.get("ActiveEndSeconds", spec["ActiveEndSeconds"])
                    spec["RecoveryEndSeconds"] = c.get("RecoveryEndSeconds", spec["RecoveryEndSeconds"])
                    break
        except Exception as e:
            print(f"[WARN] Failed to parse custom card JSON: {e}", file=sys.stderr)

    passed, report = grade_log_file(log_path, spec)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("================================================================================")
        print(" F3d PLAYBACK PROOF LOG GRADER")
        print("================================================================================")
        print(f"Log File: {log_path}")
        print(f"Verdict : {'PASS' if passed else 'FAIL'}")
        print(f"Summary : {report['summary']}\n")
        print("Individual Checks:")
        for k, v in report["checks"].items():
            status_str = "[OK]  " if v else "[FAIL]"
            print(f"  {status_str} {k}")
        if report["errors"]:
            print("\nErrors / Invariant Violations:")
            for err in report["errors"]:
                print(f"  - {err}")
        print("================================================================================")

    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
