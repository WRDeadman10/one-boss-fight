#!/usr/bin/env python3
"""Validate and render the evidence state of the A7 release gates."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA = "onebossfight.a7-release-gates/v1"
EXPECTED_IDS = {
    "A7-SHIPPING-SELECTOR", "A7-SELECTED-PERFORMANCE",
    "A7-SAVE-COOK-COMPATIBILITY", "A7-SELECTION-RECOVERY",
}
REQUIRED_GATE_FIELDS = {"id", "title", "status", "owner", "evidence_sources", "close_with", "closure_evidence"}


def _safe_file(root: Path, raw: Any, label: str, issues: list[str]) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        issues.append(f"{label}: path must be a nonempty project-relative string")
        return None
    candidate = (root / Path(raw)).resolve()
    base = root.resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        issues.append(f"{label}: path escapes project root: {raw}")
        return None
    if not candidate.is_file():
        issues.append(f"{label}: referenced file is missing: {raw}")
        return None
    return candidate


def validate_checklist(value: Any, project_root: Path) -> list[str]:
    if not isinstance(value, dict):
        return ["checklist root must be an object"]
    issues: list[str] = []
    if value.get("schema") != SCHEMA:
        issues.append(f"schema must be {SCHEMA}")
    policy = value.get("policy")
    if not isinstance(policy, dict) or policy.get("J049_shipping_selector") != "A" or policy.get("A7_legacy_retirement") != "B":
        issues.append("policy must preserve J049=A and A7=B")
    gates = value.get("gates")
    if not isinstance(gates, list) or len(gates) != len(EXPECTED_IDS):
        return issues + ["gates must contain exactly the four P15 A7 release gates"]
    seen: set[str] = set()
    for index, gate in enumerate(gates):
        prefix = f"gates[{index}]"
        if not isinstance(gate, dict):
            issues.append(f"{prefix} must be an object")
            continue
        missing = REQUIRED_GATE_FIELDS - set(gate)
        for key in sorted(missing):
            issues.append(f"{prefix} missing {key}")
        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or gate_id not in EXPECTED_IDS:
            issues.append(f"{prefix} has unknown gate id {gate_id!r}")
        elif gate_id in seen:
            issues.append(f"duplicate gate id {gate_id}")
        else:
            seen.add(gate_id)
        if gate.get("status") not in ("OPEN", "CLOSED"):
            issues.append(f"{prefix} status must be OPEN or CLOSED")
        sources = gate.get("evidence_sources")
        if not isinstance(sources, list) or not sources:
            issues.append(f"{prefix} evidence_sources must be a nonempty list")
        else:
            for source_index, source in enumerate(sources):
                _safe_file(project_root, source, f"{prefix}.evidence_sources[{source_index}]", issues)
        closure = gate.get("closure_evidence")
        if not isinstance(closure, list):
            issues.append(f"{prefix} closure_evidence must be a list")
        elif gate.get("status") == "CLOSED":
            if not closure:
                issues.append(f"{prefix} is CLOSED without closure evidence references")
            for evidence_index, item in enumerate(closure):
                _safe_file(project_root, item, f"{prefix}.closure_evidence[{evidence_index}]", issues)
        elif closure:
            for evidence_index, item in enumerate(closure):
                _safe_file(project_root, item, f"{prefix}.closure_evidence[{evidence_index}]", issues)
        for key in ("title", "owner", "close_with"):
            if key in gate and (not isinstance(gate[key], str) or not gate[key].strip()):
                issues.append(f"{prefix} {key} must be nonempty")
    if seen != EXPECTED_IDS:
        issues.append("gate IDs must match the four P15 A7 gates exactly")
    return issues


def render_report(value: Any) -> str:
    if not isinstance(value, dict) or not isinstance(value.get("gates"), list):
        return "# A7 release gates\n\nChecklist invalid; no gate status is reported.\n"
    lines = ["# A7 release gates", "", "Current owner policy: J049=A; A7=B (legacy retirement is deferred until release gates close).", "",
             "| Gate | Status | Owner | Next evidence to close |", "|---|---|---|---|"]
    for gate in value["gates"]:
        if not isinstance(gate, dict):
            continue
        close_with = str(gate.get("close_with", "UNKNOWN")).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {gate.get('id', 'UNKNOWN')} | {gate.get('status', 'UNKNOWN')} | {gate.get('owner', 'UNKNOWN')} | {close_with} |")
    lines.extend(["", "Gate states are listed individually; no aggregate completion percentage is calculated."])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checklist", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--report", action="store_true", help="render a text report instead of validation diagnostics")
    args = parser.parse_args()
    try:
        value = json.loads(args.checklist.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    issues = validate_checklist(value, args.project_root)
    if args.report:
        if issues:
            print("A7 report not generated: checklist is invalid.", file=sys.stderr)
            for issue in issues:
                print("INVALID " + issue, file=sys.stderr)
            return 1
        print(render_report(value), end="")
    if issues:
        for issue in issues:
            print("INVALID " + issue, file=sys.stderr)
        return 1
    if not args.report:
        print("PASS: A7 release-gate checklist valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
