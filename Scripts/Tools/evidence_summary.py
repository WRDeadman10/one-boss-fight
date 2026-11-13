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

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BO-28: before atomic_io too, so `python -m Scripts.Tools.*` works; helper import works as a script or as Scripts.Tools.*
from atomic_io import atomic_write_text
from redaction import add_redact_argument, display_path, display_row, install_stream_redaction, redaction_scope, redact_text
from text_input import TextInputError, read_text_input


def output_aliases(output: Path, inputs) -> Path | None:
    """BK-301..305: return the input that `output` would overwrite (same resolved path or same file), else None."""
    target = Path(output).resolve()
    for item in inputs:
        candidate = Path(item)
        if candidate.resolve() == target:
            return candidate
        if target.exists() and candidate.exists() and target.samefile(candidate):
            return candidate
    return None

TIMESTAMP = re.compile(r"\[(\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}):(\d{3})\]")
OUTCOME = re.compile(r"\[FrameworkProof\]\s+RESULT\s+.*?\boutcome=([^\s]+)")
FIELD = {"map": re.compile(r"\bmap=([^\s]+)"), "profile": re.compile(r"\bprofile=([^\s]+)")}
PROFILE_READBACK = re.compile(r'"fixture_profile"\s*:\s*"([^"]+)"')


VALIDATOR_REL = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py")


def load_validator(root: Path):
    path = root / VALIDATOR_REL
    spec = importlib.util.spec_from_file_location("evidence_summary_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def summarize(log: Path, root: Path, validator, redact: bool = False, evidence: Path | None = None) -> dict[str, str]:
    # BP-26: third-party editor logs keep errors="replace" for stray bytes, but a BOM is stripped and UTF-16 fails closed
    text = read_text_input(log, errors="replace")
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
        if redact:  # BO-05 / BO-15: no absolute path, but keep the run identity relative to the evidence folder
            try:
                run = "<evidence>/" + log.resolve().relative_to(Path(evidence).resolve()).as_posix()
            except (TypeError, ValueError):
                run = display_path(log.resolve(), True)
    if redact:
        map_value = redact_text(map_match.group(1)) if map_match else "unknown"
        profile_value = redact_text(profile_match.group(1)) if profile_match else "unknown"
    else:
        map_value = map_match.group(1) if map_match else "unknown"
        profile_value = profile_match.group(1) if profile_match else "unknown"
    return {
        "run": run,
        "map": map_value,
        "profile": profile_value,
        "date": date,
        "outcome": outcomes[-1] if outcomes else "missing",
        "validator": status,
        "schema_failures": str(syntax),
        "semantic_warnings": str(semantic),
        "sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
    }


@redaction_scope  # BO-18: restore the caller's streams when main ends
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--evidence", type=Path, default=Path("Docs/BossCombatReview/Execution/Claude"))
    parser.add_argument("--output", type=Path, required=True)
    add_redact_argument(parser)
    args = parser.parse_args()
    if args.redact:  # BO-23: only ever enable here; never unwrap a caller-owned wrapper when the flag is absent
        install_stream_redaction(True)  # BO-06..09: mask absolute machine paths in every printed line
    root = args.root.resolve()
    evidence = args.evidence if args.evidence.is_absolute() else root / args.evidence
    if not evidence.is_dir():
        parser.error(f"evidence directory does not exist: {evidence}")
    validator = load_validator(root)
    logs = sorted(evidence.rglob("editor_raw.log"))
    columns = ["run", "map", "profile", "date", "outcome", "validator", "schema_failures", "semantic_warnings", "sha256"]
    output = args.output if args.output.is_absolute() else root / args.output
    aliased = output_aliases(output, [*logs, root / VALIDATOR_REL])
    if aliased is not None:
        parser.error(f"output aliases an input; refusing to overwrite it: {aliased}")
    output.parent.mkdir(parents=True, exist_ok=True)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    try:
        for log in logs:
            writer.writerow(summarize(log, root, validator, args.redact, evidence))
    except TextInputError as error:  # BP-26: named usage error (exit 2) before any CSV is written
        parser.error(str(error))
    atomic_write_text(output, stream.getvalue())
    print(f"logs={len(logs)} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
