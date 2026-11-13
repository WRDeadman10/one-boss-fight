#!/usr/bin/env python3
"""Fail-closed structural and artifact-hash validation for BK-7 Shipping receipts."""
import argparse
import hashlib
import json
from pathlib import Path


CHECKS = ("buildcookrun_exit", "reflection_dump_exit", "shipping_binary_guard_exit", "feature_symbol_guard_exit", "source_guard_exit")


def _sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(receipt, verify_files=False):
    problems = []
    required = {"receipt_version", "build_id", "engine_root", "target", "configuration", "project", "stage_root", "source_head", "dirty_file_count", "artifacts", "checks", "shipping_smoke", "verdict"}
    missing = sorted(required - set(receipt))
    extras = sorted(set(receipt) - required)
    problems.extend(f"missing {key}" for key in missing)
    problems.extend(f"unknown property {key}" for key in extras)
    if missing:
        return problems
    if receipt["receipt_version"] != 1 or receipt["target"] != "Win64" or receipt["configuration"] != "Shipping":
        problems.append("receipt version/target/configuration is not BK-7 Win64 Shipping")
    for key in ("build_id", "engine_root", "project", "stage_root", "source_head"):
        if not isinstance(receipt[key], str) or not receipt[key].strip():
            problems.append(f"{key} must be a non-empty string")
    if not isinstance(receipt["dirty_file_count"], int) or isinstance(receipt["dirty_file_count"], bool) or receipt["dirty_file_count"] < 0:
        problems.append("dirty_file_count must be a non-negative integer")
    if receipt["shipping_smoke"] != "NOT_RUN":
        problems.append("this receipt does not prove packaged smoke")
    artifacts = receipt["artifacts"]
    if not isinstance(artifacts, dict) or set(artifacts) != {"uat_log", "shipping_executable", "reflection_dump"}:
        problems.append("artifacts must contain exactly UAT log, Shipping executable, and reflection dump")
        return problems
    for name in ("uat_log", "shipping_executable", "reflection_dump"):
        artifact = artifacts[name]
        if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str) or not isinstance(artifact.get("sha256"), str):
            problems.append(f"artifacts.{name} requires path and sha256")
        else:
            if artifact.get("build_id") != receipt["build_id"]:
                problems.append(f"artifacts.{name} build_id does not match receipt")
            if len(artifact["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in artifact["sha256"]):
                problems.append(f"artifacts.{name}.sha256 is malformed")
            elif verify_files:
                path = Path(artifact["path"])
                if not path.is_file():
                    problems.append(f"artifacts.{name} is missing: {path}")
                elif _sha(path) != artifact["sha256"]:
                    problems.append(f"artifacts.{name} hash mismatch")
    binary = artifacts["shipping_executable"]
    if isinstance(binary, dict) and (not isinstance(binary.get("bytes"), int) or binary.get("bytes", 0) <= 0):
        problems.append("shipping executable byte count must be positive")
    reflection = artifacts["reflection_dump"]
    if isinstance(reflection, dict) and (not isinstance(reflection.get("command"), str) or not reflection.get("command") or not isinstance(reflection.get("arguments"), list)):
        problems.append("reflection dump command and argument list are required")
    checks = receipt["checks"]
    if not isinstance(checks, dict) or set(checks) != set(CHECKS):
        problems.append("checks must contain the complete BK-7 exit-code set")
    else:
        for name, code in checks.items():
            if not isinstance(code, int) or isinstance(code, bool):
                problems.append(f"checks.{name} must be an integer exit code")
        all_pass = all(checks[name] == 0 for name in CHECKS)
        expected = "PASS" if all_pass else "FAIL"
        if receipt["verdict"] != expected:
            problems.append(f"verdict must be {expected} for recorded exit codes")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--verify-files", action="store_true", help="recompute hashes for every cited artifact")
    args = parser.parse_args()
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL receipt read/parse: {exc}")
        return 2
    problems = validate(receipt, args.verify_files) if isinstance(receipt, dict) else ["receipt root must be an object"]
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        return 1
    print(f"PASS build_id={receipt['build_id']} verdict={receipt['verdict']} shipping_smoke={receipt['shipping_smoke']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
