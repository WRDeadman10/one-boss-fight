#!/usr/bin/env python3
"""Compare two FrameworkProof PIE logs without considering timestamps."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

PROOF = re.compile(r"\[FrameworkProof\]\s+(\S+)(.*)")
FIELD = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")


def read_run(path: Path) -> dict[str, object]:
    result_lines: list[tuple[str, ...]] = []
    outcomes: collections.Counter[str] = collections.Counter()
    tokens: collections.Counter[str] = collections.Counter()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = PROOF.search(line)
        if not match:
            continue
        token, rest = match.groups()
        tokens[token] += 1
        fields = dict(FIELD.findall(rest))
        if token == "RESULT":
            result_lines.append(tuple(sorted(fields.items())))
        outcome = fields.get("outcome", "").rsplit("::", 1)[-1]
        if outcome and token == "hit":
            outcomes[outcome] += 1
    return {"path": str(path), "results": result_lines, "outcomes": outcomes, "tokens": tokens}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    for path in (args.baseline, args.candidate):
        if not path.is_file():
            parser.error(f"missing log: {path}")
    a, b = read_run(args.baseline), read_run(args.candidate)
    print(f"baseline RESULT={a['results'][-1] if a['results'] else 'NONE'} outcomes={dict(a['outcomes'])} parries={a['outcomes'].get('Parried', 0)} guarded={a['outcomes'].get('Guarded', 0)}")
    print(f"candidate RESULT={b['results'][-1] if b['results'] else 'NONE'} outcomes={dict(b['outcomes'])} parries={b['outcomes'].get('Parried', 0)} guarded={b['outcomes'].get('Guarded', 0)}")
    all_tokens = set(a["tokens"]) | set(b["tokens"])
    deltas = {token: b["tokens"].get(token, 0) - a["tokens"].get(token, 0) for token in sorted(all_tokens)}
    print(f"same_result={a['results'] == b['results']} same_outcomes={a['outcomes'] == b['outcomes']} token_deltas={deltas}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
