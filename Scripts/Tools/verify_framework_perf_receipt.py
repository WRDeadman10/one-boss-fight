#!/usr/bin/env python3
"""Validate explicit framework CPU scope receipts without treating frame GPU as boss-attributed."""
import argparse
import json
import math
from pathlib import Path


def validate(data):
    issues = []
    required = ("receipt_version", "run_id", "build_id", "engine_version", "map", "device_class",
                "sample_window", "cpu_scopes", "gpu_frame_global_ms", "gpu_component_attributed")
    for key in required:
        if key not in data:
            issues.append(f"missing {key}")
    if issues:
        return issues
    allowed = set(required) | {"device_label", "notes"}
    for key in sorted(set(data) - allowed):
        issues.append(f"unknown property {key}")
    if data["receipt_version"] != 1:
        issues.append("receipt_version must equal 1")
    for key in ("run_id", "build_id", "engine_version", "map"):
        if not isinstance(data[key], str) or not data[key].strip():
            issues.append(f"{key} must be a non-empty string")
    if data["device_class"] not in {"target_rtx_2060_super", "proxy", "unknown"}:
        issues.append("device_class must distinguish target, proxy, or unknown")
    window = data["sample_window"]
    if not isinstance(window, dict) or not isinstance(window.get("start_seconds"), (int, float)) or isinstance(window.get("start_seconds"), bool) or not isinstance(window.get("end_seconds"), (int, float)) or isinstance(window.get("end_seconds"), bool):
        issues.append("sample_window requires numeric start_seconds and end_seconds")
    else:
        for key in sorted(set(window) - {"start_seconds", "end_seconds"}):
            issues.append(f"sample_window unknown property {key}")
        if not math.isfinite(window["start_seconds"]) or not math.isfinite(window["end_seconds"]) or window["start_seconds"] < 0 or window["end_seconds"] <= window["start_seconds"]:
            issues.append("sample_window end must be greater than a non-negative start")
    if "device_label" in data and not isinstance(data["device_label"], str):
        issues.append("device_label must be a string")
    if "notes" in data and not isinstance(data["notes"], str):
        issues.append("notes must be a string")
    scopes = data["cpu_scopes"]
    if not isinstance(scopes, list):
        issues.append("cpu_scopes must be a list")
    else:
        for i, scope in enumerate(scopes):
            prefix = f"cpu_scopes[{i}]"
            if not isinstance(scope, dict):
                issues.append(f"{prefix} must be an object")
                continue
            scope_allowed = {"category", "unit", "samples", "total", "maximum"}
            for key in sorted(set(scope) - scope_allowed):
                issues.append(f"{prefix} unknown property {key}")
            if not isinstance(scope.get("category"), str) or not scope["category"].strip():
                issues.append(f"{prefix}.category is required")
            if scope.get("unit") != "ms":
                issues.append(f"{prefix}.unit must be ms")
            samples, total, maximum = scope.get("samples"), scope.get("total"), scope.get("maximum")
            if not isinstance(samples, int) or isinstance(samples, bool) or samples < 0:
                issues.append(f"{prefix}.samples must be a non-negative integer")
            if not isinstance(total, (int, float)) or isinstance(total, bool) or not math.isfinite(total) or total < 0:
                issues.append(f"{prefix}.total must be non-negative milliseconds")
            if not isinstance(maximum, (int, float)) or isinstance(maximum, bool) or not math.isfinite(maximum) or maximum < 0:
                issues.append(f"{prefix}.maximum must be non-negative milliseconds")
            if isinstance(samples, int) and isinstance(total, (int, float)) and samples == 0 and total != 0:
                issues.append(f"{prefix} zero samples require zero total")
            if isinstance(total, (int, float)) and isinstance(maximum, (int, float)) and maximum > total:
                issues.append(f"{prefix}.maximum cannot exceed total")
    gpu = data["gpu_frame_global_ms"]
    if gpu is not None and (not isinstance(gpu, (int, float)) or isinstance(gpu, bool) or not math.isfinite(gpu) or gpu < 0):
        issues.append("gpu_frame_global_ms must be null or a non-negative frame-global value")
    if data["gpu_component_attributed"] is not False:
        issues.append("GPU frame totals cannot be represented as component-attributed")
    if "gpu_component_ms" in data:
        issues.append("gpu_component_ms is forbidden; component GPU attribution is unavailable")
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.receipt.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL receipt: {exc}")
        return 2
    issues = validate(data) if isinstance(data, dict) else ["receipt root must be an object"]
    if issues:
        for issue in issues:
            print(f"FAIL {issue}")
        return 1
    print(f"PASS run={data['run_id']} device_class={data['device_class']} gpu_component_attributed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
