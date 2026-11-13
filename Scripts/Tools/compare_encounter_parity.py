#!/usr/bin/env python3
"""Fail-closed comparison of paired legacy/data encounter-driver JSON receipts.

Receipts are driver-produced evidence, not inferred from source or raw log text.
See Documentation/Boss/G3_PARITY_DRIVER_INVENTORY.md for the v1 contract.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
import re

sys.path.insert(0, str(Path(__file__).resolve().parent))
from encounter_parity_receipt import ReceiptError as V2ReceiptError
from encounter_parity_receipt import build_receipt, sha256_file

IDENTITY_FIELDS = (
    "map",
    "build_id",
    "content_sha256",
    "settings_sha256",
    "seed",
    "driver",
    "driver_args",
    "input_sha256",
)
REQUIRED = (
    "schema",
    "route",
    "run_id",
    "identity",
    "final_marker",
    "checks",
    "terminal",
    "activation",
    "components",
    "observables",
)
TIMING_TOLERANCE_SECONDS = 2.0 / 60.0
MESSAGE_ABSOLUTE_TOLERANCE = 2.0 / 60.0
MESSAGE_RELATIVE_TOLERANCE = 0.10
_POINTER_TOKEN = re.compile(r"0x[0-9a-f]+(?:\.\.)?", re.IGNORECASE)
_INSTANCE_SUFFIX = re.compile(r"(?<=_)\d+\b")
_BRACKETED_DETAIL = re.compile(r"\[[^\]]*\]")
_SAMPLE_COUNT = re.compile(r"\b\d+(?=\s+samples\b)", re.IGNORECASE)
_MESSAGE_NUMBER = re.compile(r"(?<![\w.])[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?(?![\w.])")
_STATE_KEYWORD = re.compile(r"\b(?:health|posture|poise|damage|stamina|hp)\b", re.IGNORECASE)
_TIMING_MESSAGE_NUMBER = re.compile(
    r"(?i)(\b(?:press[-_ ]to[-_ ]contact|onset[-_ ]gap|windup|startup|duration|"
    r"elapsed|latency|cooldown|interval|delay|frame|scale|timing)\b\s*(?:=|:)?\s*)"
    r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
    r"(\s*(?:milliseconds?|msec|ms|seconds?|secs?|sec|s|frames?)?)(?![\w.]|\s*/\s*\d)"
)
_SAMPLED_SERIES = re.compile(r"\s*[-+\d.eE,;()\s'\"]+\Z")
_SAMPLED_TUPLES = re.compile(
    r"\s*\(\s*['\"][^'\"]+['\"]\s*,\s*[-+\d.eE,;()\s]+\)(?:\s*,\s*\(\s*['\"][^'\"]+['\"]\s*,\s*[-+\d.eE,;()\s]+\))*\s*\Z"
)


def _is_sampled_detail(detail: str, before: str) -> bool:
    """Only treat numeric arrays or details following 'samples' as diagnostics."""
    if _STATE_KEYWORD.search(detail):
        return False
    follows_sample_marker = re.search(r"\bsamples\s*,?\s*\Z", before, re.IGNORECASE)
    return bool(follows_sample_marker or _SAMPLED_SERIES.fullmatch(detail) or _SAMPLED_TUPLES.fullmatch(detail))


def _message_parts(message: str) -> tuple[str, list[float]]:
    without_pointers = _POINTER_TOKEN.sub("", message)
    without_instances = _INSTANCE_SUFFIX.sub("", without_pointers)
    without_series = re.sub(
        r"\[([^\]]*)\]",
        lambda match: "" if _is_sampled_detail(match.group(1), without_instances[:match.start()]) else match.group(0),
        without_instances,
    )
    without_sample_count = _SAMPLE_COUNT.sub("", without_series)
    numbers: list[float] = []
    remaining = _MESSAGE_NUMBER.sub(lambda match: numbers.append(float(match.group(0))) or "<N>", without_sample_count)
    return " ".join(remaining.split()), numbers


def _message_mismatch(left: str, right: str) -> str | None:
    left_text, left_numbers = _message_parts(left)
    right_text, right_numbers = _message_parts(right)
    if len(left_numbers) != len(right_numbers):
        index = min(len(left_numbers), len(right_numbers))
        left_value = f"{left_numbers[index]:g}" if index < len(left_numbers) else "<missing>"
        right_value = f"{right_numbers[index]:g}" if index < len(right_numbers) else "<missing>"
        return f"numeric token {index + 1} count differs: control={left_value}, data={right_value}"
    if left_text != right_text:
        return "message text differs after pointer/object-instance removal and numeric tokenization"
    for index, (left_value, right_value) in enumerate(zip(left_numbers, right_numbers), 1):
        absolute_delta = abs(left_value - right_value)
        relative_limit = MESSAGE_RELATIVE_TOLERANCE * max(abs(left_value), abs(right_value))
        if absolute_delta > MESSAGE_ABSOLUTE_TOLERANCE and absolute_delta > relative_limit:
            return (f"numeric token {index} differs: control={left_value:g}, data={right_value:g}; "
                    f"absolute_delta={absolute_delta:g}, limits={MESSAGE_ABSOLUTE_TOLERANCE:g}s or "
                    f"{MESSAGE_RELATIVE_TOLERANCE:.0%} of max magnitude")
    return None


def _timing_message_mismatch(left: str, right: str) -> str | None:
    """Compare the residual check message after typed timing fields own their values.

    This keeps the receipt's timing comparator authoritative for labeled timing
    diagnostics, while preserving checks for health, damage, counts, and other
    non-timing numeric tokens in the same message.
    """
    def mask_timing_fields(message: str) -> str:
        return _TIMING_MESSAGE_NUMBER.sub(
            lambda match: match.group(1) + "<TIMING>" + match.group(3), message
        )

    return _message_mismatch(mask_timing_fields(left), mask_timing_fields(right))


def _volatile_message_differs(left: str, right: str) -> bool:
    """Sampled arrays and the count before 'samples' are diagnostic-only, never discarded silently."""
    def sampled_details(message: str) -> list[str]:
        return [match.group(1) for match in re.finditer(r"\[([^\]]*)\]", message)
                if _is_sampled_detail(match.group(1), message[:match.start()])]
    left_series = sampled_details(left)
    right_series = sampled_details(right)
    left_counts = _SAMPLE_COUNT.findall(left)
    right_counts = _SAMPLE_COUNT.findall(right)
    return left_series != right_series or left_counts != right_counts


def _message_warnings(control: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if control.get("schema", "").endswith("/v2"):
        for name in sorted(set(control.get("observables", {})) & set(candidate.get("observables", {}))):
            left = control["observables"][name]
            right = candidate["observables"][name]
            left_comparison = left.get("comparison")
            right_comparison = right.get("comparison")
            if (isinstance(left_comparison, dict) and isinstance(right_comparison, dict)
                    and left_comparison.get("type") == right_comparison.get("type") == "stochastic"):
                warnings.append(
                    f"WARN stochastic {name}: control={json.dumps(left.get('value'), sort_keys=True)}; "
                    f"data={json.dumps(right.get('value'), sort_keys=True)}"
                )
                continue
            # Typed measurements define their own comparison and do not use message rules.
            if left_comparison is not None or right_comparison is not None:
                continue
            left_value, right_value = left.get("value"), right.get("value")
            if not (isinstance(left_value, dict) and isinstance(right_value, dict)
                    and isinstance(left_value.get("message"), str)
                    and isinstance(right_value.get("message"), str)):
                continue
            left_message, right_message = left_value["message"], right_value["message"]
            if _volatile_message_differs(left_message, right_message):
                warnings.append(f"WARN {name}: control={left_message!r}; data={right_message!r}")
    return warnings


def _observable_value_matches(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Compare typed measurements numerically and check outcomes by status only."""
    if ("check_status" in left or "check_status" in right) and left.get("check_status") != right.get("check_status"):
        return False
    left_comparison = left.get("comparison")
    right_comparison = right.get("comparison")
    if left_comparison is None and right_comparison is None:
        left_value, right_value = left.get("value"), right.get("value")
        if (isinstance(left_value, dict) and isinstance(right_value, dict)
                and isinstance(left_value.get("status"), str)
                and isinstance(right_value.get("status"), str)):
            return (left_value["status"] == right_value["status"]
                    and _message_mismatch(left_value.get("message", ""), right_value.get("message", "")) is None)
        return left_value == right_value
    if left_comparison != right_comparison:
        return False
    if not isinstance(left_comparison, dict):
        return False
    kind = left_comparison.get("type")
    if kind == "timing_seconds":
        left_message, right_message = left.get("check_message"), right.get("check_message")
        if isinstance(left_message, str) != isinstance(right_message, str):
            return False
        if isinstance(left_message, str) and isinstance(right_message, str):
            if _timing_message_mismatch(left_message, right_message) is not None:
                return False
    if kind == "exact":
        return set(left_comparison) == {"type"} and left.get("value") == right.get("value")
    if kind == "stochastic":
        if left_comparison != right_comparison:
            return False
        threshold = left_comparison["threshold"]

        def meets(value: Any) -> bool:
            if not isinstance(value, dict) or value.get(left_comparison["scenario_ran_field"]) is not True:
                return False
            if threshold["left_field"] not in value:
                return False
            left_value = value[threshold["left_field"]]
            if "right_field" in threshold:
                if threshold["right_field"] not in value:
                    return False
                right_value = value[threshold["right_field"]]
            else:
                right_value = threshold["right_value"]
            if threshold["op"] == "gte":
                return (type(left_value) in (int, float) and type(right_value) in (int, float)
                        and left_value >= right_value)
            return left_value == right_value

        return meets(left.get("value")) and meets(right.get("value"))
    if kind == "timing_seconds":
        bounds = left_comparison["range_seconds"]
        tolerance = TIMING_TOLERANCE_SECONDS
    elif kind == "rate_ratio":
        bounds = left_comparison["range"]
        tolerance = 0.01
    else:
        return False
    values = (left.get("value"), right.get("value"))
    return all(bounds[0] <= value <= bounds[1] for value in values) and abs(values[0] - values[1]) <= tolerance


class ReceiptError(ValueError):
    pass


def read_receipt(path: Path, expected_route: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReceiptError(f"{path}: cannot read valid UTF-8 JSON ({exc})") from exc
    if not isinstance(value, dict):
        raise ReceiptError(f"{path}: root must be an object")
    missing = [key for key in REQUIRED if key not in value]
    if missing:
        raise ReceiptError(f"{path}: missing required fields: {', '.join(missing)}")
    if value["schema"] not in ("onebossfight.encounter-parity/v1", "onebossfight.encounter-parity/v2"):
        raise ReceiptError(f"{path}: unsupported schema {value['schema']!r}")
    if value["route"] != expected_route:
        raise ReceiptError(f"{path}: route must be {expected_route!r}")
    if not isinstance(value["run_id"], str) or not value["run_id"].strip():
        raise ReceiptError(f"{path}: run_id must be nonempty")
    if not isinstance(value["identity"], dict):
        raise ReceiptError(f"{path}: identity must be an object")
    missing_identity = [k for k in IDENTITY_FIELDS if k not in value["identity"]]
    if missing_identity:
        raise ReceiptError(f"{path}: incomplete identity: {', '.join(missing_identity)}")
    identity = value["identity"]
    for key in ("map", "build_id", "content_sha256", "settings_sha256", "driver", "input_sha256"):
        if not isinstance(identity[key], str) or not identity[key].strip():
            raise ReceiptError(f"{path}: identity.{key} must be nonempty text")
    for key in ("content_sha256", "settings_sha256", "input_sha256"):
        if re.fullmatch(r"[0-9a-fA-F]{64}", identity[key]) is None:
            raise ReceiptError(f"{path}: identity.{key} must be a 64-digit SHA-256")
    if type(identity["seed"]) not in (int, str) or (isinstance(identity["seed"], str) and not identity["seed"].strip()):
        raise ReceiptError(f"{path}: identity.seed must be a nonempty string or integer")
    if not isinstance(identity["driver_args"], list) or any(not isinstance(arg, str) for arg in identity["driver_args"]):
        raise ReceiptError(f"{path}: identity.driver_args must be an ordered array")
    if not value["final_marker"] or not isinstance(value["final_marker"], (str, dict)):
        raise ReceiptError(f"{path}: final_marker must be nonempty text or an object")
    if not isinstance(value["checks"], dict) or type(value["checks"].get("passed")) is not int or type(value["checks"].get("minimum")) is not int:
        raise ReceiptError(f"{path}: checks must contain integer passed and minimum")
    if value["checks"]["minimum"] <= 0 or value["checks"]["passed"] < 0:
        raise ReceiptError(f"{path}: checks.minimum must be positive and checks.passed must be nonnegative")
    marker_total = value["final_marker"].get("total") if isinstance(value["final_marker"], dict) else None
    check_limit = marker_total if type(marker_total) is int and marker_total > 0 else value["checks"]["minimum"]
    if value["checks"]["passed"] > check_limit:
        raise ReceiptError(f"{path}: checks.passed exceeds captured total ({check_limit})")
    if not isinstance(value["terminal"], dict) or type(value["terminal"].get("clean")) is not bool:
        raise ReceiptError(f"{path}: terminal.clean must be boolean")
    if not isinstance(value["terminal"].get("result"), str) or not value["terminal"]["result"].strip():
        raise ReceiptError(f"{path}: terminal.result is required")
    if not isinstance(value["activation"], dict) or not isinstance(value["activation"].get("outcome"), str) or not value["activation"]["outcome"].strip():
        raise ReceiptError(f"{path}: activation.outcome is required")
    if not isinstance(value["components"], dict):
        raise ReceiptError(f"{path}: components must be an object")
    if not isinstance(value["observables"], dict) or not value["observables"]:
        raise ReceiptError(f"{path}: observables must be a nonempty object")
    if any(not isinstance(k, str) or not k for k in value["observables"]):
        raise ReceiptError(f"{path}: observable names must be nonempty strings")
    if value["schema"].endswith("/v2"):
        try:
            build_receipt(value)
        except V2ReceiptError as exc:
            raise ReceiptError(f"{path}: {exc}") from exc
    return value


def verify_source_logs(value: dict[str, Any], receipt_path: Path) -> None:
    """Verify each v2 observable's cited raw log relative to its receipt (or by absolute path)."""
    if not value.get("schema", "").endswith("/v2"):
        raise ReceiptError(f"{receipt_path}: source-log verification requires a v2 receipt")
    for name, observable in value["observables"].items():
        cited = Path(observable["source_log"])
        resolved = cited if cited.is_absolute() else receipt_path.parent / cited
        if not resolved.is_file():
            raise ReceiptError(f"{receipt_path}: observable {name} source log is missing: {resolved}")
        actual = sha256_file(resolved)
        if actual != observable["source_log_sha256"]:
            raise ReceiptError(f"{receipt_path}: observable {name} source-log SHA-256 mismatch: {resolved}")


def report_path_conflict(report_path: Path, receipts: list[tuple[Path, dict[str, Any]]]) -> str | None:
    """Refuse a report destination that aliases any evidence input."""
    target = report_path.resolve()
    for receipt_path, value in receipts:
        if target == receipt_path.resolve():
            return f"report path would overwrite receipt input: {receipt_path}"
        if value.get("schema", "").endswith("/v2"):
            for name, observable in value.get("observables", {}).items():
                cited = Path(observable["source_log"])
                source = cited if cited.is_absolute() else receipt_path.parent / cited
                if target == source.resolve():
                    return f"report path would overwrite source log for {name}: {source}"
    return None


def compare(control: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for label, value in (("control", control), ("candidate", candidate)):
        if value["terminal"].get("clean") is not True:
            issues.append(f"{label} run failed checks: {value['checks']['passed']}/{value['checks']['minimum']}")
    for key in IDENTITY_FIELDS:
        left = control["identity"].get(key)
        right = candidate["identity"].get(key)
        if left != right:
            issues.append(f"identity mismatch {key}: control={left!r}, data={right!r}")
    for key in ("final_marker", "terminal"):
        if control[key] != candidate[key]:
            issues.append(f"parity mismatch {key}: control={control[key]!r}, data={candidate[key]!r}")
    if control["schema"] != candidate["schema"]:
        issues.append("receipt schema versions differ")
    elif control["schema"].endswith("/v2"):
        if set(control["observables"]) != set(candidate["observables"]):
            issues.append("unmatched trial observable sets")
        # Selection state and binding metadata are route-specific by design.
        # Compare stable participant identity while allowing selected-only slot,
        # definition, generation, and reset provenance to differ.
        def stable_participants(value: dict[str, Any]) -> list[tuple[str, str, str]]:
            return sorted((row["role"], row["actor_class"], row["actor_id"]) for row in value["participants"])
        if stable_participants(control) != stable_participants(candidate):
            issues.append("parity mismatch stable participant identity")
        for name in sorted(set(control["observables"]) & set(candidate["observables"])):
            left, right = control["observables"][name], candidate["observables"][name]
            if not _observable_value_matches(left, right):
                reason = None
                if left.get("check_status") != right.get("check_status"):
                    reason = f"check status differs: control={left.get('check_status')!r}, data={right.get('check_status')!r}"
                elif left.get("comparison") is None and right.get("comparison") is None:
                    left_value, right_value = left.get("value"), right.get("value")
                    if isinstance(left_value, dict) and isinstance(right_value, dict) and "status" in left_value and "status" in right_value:
                        if left_value.get("status") != right_value.get("status"):
                            reason = f"check status differs: control={left_value.get('status')!r}, data={right_value.get('status')!r}"
                        else:
                            reason = _message_mismatch(left_value.get("message", ""), right_value.get("message", ""))
                issues.append(f"parity mismatch observable {name}" + (f": {reason}" if reason else ""))
            if left.get("trial_id") != right.get("trial_id"):
                issues.append(f"unmatched trial for observable {name}")
    else:
        if set(control["observables"]) != set(candidate["observables"]):
            issues.append("observable field sets differ")
        if control["observables"] != candidate["observables"]:
            issues.append("parity mismatch observables")
    if control["run_id"] == candidate["run_id"]:
        issues.append("run_id must differ between independent paired runs")
    # Activation and component census are intentionally reported, not required to
    # match: a data route is expected to change them and the schema is explicit.
    return issues


def write_report_atomic(path: Path, report: dict[str, Any]) -> None:
    """Write a deterministic report without touching either input receipt."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temp_path = Path(stream.name)
            json.dump(report, stream, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def _observables_match(control: dict[str, Any] | None, candidate: dict[str, Any] | None) -> bool:
    if not control or not candidate or set(control["observables"]) != set(candidate["observables"]):
        return False
    if control["schema"].endswith("/v2") and candidate["schema"].endswith("/v2"):
        return all(
            _observable_value_matches(control["observables"][name], candidate["observables"][name])
            and control["observables"][name].get("trial_id") == candidate["observables"][name].get("trial_id")
            for name in control["observables"]
        )
    return control["observables"] == candidate["observables"]


def _observable_status(control: dict[str, Any] | None, candidate: dict[str, Any] | None, name: str) -> str:
    """Per-observable report status. Lead fix (C-835): v1 receipts carry scalar observables and v2
    receipts carry {value, trial_id, ...} records, so only call .get() on dict entries."""
    if not control or not candidate or name not in control["observables"] or name not in candidate["observables"]:
        return "INCONCLUSIVE"
    left, right = control["observables"][name], candidate["observables"][name]
    if isinstance(left, dict) and isinstance(right, dict):
        if left.get("trial_id") != right.get("trial_id"):
            return "INCONCLUSIVE"
        return "MATCH" if _observable_value_matches(left, right) else "MISMATCH"
    if isinstance(left, dict) or isinstance(right, dict):
        return "INCONCLUSIVE"  # mixed v1/v2 shapes cannot be compared value-for-value
    return "MATCH" if left == right else "MISMATCH"


def make_report(status: str, exit_code: int, control: dict[str, Any] | None,
                candidate: dict[str, Any] | None, issues: list[str],
                control_path: Path | None = None, data_path: Path | None = None,
                warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema": "onebossfight.encounter-parity-report/v1",
        "status": status,
        "exit_code": exit_code,
        "control_run_id": control.get("run_id") if control else None,
        "data_run_id": candidate.get("run_id") if candidate else None,
        "issues": issues,
        "warnings": warnings or [],
        "sources": {
            "control": {"receipt": str(control_path) if control_path else None,
                        "receipt_sha256": sha256_file(control_path) if control_path and control_path.is_file() else None},
            "data": {"receipt": str(data_path) if data_path else None,
                     "receipt_sha256": sha256_file(data_path) if data_path and data_path.is_file() else None},
        },
        "comparison": {
            "identity": "MATCH" if control and candidate and all(
                control["identity"].get(k) == candidate["identity"].get(k) for k in IDENTITY_FIELDS
            ) else "UNAVAILABLE_OR_MISMATCH",
            "final_marker": "MATCH" if control and candidate and control["final_marker"] == candidate["final_marker"] else "UNAVAILABLE_OR_MISMATCH",
            "terminal": "MATCH" if control and candidate and control["terminal"] == candidate["terminal"] else "UNAVAILABLE_OR_MISMATCH",
            "observables": "MATCH" if _observables_match(control, candidate) else "UNAVAILABLE_OR_MISMATCH",
        },
        "observable_sources": {
            name: {
                "status": _observable_status(control, candidate, name),
                "control": control["observables"].get(name) if control else None,
                "data": candidate["observables"].get(name) if candidate else None,
            }
            for name in sorted(set(control["observables"] if control else {}) | set(candidate["observables"] if candidate else {}))
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("control", type=Path, help="legacy-control receipt JSON")
    parser.add_argument("data", type=Path, help="data-path receipt JSON")
    parser.add_argument("--report-json", type=Path, help="optional atomic deterministic JSON report path")
    parser.add_argument("--verify-source-logs", action="store_true",
                        help="verify every v2 observable log exists and matches its cited SHA-256")
    args = parser.parse_args()
    control: dict[str, Any] | None = None
    data: dict[str, Any] | None = None
    unsafe_report_destination = bool(args.report_json and any(
        args.report_json.resolve() == input_path.resolve() for input_path in (args.control, args.data)
    ))
    if unsafe_report_destination:
        print("INCONCLUSIVE: report path would overwrite a receipt input", file=sys.stderr)
        return 2
    try:
        control = read_receipt(args.control, "legacy")
        data = read_receipt(args.data, "data")
        if args.report_json:
            conflict = report_path_conflict(args.report_json, [(args.control, control), (args.data, data)])
            if conflict:
                unsafe_report_destination = True
                raise ReceiptError(conflict)
        if args.verify_source_logs:
            verify_source_logs(control, args.control)
            verify_source_logs(data, args.data)
    except ReceiptError as exc:
        print(f"INCONCLUSIVE: {exc}", file=sys.stderr)
        if args.report_json and not unsafe_report_destination:
            try:
                write_report_atomic(args.report_json, make_report("INCONCLUSIVE", 2, control, data, [str(exc)], args.control, args.data))
            except OSError as write_exc:
                print(f"REPORT ERROR: {write_exc}", file=sys.stderr)
        return 2
    issues = compare(control, data)
    warnings = _message_warnings(control, data)
    print(f"control_run={control['run_id']} data_run={data['run_id']}")
    print(f"control_activation={json.dumps(control['activation'], sort_keys=True)}")
    print(f"data_activation={json.dumps(data['activation'], sort_keys=True)}")
    print(f"control_components={json.dumps(control['components'], sort_keys=True)}")
    print(f"data_components={json.dumps(data['components'], sort_keys=True)}")
    for warning in warnings:
        print(warning)
    if issues and any(issue.startswith("unmatched trial") for issue in issues):
        print("INCONCLUSIVE")
        for issue in issues:
            print(f"- {issue}")
        if args.report_json:
            try:
                write_report_atomic(args.report_json, make_report("INCONCLUSIVE", 2, control, data, issues, args.control, args.data, warnings))
            except OSError as write_exc:
                print(f"REPORT ERROR: {write_exc}", file=sys.stderr)
        return 2
    if issues:
        print("FAIL")
        for issue in issues:
            print(f"- {issue}")
        if args.report_json:
            try:
                write_report_atomic(args.report_json, make_report("FAIL", 1, control, data, issues, args.control, args.data, warnings))
            except OSError as write_exc:
                print(f"REPORT ERROR: {write_exc}", file=sys.stderr)
        return 1
    print("PASS: declared parity identity, final marker, terminal state, and gameplay observables match")
    if args.report_json:
        try:
            write_report_atomic(args.report_json, make_report("PASS", 0, control, data, [], args.control, args.data, warnings))
        except OSError as write_exc:
            print(f"REPORT ERROR: {write_exc}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
