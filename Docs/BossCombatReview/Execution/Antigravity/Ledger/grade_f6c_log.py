#!/usr/bin/env python3
"""
grade_f6c_log.py
================
Antigravity F6c Phase Authority and Transition Grader (Lead Orders C-429, C-430, C-431, C-432).

Parses editor raw log from PIE playback of Slice F6c (Phase Authority and MoveCard Partitioning)
and verifies the following requirements:
1. No unhandled ERROR, FATAL, or assertion failures (with targeted --expect-ki149 filter).
2. Clean Phase Transition Event:
   - At least one valid [FrameworkProof] phase_transition line is emitted.
   - Health at transition respects the threshold fraction: Health / MaxHealth <= ThresholdFraction (tolerance 0.01).
3. Neutral Gate Adherence:
   - Phase transition occurs in neutral state (not during active attack playback between playback_start and cleanup).
4. Phase Partitioning of Decisions:
   - In Phase 1 (before phase_transition), all decisions select Phase 1 cards. Any Phase 2 candidates are refused with MoveModel.Phase.
   - In Phase 2 (after phase_transition), all decisions select Phase 2 cards. Any Phase 1 candidates are refused with MoveModel.Phase (or Selector.Cooldown).
   - If 'phase=Phase_X' is logged on the decision line, it must match the expected authoritative phase.
5. Monotonic and Idempotent Latching:
   - Within the same generation, phase authority cannot transition back to Phase 1.
   - Duplicate or redundant transitions to Phase 2 are not re-triggered within the same generation.
6. Generation Reset Semantics (if encounter_reset is present):
   - On encounter_reset, phase state resets to Phase 1 and generation increments.
   - Initial decisions in the new generation select Phase 1 cards.
7. Valid RESULT token terminating the encounter (or documented KI-149 failure termination).

Log Token Specifications (per Lead Orders C-429, C-430, C-431, C-432 and F6c Implementation Plan):
- [FrameworkProof] phase_transition [attack=<n>] [from=<p1>] to=<p2> [health=<h>] [maxHealth=<m>] [fraction=<t>] [threshold=<t>] [generation=<g>]
- [FrameworkProof] decision attack=<n> [generation=<g>] chosen=<card> [phase=<p>] score=<s> range=<r>
- [FrameworkProof] candidate attack=<n> card=<card> [score=<s>]
- [FrameworkProof] refusal attack=<n> card=<card> reason=<reason>
- [FrameworkProof] playback_start encounter=<e> generation=<g> instance=<i> montage=<m> slot=<s> rate=<r>
- [FrameworkProof] cleanup / move_cleanup reason=<r> ...
- [FrameworkProof] encounter_reset generation=<g> ...
- [FrameworkProof] RESULT outcome=<outcome> ...
- [FrameworkProof] ERROR token=<token> ...

Usage:
    python grade_f6c_log.py --log <path_to_editor_raw.log>
    python grade_f6c_log.py <path_to_editor_raw.log> [--expect-ki149 "gen=2,attack=3,phase=Phase_1"]
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


def is_phase_2_card(card_name: str) -> bool:
    """Determines whether a MoveCard name/id belongs to Phase 2."""
    c = card_name.upper()
    return "_P2" in c or "PHASE_2" in c or "PHASE2" in c or "P2_" in c


def parse_ki149_spec(spec: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parses a targeted KI-149 expectation spec (Order C-432).
    Format: 'gen=2,attack=3,phase=Phase_1' (gen is optional; attack and phase are required).
    """
    if isinstance(spec, dict):
        d = dict(spec)
    elif isinstance(spec, str):
        if not spec.strip():
            raise ValueError("Empty --expect-ki149 spec. Format must be: gen=<g>,attack=<a>,phase=<p>")
        parts = [p.strip() for p in spec.replace(";", ",").split(",") if p.strip()]
        d = {}
        for p in parts:
            if "=" not in p:
                raise ValueError(f"Malformed token '{p}' in --expect-ki149 spec '{spec}'")
            k, v = p.split("=", 1)
            k = k.strip().lower()
            v = v.strip()
            if k in ("gen", "generation"):
                d["gen"] = int(v)
            elif k in ("attack", "att"):
                d["attack"] = int(v)
            elif k in ("phase", "phaseid"):
                d["phase"] = v
            else:
                raise ValueError(f"Unknown key '{k}' in --expect-ki149 spec. Allowed: gen, attack, phase")
    else:
        raise ValueError(f"Invalid type for expect_ki149 spec: {type(spec)}")

    if "attack" not in d:
        raise ValueError("Missing required 'attack' key in --expect-ki149 spec (e.g. attack=3,phase=Phase_1)")
    if "phase" not in d:
        raise ValueError("Missing required 'phase' key in --expect-ki149 spec (e.g. attack=3,phase=Phase_1)")
    return d


def grade_f6c_log_lines(lines: List[str], tolerance: float = 0.01, expect_ki149: Optional[Union[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Grades extracted [FrameworkProof] lines against F6c Phase Authority requirements.
    """
    report: Dict[str, Any] = {
        "passed": False,
        "summary": "",
        "checks": {},
        "errors": [],
        "parsed_data": {
            "transitions": [],
            "decisions": [],
            "candidates": [],
            "refusals": [],
            "playbacks": [],
            "cleanups": [],
            "resets": [],
            "results": [],
            "error_tokens": [],
            "no_candidate_context": None
        }
    }

    # Validate KI-149 expectation spec upfront if provided
    ki149_target: Optional[Dict[str, Any]] = None
    if expect_ki149:
        try:
            ki149_target = parse_ki149_spec(expect_ki149)
        except Exception as e:
            report["checks"]["no_error_tokens"] = False
            report["errors"].append(f"Invalid --expect-ki149 specification: {e}")
            report["summary"] = f"FAIL: {e}"
            return report

    # 1. Parse all structured lines with line indices and dynamic generation tracking
    current_generation = 1
    last_attack_seen: Optional[int] = None

    for idx, l in enumerate(lines):
        # ERROR lines
        if "ERROR" in l or "Fail(" in l or "Assertion failed" in l or "[BAKE_FATAL]" in l:
            report["parsed_data"]["error_tokens"].append({
                "line_index": idx,
                "generation": current_generation,
                "raw": l
            })

        # RESULT lines
        if l.startswith("[FrameworkProof] RESULT"):
            report["parsed_data"]["results"].append({
                "line_index": idx,
                "generation": current_generation,
                "raw": l
            })

        # encounter_reset: updates generation
        elif l.startswith("[FrameworkProof] encounter_reset"):
            m_gen = re.search(r"\bgeneration=(\d+)", l)
            if m_gen:
                current_generation = int(m_gen.group(1))
            else:
                current_generation += 1
            last_attack_seen = None
            report["parsed_data"]["resets"].append({
                "line_index": idx,
                "generation": current_generation,
                "raw": l
            })

        # playback_start: sync generation if present
        elif l.startswith("[FrameworkProof] playback_start"):
            m_gen = re.search(r"\bgeneration=(\d+)", l)
            if m_gen:
                current_generation = int(m_gen.group(1))
            m_att = re.search(r"\battack=(\d+)", l)
            if m_att:
                last_attack_seen = int(m_att.group(1))
            m_inst = re.search(r"\binstance=(\d+)", l)
            report["parsed_data"]["playbacks"].append({
                "line_index": idx,
                "attack": int(m_att.group(1)) if m_att else None,
                "generation": current_generation,
                "instance": int(m_inst.group(1)) if m_inst else 1,
                "raw": l
            })

        # phase_transition
        elif l.startswith("[FrameworkProof] phase_transition"):
            m_to = re.search(r"\bto=([a-zA-Z0-9_]+)", l) or re.search(r"\bphase=([a-zA-Z0-9_]+)", l)
            m_from = re.search(r"\bfrom=([a-zA-Z0-9_]+)", l)
            m_hp = re.search(r"\b(?:health|hp|value)=(-?[0-9.]+)", l)
            m_max = re.search(r"\b(?:maxHealth|max)=(-?[0-9.]+)", l)
            m_frac = re.search(r"\b(?:threshold|fraction|thresholdFraction)=(-?[0-9.]+)", l)
            m_gen = re.search(r"\bgeneration=(\d+)", l)
            m_att = re.search(r"\battack=(\d+)", l)
            if m_att:
                last_attack_seen = int(m_att.group(1))

            to_phase = m_to.group(1) if m_to else "Phase_2"
            from_phase = m_from.group(1) if m_from else "Phase_1"
            hp = float(m_hp.group(1)) if m_hp else None
            max_hp = float(m_max.group(1)) if m_max else None
            threshold = float(m_frac.group(1)) if m_frac else 0.60
            gen = int(m_gen.group(1)) if m_gen else current_generation

            report["parsed_data"]["transitions"].append({
                "line_index": idx,
                "from": from_phase,
                "to": to_phase,
                "health": hp,
                "maxHealth": max_hp,
                "threshold": threshold,
                "generation": gen,
                "raw": l
            })

        # decision
        elif l.startswith("[FrameworkProof] decision"):
            m_att = re.search(r"\battack=(\d+)", l)
            if m_att:
                last_attack_seen = int(m_att.group(1))
            m_gen = re.search(r"\bgeneration=(\d+)", l)
            m_chosen = re.search(r"\bchosen=([a-zA-Z0-9_]+)", l)
            m_phase = re.search(r"\bphase=([a-zA-Z0-9_]+)", l)

            att = int(m_att.group(1)) if m_att else None
            gen = int(m_gen.group(1)) if m_gen else current_generation
            chosen = m_chosen.group(1) if m_chosen else None
            phase_logged = m_phase.group(1) if m_phase else None

            report["parsed_data"]["decisions"].append({
                "line_index": idx,
                "attack": att,
                "generation": gen,
                "chosen": chosen,
                "phase_logged": phase_logged,
                "raw": l
            })

        # candidate
        elif l.startswith("[FrameworkProof] candidate"):
            m_att = re.search(r"\battack=(\d+)", l)
            if m_att:
                last_attack_seen = int(m_att.group(1))
            m_card = re.search(r"\bcard=([a-zA-Z0-9_]+)", l)
            if m_card:
                report["parsed_data"]["candidates"].append({
                    "line_index": idx,
                    "attack": int(m_att.group(1)) if m_att else None,
                    "generation": current_generation,
                    "card": m_card.group(1),
                    "raw": l
                })

        # refusal
        elif l.startswith("[FrameworkProof] refusal"):
            m_att = re.search(r"\battack=(\d+)", l)
            if m_att:
                last_attack_seen = int(m_att.group(1))
            m_card = re.search(r"\bcard=([a-zA-Z0-9_]+)", l)
            m_reason = re.search(r"\breason=([a-zA-Z0-9_.]+)", l)
            if m_card and m_reason:
                report["parsed_data"]["refusals"].append({
                    "line_index": idx,
                    "attack": int(m_att.group(1)) if m_att else None,
                    "generation": current_generation,
                    "card": m_card.group(1),
                    "reason": m_reason.group(1),
                    "raw": l
                })

        # cleanup
        elif l.startswith("[FrameworkProof] cleanup") or l.startswith("[FrameworkProof] move_cleanup"):
            m_att = re.search(r"\battack=(\d+)", l)
            if m_att:
                last_attack_seen = int(m_att.group(1))
            report["parsed_data"]["cleanups"].append({
                "line_index": idx,
                "attack": int(m_att.group(1)) if m_att else None,
                "raw": l
            })

            # Check for NoCandidate cleanup
            if "reason=Framework.Selector.NoCandidate" in l:
                # Determine authoritative phase at this exact line
                prior_trans = [
                    t for t in report["parsed_data"]["transitions"]
                    if t["generation"] == current_generation and t["line_index"] < idx
                ]
                prior_resets = [r for r in report["parsed_data"]["resets"] if r["line_index"] < idx]
                latest_reset_line = max([r["line_index"] for r in prior_resets], default=-1)
                active_trans = [t for t in prior_trans if t["line_index"] > latest_reset_line]
                active_phase = "Phase_2" if active_trans else "Phase_1"

                report["parsed_data"]["no_candidate_context"] = {
                    "generation": current_generation,
                    "attack": last_attack_seen,
                    "phase": active_phase,
                    "line_index": idx
                }

    # --- CHECK 1: Error Tokens & Documented KI-149 Handling ---
    error_tokens = report["parsed_data"]["error_tokens"]
    no_cand_ctx = report["parsed_data"]["no_candidate_context"]

    # Also detect if ERROR line had NoCandidate without explicit cleanup
    if not no_cand_ctx:
        for err in error_tokens:
            if "Framework.Selector.NoCandidate" in err["raw"]:
                err_line = err["line_index"]
                err_gen = err["generation"]
                prior_trans = [
                    t for t in report["parsed_data"]["transitions"]
                    if t["generation"] == err_gen and t["line_index"] < err_line
                ]
                prior_resets = [r for r in report["parsed_data"]["resets"] if r["line_index"] < err_line]
                latest_reset_line = max([r["line_index"] for r in prior_resets], default=-1)
                active_trans = [t for t in prior_trans if t["line_index"] > latest_reset_line]
                active_phase = "Phase_2" if active_trans else "Phase_1"

                no_cand_ctx = {
                    "generation": err_gen,
                    "attack": last_attack_seen,
                    "phase": active_phase,
                    "line_index": err_line
                }
                report["parsed_data"]["no_candidate_context"] = no_cand_ctx
                break

    if ki149_target is not None:
        if not no_cand_ctx:
            report["checks"]["no_error_tokens"] = False
            report["errors"].append(
                f"Flag --expect-ki149 specified '{expect_ki149}', but Framework.Selector.NoCandidate was not emitted in log."
            )
        else:
            # Check targeted parameters (Order C-432 Limit)
            mismatch = False
            if "gen" in ki149_target and ki149_target["gen"] != no_cand_ctx["generation"]:
                mismatch = True
                report["errors"].append(
                    f"KI-149 generation mismatch: expected gen={ki149_target['gen']}, but NoCandidate occurred at generation {no_cand_ctx['generation']}."
                )
            if ki149_target["attack"] != no_cand_ctx["attack"]:
                mismatch = True
                report["errors"].append(
                    f"KI-149 attack mismatch: expected attack={ki149_target['attack']}, but NoCandidate occurred at attack {no_cand_ctx['attack']}."
                )
            if ki149_target["phase"] != no_cand_ctx["phase"]:
                mismatch = True
                report["errors"].append(
                    f"KI-149 phase mismatch: expected phase='{ki149_target['phase']}', but NoCandidate occurred in phase '{no_cand_ctx['phase']}'."
                )

            # Check for any unexpected non-KI-149 errors
            unexpected_errors = [
                e["raw"] for e in error_tokens
                if "Framework.Selector.NoCandidate" not in e["raw"] and "PossessionChanged" not in e["raw"]
            ]
            if unexpected_errors:
                mismatch = True
                for err in unexpected_errors:
                    report["errors"].append(f"Unexpected error line: {err}")

            if mismatch:
                report["checks"]["no_error_tokens"] = False
            else:
                report["checks"]["no_error_tokens"] = True
    else:
        if error_tokens:
            report["checks"]["no_error_tokens"] = False
            for err in error_tokens:
                note = " (Known Issue KI-149: NoCandidate under 2-card cooldown exhaustion)" if "NoCandidate" in err["raw"] else ""
                report["errors"].append(f"Encountered error line: {err['raw']}{note}")
        else:
            report["checks"]["no_error_tokens"] = True

    # --- CHECK 2: At least one Phase Transition Emitted ---
    transitions = report["parsed_data"]["transitions"]
    if not transitions:
        report["checks"]["phase_transition_emitted"] = False
        report["errors"].append("No [FrameworkProof] phase_transition line found in log.")
    else:
        report["checks"]["phase_transition_emitted"] = True

    # --- CHECK 3: Threshold Respected ---
    threshold_ok = True
    for tr in transitions:
        hp = tr["health"]
        max_hp = tr["maxHealth"]
        thresh = tr["threshold"]
        if hp is not None and max_hp is not None and max_hp > 0.0:
            frac = hp / max_hp
            if frac > thresh + tolerance:
                threshold_ok = False
                report["errors"].append(
                    f"Phase transition triggered at HP fraction {frac:.3f} ({hp}/{max_hp}) > threshold {thresh:.3f} (+ tolerance {tolerance})"
                )
    report["checks"]["threshold_respected"] = threshold_ok if transitions else False

    # --- CHECK 4: Neutral Gate Adherence ---
    neutral_ok = True
    playbacks = report["parsed_data"]["playbacks"]
    cleanups = report["parsed_data"]["cleanups"]

    for tr in transitions:
        tr_line = tr["line_index"]
        for pb in playbacks:
            pb_line = pb["line_index"]
            if pb_line < tr_line:
                matching_cleanup = [c for c in cleanups if pb_line < c["line_index"] < tr_line]
                aborted_event = [
                    i for i, l in enumerate(lines)
                    if pb_line < i < tr_line and ("kind=Aborted" in l or "BossDead" in l or "executorAborted" in l)
                ]
                if not matching_cleanup and not aborted_event:
                    cleanup_after = [c for c in cleanups if c["line_index"] > tr_line]
                    if cleanup_after:
                        neutral_ok = False
                        report["errors"].append(
                            f"Phase transition at line {tr_line} occurred while attack playback (line {pb_line}) was still active (neutral gate violation)."
                        )
    report["checks"]["neutral_gate_adherence"] = neutral_ok

    # --- CHECK 5: Phase Partitioning of Decisions ---
    partition_ok = True
    decisions = report["parsed_data"]["decisions"]
    resets = report["parsed_data"]["resets"]
    refusals = report["parsed_data"]["refusals"]

    last_decision_line = -1
    for dec in decisions:
        dec_line = dec["line_index"]
        dec_gen = dec["generation"]
        chosen = dec["chosen"]
        phase_logged = dec["phase_logged"]

        gen_transitions = [
            t for t in transitions
            if t["generation"] == dec_gen and t["line_index"] < dec_line
        ]
        prior_resets = [r for r in resets if r["line_index"] < dec_line]
        latest_reset_line = max([r["line_index"] for r in prior_resets], default=-1)

        active_transitions = [t for t in gen_transitions if t["line_index"] > latest_reset_line]
        expected_phase = "Phase_2" if active_transitions else "Phase_1"

        if phase_logged and phase_logged != expected_phase:
            partition_ok = False
            report["errors"].append(
                f"Decision at line {dec_line} explicitly logged phase='{phase_logged}', expected '{expected_phase}'."
            )

        if chosen:
            card_is_p2 = is_phase_2_card(chosen)
            if expected_phase == "Phase_1" and card_is_p2:
                partition_ok = False
                report["errors"].append(
                    f"Decision at line {dec_line} (attack {dec['attack']}) selected Phase 2 card '{chosen}' while in Phase 1."
                )
            elif expected_phase == "Phase_2" and not card_is_p2:
                partition_ok = False
                report["errors"].append(
                    f"Decision at line {dec_line} (attack {dec['attack']}) selected Phase 1 card '{chosen}' while in Phase 2."
                )

        preceding_refusals = [
            r for r in refusals
            if last_decision_line < r["line_index"] < dec_line and r["generation"] == dec_gen
        ]
        for ref in preceding_refusals:
            ref_card = ref["card"]
            ref_reason = ref["reason"]
            ref_is_p2 = is_phase_2_card(ref_card)

            if expected_phase == "Phase_1" and ref_is_p2:
                if "Phase" not in ref_reason:
                    partition_ok = False
                    report["errors"].append(
                        f"Phase 2 card '{ref_card}' in Phase 1 was refused with reason '{ref_reason}' instead of MoveModel.Phase."
                    )
            elif expected_phase == "Phase_2" and not ref_is_p2:
                if "Phase" not in ref_reason and "Cooldown" not in ref_reason:
                    partition_ok = False
                    report["errors"].append(
                        f"Phase 1 card '{ref_card}' in Phase 2 was refused with reason '{ref_reason}' instead of MoveModel.Phase."
                    )

        last_decision_line = dec_line

    report["checks"]["phase_partitioning_decisions"] = partition_ok

    # --- CHECK 6: Monotonicity & Idempotence ---
    mono_ok = True
    gen_counts: Dict[int, int] = {}
    for tr in transitions:
        g = tr["generation"]
        gen_counts[g] = gen_counts.get(g, 0) + 1
        if tr["to"] != "Phase_2":
            mono_ok = False
            report["errors"].append(f"Unexpected transition target phase: '{tr['to']}' (expected Phase_2).")
    for g, count in gen_counts.items():
        if count > 1:
            mono_ok = False
            report["errors"].append(f"Generation {g} logged {count} phase transitions to Phase 2 (must be idempotent/monotonic).")
    report["checks"]["monotonicity_and_idempotence"] = mono_ok

    # --- CHECK 7: Generation Reset Handling ---
    reset_ok = True
    for r in resets:
        r_line = r["line_index"]
        r_gen = r["generation"]
        post_decisions = [
            d for d in decisions
            if d["line_index"] > r_line and d["generation"] == r_gen
        ]
        post_transitions = [
            t for t in transitions
            if t["line_index"] > r_line and t["generation"] == r_gen
        ]
        first_post_trans_line = min([t["line_index"] for t in post_transitions], default=float('inf'))

        pre_trans_decisions = [d for d in post_decisions if d["line_index"] < first_post_trans_line]
        for d in pre_trans_decisions:
            if d["chosen"] and is_phase_2_card(d["chosen"]):
                reset_ok = False
                report["errors"].append(
                    f"Post-reset generation {r_gen} decision at line {d['line_index']} chose Phase 2 card '{d['chosen']}' before phase transition occurred."
                )
    report["checks"]["generation_reset_handling"] = reset_ok

    # --- CHECK 8: RESULT Validity ---
    results = report["parsed_data"]["results"]
    if not results and not (ki149_target is not None and no_cand_ctx is not None):
        report["checks"]["result_validity"] = False
        report["errors"].append("No [FrameworkProof] RESULT line found in log.")
    else:
        failed_results = [r for r in results if "outcome=Failed" in r["raw"] or "outcome=Fatal" in r["raw"]]
        if failed_results:
            report["checks"]["result_validity"] = False
            for fr in failed_results:
                report["errors"].append(f"Encounter terminated with failed RESULT: {fr['raw']}")
        else:
            report["checks"]["result_validity"] = True

    # Final overall pass/fail
    all_checks = report["checks"]
    report["passed"] = (
        len(all_checks) > 0 and
        all(all_checks.values()) and
        len(report["errors"]) == 0
    )

    ki149_str = f" (with documented KI-149 verified at gen={no_cand_ctx['generation']}, attack={no_cand_ctx['attack']}, phase={no_cand_ctx['phase']})" if (ki149_target and no_cand_ctx and report["checks"].get("no_error_tokens")) else ""
    if report["passed"]:
        report["summary"] = (
            f"PASS: {len(transitions)} transition(s) to Phase 2 verified, "
            f"{len(decisions)} decision(s) strictly partitioned across phase boundaries{ki149_str}."
        )
    else:
        report["summary"] = f"FAIL: Encountered {len(report['errors'])} error(s) during F6c log grading."

    return report


def main():
    parser = argparse.ArgumentParser(description="Grade editor raw log for F6c Phase Authority proof.")
    parser.add_argument("--log", dest="log_path", default=None, help="Path to editor raw log file.")
    parser.add_argument("log_pos", nargs="?", default=None, help="Positional path to log file.")
    parser.add_argument("--tolerance", type=float, default=0.01, help="Floating-point tolerance for health fraction comparison.")
    parser.add_argument("--expect-ki149", dest="expect_ki149", default=None, help="Targeted KI-149 spec: gen=<g>,attack=<a>,phase=<p> (Order C-432).")
    parser.add_argument("--json", action="store_true", help="Output detailed report as JSON.")
    args = parser.parse_args()

    target_path = args.log_path or args.log_pos
    if not target_path:
        print("[F6C_FATAL] Error: No log path provided. Use --log <path> or provide path as argument.", file=sys.stderr)
        sys.exit(1)

    log_file = Path(target_path)
    if not log_file.is_file():
        print(f"[F6C_FATAL] Error: Log file not found: {log_file}", file=sys.stderr)
        sys.exit(1)

    raw_text = log_file.read_text(encoding="utf-8", errors="replace")
    lines = parse_framework_log(raw_text)

    if not lines:
        print(f"[F6C_FATAL] Error: No [FrameworkProof] lines found in {log_file}", file=sys.stderr)
        sys.exit(1)

    report = grade_f6c_log_lines(lines, tolerance=args.tolerance, expect_ki149=args.expect_ki149)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=" * 72)
        print(" F6C PHASE AUTHORITY PROOF LOG GRADER")
        print("=" * 72)
        for check_name, check_pass in report["checks"].items():
            status_str = "PASS" if check_pass else "FAIL"
            print(f"[F6C_CHECK] {check_name:<32} : {status_str}")
        print("-" * 72)
        print(f"[F6C_SUMMARY] {report['summary']}")
        if report["errors"]:
            print("-" * 72)
            print("ERRORS / INVARIANT VIOLATIONS:")
            for err in report["errors"]:
                print(f"  - {err}")
        print("=" * 72)

    if not report["passed"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
