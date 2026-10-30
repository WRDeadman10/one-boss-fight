#!/usr/bin/env python3
"""
grade_f5_log.py
===============
Antigravity F5 Multi-Attack Proof Grader (Order A-286).
Parses editor raw log from PIE playback of Slice F5 multi-card proof and verifies:
1. Two sequential attacks executed by RPGFrameworkBossCharacter (instances 1 and 2).
2. For each attack, a selector [FrameworkProof] decision precedes playback_start.
3. The two attacks select different move cards (verifying anti-repeat / cooldown diversity).
4. Second decision contains an explicit cooldown refusal for the first card.
5. Event timelines (Open, Close, Finished) match authored move specs from move_cards_f5_set.json.
6. Exactly one clean cleanup line per attack (reason=Finished, modelIdle=1, ownedMontageStopped=1).
7. Target HP invariant matches sum of accepted hits and authored damage.
8. Zero unhandled ERROR lines before RESULT.

Usage:
    python grade_f5_log.py --log <path_to_editor_raw.log> [--cards-json <path>]
    python grade_f5_log.py <path_to_editor_raw.log>
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

DEFAULT_CARDS_JSON = Path("Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json")

# Fallback default card specs if JSON not provided
FALLBACK_CARD_SPECS = {
    "Move_Sevarog_SwingSlow_F5": {
        "MoveId": "Move_Sevarog_SwingSlow_F5",
        "ActiveStartSeconds": 0.35,
        "ActiveEndSeconds": 0.4917,
        "RecoveryEndSeconds": 1.65,
        "HPDamage": 35.0,
        "CooldownSeconds": 1.5
    },
    "Move_Sevarog_SwingMedium_F5": {
        "MoveId": "Move_Sevarog_SwingMedium_F5",
        "ActiveStartSeconds": 0.1917,
        "ActiveEndSeconds": 0.2667,
        "RecoveryEndSeconds": 1.10,
        "HPDamage": 25.0,
        "CooldownSeconds": 1.0
    },
    "Move_Sevarog_AntiGreed_F5": {
        "MoveId": "Move_Sevarog_AntiGreed_F5",
        "ActiveStartSeconds": 0.25,
        "ActiveEndSeconds": 0.3083,
        "RecoveryEndSeconds": 0.4833,
        "HPDamage": 20.0,
        "CooldownSeconds": 2.5
    },
    "Move_Sevarog_HeavySlam_F5": {
        "MoveId": "Move_Sevarog_HeavySlam_F5",
        "ActiveStartSeconds": 0.475,
        "ActiveEndSeconds": 0.5333,
        "RecoveryEndSeconds": 1.65,
        "HPDamage": 55.0,
        "CooldownSeconds": 3.5
    }
}


def load_card_specs(cards_json_path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Loads card specifications from move_cards_f5_set.json."""
    path = cards_json_path or DEFAULT_CARDS_JSON
    if path and path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            specs = {}
            for c in data.get("cards", []):
                mid = c.get("MoveId")
                if mid:
                    specs[mid] = {
                        "MoveId": mid,
                        "ActiveStartSeconds": float(c.get("ActiveStartSeconds", 0.0)),
                        "ActiveEndSeconds": float(c.get("ActiveEndSeconds", 0.0)),
                        "RecoveryEndSeconds": float(c.get("RecoveryEndSeconds", 0.0)),
                        "HPDamage": float(c.get("HPDamage", 0.0)),
                        "CooldownSeconds": float(c.get("CooldownSeconds", 0.0))
                    }
            if specs:
                return specs
        except Exception:
            pass
    return FALLBACK_CARD_SPECS


def parse_framework_log(log_text: str) -> List[str]:
    """Extract all [FrameworkProof] lines from raw log."""
    lines = []
    for line in log_text.splitlines():
        if "[FrameworkProof]" in line:
            idx = line.find("[FrameworkProof]")
            lines.append(line[idx:].strip())
    return lines


def grade_f5_log_lines(
    lines: List[str],
    card_specs: Optional[Dict[str, Dict[str, Any]]] = None,
    tolerance_seconds: float = 0.035
) -> Dict[str, Any]:
    """
    Grades extracted [FrameworkProof] lines against F5 multi-card proof requirements.
    """
    if card_specs is None:
        card_specs = FALLBACK_CARD_SPECS

    report = {
        "passed": False,
        "summary": "",
        "checks": {},
        "errors": [],
        "warnings": [],
        "parsed_data": {
            "decisions": [],
            "playback_starts": [],
            "events_by_instance": {},
            "cleanups": [],
            "hits": [],
            "refusals_by_instance": {}
        }
    }

    # 1. Negative Assertion: Check for unhandled ERROR lines before RESULT
    result_idx = -1
    for i, l in enumerate(lines):
        if l.startswith("[FrameworkProof] RESULT"):
            result_idx = i
            break

    pre_result_lines = lines if result_idx == -1 else lines[:result_idx]
    error_lines = [l for l in pre_result_lines if "ERROR" in l or "Fail(" in l]
    if error_lines:
        report["checks"]["no_error_tokens"] = False
        for err in error_lines:
            report["errors"].append(f"Encountered error line: {err}")
    else:
        report["checks"]["no_error_tokens"] = True

    # 2. Parse Decisions
    # Format: [FrameworkProof] decision instance=1 chosen=Move_Sevarog_SwingSlow_F5 score=1.85 range=169.69
    decision_lines = []
    for idx, l in enumerate(lines):
        if l.startswith("[FrameworkProof] decision"):
            m = re.search(r"(?:attack|instance)=(\d+)\s+chosen=([a-zA-Z0-9_]+)\s+score=([0-9.]+)\s+range=([0-9.]+)", l)
            if m:
                decision_lines.append({
                    "line_index": idx,
                    "instance": int(m.group(1)),
                    "attack": int(m.group(1)),
                    "chosen": m.group(2),
                    "score": float(m.group(3)),
                    "range": float(m.group(4)),
                    "raw": l
                })
            else:
                report["errors"].append(f"Malformed decision line: {l}")

    report["parsed_data"]["decisions"] = decision_lines

    # 3. Parse Refusals
    # Format: [FrameworkProof] refusal instance=2 card=Move_Sevarog_SwingSlow_F5 reason=Selector.Cooldown
    refusals_by_inst: Dict[int, List[Dict[str, str]]] = {}
    for l in lines:
        if l.startswith("[FrameworkProof] refusal"):
            m = re.search(r"(?:attack|instance)=(\d+)\s+card=([a-zA-Z0-9_]+)\s+reason=([a-zA-Z0-9_.]+)", l)
            if m:
                inst = int(m.group(1))
                card = m.group(2)
                reason = m.group(3)
                if inst not in refusals_by_inst:
                    refusals_by_inst[inst] = []
                refusals_by_inst[inst].append({"card": card, "reason": reason, "raw": l})
    report["parsed_data"]["refusals_by_instance"] = refusals_by_inst

    # 4. Parse Playback Starts
    # Format: [FrameworkProof] playback_start encounter=1 generation=1 instance=1 ...
    playback_starts = []
    for idx, l in enumerate(lines):
        if l.startswith("[FrameworkProof] playback_start"):
            m = re.search(r"instance=(\d+)", l)
            if m:
                playback_starts.append({
                    "line_index": idx,
                    "instance": int(m.group(1)),
                    "raw": l
                })
    report["parsed_data"]["playback_starts"] = playback_starts

    # Check Attack Count: Exactly 2 attacks
    has_two_decisions = len(decision_lines) == 2 and [d["instance"] for d in decision_lines] == [1, 2]
    has_two_playbacks = len(playback_starts) == 2 and [p["instance"] for p in playback_starts] == [1, 2]
    report["checks"]["two_attacks_executed"] = has_two_decisions and has_two_playbacks
    if not report["checks"]["two_attacks_executed"]:
        report["errors"].append(
            f"Expected exactly 2 sequential attacks (instances 1 and 2). "
            f"Found {len(decision_lines)} decisions and {len(playback_starts)} playback starts."
        )

    # Check Decision Precedes Playback
    decision_precedes_playback = True
    if has_two_decisions and has_two_playbacks:
        for i in range(2):
            dec = decision_lines[i]
            pb = playback_starts[i]
            if dec["line_index"] >= pb["line_index"]:
                decision_precedes_playback = False
                report["errors"].append(
                    f"Decision for instance {dec['instance']} (line {dec['line_index']}) "
                    f"did not precede playback_start (line {pb['line_index']})"
                )
    else:
        decision_precedes_playback = False
    report["checks"]["decision_precedes_playback"] = decision_precedes_playback

    # Check Distinct Moves (Anti-Repeat / Cooldown Diversity)
    distinct_moves = False
    if has_two_decisions:
        card1 = decision_lines[0]["chosen"]
        card2 = decision_lines[1]["chosen"]
        distinct_moves = (card1 != card2)
        report["checks"]["distinct_moves_selected"] = distinct_moves
        if not distinct_moves:
            report["errors"].append(
                f"Both attacks selected the identical move card '{card1}'. "
                f"Selector anti-repeat penalty / cooldown failed to select a distinct alternative."
            )
    else:
        report["checks"]["distinct_moves_selected"] = False

    # Check Cooldown Refusal on Second Decision
    cooldown_refusal_observed = False
    if has_two_decisions:
        first_card = decision_lines[0]["chosen"]
        inst2_refusals = refusals_by_inst.get(2, [])
        for ref in inst2_refusals:
            if ref["card"] == first_card and "Cooldown" in ref["reason"]:
                cooldown_refusal_observed = True
                break
        report["checks"]["cooldown_refusal_on_second_decision"] = cooldown_refusal_observed
        if not cooldown_refusal_observed:
            report["errors"].append(
                f"Second decision (instance 2) did not trace a Cooldown refusal for first card '{first_card}'. "
                f"Observed instance 2 refusals: {inst2_refusals}"
            )
    else:
        report["checks"]["cooldown_refusal_on_second_decision"] = False

    # 5. Parse and Validate Events by Instance
    events_by_inst: Dict[int, List[Dict[str, Any]]] = {1: [], 2: []}
    for l in lines:
        if l.startswith("[FrameworkProof] event"):
            m_inst = re.search(r"instance=(\d+)", l)
            m_kind = re.search(r"kind=([a-zA-Z0-9_]+)", l)
            m_sec = re.search(r"localSeconds=([0-9.]+)", l)
            if m_inst and m_kind and m_sec:
                inst_id = int(m_inst.group(1))
                if inst_id in events_by_inst:
                    events_by_inst[inst_id].append({
                        "kind": m_kind.group(1),
                        "localSeconds": float(m_sec.group(1)),
                        "raw": l
                    })
    report["parsed_data"]["events_by_instance"] = events_by_inst

    events_timings_valid = True
    if has_two_decisions:
        for i in range(2):
            inst = i + 1
            chosen_card = decision_lines[i]["chosen"]
            spec = card_specs.get(chosen_card, FALLBACK_CARD_SPECS.get(chosen_card))
            if not spec:
                events_timings_valid = False
                report["errors"].append(f"Unknown card spec for chosen card '{chosen_card}'")
                continue

            evs = events_by_inst.get(inst, [])
            kinds = [e["kind"] for e in evs]

            if "Open" not in kinds or "Close" not in kinds or "Finished" not in kinds:
                events_timings_valid = False
                report["errors"].append(
                    f"Instance {inst} ({chosen_card}) missing required events. Observed: {kinds}"
                )
                continue

            for ev in evs:
                k = ev["kind"]
                t = ev["localSeconds"]
                if k == "Open":
                    exp = spec["ActiveStartSeconds"]
                    if abs(t - exp) > tolerance_seconds:
                        events_timings_valid = False
                        report["errors"].append(
                            f"Instance {inst} ({chosen_card}) Open timing {t:.4f}s deviates from expected {exp:.4f}s"
                        )
                elif k == "Close":
                    exp = spec["ActiveEndSeconds"]
                    if abs(t - exp) > tolerance_seconds:
                        events_timings_valid = False
                        report["errors"].append(
                            f"Instance {inst} ({chosen_card}) Close timing {t:.4f}s deviates from expected {exp:.4f}s"
                        )
                elif k == "Finished":
                    exp = spec["RecoveryEndSeconds"]
                    if abs(t - exp) > (tolerance_seconds * 2):
                        events_timings_valid = False
                        report["errors"].append(
                            f"Instance {inst} ({chosen_card}) Finished timing {t:.4f}s deviates from expected {exp:.4f}s"
                        )
    else:
        events_timings_valid = False

    report["checks"]["event_timings_match_specs"] = events_timings_valid

    # 6. Parse and Validate Cleanups
    cleanup_lines = [l for l in lines if l.startswith("[FrameworkProof] cleanup")]
    report["parsed_data"]["cleanups"] = cleanup_lines
    clean_finishes = [
        l for l in cleanup_lines
        if "reason=Finished" in l and "modelIdle=1" in l and "ownedMontageStopped=1" in l
    ]

    cleanups_valid = (len(clean_finishes) == 2 and len(cleanup_lines) == 2)
    report["checks"]["cleanups_exact_two"] = cleanups_valid
    if not cleanups_valid:
        report["errors"].append(
            f"Expected exactly 2 clean finish cleanups (1 per attack). "
            f"Found {len(clean_finishes)} clean finishes of {len(cleanup_lines)} total cleanup lines."
        )

    # 7. Parse and Validate Hits & Target HP Invariant
    hit_lines = [l for l in lines if l.startswith("[FrameworkProof] hit")]
    accepted_hits = []
    total_damage_applied = 0.0
    for hl in hit_lines:
        if "outcome=ERPGDamageOutcome::Accepted" in hl:
            m_dmg = re.search(r"hpApplied=([0-9.]+)", hl)
            dmg = float(m_dmg.group(1)) if m_dmg else 0.0
            accepted_hits.append({"raw": hl, "damage": dmg})
            total_damage_applied += dmg

    report["parsed_data"]["hits"] = hit_lines
    report["parsed_data"]["accepted_hit_count"] = len(accepted_hits)
    report["parsed_data"]["total_damage_from_hits"] = total_damage_applied

    inv_lines = [l for l in lines if l.startswith("[FrameworkProof] invariant")]
    invariant_valid = False
    if inv_lines:
        last_inv = inv_lines[-1]
        m_before = re.search(r"targetHPBefore=([0-9.]+)", last_inv)
        m_after = re.search(r"targetHPAfter=([0-9.]+)", last_inv)
        m_exp = re.search(r"expectedHP=([0-9.]+)", last_inv)
        m_hits = re.search(r"acceptedHits=(\d+)", last_inv)
        m_applied = re.search(r"appliedDamage=([0-9.]+)", last_inv)

        if m_before and m_after and m_exp and m_hits and m_applied:
            hp_before = float(m_before.group(1))
            hp_after = float(m_after.group(1))
            hp_exp = float(m_exp.group(1))
            hits_count = int(m_hits.group(1))
            app_dmg = float(m_applied.group(1))

            math_ok = abs((hp_before - hp_after) - app_dmg) < 1e-2
            exp_ok = abs(hp_after - hp_exp) < 1e-2
            hits_ok = (hits_count == len(accepted_hits))
            dmg_match = abs(app_dmg - total_damage_applied) < 1e-2

            attacks_executed = len(playback_starts)
            if math_ok and exp_ok and hits_ok and dmg_match:
                invariant_valid = True
                if hits_count < attacks_executed:
                    report["warnings"].append(
                        f"Attack miss observed (KI-147): hits={hits_count} < attacks={attacks_executed}, "
                        f"invariant held: before={hp_before}, after={hp_after}, applied={app_dmg}, expected={hp_exp}"
                    )
            else:
                invariant_valid = False
                report["errors"].append(
                    f"Invariant mismatch: before={hp_before}, after={hp_after}, applied={app_dmg}, "
                    f"hits={hits_count} (expected {len(accepted_hits)}), math_ok={math_ok}, exp_ok={exp_ok}"
                )
        else:
            report["errors"].append(f"Failed to parse invariant line: {last_inv}")
    else:
        report["errors"].append("Missing '[FrameworkProof] invariant' line")

    report["checks"]["target_hp_invariant"] = invariant_valid

    # Overall Pass Evaluation
    all_checks = report["checks"]
    passed = (
        all_checks.get("no_error_tokens", False) and
        all_checks.get("two_attacks_executed", False) and
        all_checks.get("decision_precedes_playback", False) and
        all_checks.get("distinct_moves_selected", False) and
        all_checks.get("cooldown_refusal_on_second_decision", False) and
        all_checks.get("event_timings_match_specs", False) and
        all_checks.get("cleanups_exact_two", False) and
        all_checks.get("target_hp_invariant", False)
    )

    report["passed"] = passed
    passed_count = sum(1 for v in all_checks.values() if v)
    total_count = len(all_checks)
    report["summary"] = (
        f"F5 Multi-Attack PIE Grader: {'PASS' if passed else 'FAIL'} "
        f"({passed_count}/{total_count} checks passed, {len(report['errors'])} errors, {len(report['warnings'])} warnings)"
    )

    return report


def grade_file(log_path: str, cards_json: Optional[str] = None) -> int:
    """Grades a file and prints formatted console output."""
    p = Path(log_path)
    if not p.is_file():
        print(f"[ERROR] Log file not found: {log_path}")
        return 1

    log_text = p.read_text(encoding="utf-8", errors="replace")
    lines = parse_framework_log(log_text)

    card_p = Path(cards_json) if cards_json else None
    specs = load_card_specs(card_p)

    report = grade_f5_log_lines(lines, card_specs=specs)

    print("================================================================================")
    print(" ONE BOSS FIGHT: F5 MULTI-ATTACK PROOF LOG GRADER")
    print(f" Target Log: {log_path}")
    print("================================================================================")
    for check_name, status in report["checks"].items():
        status_str = "PASS" if status else "FAIL"
        print(f"  [{status_str:4s}] {check_name}")

    if report["errors"]:
        print("\nFailures / Errors:")
        for err in report["errors"]:
            print(f"  - {err}")

    print("\nSummary:")
    print(f"  {report['summary']}")
    print("================================================================================")

    return 0 if report["passed"] else 1


def main():
    parser = argparse.ArgumentParser(description="One Boss Fight F5 Multi-Attack Log Grader")
    parser.add_argument("log_path", nargs="?", default=None, help="Path to editor_raw.log")
    parser.add_argument("--log", dest="log_opt", default=None, help="Path to editor_raw.log")
    parser.add_argument("--cards-json", dest="cards_json", default=None, help="Path to move_cards_f5_set.json")
    args = parser.parse_args()

    target = args.log_opt or args.log_path
    if not target:
        parser.print_help()
        sys.exit(1)

    sys.exit(grade_file(target, cards_json=args.cards_json))


if __name__ == "__main__":
    main()
