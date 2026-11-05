#!/usr/bin/env python3
"""Inventory and summarize supplied Round 4 benchmark evidence, without editing it."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


SCHEMA = "onebossfight.round4-benchmark/v1"
LABELS = (
    "r4_legacy_warmup", "r4_legacy_a", "r4_legacy_b", "r4_legacy_c",
    "r4_selected_warmup", "r4_selected_a", "r4_selected_b", "r4_selected_c",
)
REPLICATES = {"legacy": {"a", "b", "c"}, "selected": {"a", "b", "c"}}
IDENTITY_FIELDS = (
    "build_id", "build_sha256", "build_configuration", "engine_version", "gpu", "gpu_driver",
    "session_type", "resolution_x", "resolution_y", "map", "fight_mode",
    "warmup_seconds", "duration_seconds",
)
ROOT_FIELDS = ("owner", "capture_date", "gpu", "gpu_driver", "session_type", "gpu_utilization_before_pct", "kit_version")
RUN_FIELDS = (*IDENTITY_FIELDS, "route", "replicate", "fight_started", "avg_fps", "p99_ms",
              "summary_path", "summary_sha256", "frames_path", "frames_sha256")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path, expected: Any = None) -> dict[str, Any]:
    root = root.resolve()
    results: list[dict[str, Any]] = []
    missing_labels: list[str] = []
    issues: list[str] = []
    for label in LABELS:
        candidates = [path for path in root.rglob("*") if path.is_dir()] if root.is_dir() else []
        primary_dirs = sorted(path for path in candidates
                              if path.name.startswith(label + "_") and not path.name.startswith(label + "_retry_"))
        retry_dirs = sorted(path for path in candidates if path.name.startswith(label + "_retry_"))
        if not primary_dirs:
            missing_labels.append(label)
            issues.append(f"missing run directory for {label}")
        dirs = primary_dirs + retry_dirs
        for run_dir in dirs:
            files = []
            for name in ("summary.json", "frames.csv"):
                path = run_dir / name
                if not path.is_file():
                    issues.append(f"{run_dir}: missing {name}")
                    continue
                entry = {"file": str(path.relative_to(root)).replace("\\", "/"),
                         "bytes": path.stat().st_size, "sha256": sha256(path)}
                if name == "summary.json":
                    try:
                        summary = json.loads(path.read_text(encoding="utf-8"))
                        if not isinstance(summary, dict):
                            raise ValueError("root is not an object")
                        entry["label"] = summary.get("label")
                        if summary.get("label") not in (label, label + "_retry"):
                            issues.append(f"{path}: summary label {summary.get('label')!r} does not match {label}")
                    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
                        issues.append(f"{path}: invalid summary JSON: {error}")
                files.append(entry)
            results.append({"expected_label": label, "run_directory": str(run_dir.relative_to(root)).replace("\\", "/"),
                            "files": files})
    if expected is not None:
        if not isinstance(expected, dict) or not isinstance(expected.get("runs"), list):
            issues.append("expected inventory must be a JSON object with a runs array")
        else:
            old_files = {item.get("file"): item for row in expected["runs"] if isinstance(row, dict)
                         for item in row.get("files", []) if isinstance(item, dict) and isinstance(item.get("file"), str)}
            current_files = {item.get("file"): item for row in results for item in row["files"]}
            for name, prior in old_files.items():
                current = current_files.get(name)
                if current is None:
                    issues.append(f"expected artifact is now missing: {name}")
                elif current.get("sha256") != prior.get("sha256") or current.get("bytes") != prior.get("bytes"):
                    issues.append(f"artifact changed since expected inventory: {name}")
    return {"schema": "onebossfight.round4-inventory/v1", "root": str(root),
            "expected_labels": len(LABELS), "run_directories_found": len(results),
            "missing_labels": missing_labels, "files_hashed": sum(len(row["files"]) for row in results),
            "runs": results, "issues": issues}


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_receipt(receipt: Any) -> list[str]:
    if not isinstance(receipt, dict):
        return ["receipt root must be an object"]
    issues: list[str] = []
    if receipt.get("schema") != SCHEMA:
        issues.append(f"schema must be {SCHEMA}")
    for key in ROOT_FIELDS:
        if key not in receipt:
            issues.append(f"receipt missing {key}")
    for key in ("owner", "gpu", "gpu_driver", "session_type", "kit_version"):
        if key in receipt and (not isinstance(receipt[key], str) or not receipt[key].strip()):
            issues.append(f"receipt {key} must be a nonempty string")
    if isinstance(receipt.get("capture_date"), str):
        try:
            from datetime import date
            date.fromisoformat(receipt["capture_date"])
        except ValueError:
            issues.append("receipt capture_date must use YYYY-MM-DD")
    elif "capture_date" in receipt:
        issues.append("receipt capture_date must be a YYYY-MM-DD string")
    utilization = receipt.get("gpu_utilization_before_pct")
    if utilization is not None and (not _finite_number(utilization) or not 0 <= utilization <= 100):
        issues.append("receipt gpu_utilization_before_pct must be null or between 0 and 100")
    runs = receipt.get("runs")
    if not isinstance(runs, list) or len(runs) != 6:
        return issues + ["runs must contain exactly six measured rows (legacy and selected a/b/c)"]
    seen: set[tuple[str, str]] = set()
    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            issues.append(f"runs[{index}] must be an object")
            continue
        for key in RUN_FIELDS:
            if key not in run:
                issues.append(f"runs[{index}] missing {key}")
        route, replicate = run.get("route"), run.get("replicate")
        if not isinstance(route, str) or route not in REPLICATES or not isinstance(replicate, str) or replicate not in {"a", "b", "c"}:
            issues.append(f"runs[{index}] has invalid route/replicate")
        elif (route, replicate) in seen:
            issues.append(f"duplicate measured row {route}/{replicate}")
        else:
            seen.add((route, replicate))
        for key in ("build_sha256", "summary_sha256", "frames_sha256"):
            value = run.get(key)
            if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                issues.append(f"runs[{index}] {key} must be 64 lowercase hexadecimal characters")
        for key in ("build_id", "build_configuration", "engine_version", "gpu", "gpu_driver",
                    "session_type", "map", "summary_path", "frames_path"):
            if key in run and (not isinstance(run[key], str) or not run[key].strip()):
                issues.append(f"runs[{index}] {key} must be a nonempty string")
        for key in ("resolution_x", "resolution_y", "warmup_seconds", "duration_seconds"):
            if key in run and (not _finite_number(run[key]) or run[key] <= 0):
                issues.append(f"runs[{index}] {key} must be a positive finite number")
        for key in ("avg_fps", "p99_ms"):
            if key in run and run[key] is not None and (not _finite_number(run[key]) or run[key] < 0):
                issues.append(f"runs[{index}] {key} must be null or a nonnegative finite number")
        if "fight_started" in run and not isinstance(run["fight_started"], bool):
            issues.append(f"runs[{index}] fight_started must be boolean")
        if "fight_mode" in run and not isinstance(run["fight_mode"], bool):
            issues.append(f"runs[{index}] fight_mode must be boolean")
    expected = {(route, rep) for route, reps in REPLICATES.items() for rep in reps}
    if seen != expected:
        issues.append("measured rows must contain each legacy/selected a, b, and c exactly once")
    return issues


def compare_runs(receipt: Any) -> dict[str, Any]:
    issues = validate_receipt(receipt)
    if issues:
        return {"comparable": False, "issues": issues, "identity_differences": {}}
    runs = receipt["runs"]
    differences: dict[str, list[dict[str, Any]]] = {}
    for field in IDENTITY_FIELDS:
        values = [(f"{run['route']}/{run['replicate']}", run[field]) for run in runs]
        distinct = {json.dumps(value, sort_keys=True, ensure_ascii=False) for _, value in values}
        if len(distinct) > 1:
            differences[field] = [{"run": name, "value": value} for name, value in values]
    for run in runs:
        key = f"{run['route']}/{run['replicate']}"
        if run["gpu"] != receipt.get("gpu"):
            differences.setdefault("gpu_header", []).append({"run": key, "value": run["gpu"]})
        if run["gpu_driver"] != receipt.get("gpu_driver"):
            differences.setdefault("gpu_driver_header", []).append({"run": key, "value": run["gpu_driver"]})
        if run["session_type"] != receipt.get("session_type"):
            differences.setdefault("session_type_header", []).append({"run": key, "value": run["session_type"]})
    return {"comparable": not differences, "issues": [], "identity_differences": differences}


def _mean(rows: list[dict[str, Any]], field: str) -> float | None:
    values = [row.get(field) for row in rows]
    if len(values) != 3 or not all(_finite_number(value) for value in values):
        return None
    return sum(values) / 3


def render_report(receipt: Any) -> str:
    validation = validate_receipt(receipt)
    comparison = compare_runs(receipt)
    if validation:
        return "# Round 4 benchmark report\n\nReceipt invalid; measurements are UNKNOWN.\n\n- " + "\n- ".join(validation) + "\n"
    rows = receipt["runs"]
    aggregates = {}
    for route in ("legacy", "selected"):
        subset = [row for row in rows if row["route"] == route]
        aggregates[route] = {"avg_fps": _mean(subset, "avg_fps"), "p99_ms": _mean(subset, "p99_ms")}
    comparable = comparison["comparable"]

    def metric(value: float | None, threshold: float, op: str) -> str:
        if value is None:
            return "UNKNOWN"
        return "PASS" if (value >= threshold if op == ">=" else value <= threshold) else "FAIL"

    selected_avg = aggregates["selected"]["avg_fps"]
    selected_p99 = aggregates["selected"]["p99_ms"]
    legacy_p99 = aggregates["legacy"]["p99_ms"]
    p99_delta = selected_p99 - legacy_p99 if selected_p99 is not None and legacy_p99 is not None and comparable else None
    fight_ok = all(row.get("fight_started") is True for row in rows)
    gpu_ok = all(row.get("gpu") == receipt.get("gpu") for row in rows)
    lines = ["# Round 4 benchmark report", "", f"- Comparable setup: {'PASS' if comparable else 'FAIL'}",
             f"- GPU identity matches receipt header: {'PASS' if gpu_ok else 'FAIL'}",
             f"- Fight started in all six measured runs: {'PASS' if fight_ok else 'FAIL'}", "",
             "| Route | Mean of 3 run avg_fps | Mean of 3 run p99_ms |",
             "|---|---:|---:|"]
    for route in ("legacy", "selected"):
        agg = aggregates[route]
        afps = f"{agg['avg_fps']:.2f}" if agg["avg_fps"] is not None else "UNKNOWN"
        p99 = f"{agg['p99_ms']:.2f}" if agg["p99_ms"] is not None else "UNKNOWN"
        lines.append(f"| {route} | {afps} | {p99} |")
    lines.extend(["", "## Selected-route gates", "",
                  f"- Average >= 60 FPS: {metric(selected_avg, 60, '>=')}",
                  f"- p99 <= 16.67 ms: {metric(selected_p99, 16.67, '<=')}",
                  f"- Selected p99 <= legacy p99 + 0.5 ms: " + ("UNKNOWN" if p99_delta is None else ("PASS" if p99_delta <= 0.5 else "FAIL")),
                  "", "## Measured run rows", "", "| Route / run | Avg FPS | p99 ms | Fight started | GPU |",
                  "|---|---:|---:|---|---|"])
    for row in sorted(rows, key=lambda value: (value["route"], value["replicate"])):
        afps = f"{row['avg_fps']:.2f}" if _finite_number(row.get("avg_fps")) else "UNKNOWN"
        p99 = f"{row['p99_ms']:.2f}" if _finite_number(row.get("p99_ms")) else "UNKNOWN"
        lines.append(f"| {row['route']} / {row['replicate']} | {afps} | {p99} | {row['fight_started']} | {row['gpu']} |")
    if comparison["identity_differences"]:
        lines.extend(["", "Identity differences:"])
        lines.extend(f"- {field}" for field in sorted(comparison["identity_differences"]))
    return "\n".join(lines) + "\n"


ROUND5_SCHEMA = "onebossfight.round5-benchmark/v1"
ROUND5_METRICS = ("avg_fps", "p99_ms", "gpu_avg_ms", "gpu_p99_ms")
ROUND5_IDENTITY_FIELDS = ("build_id", "build_sha256", "build_configuration", "engine_version", "gpu", "gpu_driver",
                          "session_type", "resolution_x", "resolution_y", "map", "fight_mode", "route")
ROUND5_MODE_TOKENS = {"DLAA": "DLAA", "Quality": "MaxQuality", "Balanced": "Balanced", "Performance": "MaxPerf"}


def validate_experiment_receipt(receipt: Any) -> list[str]:
    """Validate Round 5 runs, active DLSS mode evidence, and comparison inputs."""
    if not isinstance(receipt, dict):
        return ["receipt root must be an object"]
    issues: list[str] = []
    if receipt.get("schema") != ROUND5_SCHEMA:
        issues.append(f"schema must be {ROUND5_SCHEMA}")
    runs = receipt.get("runs")
    if not isinstance(runs, list) or len(runs) < 2:
        return issues + ["runs must contain at least two baseline/treatment rows"]
    tolerance = receipt.get("baseline_metric_tolerance_percent", 5)
    if not _finite_number(tolerance) or tolerance <= 0:
        issues.append("baseline_metric_tolerance_percent must be a positive finite number")
    seen: set[str] = set()
    baselines: dict[int, dict[str, Any]] = {}
    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            issues.append(f"runs[{index}] must be an object")
            continue
        for key in ("run_id", "kind", "baseline_group", "mode", "cvars", *ROUND5_METRICS,
                    *ROUND5_IDENTITY_FIELDS, "summary_path", "summary_sha256", "active_mode_log_token",
                    "active_mode_log_line", "image_quality_note"):
            if key not in run:
                issues.append(f"runs[{index}] missing {key}")
        run_id = run.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            issues.append(f"runs[{index}] run_id must be a nonempty string")
        elif run_id in seen:
            issues.append(f"duplicate run_id {run_id}")
        else:
            seen.add(run_id)
        kind, group, cvars = run.get("kind"), run.get("baseline_group"), run.get("cvars")
        if kind not in {"baseline", "treatment"}:
            issues.append(f"runs[{index}] kind must be baseline or treatment")
        if not isinstance(group, int) or isinstance(group, bool) or group < 0:
            issues.append(f"runs[{index}] baseline_group must be a nonnegative integer")
        if not isinstance(cvars, dict) or not all(isinstance(key, str) and key for key in cvars):
            issues.append(f"runs[{index}] cvars must be an object with nonempty string keys")
        elif kind == "baseline" and cvars:
            issues.append(f"runs[{index}] baseline must not set CVars")
        elif kind == "treatment" and not 2 <= len(cvars) <= 3:
            issues.append(f"runs[{index}] treatment must set the DLSS enable and screen percentage, with optional one shadow CVar")
        mode = run.get("mode")
        if not isinstance(mode, str) or not mode.strip():
            issues.append(f"runs[{index}] mode must be a nonempty string")
        elif kind == "baseline" and mode != "TSR":
            issues.append(f"runs[{index}] baseline mode must be TSR")
        elif kind == "treatment":
            base_mode = mode.split("+", 1)[0].strip()
            expected_token = ROUND5_MODE_TOKENS.get(base_mode)
            if not {"r.NGX.DLSS.Enable", "r.ScreenPercentage"}.issubset(cvars):
                issues.append(f"runs[{index}] treatment cvars must include r.NGX.DLSS.Enable and r.ScreenPercentage")
            if cvars.get("r.NGX.DLSS.Enable") not in (1, "1", True):
                issues.append(f"runs[{index}] r.NGX.DLSS.Enable must be 1")
            if "rpg.Perf.FireShadows" in cvars and cvars["rpg.Perf.FireShadows"] not in (0, "0", 0.0):
                issues.append(f"runs[{index}] rpg.Perf.FireShadows must be 0 when present")
            if any(key not in {"r.NGX.DLSS.Enable", "r.ScreenPercentage", "rpg.Perf.FireShadows"} for key in cvars):
                issues.append(f"runs[{index}] treatment contains an unsupported Round 5 CVar")
            token = run.get("active_mode_log_token")
            line = run.get("active_mode_log_line")
            if expected_token is None:
                issues.append(f"runs[{index}] unsupported DLSS mode {mode!r}")
            elif token != expected_token:
                issues.append(f"runs[{index}] active mode token must be {expected_token!r} for {mode}")
            if not isinstance(line, str) or "Creating" not in line or "NGXPerfQuality=" not in line or "DenoiseMode=Off" not in line:
                issues.append(f"runs[{index}] active_mode_log_line must prove an active SR feature with DenoiseMode=Off")
            elif expected_token and f"NGXPerfQuality={expected_token}" not in line:
                issues.append(f"runs[{index}] active mode log line does not match {expected_token}")
        elif kind == "baseline" and run.get("active_mode_log_token") != "TSR":
            issues.append(f"runs[{index}] baseline active_mode_log_token must be TSR")
        if not isinstance(run.get("active_mode_log_token"), str) or not run["active_mode_log_token"].strip():
            issues.append(f"runs[{index}] active_mode_log_token must be nonempty text")
        if not isinstance(run.get("active_mode_log_line"), str):
            issues.append(f"runs[{index}] active_mode_log_line must be text")
        if not isinstance(run.get("image_quality_note"), str):
            issues.append(f"runs[{index}] image_quality_note must be text (use UNKNOWN if not captured)")
        if kind == "baseline" and isinstance(group, int) and not isinstance(group, bool):
            if group in baselines:
                issues.append(f"duplicate baseline for group {group}")
            else:
                baselines[group] = run
        for metric in ROUND5_METRICS:
            value = run.get(metric)
            if not _finite_number(value) or value <= 0:
                issues.append(f"runs[{index}] {metric} must be a positive finite number")
        for identity in ("build_id", "build_configuration", "engine_version", "gpu", "gpu_driver", "session_type", "map", "route"):
            value = run.get(identity)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"runs[{index}] {identity} must be a nonempty string")
        for identity in ("resolution_x", "resolution_y"):
            value = run.get(identity)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                issues.append(f"runs[{index}] {identity} must be a positive integer")
        if "fight_mode" in run and not isinstance(run["fight_mode"], bool):
            issues.append(f"runs[{index}] fight_mode must be boolean")
        value = run.get("build_sha256")
        if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            issues.append(f"runs[{index}] build_sha256 must be 64 lowercase hexadecimal characters")
        path, digest = run.get("summary_path"), run.get("summary_sha256")
        if not isinstance(path, str) or not path.strip():
            issues.append(f"runs[{index}] summary_path must be a nonempty string")
        if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            issues.append(f"runs[{index}] summary_sha256 must be 64 lowercase hexadecimal characters")
    if 0 not in baselines:
        issues.append("baseline group 0 (drift anchor) is required")
    for index, run in enumerate(runs):
        if isinstance(run, dict) and run.get("kind") == "treatment":
            group = run.get("baseline_group")
            if isinstance(group, int) and not isinstance(group, bool) and group not in baselines:
                issues.append(f"runs[{index}] has no baseline for group {group}")
    return issues


def analyze_experiments(receipt: Any) -> dict[str, Any]:
    issues = validate_experiment_receipt(receipt)
    if issues:
        return {"valid": False, "stable": False, "comparable": False, "identity_differences": {},
                "issues": issues, "baseline_drift": [], "comparisons": []}
    runs = receipt["runs"]
    baselines = {row["baseline_group"]: row for row in runs if row["kind"] == "baseline"}
    anchor = baselines[0]
    tolerance = receipt.get("baseline_metric_tolerance_percent", 5)
    drift: list[dict[str, Any]] = []
    for group, baseline in sorted(baselines.items()):
        for metric in ROUND5_METRICS:
            reference = anchor[metric]
            observed = baseline[metric]
            delta = abs(observed - reference) / reference * 100
            if group and delta > tolerance:
                drift.append({"group": group, "metric": metric, "anchor": reference,
                              "observed": observed, "delta_percent": delta, "tolerance_percent": tolerance})
    stable = not drift
    identity_differences: dict[str, list[dict[str, Any]]] = {}
    for field in ROUND5_IDENTITY_FIELDS:
        values = [(run["run_id"], run[field]) for run in runs]
        if len({json.dumps(value, sort_keys=True, ensure_ascii=False) for _, value in values}) > 1:
            identity_differences[field] = [{"run": name, "value": value} for name, value in values]
    comparable = stable and not identity_differences
    comparisons = []
    by_mode: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        if run["kind"] != "treatment":
            continue
        by_mode.setdefault(run["mode"], []).append(run)
        baseline = baselines[run["baseline_group"]]
        comparison = {"run_id": run["run_id"], "baseline_group": run["baseline_group"],
                      "mode": run["mode"], "cvars": run["cvars"], "active_mode_log_token": run["active_mode_log_token"],
                      "image_quality_note": run["image_quality_note"], "usable": comparable}
        for metric in ROUND5_METRICS:
            comparison[metric] = run[metric]
            comparison[f"{metric}_delta_percent"] = ((run[metric] - baseline[metric]) / baseline[metric] * 100) if comparable else None
        comparisons.append(comparison)
    mode_summaries = []
    baseline_means = {
        metric: (sum(row[metric] for row in baselines.values()) / len(baselines))
        if len(baselines) >= 3 else None
        for metric in ROUND5_METRICS
    }
    for mode, mode_runs in sorted(by_mode.items()):
        summary: dict[str, Any] = {"mode": mode, "run_count": len(mode_runs),
                                   "image_quality_notes": [row["image_quality_note"] for row in mode_runs]}
        for metric in ROUND5_METRICS:
            values = [row[metric] for row in mode_runs]
            mean = sum(values) / len(values) if len(values) == 3 else None
            reference = baseline_means[metric]
            summary[f"{metric}_mean"] = mean
            summary[f"{metric}_delta_vs_tsr_percent"] = (
                (mean - reference) / reference * 100 if comparable and mean is not None and reference is not None else None
            )
        mode_summaries.append(summary)
    return {"valid": True, "stable": stable, "comparable": comparable, "identity_differences": identity_differences,
            "issues": [], "baseline_drift": drift, "baseline_means": baseline_means,
            "comparisons": comparisons, "mode_summaries": mode_summaries}


def render_experiment_report(receipt: Any) -> str:
    result = analyze_experiments(receipt)
    if not result["valid"]:
        return "# Round 5 benchmark experiment report\n\nReceipt invalid; comparisons are UNKNOWN.\n\n- " + "\n- ".join(result["issues"]) + "\n"
    lines = ["# Round 5 benchmark experiment report", "",
             f"- Baseline stability (all metrics within {receipt.get('baseline_metric_tolerance_percent', 5):g}% of group 0): {'PASS' if result['stable'] else 'FAIL'}",
             f"- Setup identity comparable across runs: {'PASS' if not result['identity_differences'] else 'FAIL'}",
             f"- Treatment comparisons usable: {'YES' if result['comparable'] else 'NO — baseline drift or identity mismatch quarantines all treatment deltas'}", "",
             "## TSR reference mean", "",
             "| Avg FPS | p99 ms | GPU avg ms | GPU p99 ms |", "|---:|---:|---:|---:|"]
    baseline = result["baseline_means"]
    lines.append("| " + " | ".join(
        f"{baseline[metric]:.2f}" if baseline[metric] is not None else "UNKNOWN"
        for metric in ROUND5_METRICS
    ) + " |")
    lines.extend(["", "## Per-mode means (exactly three treatment runs required for a mean)", "",
             "| Mode | Trials | Mean FPS | Mean p99 ms | Mean GPU p99 ms | Δ FPS vs TSR | Δ p99 vs TSR | Δ GPU p99 vs TSR | Image-quality notes |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---|"])
    for row in result["mode_summaries"]:
        def display(value: float | None, digits: int = 2) -> str:
            return f"{value:.{digits}f}" if value is not None else "UNKNOWN"
        deltas = [row[f"{metric}_delta_vs_tsr_percent"] for metric in ("avg_fps", "p99_ms", "gpu_p99_ms")]
        note = " / ".join(note or "UNKNOWN" for note in row["image_quality_notes"])
        lines.append(f"| {row['mode']} | {row['run_count']} | {display(row['avg_fps_mean'])} | "
                     f"{display(row['p99_ms_mean'])} | {display(row['gpu_p99_ms_mean'])} | "
                     f"{display(deltas[0])}% | {display(deltas[1])}% | {display(deltas[2])}% | {note} |")
    lines.extend(["", "## Per-run evidence", "", "| Run | Mode | CVars | avg_fps | p99 ms | GPU p99 ms | Δ FPS vs block TSR | Active mode token | Image-quality note |", "|---|---|---|---:|---:|---:|---:|---|---|"])
    for row in result["comparisons"]:
        cvars = "; ".join(f"{name}={value}" for name, value in sorted(row["cvars"].items()))
        values = [f"{row[metric]:.2f}" if row[metric] is not None else "UNKNOWN"
                  for metric in ("avg_fps", "p99_ms", "gpu_p99_ms")]
        delta = row["avg_fps_delta_percent"]
        lines.append(f"| {row['run_id']} | {row['mode']} | `{cvars}` | " + " | ".join(values) +
                     f" | {f'{delta:+.2f}%' if delta is not None else 'UNKNOWN'} | "
                     f"{row['active_mode_log_token']} | {row['image_quality_note'] or 'UNKNOWN'} |")
    if result["baseline_drift"]:
        lines.extend(["", "## Baseline drift over tolerance", ""])
        lines.extend(f"- Group {row['group']} {row['metric']}: {row['delta_percent']:.2f}% (limit {row['tolerance_percent']:g}%)."
                     for row in result["baseline_drift"])
    else:
        lines.extend(["", "No repeated baseline metric exceeded the drift threshold."])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory", help="hash expected Round 4 run artifacts; read-only")
    inv.add_argument("root", type=Path)
    inv.add_argument("--expected", type=Path, help="previous inventory JSON; report missing or changed listed files")
    comp = sub.add_parser("compare", help="check six measured rows use comparable identity fields")
    comp.add_argument("receipt", type=Path)
    report = sub.add_parser("report", help="render aggregates and gate statuses from a supplied receipt")
    report.add_argument("receipt", type=Path)
    experiments = sub.add_parser("experiments", help="validate N Round 5 runs and report baseline drift")
    experiments.add_argument("receipt", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "inventory":
            expected = json.loads(args.expected.read_text(encoding="utf-8")) if args.expected else None
            value = inventory(args.root, expected)
            print(json.dumps(value, indent=2, sort_keys=True))
            return 1 if value["issues"] else 0
        value = json.loads(args.receipt.read_text(encoding="utf-8"))
        if args.command == "experiments":
            result = analyze_experiments(value)
            print(render_experiment_report(value), end="")
            return 0 if result["valid"] else 1
        if args.command == "compare":
            result = compare_runs(value)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["comparable"] else 1
        print(render_report(value), end="")
        return 0 if not validate_receipt(value) else 1
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
