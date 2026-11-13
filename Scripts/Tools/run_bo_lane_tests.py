#!/usr/bin/env python3
"""BO-46: one-command offline runner for the lane BO test suites (KI-163..167 tool hardening and --redact).

Runs every suite in its own `python -m unittest` subprocess, prints one row per suite, and exits nonzero when any suite
fails, cannot run, or reports no tests. Nothing here needs Unreal; the suites use synthetic temp fixtures only.

  python Scripts/Tools/run_bo_lane_tests.py              # all suites
  python Scripts/Tools/run_bo_lane_tests.py --only test_bo_json_inputs
  python Scripts/Tools/run_bo_lane_tests.py --list
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

# Lane BO suites, then the earlier suites that exercise the same tools (regression set used in every BO batch report).
BO_SUITES = (
    "test_bo_tool_hardening", "test_bo_redaction_matrix", "test_bo_redaction_boundaries", "test_bo_redaction_lifecycle",
    "test_bo_redaction_robustness", "test_bo_redaction_cli", "test_bo_redaction_argv", "test_bo_json_inputs",
    "test_bo_remaining_tools", "test_bo_lane_static_pins", "test_bo_lane_runner",
)
REGRESSION_SUITES = (
    "test_audit_source_error_token_coverage", "test_bi_a19_cli_tooling_contract", "test_bk221_225_evidence_manifest_hotfix",
    "test_bk226_230_evidence_pack_audit", "test_bk231_235_evidence_pack_failure_paths", "test_bk236_240_atomic_io_audit",
    "test_bk246_250_atomic_io_callers", "test_bk276_280_replace_caller_failures", "test_bk281_285_evidence_pack_partial",
    "test_bk286_290_evidence_pack_source_race", "test_bk291_295_replace_caller_early_faults",
    "test_bk296_300_post_preflight_collisions", "test_bk301_305_output_input_aliasing", "test_bk306_310_alias_normalization",
    "test_bk311_315_alias_edges", "test_bk316_320_lane_static_checks", "test_evidence_pack_hashes",
    "test_ki165_166_characterization", "test_path_normalization_s170", "test_plot_framework_timeline", "test_queue_c_s36_s40",
    "test_queue_c_tools",
)
# Suites that import their tool as a package (`Scripts.Tools.*`) and must run from the repo root.
PACKAGE_SUITES = ("Scripts.Tools.test_summarize_framework_log",)

RAN = re.compile(r"^Ran (\d+) tests? in", re.MULTILINE)
SKIPPED = re.compile(r"skipped=(\d+)")


def all_suites() -> list[str]:
    return [*BO_SUITES, *REGRESSION_SUITES, *PACKAGE_SUITES]


def run_suite(name: str, timeout: int) -> dict:
    package = name.startswith("Scripts.")
    cwd = REPO if package else HERE
    try:
        proc = subprocess.run([sys.executable, "-m", "unittest", name], cwd=cwd, capture_output=True, text=True,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"suite": name, "status": "TIMEOUT", "tests": 0, "skipped": 0, "detail": f"exceeded {timeout} s"}
    text = proc.stdout + proc.stderr
    ran = RAN.search(text)
    tests = int(ran.group(1)) if ran else 0
    skipped = sum(int(n) for n in SKIPPED.findall(text.splitlines()[-1] if text.strip() else ""))
    if proc.returncode == 0 and tests > 0:
        status = "OK"
    elif proc.returncode == 0:
        status = "NO TESTS"
    else:
        status = "FAIL"
    detail = "" if status == "OK" else (text.strip().splitlines() or ["(no output)"])[-1][:160]
    return {"suite": name, "status": status, "tests": tests, "skipped": skipped, "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", action="append", default=[], metavar="SUITE", help="run only this suite (repeatable)")
    parser.add_argument("--list", action="store_true", help="list the suites and exit")
    parser.add_argument("--timeout", type=int, default=600, help="per-suite timeout in seconds (default 600)")
    args = parser.parse_args()
    suites = all_suites()
    if args.list:
        print("\n".join(suites))
        return 0
    if args.only:
        unknown = [name for name in args.only if name not in suites]
        if unknown:
            parser.error("unknown suite(s): " + ", ".join(unknown) + " (see --list)")
        suites = [name for name in suites if name in args.only]
    rows = [run_suite(name, args.timeout) for name in suites]
    width = max(len(row["suite"]) for row in rows)
    for row in rows:
        skipped = f" (skipped {row['skipped']})" if row["skipped"] else ""
        print(f"{row['status']:<8} {row['suite']:<{width}} {row['tests']:>4} tests{skipped}"
              + (f"  | {row['detail']}" if row["detail"] else ""))
    failed = [row for row in rows if row["status"] != "OK"]
    total = sum(row["tests"] for row in rows)
    print(f"suites={len(rows)} tests={total} failing={len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
