#!/usr/bin/env python3
"""Summarize cold/warm Lead cost samples without dropping run identities."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from atomic_io import atomic_write_text


SCHEMA = "onebossfight.encounter-cost-runs/v1"
REPORT_SCHEMA = "onebossfight.encounter-cost-report/v1"
HEX256 = re.compile(r"[0-9a-f]{64}")
PERCENTILES = (50, 95, 99)


def _digest(value: Any) -> bool:
    return isinstance(value, str) and HEX256.fullmatch(value) is not None


def nearest_rank(values: list[float], percentile: int) -> float:
    if not values or percentile not in PERCENTILES:
        raise ValueError("nearest-rank input must be nonempty and percentile must be 50, 95, or 99")
    ordered = sorted(values)
    return ordered[math.ceil(percentile * len(ordered) / 100) - 1]


def summarize(data: Any, source_path: str | None = None) -> dict[str, Any]:
    issues: list[str] = []
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        issues.append(f"schema must be {SCHEMA}")
        samples: list[Any] = []
    else:
        samples = data.get("samples")
        if not isinstance(samples, list):
            issues.append("samples must be an array")
            samples = []
    valid: list[dict[str, Any]] = []
    seen: set[str] = set()
    build_ids: set[str] = set()
    binary_hashes: set[str] = set()
    content_hashes: set[str] = set()
    for index, row in enumerate(samples):
        label = f"samples[{index}]"
        if not isinstance(row, dict):
            issues.append(f"{label} must be an object")
            continue
        required = ("sample_id", "run_id", "phase", "build_id", "binary_sha256", "content_sha256",
                    "elapsed_ms", "source_log", "source_log_sha256")
        missing = [key for key in required if key not in row]
        if missing:
            issues.append(f"{label} missing identity/evidence fields: {', '.join(missing)}")
            continue
        if row["phase"] not in ("cold", "warm"):
            issues.append(f"{label}.phase must be cold or warm")
        for key in ("sample_id", "run_id", "build_id", "source_log"):
            if not isinstance(row[key], str) or not row[key].strip():
                issues.append(f"{label}.{key} must be nonempty text")
        if isinstance(row["sample_id"], str) and row["sample_id"]:
            if row["sample_id"] in seen:
                issues.append(f"duplicate sample_id {row['sample_id']!r}")
            seen.add(row["sample_id"])
        if not _digest(row["binary_sha256"]) or not _digest(row["content_sha256"]) or not _digest(row["source_log_sha256"]):
            issues.append(f"{label} binary/content/log hashes must be lowercase SHA-256")
        elapsed = row["elapsed_ms"]
        if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed < 0:
            issues.append(f"{label}.elapsed_ms must be finite and nonnegative")
        if isinstance(row["build_id"], str):
            build_ids.add(row["build_id"])
        if _digest(row["binary_sha256"]):
            binary_hashes.add(row["binary_sha256"])
        if _digest(row["content_sha256"]):
            content_hashes.add(row["content_sha256"])
        valid.append(row)
    if len(build_ids) > 1:
        issues.append("samples mix build IDs; separate captures before comparison")
    if len(binary_hashes) > 1 or len(content_hashes) > 1:
        issues.append("samples mix binary or content identities; separate captures before comparison")
    for phase in ("cold", "warm"):
        if not any(row.get("phase") == phase for row in valid):
            issues.append(f"missing {phase} samples")
    metrics: dict[str, dict[str, float | int]] = {}
    for phase in ("cold", "warm"):
        values = [float(row["elapsed_ms"]) for row in valid if row.get("phase") == phase
                  and isinstance(row.get("elapsed_ms"), (int, float)) and not isinstance(row.get("elapsed_ms"), bool)
                  and math.isfinite(row["elapsed_ms"]) and row["elapsed_ms"] >= 0]
        if values:
            metrics[phase] = {"sample_count": len(values), **{
                f"p{p}": nearest_rank(values, p) for p in PERCENTILES
            }}
    status = "INCONCLUSIVE" if issues else "PASS"
    return {
        "schema": REPORT_SCHEMA,
        "status": status,
        "method": "nearest-rank: sorted_values[ceil(p*n)-1], zero-based index",
        "source_receipt": source_path,
        "issues": issues,
        "metrics_ms": metrics,
        "samples": valid,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="Lead-captured cold/warm cost receipt JSON")
    parser.add_argument("--report-json", type=Path, help="optional atomic JSON report destination")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report = summarize(None, str(args.receipt))
        report["issues"] = [f"cannot read valid UTF-8 receipt: {exc}"]
        print(json.dumps(report, sort_keys=True))
        if args.report_json:
            atomic_write_text(args.report_json, json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n")
        return 2
    report = summarize(data, str(args.receipt))
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.report_json:
        atomic_write_text(args.report_json, encoded)
    print(encoded.rstrip())
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
