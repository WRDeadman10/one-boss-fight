#!/usr/bin/env python3
"""Summarize Unreal automation Test Completed records as text or JSON."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

COMPLETED = re.compile(r"Test Completed\. Result=\{([^}]+)\} Name=\{([^}]*)\}(?: Path=\{([^}]*)\})?")
COMPLETE_MARKER = "TEST COMPLETE. EXIT CODE: 0"


def summarize(path: Path) -> dict[str, object]:
    tests = []
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = COMPLETED.search(line)
        if match:
            result, name, test_path = match.groups()
            tests.append({"line": number, "name": name, "path": test_path or "", "result": result})
    failures = sorted(test["path"] or test["name"] for test in tests if test["result"] != "Success")
    counts = Counter(test["result"] for test in tests)
    duplicate_keys = sorted(key for key, count in Counter(test["path"] or test["name"] for test in tests).items() if count > 1)
    complete = COMPLETE_MARKER in path.read_text(encoding="utf-8", errors="replace")
    return {"file": str(path), "complete": complete, "finished": len(tests), "passed": counts["Success"],
            "failed": len(tests) - counts["Success"], "failures": failures,
            "duplicate_names": duplicate_keys, "tests": tests}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--json", action="store_true", help="emit stable machine-readable JSON")
    parser.add_argument("--allow-partial", action="store_true", help="summarize without a terminal successful-suite marker; output is not a pass certificate")
    args = parser.parse_args()
    if not args.log.is_file():
        parser.error(f"missing log: {args.log}")
    report = summarize(args.log)
    if report["finished"] == 0:
        if args.json:
            print(json.dumps(report, sort_keys=True, indent=2))
        else:
            print("PARTIAL: no Test Completed records found")
        return 2
    if not report["complete"] and not args.allow_partial:
        if args.json:
            print(json.dumps(report, sort_keys=True, indent=2))
        else:
            print(f"completion=PARTIAL finished={report['finished']} passed={report['passed']} failed={report['failed']}")
            print("PARTIAL: missing terminal " + COMPLETE_MARKER)
        return 2
    if args.json:
        print(json.dumps(report, sort_keys=True, indent=2))
    else:
        print("completion=COMPLETE" if report["complete"] else "completion=PARTIAL (explicitly allowed; not a pass certificate)")
        print(f"finished={report['finished']} passed={report['passed']} failed={report['failed']}")
        print("failures=" + (", ".join(report["failures"]) or "none"))
        print("duplicate_names=" + (", ".join(report["duplicate_names"]) or "none"))
    return 1 if report["failed"] or report["duplicate_names"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
