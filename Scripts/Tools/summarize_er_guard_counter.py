"""Summarize retained ER guard-counter probe markers without inferring a hit."""

import argparse
import json
import re
from pathlib import Path


FIELDS = (
    "synthetic_arm_used", "guard_armed_api_seen", "guard_source_log_seen",
    "counter_accept_logged", "er_strong_count_before", "er_strong_count_after",
    "counter_montages_seen", "boss_hp_delta", "hit_count_before", "hit_count_after",
)
PAIR = re.compile(r"([a-z_]+)=((?:\[[^\]]*\])|(?:[^ ]+))")


def summarize(source: str) -> dict:
    results = [line.split(" RESULT ", 1)[1] for line in source.splitlines() if "[ERGuardCounter] RESULT " in line]
    if len(results) != 1:
        return {"result_count": len(results), "fields": {}, "missing": list(FIELDS), "error": "expected exactly one RESULT line"}
    fields = dict(PAIR.findall(results[0]))
    return {
        "result_count": 1,
        "fields": {key: fields[key] for key in FIELDS if key in fields},
        "missing": [key for key in FIELDS if key not in fields],
        "evidence_block": "[ERGuardCounter] GUARD_COUNTER_EVIDENCE_BEGIN" in source and "[ERGuardCounter] GUARD_COUNTER_EVIDENCE_END" in source,
        "swing_log_count": source.count("LogRPGSwing: swing "),
        "hit_log_count": source.count("LogRPGHitIntake: hit "),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.paths:
        print(json.dumps({"path": str(path), **summarize(path.read_text(encoding="utf-8", errors="replace"))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
