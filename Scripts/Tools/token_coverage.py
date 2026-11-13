#!/usr/bin/env python3
"""Compare FrameworkProof tokens observed in evidence logs with registered schemas."""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BO-28: before atomic_io too, so `python -m Scripts.Tools.*` works; helper import works as a script or as Scripts.Tools.*
from atomic_io import atomic_write_text
from redaction import add_redact_argument, display_path, display_row, install_stream_redaction, redaction_scope


def output_aliases(output: Path, inputs) -> Path | None:
    """BK-301..305: return the input that `output` would overwrite (same resolved path or same file), else None."""
    target = Path(output).resolve()
    for item in inputs:
        candidate = Path(item)
        if candidate.resolve() == target:
            return candidate
        if target.exists() and candidate.exists() and target.samefile(candidate):
            return candidate
    return None

TOKEN = re.compile(r"\[FrameworkProof\]\s+(\S+)")


def schema_tokens(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SCHEMAS" for t in node.targets):
            return {key.value for key in node.value.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)}
    raise ValueError(f"SCHEMAS dict not found in {path}")


@redaction_scope  # BO-18: restore the caller's streams when main ends
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])  # BP-03: repo root, not the current folder
    parser.add_argument("--samples-output", type=Path, help="write a JSON manifest with one first real sample per schema token")
    parser.add_argument("logs", nargs="*")
    add_redact_argument(parser)  # BO-05 / KI-167
    args = parser.parse_args()
    if args.redact:  # BO-23: only ever enable here; never unwrap a caller-owned wrapper when the flag is absent
        install_stream_redaction(True)  # BO-06..09: mask absolute machine paths in every printed line
    root = args.root.resolve()
    validator = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py"
    declared = schema_tokens(validator)
    logs = [Path(p) if Path(p).is_absolute() else root / p for p in args.logs] if args.logs else sorted((root / "Docs/BossCombatReview/Execution/Claude").rglob("*.log"))
    samples: dict[str, dict[str, str | int]] = {}
    missing = []  # BO-01 / KI-163: a missing log is an error, not a silent skip.
    for path in logs:
        if not path.is_file():
            print(f"MISSING {display_path(path, args.redact, root)}")
            missing.append(path)
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            match = TOKEN.search(line)
            if match and match.group(1) not in samples:
                try:
                    source_path = path.resolve().relative_to(root).as_posix()
                except ValueError:
                    source_path = display_path(path.resolve(), args.redact, root)
                samples[match.group(1)] = {"source": "real_log", "path": source_path, "line": number, "sample": display_row(line.strip(), args.redact)}
    seen = set(samples)
    print(f"logs_scanned={len(logs)} schemas={len(declared)} observed={len(seen)}")
    print("SCHEMA NEVER OBSERVED:")
    for token in sorted(declared - seen):
        print(f"  {token}")
    unknown = seen - declared
    print("OBSERVED WITHOUT SCHEMA:")
    for token in sorted(unknown):
        print(f"  {token}")
    if missing:
        print(f"ERROR missing_logs={len(missing)}; no samples manifest written")
        return 2
    if args.samples_output:
        output = args.samples_output if args.samples_output.is_absolute() else root / args.samples_output
        aliased = output_aliases(output, [*logs, validator])
        if aliased is not None:
            parser.error(f"--samples-output aliases an input; refusing to overwrite it: {aliased}")
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
        print(f"sample_manifest={display_path(output, args.redact, root)} real={len(declared & seen)} missing={len(declared - seen)}")
    return 1 if unknown else 0


if __name__ == "__main__":
    raise SystemExit(main())
