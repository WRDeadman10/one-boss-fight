#!/usr/bin/env python3
"""
grade_f8_log.py
================
Antigravity F8 Posture and Stance Break Grader (Lead Orders C-447, C-448, C-449, C-450).

Parses editor raw log from PIE playback of Slice F8 (Boss Posture and Stance Break)
and verifies the following fail-closed requirements:
1. No unhandled ERROR, FATAL, or assertion failures.
2. Posture Drain Integrity:
   - postureBefore - amount == postureAfter (within tolerance).
   - postureAfter >= 0 and postureBefore <= max.
3. Drain Sum to Max & Zero Gate before Stance Break:
   - posture_drain amounts sum to max before a stance_break.
   - stance_break occurs only after a drain that reaches postureAfter == 0.
   - stance_break NEVER occurs after boss_dead.
4. Cleanup Precedence for MidAttack Stance Break:
   - For stance_break state=MidAttack, cleanup reason=StanceBreak precedes stance_break.
   - For stance_break state=Neutral, cleanup reason=StanceBreak is not expected.
5. No Decision or Playback during Stagger:
   - No 'decision' or 'playback_start' lines between stance_break and stagger_recovery of the same generation.
6. Posture Refill on Recovery:
   - stagger_recovery postureRefilled == max.
7. Deferred Phase Transition:
   - A phase_transition that is due (health <= fraction * max) while staggered appears only AFTER stagger_recovery.
8. Neutral Walk Resume (C-449, C-450):
   - A stance_break state=Neutral before walk start= must be followed by stagger_recovery,
     then walk_resumed generation=<g>, then walk start=.
9. Generation & Lifecycle Cleanliness:
   - Stance break state does not leak across encounter_reset (the pair must close or boss_dead must follow).
   - Encounter reset resets posture state cleanly.
10. Regression / Non-posture Mode (--expect-no-posture):
   - Verified that zero posture or stance_break lines exist.
11. Clean Terminal Outcome:
   - Encounters conclude with a valid [FrameworkProof] RESULT line.

Log Token Specifications (per C-448, C-449):
- [FrameworkProof] boss_health max=%g playerHitDamage=%g ...
- [FrameworkProof] boss_hit damage=%g healthBefore=%g healthAfter=%g
- [FrameworkProof] posture_drain amount=%g postureBefore=%g postureAfter=%g max=%g
- [FrameworkProof] posture_held reason=StaggerActive posture=%g
- [FrameworkProof] cleanup reason=StanceBreak modelIdle=1 ownedMontageStopped=1
- [FrameworkProof] stance_break state=<MidAttack|Neutral> duration=%g generation=%llu phase=<id>
- [FrameworkProof] stagger_recovery postureRefilled=%g generation=%llu
- [FrameworkProof] walk_resumed generation=%llu
- [FrameworkProof] walk start=...
- [FrameworkProof] posture_regen_full posture=%g max=%g
- [FrameworkProof] phase_transition ...
- [FrameworkProof] decision ...
- [FrameworkProof] playback_start ...
- [FrameworkProof] boss_dead generation=%llu ...
- [FrameworkProof] encounter_reset generation=%llu ...
- [FrameworkProof] RESULT outcome=<outcome> ...
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union


def parse_framework_log(log_text: str) -> List[str]:
    """Extracts all [FrameworkProof] lines from editor or game raw logs."""
    extracted = []
    for line in log_text.splitlines():
        if "[FrameworkProof]" in line:
            idx = line.find("[FrameworkProof]")
            extracted.append(line[idx:].strip())
    return extracted


def grade_f8_log_lines(lines: List[str], tolerance: float = 1e-4, expect_no_posture: bool = False) -> Dict[str, Any]:
    """
    Grades extracted [FrameworkProof] lines against F8 Posture and Stance Break requirements.
    """
    report: Dict[str, Any] = {
        "passed": False,
        "summary": "",
        "checks": {},
        "errors": [],
        "parsed_data": {
            "drains": [],
            "stance_breaks": [],
            "stagger_recoveries": [],
            "walk_resumes": [],
            "walk_starts": [],
            "posture_held": [],
            "regens": [],
            "cleanups": [],
            "transitions": [],
            "decisions": [],
            "playbacks": [],
            "deaths": [],
            "resets": [],
            "results": [],
            "error_tokens": []
        }
    }

    # Tracking state
    current_generation = 1
    boss_max_health: Optional[float] = None
    boss_current_health: Optional[float] = None
    phase_two_fraction: Optional[float] = None

    posture_max: Optional[float] = None
    current_posture: Optional[float] = None
    cycle_drains_sum: float = 0.0
    last_drain_after: Optional[float] = None

    is_staggered = False
    stagger_started_at_idx: Optional[int] = None
    stagger_phase_transition_due = False
    is_boss_dead = False
    last_cleanup: Optional[Dict[str, Any]] = None

    has_walk_started = False
    pending_neutral_break_walk_resume = False

    # Line regex matchers
    re_boss_health = re.compile(r"boss_health\s+max=([\d.]+)")
    re_boss_hit = re.compile(r"boss_hit\s+damage=([\d.]+)\s+healthBefore=([\d.]+)\s+healthAfter=([\d.]+)")
    re_drain = re.compile(r"posture_drain\s+amount=([\d.]+)\s+postureBefore=([\d.]+)\s+postureAfter=([\d.]+)\s+max=([\d.]+)")
    re_held = re.compile(r"posture_held\s+reason=(\w+)\s+posture=([\d.]+)")
    re_regen = re.compile(r"posture_regen_full\s+posture=([\d.]+)\s+max=([\d.]+)")
    re_cleanup = re.compile(r"cleanup\s+reason=(\w+)(?:\s+modelIdle=(\d+))?(?:\s+ownedMontageStopped=(\d+))?")
    re_break = re.compile(r"stance_break\s+state=(\w+)\s+duration=([\d.]+)\s+generation=(\d+)\s+phase=(\w+)")
    re_recovery = re.compile(r"stagger_recovery\s+postureRefilled=([\d.]+)\s+generation=(\d+)")
    re_walk_resumed = re.compile(r"walk_resumed\s+generation=(\d+)")
    re_walk_start = re.compile(r"walk\s+start=")
    re_transition = re.compile(r"phase_transition.*?(?:health=([\d.]+)\s+max=([\d.]+)\s+fraction=([\d.]+)|from=(\w+)\s+to=(\w+))")
    re_decision = re.compile(r"decision\s+attack=(\d+)")
    re_playback = re.compile(r"playback_start\s+encounter=(\d+)\s+generation=(\d+)\s+instance=(\d+)")
    re_dead = re.compile(r"boss_dead\s+generation=(\d+)")
    re_reset = re.compile(r"encounter_reset\s+generation=(\d+)")
    re_result = re.compile(r"RESULT\s+outcome=(\w+)")

    for idx, l in enumerate(lines):
        # 1. Error detection
        if "ERROR" in l or "Fail(" in l or "Assertion failed" in l or "[BAKE_FATAL]" in l:
            report["parsed_data"]["error_tokens"].append({"idx": idx, "raw": l, "gen": current_generation})

        # 2. boss_health
        m = re_boss_health.search(l)
        if m:
            boss_max_health = float(m.group(1))
            boss_current_health = boss_max_health

        # 3. boss_hit
        m = re_boss_hit.search(l)
        if m:
            dmg = float(m.group(1))
            h_before = float(m.group(2))
            h_after = float(m.group(3))
            boss_current_health = h_after

            # Check if phase transition became due
            if boss_max_health and phase_two_fraction is not None:
                if boss_current_health <= phase_two_fraction * boss_max_health:
                    if is_staggered:
                        stagger_phase_transition_due = True

        # 4. posture_drain
        m = re_drain.search(l)
        if m:
            amount = float(m.group(1))
            before = float(m.group(2))
            after = float(m.group(3))
            p_max = float(m.group(4))
            report["parsed_data"]["drains"].append({
                "idx": idx, "amount": amount, "before": before, "after": after, "max": p_max, "gen": current_generation
            })
            posture_max = p_max
            current_posture = after
            last_drain_after = after
            cycle_drains_sum += amount

            # Invariant: before - amount == after
            if abs((before - amount) - after) > tolerance:
                report["errors"].append(
                    f"Line {idx}: posture_drain math mismatch: before({before}) - amount({amount}) != after({after})"
                )
            if after < -tolerance:
                report["errors"].append(f"Line {idx}: posture_drain resulted in negative posture ({after})")
            if before > p_max + tolerance:
                report["errors"].append(f"Line {idx}: posture_drain before({before}) exceeds max({p_max})")

        # 5. posture_held
        m = re_held.search(l)
        if m:
            reason = m.group(1)
            p = float(m.group(2))
            report["parsed_data"]["posture_held"].append({
                "idx": idx, "reason": reason, "posture": p, "gen": current_generation
            })
            if not is_staggered:
                report["errors"].append(f"Line {idx}: posture_held emitted while boss is not staggered")

        # 6. posture_regen_full
        m = re_regen.search(l)
        if m:
            p = float(m.group(1))
            p_max = float(m.group(2))
            report["parsed_data"]["regens"].append({
                "idx": idx, "posture": p, "max": p_max, "gen": current_generation
            })
            current_posture = p
            cycle_drains_sum = 0.0

        # 7. cleanup
        m = re_cleanup.search(l)
        if m:
            reason = m.group(1)
            c_data = {"idx": idx, "reason": reason, "gen": current_generation, "raw": l}
            report["parsed_data"]["cleanups"].append(c_data)
            last_cleanup = c_data

        # 8. stance_break
        m = re_break.search(l)
        if m:
            state = m.group(1)
            duration = float(m.group(2))
            gen = int(m.group(3))
            phase = m.group(4)
            b_data = {
                "idx": idx, "state": state, "duration": duration, "gen": gen, "phase": phase, "raw": l
            }
            report["parsed_data"]["stance_breaks"].append(b_data)

            # Rule: never after boss_dead
            if is_boss_dead:
                report["errors"].append(f"Line {idx}: stance_break emitted while boss is dead (gen={gen})")

            # Rule: must follow a drain that reached 0
            if last_drain_after is None or abs(last_drain_after) > tolerance:
                report["errors"].append(
                    f"Line {idx}: stance_break emitted without prior posture drain reaching 0 (last after={last_drain_after})"
                )

            # Rule: drain amounts must sum to max
            if posture_max is not None and abs(cycle_drains_sum - posture_max) > tolerance:
                report["errors"].append(
                    f"Line {idx}: posture drains sum ({cycle_drains_sum}) does not equal max posture ({posture_max})"
                )

            # Rule: cleanup reason=StanceBreak precedes stance_break state=MidAttack
            if state == "MidAttack":
                if not last_cleanup or last_cleanup["reason"] != "StanceBreak":
                    report["errors"].append(
                        f"Line {idx}: stance_break state=MidAttack was not preceded by cleanup reason=StanceBreak"
                    )
                elif idx - last_cleanup["idx"] > 2:
                    report["errors"].append(
                        f"Line {idx}: cleanup reason=StanceBreak too distant from stance_break (gap {idx - last_cleanup['idx']})"
                    )

            # Rule: Neutral break before walk arrival requires walk_resumed before walk start
            if state == "Neutral" and not has_walk_started:
                pending_neutral_break_walk_resume = True

            is_staggered = True
            stagger_started_at_idx = idx

        # 9. stagger_recovery
        m = re_recovery.search(l)
        if m:
            refilled = float(m.group(1))
            gen = int(m.group(2))
            report["parsed_data"]["stagger_recoveries"].append({
                "idx": idx, "refilled": refilled, "gen": gen, "raw": l
            })

            # Rule: must have been staggered
            if not is_staggered:
                report["errors"].append(f"Line {idx}: stagger_recovery emitted while not staggered (gen={gen})")

            # Rule: refills to max
            if posture_max is not None and abs(refilled - posture_max) > tolerance:
                report["errors"].append(
                    f"Line {idx}: stagger_recovery refilled ({refilled}) does not match max posture ({posture_max})"
                )

            is_staggered = False
            cycle_drains_sum = 0.0
            last_drain_after = None
            stagger_phase_transition_due = False

        # 10. walk_resumed (C-449, C-450)
        m = re_walk_resumed.search(l)
        if m:
            gen = int(m.group(1))
            report["parsed_data"]["walk_resumes"].append({"idx": idx, "gen": gen, "raw": l})
            if is_staggered:
                report["errors"].append(f"Line {idx}: walk_resumed emitted while boss is still staggered (gen={gen})")
            pending_neutral_break_walk_resume = False

        # 11. walk start
        m = re_walk_start.search(l)
        if m:
            has_walk_started = True
            report["parsed_data"]["walk_starts"].append({"idx": idx, "raw": l})
            if pending_neutral_break_walk_resume:
                report["errors"].append(
                    f"Line {idx}: walk start= occurred after Neutral stance_break without preceding walk_resumed"
                )

        # 12. phase_transition
        if "phase_transition" in l:
            report["parsed_data"]["transitions"].append({"idx": idx, "gen": current_generation, "raw": l})
            m_frac = re.search(r"fraction=([\d.]+)|threshold=([\d.]+)", l)
            if m_frac:
                phase_two_fraction = float(m_frac.group(1) or m_frac.group(2))

            # Rule: A phase_transition that is due while staggered appears only AFTER stagger_recovery
            if is_staggered:
                report["errors"].append(
                    f"Line {idx}: phase_transition fired while boss was staggered (stagger started at line {stagger_started_at_idx})"
                )

        # 13. decision
        m = re_decision.search(l)
        if m:
            att = int(m.group(1))
            report["parsed_data"]["decisions"].append({"idx": idx, "attack": att, "gen": current_generation, "raw": l})
            # Rule: no decision line between stance_break and stagger_recovery
            if is_staggered:
                report["errors"].append(
                    f"Line {idx}: decision (attack={att}) emitted while boss is staggered (stagger started at line {stagger_started_at_idx})"
                )

        # 14. playback_start
        m = re_playback.search(l)
        if m:
            report["parsed_data"]["playbacks"].append({"idx": idx, "gen": current_generation, "raw": l})
            if is_staggered:
                report["errors"].append(f"Line {idx}: playback_start emitted while boss is staggered")

        # 15. boss_dead
        m = re_dead.search(l)
        if m:
            gen = int(m.group(1))
            report["parsed_data"]["deaths"].append({"idx": idx, "gen": gen, "raw": l})
            is_boss_dead = True
            is_staggered = False

        # 16. encounter_reset
        m = re_reset.search(l)
        if m:
            new_gen = int(m.group(1))
            report["parsed_data"]["resets"].append({"idx": idx, "gen": new_gen, "raw": l})
            current_generation = new_gen

            # Rule: generation reset: no stance_break state leaks across encounter_reset
            if is_staggered and not is_boss_dead:
                report["errors"].append(
                    f"Line {idx}: encounter_reset called while boss is actively staggered without prior death"
                )

            # Reset life state
            is_staggered = False
            is_boss_dead = False
            cycle_drains_sum = 0.0
            last_drain_after = None
            stagger_phase_transition_due = False
            has_walk_started = False
            pending_neutral_break_walk_resume = False

        # 17. RESULT
        m = re_result.search(l)
        if m:
            outcome = m.group(1)
            report["parsed_data"]["results"].append({"idx": idx, "outcome": outcome, "gen": current_generation, "raw": l})

    if pending_neutral_break_walk_resume:
        report["errors"].append(
            "Neutral stance_break was not followed by walk_resumed before encounter end"
        )

    # Summary evaluation and check predicates
    report["checks"]["no_error_tokens"] = (len(report["parsed_data"]["error_tokens"]) == 0)
    report["checks"]["has_terminal_result"] = (len(report["parsed_data"]["results"]) > 0)

    if expect_no_posture:
        total_posture_lines = (
            len(report["parsed_data"]["drains"]) +
            len(report["parsed_data"]["stance_breaks"]) +
            len(report["parsed_data"]["stagger_recoveries"]) +
            len(report["parsed_data"]["posture_held"]) +
            len(report["parsed_data"]["regens"])
        )
        report["checks"]["no_posture_lines_emitted"] = (total_posture_lines == 0)
        if total_posture_lines > 0:
            report["errors"].append(f"Expected no posture lines (--expect-no-posture), but found {total_posture_lines}")
    else:
        has_breaks = len(report["parsed_data"]["stance_breaks"]) > 0
        has_recoveries = len(report["parsed_data"]["stagger_recoveries"]) > 0
        has_deaths = len(report["parsed_data"]["deaths"]) > 0

        report["checks"]["has_stance_break"] = has_breaks
        report["checks"]["stagger_closed_or_dead"] = (has_recoveries or has_deaths)

        if not has_breaks:
            report["errors"].append("No stance_break events found in log")
        if not (has_recoveries or has_deaths):
            report["errors"].append("Stance break occurred but neither stagger_recovery nor boss_dead occurred")

    # Final overall pass determination
    all_checks_passed = all(report["checks"].values())
    no_errors = (len(report["errors"]) == 0)
    report["passed"] = all_checks_passed and no_errors

    if report["passed"]:
        if expect_no_posture:
            report["summary"] = "PASS: Non-posture regression run verified clean (0 posture lines, 0 errors, valid RESULT)."
        else:
            breaks_cnt = len(report["parsed_data"]["stance_breaks"])
            recoveries_cnt = len(report["parsed_data"]["stagger_recoveries"])
            drains_cnt = len(report["parsed_data"]["drains"])
            report["summary"] = (
                f"PASS: F8 posture authority verified ({breaks_cnt} breaks, {recoveries_cnt} recoveries, "
                f"{drains_cnt} drains, 0 decisions during stagger, clean lifecycle)."
            )
    else:
        err_msg = "; ".join(report["errors"][:3])
        if len(report["errors"]) > 3:
            err_msg += f" (+{len(report['errors']) - 3} more)"
        report["summary"] = f"FAIL: {err_msg}"

    return report


def grade_f8_file(file_path: Union[str, Path], tolerance: float = 1e-4, expect_no_posture: bool = False) -> Dict[str, Any]:
    """Reads a file, parses FrameworkProof lines, and runs F8 grading."""
    p = Path(file_path)
    if not p.is_file():
        return {
            "passed": False,
            "summary": f"FAIL: File not found '{file_path}'",
            "checks": {"file_exists": False},
            "errors": [f"File not found: {file_path}"]
        }
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return {
            "passed": False,
            "summary": f"FAIL: Could not read file '{file_path}': {e}",
            "checks": {"file_readable": False},
            "errors": [str(e)]
        }
    lines = parse_framework_log(text)
    return grade_f8_log_lines(lines, tolerance=tolerance, expect_no_posture=expect_no_posture)


def main():
    parser = argparse.ArgumentParser(description="Antigravity F8 Posture and Stance Break Grader")
    parser.add_argument("log_file", nargs="?", help="Path to editor_raw.log")
    parser.add_argument("--log", dest="log_opt", help="Path to editor_raw.log (named option)")
    parser.add_argument("--expect-no-posture", action="store_true", help="Assert that posture is disabled (zero posture lines)")
    parser.add_argument("--tolerance", type=float, default=1e-4, help="Float comparison tolerance (default: 1e-4)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON report")

    args = parser.parse_args()
    target_path = args.log_opt or args.log_file

    if not target_path:
        parser.print_help()
        sys.exit(2)

    report = grade_f8_file(target_path, tolerance=args.tolerance, expect_no_posture=args.expect_no_posture)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(report["summary"])
        if not report["passed"]:
            for err in report["errors"]:
                print(f"  - ERROR: {err}")

    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
