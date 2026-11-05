from __future__ import annotations

import argparse
import json
from pathlib import Path

DRIVERS = ("pie_phase_reset", "pie_boss_death", "pie_authored_close_clips", "pie_legend", "pie_iframes")


def summarize(root: Path, suffix: str) -> dict[str, object]:
    rows = []
    for driver in DRIVERS:
        folder = root / (driver + suffix)
        report_path = folder / "parity_report.json"
        if not report_path.is_file():
            rows.append({"driver": driver, "status": "MISSING", "issues": ["parity_report.json absent"]})
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        rows.append({"driver": driver, "status": report.get("status", "INVALID"),
                     "exit_code": report.get("exit_code"), "issues": report.get("issues", [])})
    return {"schema": "onebossfight.selected-parity-summary/v1", "pairs": rows,
            "passed": sum(row["status"] == "PASS" for row in rows),
            "failed_or_missing": sum(row["status"] != "PASS" for row in rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize the five default-off parity comparator reports.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--suffix", required=True)
    args = parser.parse_args()
    result = summarize(args.root, args.suffix)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["failed_or_missing"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
