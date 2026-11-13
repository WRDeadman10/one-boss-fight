"""Offline inventory of PIE driver RESULT and key-release readiness risks."""
import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE = re.compile(r"(?:set_key_down|SetKeyDown)\s*\([^\n)]*,\s*(?:False|false|0)\s*\)")
READY_MARKERS = ("MappingReadinessGate", "HasMappingContext", "is_elden_ring_input_active")
DRIVER_MARKERS = ("register_slate_post_tick_callback", "editor_request_begin_play")
RESULT_MARKERS = ("RESULT=PASS", "RESULT=FAIL", "FinalResult(")


def scan_text(path, source):
    if not any(marker in source for marker in DRIVER_MARKERS):
        return None
    findings = []
    if not any(marker in source for marker in RESULT_MARKERS):
        findings.append("missing_final_result")
    if RELEASE.search(source) and not any(marker in source for marker in READY_MARKERS):
        findings.append("key_release_without_readiness_gate")
    return {"path": str(path), "findings": findings}


def scan(root):
    rows = []
    for path in sorted(Path(root).glob("pie_*.py")):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            rows.append({"path": str(path), "findings": ["unreadable:%s" % exc]})
            continue
        row = scan_text(path.name, source)
        if row is not None:
            rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT / "Scripts" / "Editor")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="exit 1 when findings exist")
    args = parser.parse_args()
    rows = scan(args.root)
    if args.json:
        print(json.dumps({"drivers": len(rows), "findings": sum(len(r["findings"]) for r in rows),
                          "rows": rows}, indent=2))
    else:
        for row in rows:
            if row["findings"]:
                print("%s: %s" % (row["path"], ", ".join(row["findings"])))
        print("drivers=%d findings=%d" % (len(rows), sum(len(r["findings"]) for r in rows)))
    return 1 if args.strict and any(r["findings"] for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
