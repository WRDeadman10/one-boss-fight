#!/usr/bin/env python3
"""Cross-check receipt-registered A5 drivers against the RunDrivers schedule."""
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROW = re.compile(r"\@\{\s*N\s*=\s*'([^']+)';\s*K\s*=\s*'([RS])';\s*Min\s*=\s*(\d+)(?:;\s*T\s*=\s*(\d+))?")


def literal_assignment(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(f"missing literal assignment {name} in {path}")


def run_driver_rows(text: str) -> dict[str, tuple[str, int, int]]:
    primary = text.split("# Balance runs", 1)[0]
    return {name: (kind, int(minimum), int(timeout or 420))
            for name, kind, minimum, timeout in ROW.findall(primary)}


def audit(expected: dict[str, tuple[str, int]], scheduled: dict[str, tuple[str, int, int]],
          allowed: dict[str, float], a4_registered: bool = False):
    issues = []
    for name in sorted(expected.keys() - scheduled.keys()):
        issues.append(f"MISSING RunDrivers registration: {name}")
    # These are valid A5-host entries with standalone contracts, not parity
    # receipt rows: refusal testing and the memory soak use their own receipts.
    independently_registered = {"pie_selection_refusal", "pie_memory_soak"} | ({"pie_a4_low_sweep"} if a4_registered else set())
    for name in sorted(expected.keys() - allowed.keys() - independently_registered):
        issues.append(f"MISSING A5 runner registration: {name}")
    for name in sorted(allowed.keys() - expected.keys() - {"pie_selection_refusal", "pie_memory_soak"}):
        issues.append(f"EXTRA A5 runner registration: {name}")
    rows = []
    for name in sorted(expected):
        if name not in scheduled:
            continue
        prefix, minimum = expected[name]
        kind, observed_minimum, timeout = scheduled[name]
        if minimum != observed_minimum:
            issues.append(f"MISMATCH {name}: receipt minimum {minimum}, RunDrivers minimum {observed_minimum}")
        rows.append((name, prefix, kind, observed_minimum, timeout))
    return rows, issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    tools = args.root / "Scripts/Tools"
    expected = literal_assignment(tools / "write_a4_parity_receipt.py", "DRIVERS")
    allowed = literal_assignment(args.root / "Scripts/Editor/run_a5_parity_driver_and_quit.py", "ALLOWED")
    scheduled = run_driver_rows((args.root / "Scripts/RunDrivers.ps1").read_text(encoding="utf-8"))
    pair_runner = (args.root / "Scripts/RunA5ParityPair.ps1").read_text(encoding="utf-8")
    a4_registered = ((args.root / "Scripts/Editor/run_a4_parity_and_quit.py").is_file()
                     and "run_a4_parity_and_quit.py" in pair_runner
                     and "pie_a4_low_sweep" in pair_runner)
    rows, issues = audit(expected, scheduled, allowed, a4_registered=a4_registered)
    print(f"[A5_REGISTRATION] receipt={len(expected)} scheduled={len(scheduled)} runner={len(allowed)} checked={len(rows)} issues={len(issues)}")
    for name, prefix, kind, minimum, timeout in rows:
        print(f"MATCH {name} prefix={prefix} marker={kind} minimum={minimum} timeout_seconds={timeout}")
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
