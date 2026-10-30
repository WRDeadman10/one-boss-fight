#!/usr/bin/env python3
"""
grade_f6a_log.py
================
Antigravity F6a Boss Target & Life Proof Grader (Order A-295 / Lead C-416).

Parses editor raw log from PIE playback of Slice F6a target proof and verifies:
1. One or more player hits registered on the framework boss (boss_hit lines).
2. For every hit:
   - healthBefore - healthAfter == damage (within float tolerance)
   - damage > 0.0 and healthAfter < healthBefore (strictly monotonic decrease)
   - Sequential continuity across hits (hit[k].healthBefore == hit[k-1].healthAfter)
3. For every hit, an associated or subsequent boss_health_read with reader=ReadAttribute
   verifies that the ReadAttribute bridge reflects value == healthAfter and max > 0.
4. For lethal runs (terminal healthAfter <= 0.0):
   - Exactly one boss_dead event is emitted.
   - boss_dead reports executorAborted=1 and a valid generation token (> 0).
5. Post-mortem invariant: after boss_dead, zero subsequent attack decisions,
   playback_start events, player-damage lines, or further boss hits are emitted.
6. Zero unhandled ERROR lines before RESULT.

Log Token Specifications (per Lead Order C-416):
- [FrameworkProof] boss_hit attack=<n> source=injected damage=<d> healthBefore=<h> healthAfter=<h>
- [FrameworkProof] boss_health_read reader=ReadAttribute value=<h> max=<m>
- [FrameworkProof] boss_dead generation=<g> executorAborted=1
- [FrameworkProof] decision ...
- [FrameworkProof] playback_start ...
- [FrameworkProof] damage ... / damage_attempt ...
- [FrameworkProof] RESULT ...

Usage:
    python grade_f6a_log.py --log <path_to_editor_raw.log>
    python grade_f6a_log.py <path_to_editor_raw.log>
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional


def parse_framework_log(log_text: str) -> List[str]:
    """Extracts all [FrameworkProof] lines from editor or game raw logs."""
    extracted = []
    for line in log_text.splitlines():
        if "[FrameworkProof]" in line:
            idx = line.find("[FrameworkProof]")
            extracted.append(line[idx:].strip())
    return extracted


def grade_f6a_log_lines(lines: List[str], tolerance: float = 0.01) -> Dict[str, Any]:
    """
    Grades extracted [FrameworkProof] lines against F6a boss target and life requirements.
    """
    report: Dict[str, Any] = {
        "passed": False,
        "summary": "",
        "checks": {},
        "errors": [],
        "parsed_data": {
            "boss_hits": [],
            "health_reads": [],
            "boss_dead": [],
            "decisions": [],
            "playback_starts": [],
            "player_damages": [],
            "result_line": None
        }
    }

    # 1. Check for unhandled ERROR lines before RESULT
    result_idx = -1
    for i, l in enumerate(lines):
        if l.startswith("[FrameworkProof] RESULT"):
            result_idx = i
            report["parsed_data"]["result_line"] = l
            break

    pre_result_lines = lines if result_idx == -1 else lines[:result_idx]
    error_lines = [l for l in pre_result_lines if "ERROR" in l or "Fail(" in l or "Assertion failed" in l]
    if error_lines:
        report["checks"]["no_error_tokens"] = False
        for err in error_lines:
            report["errors"].append(f"Encountered error line: {err}")
    else:
        report["checks"]["no_error_tokens"] = True

    # 2. Parse all structured lines with line indices
    for idx, l in enumerate(lines):
        # boss_hit: [attack=<n>] [source=<src>] damage=<d> healthBefore=<b> healthAfter=<a>
        if l.startswith("[FrameworkProof] boss_hit"):
            m_full = re.search(
                r"(?:attack=(\d+)\s+)?(?:source=([a-zA-Z0-9_]+)\s+)?damage=(-?[0-9.]+)\s+healthBefore=(-?[0-9.]+)\s+healthAfter=(-?[0-9.]+)",
                l
            )
            if m_full:
                att = int(m_full.group(1)) if m_full.group(1) else len(report["parsed_data"]["boss_hits"]) + 1
                src = m_full.group(2) if m_full.group(2) else "injected"
                report["parsed_data"]["boss_hits"].append({
                    "line_index": idx,
                    "attack": att,
                    "source": src,
                    "damage": float(m_full.group(3)),
                    "healthBefore": float(m_full.group(4)),
                    "healthAfter": float(m_full.group(5)),
                    "raw": l
                })
            else:
                report["errors"].append(f"Malformed boss_hit line at {idx}: {l}")

        # boss_health_read: reader=<r> value=<v> max=<m>
        elif l.startswith("[FrameworkProof] boss_health_read"):
            m = re.search(r"reader=([a-zA-Z0-9_]+).*?\bvalue=(-?[0-9.]+)\s+max=(-?[0-9.]+)", l)
            if m:
                report["parsed_data"]["health_reads"].append({
                    "line_index": idx,
                    "reader": m.group(1),
                    "value": float(m.group(2)),
                    "max": float(m.group(3)),
                    "raw": l
                })
            else:
                report["errors"].append(f"Malformed boss_health_read line at {idx}: {l}")

        # boss_dead: generation=<g> executorAborted=<0|1>
        elif l.startswith("[FrameworkProof] boss_dead"):
            m = re.search(r"generation=(\d+)\s+executorAborted=(\d+)", l)
            if m:
                report["parsed_data"]["boss_dead"].append({
                    "line_index": idx,
                    "generation": int(m.group(1)),
                    "executorAborted": int(m.group(2)),
                    "raw": l
                })
            else:
                report["errors"].append(f"Malformed boss_dead line at {idx}: {l}")

        elif l.startswith("[FrameworkProof] decision"):
            report["parsed_data"]["decisions"].append({"line_index": idx, "raw": l})

        elif l.startswith("[FrameworkProof] playback_start"):
            report["parsed_data"]["playback_starts"].append({"line_index": idx, "raw": l})

        elif l.startswith("[FrameworkProof] damage") or l.startswith("[FrameworkProof] damage_attempt"):
            report["parsed_data"]["player_damages"].append({"line_index": idx, "raw": l})

    hits = report["parsed_data"]["boss_hits"]
    reads = report["parsed_data"]["health_reads"]
    dead_events = report["parsed_data"]["boss_dead"]

    # 3. Check Hits Validation & Arithmetic
    if not hits:
        report["checks"]["has_boss_hits"] = False
        report["errors"].append("Zero boss_hit lines found in log.")
    else:
        report["checks"]["has_boss_hits"] = True
        hits_arithmetic_ok = True
        for i, h in enumerate(hits):
            expected_delta = h["healthBefore"] - h["healthAfter"]
            if abs(expected_delta - h["damage"]) > tolerance:
                hits_arithmetic_ok = False
                report["errors"].append(
                    f"Hit #{h['attack']}: damage arithmetic mismatch: {h['healthBefore']} -> {h['healthAfter']} "
                    f"(delta {expected_delta:.2f}) != damage {h['damage']:.2f}"
                )
            if h["damage"] <= 0.0:
                hits_arithmetic_ok = False
                report["errors"].append(f"Hit #{h['attack']}: non-positive damage {h['damage']}")
            if h["healthAfter"] >= h["healthBefore"]:
                hits_arithmetic_ok = False
                report["errors"].append(f"Hit #{h['attack']}: healthAfter ({h['healthAfter']}) >= healthBefore ({h['healthBefore']})")
            if i > 0:
                prev_h = hits[i - 1]
                if abs(h["healthBefore"] - prev_h["healthAfter"]) > tolerance:
                    hits_arithmetic_ok = False
                    report["errors"].append(
                        f"Hit #{h['attack']}: continuity gap: healthBefore ({h['healthBefore']}) != previous healthAfter ({prev_h['healthAfter']})"
                    )

        report["checks"]["hits_arithmetic"] = hits_arithmetic_ok

    # 4. Check ReadAttribute Bridge Reflection
    # Each hit must have a subsequent ReadAttribute reading value == healthAfter
    read_attribute_ok = True
    if not hits:
        read_attribute_ok = False
    else:
        for h in hits:
            # Find ReadAttribute reads occurring at or after this hit
            matching_reads = [
                r for r in reads
                if r["reader"] == "ReadAttribute"
                and r["line_index"] >= h["line_index"]
                and abs(r["value"] - h["healthAfter"]) <= tolerance
            ]
            if not matching_reads:
                read_attribute_ok = False
                report["errors"].append(
                    f"Hit #{h['attack']} (healthAfter={h['healthAfter']}): no ReadAttribute read matches value={h['healthAfter']}"
                )
            else:
                for mr in matching_reads:
                    if mr["max"] <= 0.0:
                        read_attribute_ok = False
                        report["errors"].append(f"ReadAttribute reported non-positive max={mr['max']}")

    report["checks"]["read_attribute_bridge"] = read_attribute_ok

    # 5. Check Death Authority
    is_lethal = hits and hits[-1]["healthAfter"] <= 0.0
    if is_lethal:
        if len(dead_events) != 1:
            report["checks"]["single_boss_dead"] = False
            report["errors"].append(f"Lethal run requires exactly 1 boss_dead event, found {len(dead_events)}")
        else:
            dead = dead_events[0]
            if dead["executorAborted"] != 1:
                report["checks"]["single_boss_dead"] = False
                report["errors"].append(f"boss_dead has executorAborted={dead['executorAborted']}, expected 1")
            elif dead["generation"] <= 0:
                report["checks"]["single_boss_dead"] = False
                report["errors"].append(f"boss_dead has non-positive generation={dead['generation']}")
            else:
                report["checks"]["single_boss_dead"] = True
    else:
        if dead_events:
            report["checks"]["single_boss_dead"] = False
            report["errors"].append("Non-lethal run emitted unexpected boss_dead event")
        else:
            report["checks"]["single_boss_dead"] = True

    # 6. Post-Mortem Invariant: No decision/playback/player-damage after death
    if dead_events:
        death_line_idx = dead_events[0]["line_index"]
        post_mortem_violations = []

        for d in report["parsed_data"]["decisions"]:
            if d["line_index"] > death_line_idx:
                post_mortem_violations.append(f"Decision emitted after death at line {d['line_index']}: {d['raw']}")

        for p in report["parsed_data"]["playback_starts"]:
            if p["line_index"] > death_line_idx:
                post_mortem_violations.append(f"Playback_start emitted after death at line {p['line_index']}: {p['raw']}")

        for dmg in report["parsed_data"]["player_damages"]:
            if dmg["line_index"] > death_line_idx:
                post_mortem_violations.append(f"Player damage emitted after death at line {dmg['line_index']}: {dmg['raw']}")

        for h in hits:
            if h["line_index"] > death_line_idx:
                post_mortem_violations.append(f"Boss hit registered after death at line {h['line_index']}: {h['raw']}")

        if post_mortem_violations:
            report["checks"]["no_activity_after_death"] = False
            report["errors"].extend(post_mortem_violations)
        else:
            report["checks"]["no_activity_after_death"] = True
    else:
        report["checks"]["no_activity_after_death"] = True

    # 7. Overall Verdict
    all_passed = len(report["errors"]) == 0 and all(report["checks"].values())
    report["passed"] = all_passed
    summary_status = "PASS" if all_passed else "FAIL"
    report["summary"] = (
        f"[{summary_status}] F6a proof: hits={len(hits)} reads={len(reads)} "
        f"dead={'YES' if dead_events else 'NO'} errors={len(report['errors'])}"
    )

    return report


def grade_file(log_path: str) -> int:
    path = Path(log_path)
    if not path.is_file():
        print(f"ERROR: log file not found: {log_path}", file=sys.stderr)
        return 2

    raw_text = path.read_text(encoding="utf-8", errors="replace")
    framework_lines = parse_framework_log(raw_text)

    if not framework_lines:
        print(f"ERROR: no [FrameworkProof] lines found in {log_path}", file=sys.stderr)
        return 2

    report = grade_f6a_log_lines(framework_lines)

    print("================================================================================")
    print(f" F6A LOG GRADING: {path.name}")
    print("================================================================================")
    print(f"Verdict: {report['summary']}")
    print("\nChecks:")
    for check_name, status in report["checks"].items():
        print(f"  - {check_name}: {'PASS' if status else 'FAIL'}")

    if report["errors"]:
        print("\nErrors / Invariant Violations:")
        for err in report["errors"]:
            print(f"  [X] {err}")

    print("\nParsed Summary:")
    print(f"  - Registered Boss Hits:  {len(report['parsed_data']['boss_hits'])}")
    print(f"  - Health Reads:          {len(report['parsed_data']['health_reads'])}")
    print(f"  - Death Events:          {len(report['parsed_data']['boss_dead'])}")
    print("================================================================================")

    return 0 if report["passed"] else 1


def main():
    parser = argparse.ArgumentParser(description="Antigravity F6a Boss Target Proof Grader")
    parser.add_argument("log", nargs="?", help="Path to editor_raw.log")
    parser.add_argument("--log", dest="log_opt", help="Path to editor_raw.log")
    args = parser.parse_args()

    log_file = args.log_opt or args.log
    if not log_file:
        parser.print_help()
        sys.exit(2)

    sys.exit(grade_file(log_file))


if __name__ == "__main__":
    main()
