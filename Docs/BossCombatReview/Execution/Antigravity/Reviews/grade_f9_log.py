#!/usr/bin/env python3
"""
grade_f9_log.py
================
Antigravity F9 Bleed / Ailment Grader (Lead Order C-453).

Parses editor raw log from PIE playback of Slice F9 (Boss Bleed / Ailment on Framework Boss)
and verifies the following fail-closed requirements:
1. No unhandled ERROR, FATAL, or assertion failures.
2. Exact Log Line Formats (all [FrameworkProof] ...):
   - bleed_buildup amount=%g buildup=%g threshold=%g result=<added|proc|no buildup|dead|dormant|transition|same frame as a proc>
   - bleed_proc procs=%d damage=%g healthBefore=%g healthAfter=%g nextThreshold=%g
   - boss_hit damage=%g healthBefore=%g healthAfter=%g
   - phase_transition attack=%d from=%s to=%s health=%g max=%g fraction=%g
   - boss_dead generation=%llu ...
   - encounter_reset generation=%llu ...
   - RESULT outcome=<outcome> ...
3. Fail-Closed Rules:
   - Every result=proc is followed immediately by exactly one bleed_proc line.
   - Buildup math: when result=added, buildup == prev_buildup + amount.
   - At proc: buildup resets to 0, threshold advances to nextThreshold == min(threshold + 20, 200).
   - Non-lethal bleed proc damage:
     * healthAfter >= 1 (bleed proc NEVER kills).
     * damage <= 20% of max health (min(0.20 * max, healthBefore - 1)).
     * healthAfter == healthBefore - damage.
   - Lifecycle rules:
     * No bleed_buildup (with result=added or result=proc) after boss_dead until encounter_reset.
     * After encounter_reset, the buildup resets to 0 and threshold resets to initial (100).
4. Regression Mode (--expect-no-bleed):
   - Verified that zero bleed_buildup and zero bleed_proc lines exist.
5. Clean Terminal Outcome:
   - Encounters conclude with a valid [FrameworkProof] RESULT line.
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional


def grade_f9_log_lines(lines: List[str], expect_no_bleed: bool = False, verbose: bool = False) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    # Parsed state
    boss_max_health: Optional[float] = None
    current_health: Optional[float] = None
    current_buildup: float = 0.0
    current_threshold: float = 100.0  # Initial threshold default
    proc_count: int = 0
    is_dead: bool = False
    pending_proc_after_result: bool = False
    current_generation: int = 1

    # Configuration constants for F9 proof profile
    INITIAL_THRESHOLD: float = 100.0
    THRESHOLD_INCREASE: float = 20.0
    THRESHOLD_MAX: float = 200.0
    BLEED_HP_FRACTION: float = 0.20

    # Records for audit summary
    buildup_events: List[Dict[str, Any]] = []
    proc_events: List[Dict[str, Any]] = []
    boss_hits: List[Dict[str, Any]] = []
    phase_transitions: List[Dict[str, Any]] = []
    results: List[str] = []

    # Regex patterns
    re_boss_health = re.compile(r"\[FrameworkProof\]\s+boss_health\s+max=([\d.]+)")
    re_boss_hit = re.compile(r"\[FrameworkProof\]\s+boss_hit\s+damage=([\d.]+)\s+healthBefore=([\d.]+)\s+healthAfter=([\d.]+)")
    re_bleed_buildup = re.compile(
        r"\[FrameworkProof\]\s+bleed_buildup\s+amount=([\d.]+)\s+buildup=([\d.]+)\s+threshold=([\d.]+)\s+result=([a-zA-Z0-9_ ]+)"
    )
    re_bleed_proc = re.compile(
        r"\[FrameworkProof\]\s+bleed_proc\s+procs=(\d+)\s+damage=([\d.]+)\s+healthBefore=([\d.]+)\s+healthAfter=([\d.]+)\s+nextThreshold=([\d.]+)"
    )
    re_boss_dead = re.compile(r"\[FrameworkProof\]\s+boss_dead\s+generation=(\d+)")
    re_encounter_reset = re.compile(r"\[FrameworkProof\]\s+encounter_reset\s+generation=(\d+)")
    re_phase_transition = re.compile(
        r"\[FrameworkProof\]\s+phase_transition\s+attack=(\d+)\s+from=(\w+)\s+to=(\w+)\s+health=([\d.]+)\s+max=([\d.]+)\s+fraction=([\d.]+)"
    )
    re_result = re.compile(r"\[FrameworkProof\]\s+RESULT\s+outcome=(\w+)")
    re_error = re.compile(r"(?:\[FrameworkProof\]\s+ERROR:|Fatal error:|Assertion failed:)", re.IGNORECASE)

    for line_idx, line in enumerate(lines, 1):
        line_clean = line.strip()

        # 1. Error check
        if re_error.search(line_clean):
            errors.append(f"Line {line_idx}: Explicit error detected: {line_clean}")

        # Check pending proc fulfillment immediately
        if pending_proc_after_result:
            m_proc = re_bleed_proc.search(line_clean)
            if not m_proc:
                errors.append(
                    f"Line {line_idx}: bleed_buildup with result=proc was not followed immediately by bleed_proc (found: {line_clean})"
                )
            pending_proc_after_result = False

        # 2. boss_health
        m = re_boss_health.search(line_clean)
        if m:
            boss_max_health = float(m.group(1))
            current_health = boss_max_health
            continue

        # 3. boss_hit
        m = re_boss_hit.search(line_clean)
        if m:
            dmg = float(m.group(1))
            hb = float(m.group(2))
            ha = float(m.group(3))
            current_health = ha
            boss_hits.append({"line": line_idx, "damage": dmg, "healthBefore": hb, "healthAfter": ha})
            continue

        # 4. bleed_buildup
        m = re_bleed_buildup.search(line_clean)
        if m:
            amt = float(m.group(1))
            bld = float(m.group(2))
            thr = float(m.group(3))
            res = m.group(4).strip()

            buildup_events.append({
                "line": line_idx,
                "amount": amt,
                "buildup": bld,
                "threshold": thr,
                "result": res,
                "generation": current_generation,
            })

            if expect_no_bleed:
                errors.append(f"Line {line_idx}: Found unexpected bleed_buildup while --expect-no-bleed is active")

            # Check dead boss rule
            if is_dead and res not in ("dead", "no buildup"):
                errors.append(f"Line {line_idx}: bleed_buildup on dead boss with invalid result='{res}' (expected 'dead')")

            if res == "added":
                # For regular addition, threshold is the current threshold
                if abs(thr - current_threshold) > 1e-4:
                    errors.append(
                        f"Line {line_idx}: bleed_buildup threshold={thr} does not match expected threshold={current_threshold}"
                    )
                expected_buildup = current_buildup + amt
                if abs(bld - expected_buildup) > 1e-4:
                    errors.append(
                        f"Line {line_idx}: bleed_buildup result=added has buildup={bld}, expected {expected_buildup} (prev {current_buildup} + {amt})"
                    )
                current_buildup = bld
            elif res == "proc":
                # When RPGBleedRules::Apply returns Proc, BleedState.Threshold is already incremented to nextThreshold
                expected_new_threshold = min(current_threshold + THRESHOLD_INCREASE, THRESHOLD_MAX)
                if abs(thr - expected_new_threshold) > 1e-4:
                    errors.append(
                        f"Line {line_idx}: bleed_buildup result=proc threshold={thr} does not match expected new threshold={expected_new_threshold}"
                    )
                if abs(bld - 0.0) > 1e-4:
                    errors.append(f"Line {line_idx}: bleed_buildup result=proc must reset buildup to 0, found {bld}")
                if current_buildup + amt < current_threshold - 1e-4:
                    errors.append(
                        f"Line {line_idx}: bleed_buildup result=proc triggered before reaching threshold (prev {current_buildup} + {amt} < {current_threshold})"
                    )
                current_buildup = 0.0
                current_threshold = expected_new_threshold
                pending_proc_after_result = True
            elif res in ("no buildup", "dead", "dormant", "transition", "same frame as a proc"):
                # Non-accumulating states
                pass
            else:
                warnings.append(f"Line {line_idx}: Unrecognized bleed_buildup result: '{res}'")
            continue

        # 5. bleed_proc
        m = re_bleed_proc.search(line_clean)
        if m:
            p_procs = int(m.group(1))
            p_dmg = float(m.group(2))
            p_hb = float(m.group(3))
            p_ha = float(m.group(4))
            p_next_thr = float(m.group(5))

            proc_events.append({
                "line": line_idx,
                "procs": p_procs,
                "damage": p_dmg,
                "healthBefore": p_hb,
                "healthAfter": p_ha,
                "nextThreshold": p_next_thr,
            })

            if expect_no_bleed:
                errors.append(f"Line {line_idx}: Found unexpected bleed_proc while --expect-no-bleed is active")

            # Check proc sequence counter
            expected_proc_count = proc_count + 1
            if p_procs != expected_proc_count:
                errors.append(
                    f"Line {line_idx}: bleed_proc procs={p_procs} out of order (expected {expected_proc_count})"
                )
            proc_count = p_procs

            # Check health non-lethal rule: healthAfter >= 1
            if p_ha < 1.0:
                errors.append(
                    f"Line {line_idx}: bleed_proc healthAfter={p_ha} violates non-lethal contract (must be >= 1.0)"
                )

            # Check damage calculation
            max_hp = boss_max_health if boss_max_health is not None else 250.0
            nominal_proc_damage = max_hp * BLEED_HP_FRACTION
            expected_dmg = min(nominal_proc_damage, max(0.0, p_hb - 1.0))
            if abs(p_dmg - expected_dmg) > 1e-3:
                errors.append(
                    f"Line {line_idx}: bleed_proc damage={p_dmg} does not match expected damage={expected_dmg} (nominal {nominal_proc_damage}, healthBefore {p_hb})"
                )

            if abs(p_ha - (p_hb - p_dmg)) > 1e-3:
                errors.append(
                    f"Line {line_idx}: bleed_proc health math mismatch: healthAfter {p_ha} != healthBefore {p_hb} - damage {p_dmg}"
                )

            current_health = p_ha

            # Check nextThreshold matches current_threshold (which was updated at result=proc)
            if abs(p_next_thr - current_threshold) > 1e-4:
                errors.append(
                    f"Line {line_idx}: bleed_proc nextThreshold={p_next_thr} does not match expected {current_threshold}"
                )
            continue

        # 6. phase_transition
        m = re_phase_transition.search(line_clean)
        if m:
            atk = int(m.group(1))
            frm = m.group(2)
            to = m.group(3)
            hp = float(m.group(4))
            mx = float(m.group(5))
            frac = float(m.group(6))
            phase_transitions.append({
                "line": line_idx,
                "attack": atk,
                "from": frm,
                "to": to,
                "health": hp,
                "max": mx,
                "fraction": frac,
            })
            continue

        # 7. boss_dead
        m = re_boss_dead.search(line_clean)
        if m:
            is_dead = True
            continue

        # 8. encounter_reset
        m = re_encounter_reset.search(line_clean)
        if m:
            current_generation = int(m.group(1))
            is_dead = False
            current_buildup = 0.0
            current_threshold = INITIAL_THRESHOLD
            continue

        # 9. RESULT
        m = re_result.search(line_clean)
        if m:
            results.append(m.group(1))
            continue

    # Terminal checks
    if pending_proc_after_result:
        errors.append("Log ended with unfulfilled bleed_buildup result=proc (missing bleed_proc)")

    if len(results) == 0:
        errors.append("No valid [FrameworkProof] RESULT line found in log")

    if not expect_no_bleed and len(buildup_events) == 0:
        errors.append("Expected bleed events in proof run, but 0 bleed_buildup lines were found")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "parsed_data": {
            "boss_max_health": boss_max_health,
            "final_current_health": current_health,
            "final_buildup": current_buildup,
            "final_threshold": current_threshold,
            "procs_total": proc_count,
            "buildup_event_count": len(buildup_events),
            "proc_event_count": len(proc_events),
            "boss_hit_count": len(boss_hits),
            "phase_transition_count": len(phase_transitions),
            "results": results,
        },
    }


def grade_f9_file(file_path: str, expect_no_bleed: bool = False, verbose: bool = False) -> Dict[str, Any]:
    if not os.path.exists(file_path):
        return {
            "passed": False,
            "errors": [f"File not found: {file_path}"],
            "warnings": [],
            "parsed_data": {},
        }
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return grade_f9_log_lines(lines, expect_no_bleed=expect_no_bleed, verbose=verbose)


def main():
    parser = argparse.ArgumentParser(description="Antigravity F9 Bleed / Ailment Log Grader")
    parser.add_argument("log_path", help="Path to editor_raw.log to grade")
    parser.add_argument(
        "--expect-no-bleed",
        action="store_true",
        help="Assert that zero bleed_buildup and bleed_proc lines exist (regression mode)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose execution trace")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON result")

    args = parser.parse_args()
    res = grade_f9_file(args.log_path, expect_no_bleed=args.expect_no_bleed, verbose=args.verbose)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        status_str = "PASS" if res["passed"] else "FAIL"
        print(f"[{status_str}] Grading {args.log_path}")
        if res["errors"]:
            print("Errors:")
            for err in res["errors"]:
                print(f"  - {err}")
        if res["warnings"] and args.verbose:
            print("Warnings:")
            for warn in res["warnings"]:
                print(f"  - {warn}")
        data = res.get("parsed_data", {})
        print(
            f"Summary: procs={data.get('procs_total', 0)}, buildups={data.get('buildup_event_count', 0)}, "
            f"hits={data.get('boss_hit_count', 0)}, phase_transitions={data.get('phase_transition_count', 0)}, "
            f"results={data.get('results', [])}"
        )

    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
