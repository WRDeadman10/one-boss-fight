#!/usr/bin/env python3
"""Finalize an A4 driver capture as a v2 receipt after the source log is closed."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from encounter_parity_receipt import ReceiptError, build_receipt_from_snapshot, sha256_file, write_receipt

CAPTURE_MARKER = "PARITY_CAPTURE_JSON "
SNAPSHOT_MARKER = "[A5ParityRunner] SNAPSHOT_JSON "
DRIVERS = {
    "pie_a4_low_sweep": ("A4", 14),
    "pie_dormant_wake": ("DormantWake", 11),
    "pie_damage_path": ("Dmg", 17),
    "pie_player_death_reset": ("DeathReset", 25),
    "pie_telegraph": ("Telegraph", 25),
    "pie_boss_hud": ("BossHud", 29),
    "pie_phase_reset": ("PhaseReset", 14),
    "pie_boss_death": ("BossDeath", 11),
    "pie_boss_death_states": ("DeathStates", 28),
    "pie_victory_lock": ("VictoryLock", 9),
    "pie_transition_rules": ("Transition", 28),
    "pie_a5_heal_punish": ("A5", 31),
    "pie_bleed": ("Bleed", 19),
    "pie_leap_wave": ("Leap", 17),
    "pie_posture_hits": ("Posture", 25),
    "pie_hyperarmor": ("HyperArmor", 23),
    "pie_close_attacks": ("Close", 55),
    "pie_authored_close_clips": ("AuthoredClose", 14),
    "pie_boss_clips": ("BossClips", 14),
    "pie_attack_rules": ("Rules", 13),
    "pie_boss_look": ("BossLook", 14),
    "pie_riposte": ("Riposte", 5),
    "pie_riposte_exec": ("RipostExec", 15),
    "pie_riposte_lethal": ("RipostLethal", 3),
    "pie_trace_audit": ("Trace", 30),
    "pie_hit_intake": ("Intake", 36),
    "pie_iframes": ("IFrame", 19),
    "pie_fog_gate": ("FogGate", 6),
    "pie_remains": ("Remains", 4),
    "pie_soak": ("Soak", 213),
    "pie_legend": ("Legend", 25),
}

# The timing key can be a semantic label rather than a literal prefix of the
# check text. Keep the explicit alias narrow and backed by the live Legend log.
TIMING_OBSERVABLE_CHECK_PREFIXES = {
    "L8 perfect parry slow motion duration": ("L8 real perfect parry contact starts",),
}


def read_capture(log_path: Path) -> dict[str, Any]:
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ReceiptError(f"cannot read source log {log_path}: {exc}") from exc
    captures = [line.split(CAPTURE_MARKER, 1)[1] for line in lines if "[A4] " + CAPTURE_MARKER in line]
    if captures:
        try:
            payload = json.loads(captures[-1])
        except json.JSONDecodeError as exc:
            raise ReceiptError(f"A4 parity capture is invalid JSON: {exc}") from exc
        if isinstance(payload, dict) and isinstance(payload.get("snapshot"), dict) and isinstance(payload.get("run_facts"), dict):
            # Only S9's 0.40 s roll outcome is declared boundary-noisy. Keep
            # all other fields exact, and expose invulnerability as WARN data.
            observables = payload["run_facts"].get("observables", {})
            boundary_name = "S9 info roll at 0.40 s"
            boundary = observables.get(boundary_name) if isinstance(observables, dict) else None
            if isinstance(boundary, dict) and boundary.get("trials") == 3:
                observables[boundary_name + " exact fields"] = {
                    key: boundary[key] for key in ("hits", "jumped", "scenario_checks") if key in boundary
                }
                observables[boundary_name] = {
                    "value": {"scenario_ran": True, "trials": 3,
                              "invulnerable": boundary.get("invulnerable")},
                    "comparison": {"type": "stochastic", "scenario_ran_field": "scenario_ran",
                                   "threshold": {"left_field": "trials", "op": "eq", "right_value": 3}},
                }
            return payload
        raise ReceiptError("A4 parity capture must contain snapshot and run_facts objects")
    raise ReceiptError("driver capture requires driver identity; use read_driver_capture")


def _gameplay_measurements(message: str) -> list[dict[str, Any]]:
    """Promote explicit health/posture/damage numbers from a check message to typed values.

    Keep labels and source text alongside the values: this deliberately does not infer a
    delta, classify a threshold as an observation, or reinterpret an unlabelled number.
    """
    values: list[dict[str, Any]] = []
    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    health_transition = re.search(rf"\bhealth\s+({number})\s*(?:->|→|to)\s*({number})\b", message, re.I)
    if health_transition:
        values.extend((
            {"field": "health_before", "value": float(health_transition.group(1))},
            {"field": "health_after", "value": float(health_transition.group(2))},
        ))
    else:
        health_ratio = re.search(rf"\bhealth(?:\s+(?:loss|drop|stays?|exactly|at|is|of|remaining|full)){{0,3}}\s*(?:[:=]\s*)?({number})\s*/\s*({number})\b", message, re.I)
        health_to_zero = re.search(rf"(?:\bhealth\s+from\s+({number})\s+to\s+zero\b|\bfrom\s+({number})\s+health\s+to\s+zero\b)", message, re.I)
        labeled = re.search(rf"\bhealth(?:\s+(?:loss|drop|stays?|exactly|at|is|of|remaining|full)){{0,3}}\s*(?:[:=]\s*)?({number})\b", message, re.I)
        if health_ratio:
            values.extend((
                {"field": "health_current", "value": float(health_ratio.group(1))},
                {"field": "health_maximum", "value": float(health_ratio.group(2))},
            ))
        elif health_to_zero:
            before = health_to_zero.group(1) or health_to_zero.group(2)
            values.extend((
                {"field": "health_before", "value": float(before)},
                {"field": "health_after", "value": 0.0},
            ))
        elif labeled:
            values.append({"field": "health", "value": float(labeled.group(1))})
    for label in ("posture", "damage"):
        match = re.search(
            rf"\b{label}(?:\s+(?:loss|drop|taken|event|equals?|exactly|at|is|of|remaining|full|value|per\s+event)){{0,3}}\s*(?:[:=]\s*)?({number})\b",
            message, re.I,
        )
        if match:
            values.append({"field": label, "value": float(match.group(1))})
    return values


def read_driver_capture(log_path: Path, driver: str) -> dict[str, Any]:
    if driver not in DRIVERS:
        raise ReceiptError("unsupported driver: " + driver)
    prefix, minimum = DRIVERS[driver]
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ReceiptError(f"cannot read source log {log_path}: {exc}") from exc
    snapshots = [line.split(SNAPSHOT_MARKER, 1)[1] for line in lines if SNAPSHOT_MARKER in line]
    if not snapshots and driver == "pie_a4_low_sweep":
        payload = read_capture(log_path)
        if payload.get("snapshot"):
            return payload
    if not snapshots:
        raise ReceiptError("source log has no A5ParityRunner SNAPSHOT_JSON line")
    try:
        snapshot = json.loads(snapshots[-1])
    except json.JSONDecodeError as exc:
        raise ReceiptError(f"runtime snapshot is invalid JSON: {exc}") from exc
    result_pattern = re.compile(rf"\[{re.escape(prefix)}\] RESULT (\d+)/(\d+) passed")
    summary_pattern = re.compile(rf"\[{re.escape(prefix)}\] SUMMARY (\d+) checks, (\d+) failed")
    terminal = None
    checks: list[dict[str, Any]] = []
    check_pattern = re.compile(rf"\[{re.escape(prefix)}\] (PASS|FAIL) (.*)")
    for line in lines:
        match = result_pattern.search(line)
        if match:
            terminal = (int(match.group(1)), int(match.group(2)))
        summary = summary_pattern.search(line)
        if summary:
            total, failed = int(summary.group(1)), int(summary.group(2))
            terminal = (total - failed, total)
        check = check_pattern.search(line)
        if check:
            checks.append({"status": check.group(1), "message": check.group(2)})
    if terminal is None:
        raise ReceiptError(f"source log has no terminal RESULT for {driver}")
    passed, total = terminal
    if total <= 0 or passed < 0 or passed > total:
        raise ReceiptError(f"{driver} terminal RESULT has invalid counts {passed}/{total}")
    observables = {f"check-{index:04d}": value for index, value in enumerate(checks, 1)}
    for index, check in enumerate(checks, 1):
        measurements = _gameplay_measurements(check["message"])
        if measurements:
            observables[f"gameplay-check-{index:04d}"] = {
                "value": {"source_check": f"check-{index:04d}", "fields": measurements},
                "comparison": {"type": "exact"},
                "check_status": check["status"],
                "check_message": check["message"],
            }
    timing_marker = f"[{prefix}] TIMING_OBSERVABLES_JSON "
    timing_lines = [line.split(timing_marker, 1)[1] for line in lines if timing_marker in line]
    if timing_lines:
        try:
            timing_values = json.loads(timing_lines[-1])
        except json.JSONDecodeError as exc:
            raise ReceiptError(f"{driver} timing observables are invalid JSON: {exc}") from exc
        if not isinstance(timing_values, dict):
            raise ReceiptError(f"{driver} timing observables must be an object")
        for check_name, typed_value in timing_values.items():
            if not isinstance(typed_value, dict) or "value" not in typed_value or "comparison" not in typed_value:
                raise ReceiptError(f"{driver} timing observable {check_name!r} must have value and comparison")
            prefixes = TIMING_OBSERVABLE_CHECK_PREFIXES.get(check_name, (check_name,))
            matching_indices = [index for index, check in enumerate(checks, 1)
                                if any(check["message"].startswith(prefix) for prefix in prefixes)]
            if len(matching_indices) != 1:
                raise ReceiptError(f"{driver} timing observable {check_name!r} matched {len(matching_indices)} checks")
            check_result = checks[matching_indices[0] - 1]
            observables[f"check-{matching_indices[0]:04d}"] = {
                **typed_value,
                "check_status": check_result["status"],
                "check_message": check_result["message"],
            }
    # Backfill P06 per-trial rows from source INFO lines. Trial identities,
    # hits, and iframe_passes stay exact; only world_hits is WARN-stochastic.
    if driver == "pie_a5_heal_punish":
        p06_rows: list[dict[str, Any]] = []
        row_pattern = re.compile(r"\[A5\] INFO P06 (.+): hits (\d+), i-frame pass (\d+), world (\d+)$")
        for line in lines:
            match = row_pattern.search(line)
            if match:
                p06_rows.append({"trial": match.group(1), "hits": int(match.group(2)),
                                 "iframe_passes": int(match.group(3)), "world_hits": int(match.group(4))})
        matches = [index for index, check in enumerate(checks, 1)
                   if check["message"].startswith("P06 a side roll pressed on the heal exit")]
        if len(matches) == 1 and not p06_rows:
            current = observables.get(f"check-{matches[0]:04d}", {})
            current_rows = current.get("value") if isinstance(current, dict) else None
            if isinstance(current_rows, list) and all(
                isinstance(row, dict) and all(key in row for key in ("trial", "hits", "iframe_passes", "world_hits"))
                for row in current_rows
            ):
                p06_rows = current_rows
        if p06_rows and len(matches) == 1:
            index = matches[0]
            check_result = checks[index - 1]
            observables[f"check-{index:04d}"] = {
                "value": [{key: row[key] for key in ("trial", "hits", "iframe_passes")} for row in p06_rows],
                "comparison": {"type": "exact"},
                "check_status": check_result["status"],
                "check_message": check_result["message"],
            }
            observables["p06-world-hits"] = {
                "value": {"scenario_ran": True, "trials": len(p06_rows), "rows": p06_rows},
                "comparison": {"type": "stochastic", "scenario_ran_field": "scenario_ran",
                               "threshold": {"left_field": "trials", "op": "gte", "right_value": 1}},
                "check_status": check_result["status"],
                "check_message": "P06 world_hits boundary field; all per-trial values retained as WARN",
            }
    if driver == "pie_close_attacks" and not any(
        isinstance(value, dict) and isinstance(value.get("comparison"), dict)
        and value["comparison"].get("type") == "stochastic"
        for value in observables.values()
    ):
        c7_matches = [index for index, check in enumerate(checks, 1)
                      if check["message"].startswith("C7 the close attack hurts a player in front (90 cm)")]
        hit_rows = re.findall(r"\[Close\] INFO C7 trial at (\d+) cm: (hit|miss) ", "\n".join(lines))
        close_rows = [(distance, result) for distance, result in hit_rows if int(distance) <= 100]
        if close_rows and len(c7_matches) == 1:
            index = c7_matches[0]
            check_result = checks[index - 1]
            observables[f"check-{index:04d}"] = {
                "value": {"scenario_ran": len(close_rows) == 5,
                          "hits": sum(result == "hit" for _, result in close_rows),
                          "trials": len(close_rows)},
                "comparison": {
                    "type": "stochastic", "scenario_ran_field": "scenario_ran",
                    "threshold": {"left_field": "hits", "op": "gte", "right_value": 1},
                },
                "check_status": check_result["status"],
                "check_message": check_result["message"],
            }
    if driver == "pie_attack_rules" and not any(
        isinstance(value, dict) and isinstance(value.get("comparison"), dict)
        and value["comparison"].get("type") == "stochastic"
        for value in observables.values()
    ):
        attack_rows = [(index, re.search(r"R5 the boss attacked in the fight \((\d+) tracked attacks\)", check["message"]))
                       for index, check in enumerate(checks, 1)]
        commit_rows = [(index, re.search(
            r"R5 every tracked attack that reached its commit point committed once \((\d+) attacks, (\d+) stopped in the windup\).*?commits (\d+)",
            check["message"])) for index, check in enumerate(checks, 1)]
        attack_match = next(((index, match) for index, match in attack_rows if match), None)
        commit_match = next(((index, match) for index, match in commit_rows if match), None)
        if attack_match and commit_match:
            index, match = attack_match
            n = int(match.group(1))
            check_result = checks[index - 1]
            observables[f"check-{index:04d}"] = {
                "value": {"scenario_ran": True, "tracked_attacks": n},
                "comparison": {
                    "type": "stochastic", "scenario_ran_field": "scenario_ran",
                    "threshold": {"left_field": "tracked_attacks", "op": "gte", "right_value": 1},
                },
                "check_status": check_result["status"],
                "check_message": check_result["message"],
            }
            index, match = commit_match
            n, cut, commits = (int(match.group(i)) for i in (1, 2, 3))
            check_result = checks[index - 1]
            observables[f"check-{index:04d}"] = {
                "value": {"scenario_ran": True, "tracked_attacks": n, "commits": commits,
                          "stopped_in_windup": cut, "accounted_attacks": commits + cut},
                "comparison": {
                    "type": "stochastic", "scenario_ran_field": "scenario_ran",
                    "threshold": {"left_field": "accounted_attacks", "op": "gte", "right_field": "tracked_attacks"},
                },
                "check_status": check_result["status"],
                "check_message": check_result["message"],
            }
    if driver == "pie_soak":
        # Only the six naturally fought encounters depend on the fight's
        # preceding health trajectory. Preserve the health values as a WARN,
        # while comparing that each route met the check's own no-damage rule.
        natural_pattern = re.compile(
            r"^(\d+) natural no damage after reset \(([-+\d.eE]+),\s*([-+\d.eE]+)\)$"
        )
        for index, check_result in enumerate(checks, 1):
            match = natural_pattern.search(check_result["message"])
            if not match:
                continue
            before, after = float(match.group(2)), float(match.group(3))
            observables[f"check-{index:04d}"] = {
                "value": {"scenario_ran": True, "before": before, "after": after},
                "comparison": {
                    "type": "stochastic", "scenario_ran_field": "scenario_ran",
                    "threshold": {"left_field": "before", "op": "eq", "right_field": "after"},
                },
                "check_status": check_result["status"],
                "check_message": check_result["message"],
            }
    return {
        "snapshot": snapshot,
        "run_facts": {
            "final_marker": {"kind": "R", "passed": passed, "total": total},
            # `minimum` is the registered expected total. Preserve a short run as
            # failed evidence so the comparator can report it instead of hiding it.
            "checks": {"passed": passed, "minimum": minimum},
            "terminal": {"clean": passed == total and total >= minimum,
                         "result": "Completed" if passed == total and total >= minimum else "Failed"},
            "observables": observables,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True, help="closed, complete OneBossFight.log from this run")
    parser.add_argument("--identity", type=Path, required=True, help="JSON object with the eight v2 identity fields")
    parser.add_argument("--run-id", required=True, help="unique identifier for this individual arm")
    parser.add_argument("--out", type=Path, required=True, help="new receipt path; existing output is refused")
    args = parser.parse_args(argv)
    try:
        log_path = args.log.resolve(strict=True)
        out_path = args.out.resolve()
        if out_path.exists():
            raise ReceiptError(f"refusing to overwrite existing receipt: {out_path}")
        try:
            identity = json.loads(args.identity.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ReceiptError(f"cannot read identity JSON: {exc}") from exc
        if not isinstance(identity, dict):
            raise ReceiptError("identity JSON root must be an object")
        driver = identity.get("driver")
        if driver not in DRIVERS:
            raise ReceiptError("identity.driver must name a registered A5 parity driver")
        payload = read_driver_capture(log_path, driver)
        facts = dict(payload["run_facts"])
        facts.update(run_id=args.run_id, identity=identity)
        log_hash = sha256_file(log_path)
        facts["observables"] = {
            name: {
                **(value if isinstance(value, dict) and "value" in value and "comparison" in value
                   else {"value": value}),
                "source_log": str(log_path),
                "source_log_sha256": log_hash,
                "trial_id": name,
            }
            for name, value in facts.get("observables", {}).items()
        }
        receipt = build_receipt_from_snapshot(payload["snapshot"], facts)
        write_receipt(out_path, {
            "route": receipt["route"],
            **{key: receipt[key] for key in (
                "run_id", "identity", "selection", "participants", "final_marker", "checks",
                "terminal", "activation", "components", "observables")},
        })
        print(f"WROTE {out_path} schema={receipt['schema']} route={receipt['route']} observables={len(receipt['observables'])}")
        return 0
    except (ReceiptError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
