#!/usr/bin/env python3
"""Write a CSV index of retained FrameworkProof editor logs."""
from __future__ import annotations

import argparse
import csv
import io
import hashlib
import importlib.util
import re
from datetime import datetime
from pathlib import Path

from atomic_io import atomic_write_text

TIMESTAMP = re.compile(r"\[(\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}):(\d{3})\]")
OUTCOME = re.compile(r"\[FrameworkProof\]\s+RESULT\s+.*?\boutcome=([^\s]+)")
FIELD = {"map": re.compile(r"\bmap=([^\s]+)"), "profile": re.compile(r"\bprofile=([^\s]+)")}
PROFILE_READBACK = re.compile(r'"fixture_profile"\s*:\s*"([^"]+)"')


def load_validator(root: Path):
    path = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py"
    spec = importlib.util.spec_from_file_location("evidence_summary_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def summarize(log: Path, root: Path, validator) -> dict[str, str]:
    text = log.read_text(encoding="utf-8", errors="replace")
    timestamp = TIMESTAMP.search(text)
    date = "unknown"
    if timestamp:
        parts = [int(part) for part in timestamp.groups()]
        date = datetime(*parts[:6], parts[6] * 1000).isoformat(timespec="milliseconds")
    outcomes = OUTCOME.findall(text)
    map_match = FIELD["map"].search(text)
    profile_match = PROFILE_READBACK.search(text) or FIELD["profile"].search(text)
    result = validator.validate_log_file(log)
    syntax = len(result["syntax_failures"])
    semantic = len(result["semantic_violations"])
    status = "PASS" if not syntax and not semantic else "SCHEMA_FAIL" if syntax else "SEMANTIC_WARN"
    try:
        run = log.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        run = str(log.resolve())
    return {
        "run": run,
        "map": map_match.group(1) if map_match else "unknown",
        "profile": profile_match.group(1) if profile_match else "unknown",
        "date": date,
        "outcome": outcomes[-1] if outcomes else "missing",
        "validator": status,
        "schema_failures": str(syntax),
        "semantic_warnings": str(semantic),
        "sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--evidence", type=Path, default=Path("Docs/BossCombatReview/Execution/Claude"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    evidence = args.evidence if args.evidence.is_absolute() else root / args.evidence
    if not evidence.is_dir():
        parser.error(f"evidence directory does not exist: {evidence}")
    validator = load_validator(root)
    logs = sorted(evidence.rglob("editor_raw.log"))
    columns = ["run", "map", "profile", "date", "outcome", "validator", "schema_failures", "semantic_warnings", "sha256"]
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    for log in logs:
        writer.writerow(summarize(log, root, validator))
    atomic_write_text(output, stream.getvalue())
    print(f"logs={len(logs)} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
