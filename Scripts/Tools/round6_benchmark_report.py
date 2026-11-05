#!/usr/bin/env python3
"""Validate and summarize Round 6 receipts; never edits benchmark evidence."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


SCHEMA = "onebossfight.round6-benchmark/v1"
METRICS = ("avg_fps", "p99_ms", "gpu_avg_ms", "gpu_p99_ms")
PHASE_MODES = {"phase1": ("Quality", "Balanced", "Performance"),
               "phase2": ("best",)}
MODE_WITNESSES = {"Quality": "NGXPerfQuality=MaxQuality", "Balanced": "NGXPerfQuality=Balanced",
                  "Performance": "NGXPerfQuality=MaxPerf"}


def validate(receipt: Any) -> list[str]:
    issues: list[str] = []
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
        return [f"schema must be {SCHEMA}"]
    phase = receipt.get("phase")
    if phase not in PHASE_MODES:
        return ["phase must be phase1 or phase2"]
    runs = receipt.get("runs")
    if not isinstance(runs, list):
        return ["runs must be an array"]
    if len(runs) != (13 if phase == "phase1" else 16):
        issues.append(f"{phase} requires {13 if phase == 'phase1' else 16} rows")
    ids: set[str] = set()
    anchors = []
    treatments: dict[str, list[dict[str, Any]]] = {}
    for i, row in enumerate(runs):
        prefix = f"runs[{i}]"
        if not isinstance(row, dict):
            issues.append(f"{prefix} must be an object")
            continue
        run_id = row.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            issues.append(f"{prefix}.run_id is required")
        elif run_id in ids:
            issues.append(f"duplicate run_id {run_id}")
        else:
            ids.add(run_id)
        if row.get("kind") not in ("baseline", "treatment"):
            issues.append(f"{prefix}.kind must be baseline or treatment")
        if row.get("kind") == "baseline":
            anchors.append(row)
            if row.get("temporal_upscaler") != "TSR":
                issues.append(f"{prefix} baseline temporal_upscaler must be TSR")
        else:
            mode = row.get("mode")
            if phase == "phase1" and mode not in PHASE_MODES[phase]:
                issues.append(f"{prefix}.mode is not a Phase 1 DLSS mode")
            if phase == "phase2" and mode != "best":
                issues.append(f"{prefix}.mode must be best in Phase 2")
            treatments.setdefault(str(mode), []).append(row)
            if row.get("temporal_upscaler") != "DLSS":
                issues.append(f"{prefix} treatment temporal_upscaler must be DLSS")
            if not isinstance(row.get("active_mode_log_line"), str) or "Creating NGX DLSS Feature" not in row["active_mode_log_line"]:
                issues.append(f"{prefix}.active_mode_log_line must prove active DLSS")
            expected_witness = MODE_WITNESSES.get(str(mode))
            if expected_witness and expected_witness not in row["active_mode_log_line"]:
                issues.append(f"{prefix}.active_mode_log_line does not witness {mode}")
        for field in METRICS:
            value = row.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                issues.append(f"{prefix}.{field} must be positive numeric")
        if not isinstance(row.get("effective_primary_screen_percentage"), (int, float)):
            issues.append(f"{prefix}.effective_primary_screen_percentage is required")
        if not isinstance(row.get("anti_aliasing_method"), (int, str)):
            issues.append(f"{prefix}.anti_aliasing_method is required")
        if not isinstance(row.get("cvars"), dict):
            issues.append(f"{prefix}.cvars must be an object")
        if not isinstance(row.get("predicted_gpu_saving_ms"), (int, float)):
            issues.append(f"{prefix}.predicted_gpu_saving_ms is required")
    if len(anchors) != 4:
        issues.append("exactly four TSR anchors are required")
    expected_modes = PHASE_MODES[phase]
    for mode in expected_modes:
        if len(treatments.get(mode, [])) != 3:
            issues.append(f"{mode} requires exactly three treatments")
    return issues


def summarize(receipt: dict[str, Any]) -> dict[str, Any]:
    issues = validate(receipt)
    if issues:
        raise ValueError("; ".join(issues))
    anchors = [r for r in receipt["runs"] if r["kind"] == "baseline"]
    baseline = {m: statistics.median(r[m] for r in anchors) for m in METRICS}
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in receipt["runs"]:
        if row["kind"] == "treatment":
            groups.setdefault(row["mode"], []).append(row)
    rows = []
    for mode, runs in groups.items():
        median = {m: statistics.median(r[m] for r in runs) for m in METRICS}
        predicted = statistics.median(float(r["predicted_gpu_saving_ms"]) for r in runs)
        measured = baseline["gpu_avg_ms"] - median["gpu_avg_ms"]
        rows.append({"mode": mode, "trials": len(runs), **median,
                     "active_upscaler_proof": all(r["temporal_upscaler"] == "DLSS" and r["active_mode_log_line"] for r in runs),
                     "delta_vs_tsr_percent": {m: round((median[m] - baseline[m]) / baseline[m] * 100, 2) for m in METRICS},
                     "predicted_gpu_saving_ms": predicted,
                     "measured_gpu_saving_ms": round(measured, 3),
                     "prediction_error_ms": round(measured - predicted, 3),
                     "image_quality_notes": [r.get("image_quality_note", "") for r in runs]})
    return {"schema": SCHEMA, "phase": receipt["phase"], "baseline_median": baseline, "modes": rows}


def render(summary: dict[str, Any]) -> str:
    lines = [f"Round 6 {summary['phase']} — medians; deltas vs four-anchor TSR median",
             "| Mode | Trials | Avg FPS | p99 ms | GPU avg ms | GPU p99 ms | Active DLSS proof | Δ avg FPS | Δ p99 | Pred. GPU ms saved | Measured GPU ms saved | Error ms |",
             "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|"]
    for r in summary["modes"]:
        d = r["delta_vs_tsr_percent"]
        lines.append(f"| {r['mode']} | {r['trials']} | {r['avg_fps']:.1f} | {r['p99_ms']:.2f} | {r['gpu_avg_ms']:.2f} | {r['gpu_p99_ms']:.2f} | {'yes' if r['active_upscaler_proof'] else 'no'} | {d['avg_fps']:+.2f}% | {d['p99_ms']:+.2f}% | {r['predicted_gpu_saving_ms']:.2f} | {r['measured_gpu_saving_ms']:+.2f} | {r['prediction_error_ms']:+.2f} |")
    for r in summary["modes"]:
        for i, note in enumerate(r["image_quality_notes"], 1):
            if note:
                lines.append(f"- {r['mode']} trial {i} image-quality note: {note}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--json", action="store_true", help="print summary as JSON")
    args = parser.parse_args()
    value = json.loads(args.receipt.read_text(encoding="utf-8"))
    issues = validate(value)
    if issues:
        print("INVALID: " + "; ".join(issues))
        return 2
    summary = summarize(value)
    print(json.dumps(summary, indent=2) if args.json else render(summary), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
