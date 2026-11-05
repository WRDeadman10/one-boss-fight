"""scan_doc_citations.py - Scanner to detect uncited measurements in Lane A documents.

Enforces the binding Evidence Rule (C-932):
Every number or percentage in an A- document must cite a source
(file:line, evidence folder, log line, or ledger row) or be labelled PROPOSAL.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
BOSS_DOCS_DIR = REPO_ROOT / "Documentation" / "Boss"

# Regex for empirical measurements
MEASUREMENT_RE = re.compile(
    r"(?:\b\d+(?:\.\d+)?\s*(?:ms|dB|frames?|FPS)\b|\b\d+(?:\.\d+)?\s*%)",
    re.IGNORECASE,
)

# Citation indicators
CITATION_INDICATORS = [
    "PROPOSAL",
    "DESIGN TARGET",
    "file://",
    ".cpp",
    ".h",
    ".ini",
    ".json",
    ".log",
    ".csv",
    ".ps1",
    ".py",
    "evidence",
    "ledger",
    "witness_status",
    "Source/",
    "Config/",
    "Scripts/",
    "Docs/",
    "Documentation/",
    "CVar",
    "rpg.",
    "B_C",
]


def line_has_citation(context_lines: List[str]) -> bool:
    """Return True if any line in context_lines contains a citation or proposal indicator."""
    combined = " ".join(context_lines)
    return any(indicator.lower() in combined.lower() for indicator in CITATION_INDICATORS)


def scan_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """Scan a markdown document and return list of (line_num, match_str, line_text) for uncited claims."""
    findings = []
    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Check if document has global Sources block
    doc_text = "\n".join(lines[:25])
    has_global_sources = "**sources:**" in doc_text.lower() or "## sources" in doc_text.lower()

    for i, line in enumerate(lines):
        line_num = i + 1
        matches = MEASUREMENT_RE.findall(line)
        if not matches:
            continue

        # Look around context: current line +/- 2 lines
        start_idx = max(0, i - 2)
        end_idx = min(len(lines), i + 3)
        context = lines[start_idx:end_idx]

        if not line_has_citation(context) and not has_global_sources:
            findings.append((line_num, ", ".join(matches), line.strip()))

    return findings


def scan_all_va_docs(docs_dir: Path = BOSS_DOCS_DIR) -> dict[str, List[Tuple[int, str, str]]]:
    """Scan all V_A*.md files in the specified directory."""
    results = {}
    pattern = str(docs_dir / "V_A*.md")
    for file_str in sorted(glob.glob(pattern)):
        fp = Path(file_str)
        findings = scan_file(fp)
        if findings:
            results[fp.name] = findings
    return results


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Scan Lane A documents for uncited measurements.")
    parser.add_argument("--check", action="store_true", help="Exit with non-zero code if uncited claims found.")
    parser.add_argument("--dir", type=str, default=str(BOSS_DOCS_DIR), help="Path to Documentation/Boss directory.")
    args = parser.parse_args()

    results = scan_all_va_docs(Path(args.dir))
    total_findings = sum(len(f) for f in results.values())

    print(f"=== Lane A Citation Scanner (Evidence Rule C-932) ===")
    print(f"Scanned directory: {args.dir}")
    print(f"Files with uncited claims: {len(results)}")
    print(f"Total uncited measurement occurrences: {total_findings}\n")

    for fname, findings in results.items():
        print(f"[{fname}] ({len(findings)} uncited claims):")
        for line_num, match_str, text in findings[:5]:
            print(f"  Line {line_num}: [{match_str}] -> {text[:80]}")
        if len(findings) > 5:
            print(f"  ... and {len(findings) - 5} more.")
        print()

    if args.check and total_findings > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
