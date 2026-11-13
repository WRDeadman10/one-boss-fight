#!/usr/bin/env python3
"""BP-46: run the Queue BP static and in-process test suites in this process and print one row per suite.

The suites are loaded with unittest and run IN THIS PROCESS: no tool main(), CLI or subprocess is started (X-2295).
BP_SMOKE_EXECUTE is forced off so the gated execution class in test_bp_cli_smoke stays skipped. Exits 1 if any suite fails
or errors, 0 otherwise.
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

BP_SUITES = (
    "test_bp_cli_smoke", "test_bp_static_contract", "test_bp_json_inputs", "test_bp_missing_inputs",
    "test_bp_atomic_writes", "test_bp_exit_codes", "test_bp_bom_json_reads", "test_bp_core_functions",
    "test_bp_text_inputs", "test_bp_doc_sync", "test_bp_large_inputs", "test_bp_lane_runner",
)


def run_suites(names) -> list[dict]:
    """Run each named suite in-process; returns one result row per suite. BP_SMOKE_EXECUTE is removed first."""
    os.environ.pop("BP_SMOKE_EXECUTE", None)
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    rows = []
    for name in names:
        suite = unittest.defaultTestLoader.loadTestsFromName(name)
        result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        rows.append({"suite": name, "tests": result.testsRun, "failures": len(result.failures),
                     "errors": len(result.errors), "skipped": len(result.skipped),
                     "ok": result.wasSuccessful() and result.testsRun > 0})
    return rows


def select_suites(only) -> list[str]:
    """X-2315: the suites to run for the given --only values. Unknown names raise ValueError (fail closed), and an
    empty selection is impossible: with no --only, every suite runs."""
    unknown = [name for name in only if name not in BP_SUITES]
    if unknown:
        raise ValueError("unknown suite(s): " + ", ".join(unknown))
    names = [name for name in BP_SUITES if not only or name in only]
    if not names:
        raise ValueError("no suites selected")
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", default=[], metavar="SUITE", help="run only this suite (repeatable)")
    args = parser.parse_args()
    try:
        names = select_suites(args.only)
    except ValueError as error:  # X-2315: an unknown --only value is a usage error (exit 2), never a 0-suite success
        parser.error(str(error))
    rows = run_suites(names)
    for row in rows:
        status = "OK" if row["ok"] else "FAIL"
        print(f"{status:<5} {row['suite']:<26} tests={row['tests']} failures={row['failures']} errors={row['errors']} skipped={row['skipped']}")
    failing = [row for row in rows if not row["ok"]]
    print(f"suites={len(rows)} tests={sum(r['tests'] for r in rows)} failing={len(failing)}")
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
