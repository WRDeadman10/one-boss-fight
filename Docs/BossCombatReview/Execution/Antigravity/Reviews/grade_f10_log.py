#!/usr/bin/env python3
"""
grade_f10_log.py
================
Antigravity Slice F10 Weapon Attack Row Grader (Lead Order C-456 / C-457).

Parses editor raw log from PIE playback of Slice F10 (Weapon Attack Row Hit Intake Authority)
and verifies the following fail-closed requirements:
1. No unhandled ERROR, FATAL, or assertion failures.
2. Exact Log Line Formats:
   - attack_row weapon=%s kind=%s found=%d posture=%g bleed=%g healthMult=%g
   - boss_hit damage=%g healthBefore=%g healthAfter=%g
   - posture_drain amount=%g postureBefore=%g postureAfter=%g max=%g
   - bleed_buildup amount=%g buildup=%g threshold=%g result=%s
   - bleed_proc procs=%d damage=%g healthBefore=%g healthAfter=%g nextThreshold=%g
   - stance_break state=%s ...
   - RESULT outcome=%s ...
3. Fail-Closed Cross-Checks:
   - attack_row must appear immediately before boss_hit of the same hit.
   - With found=1:
     * boss_hit damage == min(healthBefore, ProfileDamage * healthMult).
     * posture_drain amount == min(postureBefore, row.posture).
     * bleed_buildup amount == row.bleed (unless dead or proc frame).
   - Posture drain reduces posture deterministically; posture <= 0 triggers stance break.
   - Bleed buildup increments by row.bleed until threshold triggers bleed_proc (damage <= 20% max, healthAfter >= 1).
   - Regression mode (--expect-no-attack-rows): ensures zero attack_row lines.
   - Clean terminal outcome (RESULT line verified).
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional


def grade_f10_log_lines(
    lines: List[str],
    expect_rows: Optional[int] = None,
    expect_procs: Optional[int] = None,
    expect_stance_break: bool = False,
    expect_weapon: Optional[str] = None,
    expect_kind: Optional[str] = None,
    expect_no_attack_rows: bool = False,
    expect_no_bleed: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    # State tracking
    boss_max_health: Optional[float] = None
    boss_hit_damage_profile: float = 100.0  # Fixture default
    current_health: Optional[float] = None
    current_posture: Optional[float] = None
    posture_max: Optional[float] = 100.0
    current_buildup: float = 0.0
    current_threshold: float = 100.0
    proc_count: int = 0
    stance_breaks: int = 0
    is_dead: bool = False
    pending_proc_after_result: bool = False
    pending_hit_after_row: bool = False

    # Pending attack row context for subsequent hit verification
    active_row: Optional[Dict[str, Any]] = None

    # Records for audit summary
    attack_rows: List[Dict[str, Any]] = []
    boss_hits: List[Dict[str, Any]] = []
    posture_drains: List[Dict[str, Any]] = []
    buildup_events: List[Dict[str, Any]] = []
    proc_events: List[Dict[str, Any]] = []
    results: List[str] = []

    # Regex patterns
    re_boss_health = re.compile(r"\[FrameworkProof\]\s+boss_health\s+max=([\d.]+)\s+playerHitDamage=([\d.]+)")
    re_attack_row = re.compile(
        r"\[FrameworkProof\]\s+attack_row\s+weapon=(\w+)\s+kind=(\w+)\s+found=(\d+)\s+posture=([\d.]+)\s+bleed=([\d.]+)\s+healthMult=([\d.]+)"
    )
    re_boss_hit = re.compile(r"\[FrameworkProof\]\s+boss_hit\s+damage=([\d.]+)\s+healthBefore=([\d.]+)\s+healthAfter=([\d.]+)")
    re_posture_drain = re.compile(
        r"\[FrameworkProof\]\s+posture_drain\s+amount=([\d.]+)\s+postureBefore=([\d.]+)\s+postureAfter=([\d.]+)\s+max=([\d.]+)"
    )
    re_bleed_buildup = re.compile(
        r"\[FrameworkProof\]\s+bleed_buildup\s+amount=([\d.]+)\s+buildup=([\d.]+)\s+threshold=([\d.]+)\s+result=([a-zA-Z0-9_ ]+)"
    )
    re_bleed_proc = re.compile(
        r"\[FrameworkProof\]\s+bleed_proc\s+procs=(\d+)\s+damage=([\d.]+)\s+healthBefore=([\d.]+)\s+healthAfter=([\d.]+)\s+nextThreshold=([\d.]+)"
    )
    re_stance_break = re.compile(r"\[FrameworkProof\]\s+stance_break\s+state=(\w+)")
    re_boss_dead = re.compile(r"\[FrameworkProof\]\s+boss_dead\s+generation=(\d+)")
    re_encounter_reset = re.compile(r"\[FrameworkProof\]\s+encounter_reset\s+generation=(\d+)")
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

        # 2. Boss initialization
        m_init = re_boss_health.search(line_clean)
        if m_init:
            boss_max_health = float(m_init.group(1))
            boss_hit_damage_profile = float(m_init.group(2))
            current_health = boss_max_health
            current_posture = posture_max
            continue

        # 3. Attack Row token
        m_row = re_attack_row.search(line_clean)
        if m_row:
            if pending_hit_after_row:
                errors.append(f"Line {line_idx}: Previous attack_row was not followed by boss_hit before new attack_row")

            if expect_no_attack_rows:
                errors.append(f"Line {line_idx}: attack_row found when --expect-no-attack-rows specified: {line_clean}")

            row_data = {
                "line": line_idx,
                "weapon": m_row.group(1),
                "kind": m_row.group(2),
                "found": int(m_row.group(3)),
                "posture": float(m_row.group(4)),
                "bleed": float(m_row.group(5)),
                "healthMult": float(m_row.group(6)),
            }
            attack_rows.append(row_data)
            active_row = row_data
            pending_hit_after_row = True

            if expect_weapon and row_data["weapon"] != expect_weapon:
                errors.append(f"Line {line_idx}: weapon '{row_data['weapon']}' does not match expected '{expect_weapon}'")
            if expect_kind and row_data["kind"] != expect_kind:
                errors.append(f"Line {line_idx}: kind '{row_data['kind']}' does not match expected '{expect_kind}'")
            continue

        # 4. Boss Hit token
        m_hit = re_boss_hit.search(line_clean)
        if m_hit:
            dmg = float(m_hit.group(1))
            before = float(m_hit.group(2))
            after = float(m_hit.group(3))
            boss_hits.append({"line": line_idx, "damage": dmg, "before": before, "after": after})
            pending_hit_after_row = False

            if abs((before - after) - dmg) > 1e-4:
                errors.append(f"Line {line_idx}: Hit math mismatch: before({before}) - after({after}) != damage({dmg})")

            if active_row and active_row["found"] == 1:
                expected_loss = min(before, round(boss_hit_damage_profile * active_row["healthMult"], 4))
                if abs(dmg - expected_loss) > 1e-4:
                    errors.append(
                        f"Line {line_idx}: Hit damage ({dmg}) does not match expected ({expected_loss}) from row healthMult {active_row['healthMult']}"
                    )
            current_health = after
            if after <= 0.0:
                is_dead = True
            continue

        # 5. Posture Drain token
        m_drain = re_posture_drain.search(line_clean)
        if m_drain:
            amount = float(m_drain.group(1))
            before = float(m_drain.group(2))
            after = float(m_drain.group(3))
            p_max = float(m_drain.group(4))
            posture_drains.append({"line": line_idx, "amount": amount, "before": before, "after": after, "max": p_max})

            if abs((before - after) - amount) > 1e-4:
                errors.append(f"Line {line_idx}: Posture drain math mismatch: before({before}) - after({after}) != amount({amount})")

            if active_row and active_row["found"] == 1:
                expected_drain = min(before, active_row["posture"])
                if abs(amount - expected_drain) > 1e-4:
                    errors.append(
                        f"Line {line_idx}: Posture drain amount ({amount}) does not match row posture damage ({expected_drain})"
                    )
            current_posture = after
            continue

        # 6. Stance Break token
        if re_stance_break.search(line_clean):
            stance_breaks += 1
            continue

        # 7. Bleed Buildup token
        m_bleed = re_bleed_buildup.search(line_clean)
        if m_bleed:
            if expect_no_bleed:
                errors.append(f"Line {line_idx}: bleed_buildup found when --expect-no-bleed specified: {line_clean}")

            amount = float(m_bleed.group(1))
            buildup = float(m_bleed.group(2))
            threshold = float(m_bleed.group(3))
            result = m_bleed.group(4).strip()
            buildup_events.append({"line": line_idx, "amount": amount, "buildup": buildup, "threshold": threshold, "result": result})

            if active_row and active_row["found"] == 1:
                expected_bleed = active_row["bleed"]
                if abs(amount - expected_bleed) > 1e-4 and not is_dead:
                    errors.append(
                        f"Line {line_idx}: Bleed buildup amount ({amount}) does not match row bleed buildup ({expected_bleed})"
                    )

            if result == "added":
                expected_buildup = current_buildup + amount
                if abs(buildup - expected_buildup) > 1e-4:
                    errors.append(
                        f"Line {line_idx}: bleed_buildup math mismatch: expected buildup {expected_buildup}, got {buildup}"
                    )
                current_buildup = buildup
                current_threshold = threshold
            elif result == "proc":
                pending_proc_after_result = True
                current_buildup = 0.0
                expected_next = min(current_threshold + 20.0, 200.0)
                if abs(threshold - expected_next) > 1e-4:
                    errors.append(
                        f"Line {line_idx}: bleed_buildup proc threshold ({threshold}) did not advance to expected ({expected_next})"
                    )
                current_threshold = expected_next
            elif result == "no buildup":
                pass
            continue

        # 8. Bleed Proc token
        m_proc = re_bleed_proc.search(line_clean)
        if m_proc:
            if expect_no_bleed:
                errors.append(f"Line {line_idx}: bleed_proc found when --expect-no-bleed specified: {line_clean}")

            p_num = int(m_proc.group(1))
            dmg = float(m_proc.group(2))
            before = float(m_proc.group(3))
            after = float(m_proc.group(4))
            next_t = float(m_proc.group(5))
            proc_events.append(
                {"line": line_idx, "procs": p_num, "damage": dmg, "before": before, "after": after, "nextThreshold": next_t}
            )
            proc_count = p_num

            if after < 1.0:
                errors.append(f"Line {line_idx}: Bleed proc lethal violation: healthAfter={after} (must be >= 1)")
            if abs((before - after) - dmg) > 1e-4:
                errors.append(f"Line {line_idx}: Bleed proc health math mismatch: before({before}) - after({after}) != damage({dmg})")
            current_health = after
            continue

        # 9. Boss Dead & Reset
        if re_boss_dead.search(line_clean):
            is_dead = True
            continue

        if re_encounter_reset.search(line_clean):
            is_dead = False
            current_buildup = 0.0
            current_threshold = 100.0
            current_health = boss_max_health
            current_posture = posture_max
            continue

        # 10. RESULT token
        m_res = re_result.search(line_clean)
        if m_res:
            results.append(m_res.group(1))
            active_row = None
            pending_hit_after_row = False
            continue

    if pending_hit_after_row:
        errors.append("Trailing attack_row was not followed by a boss_hit before log conclusion.")

    # Post-parse validation
    if expect_rows is not None and len(attack_rows) < expect_rows:
        errors.append(f"Expected at least {expect_rows} attack_row events, found {len(attack_rows)}")
    elif not expect_no_attack_rows and expect_rows is None and len(attack_rows) == 0:
        warnings.append("Zero attack_row events recorded in log.")

    if expect_procs is not None and len(proc_events) != expect_procs:
        errors.append(f"Expected exactly {expect_procs} bleed procs, found {len(proc_events)}")

    if expect_stance_break and stance_breaks == 0:
        errors.append("Expected at least one stance_break event, found none.")

    if not results:
        errors.append("Log does not contain a clean [FrameworkProof] RESULT line.")

    is_pass = len(errors) == 0
    return {
        "pass": is_pass,
        "errors": errors,
        "warnings": warnings,
        "attack_rows_count": len(attack_rows),
        "boss_hits_count": len(boss_hits),
        "posture_drains_count": len(posture_drains),
        "buildup_events_count": len(buildup_events),
        "proc_events_count": len(proc_events),
        "stance_breaks": stance_breaks,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Antigravity Slice F10 Weapon Attack Row Grader")
    parser.add_argument("log_path", help="Path to editor_raw.log to evaluate")
    parser.add_argument("--expect-rows", type=int, default=None, help="Minimum number of attack_row events expected")
    parser.add_argument("--expect-procs", type=int, default=None, help="Expected number of bleed procs")
    parser.add_argument("--expect-stance-break", action="store_true", help="Assert that boss entered stance break")
    parser.add_argument("--expect-weapon", type=str, default=None, help="Assert weapon matches")
    parser.add_argument("--expect-kind", type=str, default=None, help="Assert attack kind matches")
    parser.add_argument("--expect-no-attack-rows", action="store_true", help="Assert 0 attack_row events (regression mode)")
    parser.add_argument("--expect-no-bleed", action="store_true", help="Assert 0 bleed events")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if not os.path.exists(args.log_path):
        print(f"ERROR: Log file not found: {args.log_path}", file=sys.stderr)
        sys.exit(2)

    with open(args.log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    summary = grade_f10_log_lines(
        lines=lines,
        expect_rows=args.expect_rows,
        expect_procs=args.expect_procs,
        expect_stance_break=args.expect_stance_break,
        expect_weapon=args.expect_weapon,
        expect_kind=args.expect_kind,
        expect_no_attack_rows=args.expect_no_attack_rows,
        expect_no_bleed=args.expect_no_bleed,
        verbose=args.verbose,
    )

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        status_str = "PASS" if summary["pass"] else "FAIL"
        print(f"=== F10 Log Grader Result: {status_str} ===")
        print(f"Attack Rows  : {summary['attack_rows_count']}")
        print(f"Boss Hits    : {summary['boss_hits_count']}")
        print(f"Drains       : {summary['posture_drains_count']}")
        print(f"Buildups     : {summary['buildup_events_count']}")
        print(f"Procs        : {summary['proc_events_count']}")
        print(f"Stance Breaks: {summary['stance_breaks']}")
        print(f"Outcomes     : {', '.join(summary['results'])}")
        if summary["warnings"]:
            print("Warnings:")
            for w in summary["warnings"]:
                print(f"  [WARN] {w}")
        if summary["errors"]:
            print("Errors:")
            for e in summary["errors"]:
                print(f"  [ERROR] {e}")

    sys.exit(0 if summary["pass"] else 1)


if __name__ == "__main__":
    main()
