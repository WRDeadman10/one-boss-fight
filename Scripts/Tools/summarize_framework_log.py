#!/usr/bin/env python3
"""Summarize [FrameworkProof] tokens and hit outcomes for one or more Unreal logs."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

PREFIX = re.compile(r"\[FrameworkProof\]\s+(\S+)(.*)")
FIELD = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")
WINDOW_CARD = re.compile(r"^Window_(.+?)_(?:Primary|Secondary|Ring)$")


def summarize(path: Path) -> dict[str, object]:
    tokens: collections.Counter[str] = collections.Counter()
    outcomes: collections.Counter[str] = collections.Counter()
    cards: dict[str, dict[str, object]] = {}
    decisions = parried = guarded = accepted = 0
    reported_hits: list[int] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = PREFIX.search(line)
        if not match:
            continue
        token, remainder = match.groups()
        tokens[token] += 1
        fields = dict(FIELD.findall(remainder))
        instance = fields.get("instance")
        if instance is not None:
            row = cards.setdefault(instance, {"instance": instance, "card": "?", "starts": 0, "hits": 0, "accepted": 0, "parried": 0, "last_outcome": "-"})
            if token == "playback_start":
                row["starts"] = int(row["starts"]) + 1
                row["card"] = fields.get("card", fields.get("montage", "?"))
            if token == "hit":
                outcome = fields.get("outcome", "").rsplit("::", 1)[-1]
                row["hits"] = int(row["hits"]) + 1
                row["accepted"] = int(row["accepted"]) + int(outcome == "Accepted")
                row["parried"] = int(row["parried"]) + int(outcome == "Parried")
                row["last_outcome"] = outcome or "?"
            window_match = WINDOW_CARD.match(fields.get("window", ""))
            if window_match:
                row["card"] = window_match.group(1)
        if token == "decision":
            decisions += 1
        outcome = fields.get("outcome", "")
        if outcome and token == "hit":
            outcomes[outcome.rsplit("::", 1)[-1]] += 1
            parried += int("Parried" in outcome)
            guarded += int("Guarded" in outcome)
            accepted += int(outcome.endswith("Accepted"))
        if token == "RESULT" and "acceptedHits" in fields:
            try:
                reported_hits.append(int(fields["acceptedHits"]))
            except ValueError:
                pass
    return {
        "file": str(path), "tokens": dict(sorted(tokens.items())),
        "decisions": decisions, "parried_outcomes": parried,
        "guarded_outcomes": guarded, "accepted_outcomes": accepted,
        "reported_accepted_hits": reported_hits[-1] if reported_hits else None,
        "outcomes": dict(sorted(outcomes.items())),
        "per_card": _per_card(cards),
    }


def _per_card(instances: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for instance, source in instances.items():
        name = str(source["card"])
        row = grouped.setdefault(name, {"card": name, "instances": [], "starts": 0, "hits": 0, "accepted": 0, "parried": 0, "last_outcome": "-"})
        row["instances"].append(instance)
        for field in ("starts", "hits", "accepted", "parried"):
            row[field] = int(row[field]) + int(source[field])
        row["last_outcome"] = source["last_outcome"]
    return [grouped[key] for key in sorted(grouped)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path, help="one or more editor/PIE logs")
    args = parser.parse_args()
    failed = False
    for path in args.logs:
        if not path.is_file():
            print(f"ERROR missing log: {path}")
            failed = True
            continue
        result = summarize(path)
        print(f"\n{result['file']}")
        print("token counts:", result["tokens"])
        print(f"decisions={result['decisions']} hits accepted={result['accepted_outcomes']} parried={result['parried_outcomes']} guarded={result['guarded_outcomes']} reported={result['reported_accepted_hits']}")
        print("card | instances | starts | hits | accepted | parried | last outcome")
        for row in result["per_card"]:
            print(f"{row['card']} | {','.join(row['instances'])} | {row['starts']:>6} | {row['hits']:>4} | {row['accepted']:>8} | {row['parried']:>7} | {row['last_outcome']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
