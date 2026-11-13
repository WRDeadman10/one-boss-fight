#!/usr/bin/env python3
"""Summarize Lead-captured packaged metrics by phase without mixing identities.

This offline tool summarizes declared per-run metrics; it does not scrape logs,
choose acceptance budgets, or prove that a measurement is truthful.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BP-01/02: sibling imports work as a script or as `python -m Scripts.Tools.*`
from atomic_io import atomic_write_text

SCHEMA = "onebossfight.packaged-metric-runs/v1"
REPORT_SCHEMA = "onebossfight.packaged-metric-report/v1"
HEX256 = re.compile(r"[0-9a-f]{64}")
IDENTITY_FIELDS = (
    "map", "build_id", "binary_sha256", "content_sha256", "settings_sha256",
    "input_sha256", "launch_args", "resolution", "hardware", "cvars",
)


def nearest_rank(values: list[float], percentile: int) -> float:
    if not values or percentile not in (50, 95, 99):
        raise ValueError("nearest-rank requires values and percentile 50, 95, or 99")
    ordered = sorted(values)
    return ordered[math.ceil(percentile * len(ordered) / 100) - 1]


def _digest(value: Any) -> bool:
    return isinstance(value, str) and HEX256.fullmatch(value) is not None


def summarize(data: Any, receipt_path: Path) -> dict[str, Any]:
    issues: list[str] = []
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        return {"schema": REPORT_SCHEMA, "status": "INCONCLUSIVE",
                "issues": [f"schema must be {SCHEMA}"], "metrics": {}, "samples": []}
    required_metrics = data.get("required_metrics")
    samples = data.get("samples")
    if not isinstance(required_metrics, list) or not required_metrics or any(
            not isinstance(name, str) or not name.strip() for name in required_metrics):
        issues.append("required_metrics must be a nonempty array of metric names")
        required_metrics = []
    elif len(set(required_metrics)) != len(required_metrics):
        issues.append("required_metrics contains duplicates")
    if not isinstance(samples, list) or not samples:
        issues.append("samples must be a nonempty array")
        samples = []

    ids: set[str] = set()
    run_ids: set[str] = set()
    baseline_identity: dict[str, Any] | None = None
    valid: list[dict[str, Any]] = []
    for index, row in enumerate(samples):
        label = f"samples[{index}]"
        if not isinstance(row, dict):
            issues.append(f"{label} must be an object")
            continue
        missing = [key for key in ("sample_id", "run_id", "phase", "identity", "metrics", "source_log", "source_log_sha256") if key not in row]
        if missing:
            issues.append(f"{label} missing fields: {', '.join(missing)}")
            continue
        sample_id, run_id = row["sample_id"], row["run_id"]
        if not isinstance(sample_id, str) or not sample_id.strip():
            issues.append(f"{label}.sample_id must be nonempty text")
        elif sample_id in ids:
            issues.append(f"duplicate sample_id {sample_id!r}")
        else:
            ids.add(sample_id)
        if not isinstance(run_id, str) or not run_id.strip():
            issues.append(f"{label}.run_id must be nonempty text")
        elif run_id in run_ids:
            issues.append(f"duplicate run_id {run_id!r}")
        else:
            run_ids.add(run_id)
        if row["phase"] not in ("cold", "warm"):
            issues.append(f"{label}.phase must be cold or warm")
        identity = row["identity"]
        if not isinstance(identity, dict):
            issues.append(f"{label}.identity must be an object")
        else:
            missing_identity = [key for key in IDENTITY_FIELDS if key not in identity]
            if missing_identity:
                issues.append(f"{label}.identity missing fields: {', '.join(missing_identity)}")
            for key in ("map", "build_id"):
                if not isinstance(identity.get(key), str) or not identity[key].strip():
                    issues.append(f"{label}.identity.{key} must be nonempty text")
            for key in ("binary_sha256", "content_sha256", "settings_sha256", "input_sha256"):
                if not _digest(identity.get(key)):
                    issues.append(f"{label}.identity.{key} must be lowercase SHA-256")
            if not isinstance(identity.get("launch_args"), list) or any(not isinstance(arg, str) for arg in identity.get("launch_args", [])):
                issues.append(f"{label}.identity.launch_args must be an ordered string array")
            resolution = identity.get("resolution")
            if (not isinstance(resolution, dict) or type(resolution.get("width")) is not int
                    or type(resolution.get("height")) is not int or resolution["width"] <= 0 or resolution["height"] <= 0):
                issues.append(f"{label}.identity.resolution requires positive integer width and height")
            hardware = identity.get("hardware")
            if not isinstance(hardware, dict) or any(
                    not isinstance(hardware.get(key), str) or not hardware[key].strip()
                    for key in ("gpu", "gpu_driver", "cpu", "session")):
                issues.append(f"{label}.identity.hardware requires gpu, gpu_driver, cpu, and session text")
            if not isinstance(identity.get("cvars"), dict):
                issues.append(f"{label}.identity.cvars must be a captured object")
            if baseline_identity is None:
                baseline_identity = identity
            elif any(identity.get(key) != baseline_identity.get(key) for key in IDENTITY_FIELDS):
                issues.append(f"{label} identity differs from the other samples; split captures by identity")

        metrics = row["metrics"]
        if not isinstance(metrics, dict):
            issues.append(f"{label}.metrics must be an object")
            metrics = {}
        for name in required_metrics:
            metric = metrics.get(name)
            if not isinstance(metric, dict) or "value" not in metric or not isinstance(metric.get("unit"), str) or not metric["unit"].strip() or not isinstance(metric.get("scope"), str) or not metric["scope"].strip():
                issues.append(f"{label}.metrics.{name} requires finite value, unit, and scope")
                continue
            value = metric["value"]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                issues.append(f"{label}.metrics.{name}.value must be finite and nonnegative")
        if set(metrics) != set(required_metrics):
            issues.append(f"{label}.metrics must contain exactly the declared required_metrics")

        source = row["source_log"]
        if not isinstance(source, str) or not source.strip():
            issues.append(f"{label}.source_log must be nonempty text")
        elif not _digest(row["source_log_sha256"]):
            issues.append(f"{label}.source_log_sha256 must be lowercase SHA-256")
        else:
            cited = Path(source)
            path = cited if cited.is_absolute() else receipt_path.parent / cited
            resolved_root = receipt_path.parent.resolve()
            try:
                resolved = path.resolve(strict=True)
                if not resolved.is_relative_to(resolved_root):
                    issues.append(f"{label}.source_log escapes the receipt directory")
                elif not resolved.is_file():
                    issues.append(f"{label}.source_log is not a file")
                elif hashlib.sha256(resolved.read_bytes()).hexdigest() != row["source_log_sha256"]:
                    issues.append(f"{label}.source_log_sha256 mismatch")
            except OSError as exc:
                issues.append(f"{label}.source_log cannot be read: {exc}")
        valid.append(row)

    phases = {row.get("phase") for row in valid}
    if "cold" not in phases:
        issues.append("missing cold samples")
    if "warm" not in phases:
        issues.append("missing warm samples")
    summaries: dict[str, Any] = {}
    if required_metrics:
        for phase in ("cold", "warm"):
            phase_rows = [row for row in valid if row.get("phase") == phase]
            per_metric: dict[str, Any] = {}
            for name in required_metrics:
                groups: dict[tuple[str, str], list[float]] = {}
                for row in phase_rows:
                    metric = row.get("metrics", {}).get(name)
                    if isinstance(metric, dict) and isinstance(metric.get("value"), (int, float)) and not isinstance(metric.get("value"), bool) and math.isfinite(metric["value"]) and metric["value"] >= 0:
                        groups.setdefault((str(metric.get("scope")), str(metric.get("unit"))), []).append(float(metric["value"]))
                per_metric[name] = [
                    {"scope": scope, "unit": unit, "sample_count": len(values), **{
                        f"p{p}": nearest_rank(values, p) for p in (50, 95, 99)
                    }} for (scope, unit), values in sorted(groups.items()) if values
                ]
            summaries[phase] = per_metric
    return {
        "schema": REPORT_SCHEMA,
        "status": "INCONCLUSIVE" if issues else "PASS",
        "method": "nearest-rank by phase, metric scope, and unit; sorted[ceil(p*n)-1]",
        "source_receipt": str(receipt_path),
        "issues": issues,
        "metrics": summaries,
        "samples": valid,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="captured packaged metrics receipt JSON")
    parser.add_argument("--report-json", type=Path, help="optional report path outside the evidence receipt/logs")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.receipt.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"INCONCLUSIVE: cannot read receipt: {exc}", file=sys.stderr)
        return 2
    report_path = args.report_json.resolve() if args.report_json else None
    evidence_paths = {args.receipt.resolve()}
    if isinstance(data, dict) and isinstance(data.get("samples"), list):
        for row in data["samples"]:
            if isinstance(row, dict) and isinstance(row.get("source_log"), str):
                cited = Path(row["source_log"])
                evidence_paths.add((cited if cited.is_absolute() else args.receipt.parent / cited).resolve())
    if report_path is not None:
        try:
            aliases_evidence = report_path in evidence_paths or any(
                args.report_json.exists() and evidence.exists() and args.report_json.samefile(evidence)
                for evidence in evidence_paths
            )
        except OSError as exc:
            print(f"INCONCLUSIVE: cannot safely compare report/evidence paths: {exc}", file=sys.stderr)
            return 2
        if aliases_evidence:
            print("INCONCLUSIVE: report destination aliases an evidence input", file=sys.stderr)
            return 2
    report = summarize(data, args.receipt)
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.report_json:
        atomic_write_text(args.report_json, encoded)
    print(encoded.rstrip())
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
