#!/usr/bin/env python3
"""Compare FrameworkProof tokens observed in evidence logs with registered schemas."""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

from atomic_io import atomic_write_text

TOKEN = re.compile(r"\[FrameworkProof\]\s+(\S+)")


def schema_tokens(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SCHEMAS" for t in node.targets):
            return {key.value for key in node.value.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)}
    raise ValueError(f"SCHEMAS dict not found in {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--samples-output", type=Path, help="write a JSON manifest with one first real sample per schema token")
    parser.add_argument("logs", nargs="*")
    args = parser.parse_args()
    root = args.root.resolve()
    validator = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py"
    declared = schema_tokens(validator)
    logs = [Path(p) if Path(p).is_absolute() else root / p for p in args.logs] if args.logs else sorted((root / "Docs/BossCombatReview/Execution/Claude").rglob("*.log"))
    samples: dict[str, dict[str, str | int]] = {}
    for path in logs:
        if not path.is_file():
            print(f"MISSING {path}")
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            match = TOKEN.search(line)
            if match and match.group(1) not in samples:
                try:
                    source_path = path.resolve().relative_to(root).as_posix()
                except ValueError:
                    source_path = str(path.resolve())
                samples[match.group(1)] = {"source": "real_log", "path": source_path, "line": number, "sample": line.strip()}
    seen = set(samples)
    print(f"logs_scanned={len(logs)} schemas={len(declared)} observed={len(seen)}")
    print("SCHEMA NEVER OBSERVED:")
    for token in sorted(declared - seen):
        print(f"  {token}")
    unknown = seen - declared
    print("OBSERVED WITHOUT SCHEMA:")
    for token in sorted(unknown):
        print(f"  {token}")
    if args.samples_output:
        output = args.samples_output if args.samples_output.is_absolute() else root / args.samples_output
        output.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "schema": 1,
            "source_note": "Samples are first retained real log occurrences; missing entries are explicitly not represented by synthetic examples.",
            "schema_count": len(declared),
            "tokens": [
                {"token": token, **samples[token]} if token in samples else
                {"token": token, "source": "no_real_sample", "path": None, "line": None, "sample": None}
                for token in sorted(declared)
            ],
        }
        atomic_write_text(output, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        print(f"sample_manifest={output} real={len(declared & seen)} missing={len(declared - seen)}")
    return 1 if unknown else 0


if __name__ == "__main__":
    raise SystemExit(main())
