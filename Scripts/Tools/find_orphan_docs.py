#!/usr/bin/env python3
"""
Finds unreferenced (.md, .patch, .txt) documents under Documentation/ and Docs/ that are candidates for cleanup.
Rule compliance:
- Never lists raw evidence (directories holding .log, .json, .csv, .png or evidence_sha256.txt).
- Never lists recovery copies (backup, recovery, pre_state, post_state).
- Never lists files modified newer than cutoff (default 2026-11-04 23:59:59).
- Never lists active core docs or files referenced by any active doc, script, C++ source, or ledger.
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

ACTIVE_DOC_PATHS = [
    "CLAUDE.md",
    "Documentation/PROJECT_STATE.md",
    "Documentation/TASKS.md",
    "Documentation/TEST_PLAN.md",
    "Documentation/DECISIONS.md",
    "Documentation/KNOWN_ISSUES.md",
    "Documentation/PERFORMANCE_LOG.md",
    "Documentation/GATE4_RUNBOOK.md",
    "Documentation/BENCHKIT_README.md",
    "Documentation/Boss/QUEUE_U.md",
    "Documentation/Boss/witness_status_v3.json",
]


def collect_active_corpus(root: Path) -> str:
    """Collects text from all active core docs, scripts, sources, and ledger files."""
    texts = []
    # Core active docs
    for rel in ACTIVE_DOC_PATHS:
        p = root / rel
        if p.is_file():
            try:
                texts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass

    # All Scripts and Source files
    for folder in ["Scripts", "Source"]:
        f_path = root / folder
        if f_path.is_dir():
            for p in f_path.rglob("*"):
                if p.is_file():
                    try:
                        texts.append(p.read_text(encoding="utf-8", errors="ignore"))
                    except Exception:
                        pass

    return "\n".join(texts)


def find_evidence_directories(root: Path) -> set[Path]:
    """Finds all directories holding raw evidence files (.log, .json, .csv, .png, evidence_sha256.txt)."""
    evidence_dirs = set()
    exec_root = root / "Docs" / "BossCombatReview" / "Execution"
    if exec_root.is_dir():
        for p in exec_root.rglob("*"):
            if p.is_file():
                name_lower = p.name.lower()
                if name_lower.endswith((".log", ".json", ".csv", ".png")) or name_lower == "evidence_sha256.txt":
                    evidence_dirs.add(p.parent.resolve())
    return evidence_dirs


def is_recovery_or_backup(rel_path: str) -> bool:
    lp = rel_path.lower()
    return any(k in lp for k in ["recovery", "backup", "pre_state", "post_state", "current_log", "current_map", "current_console"])


def classify_category(rel_path: str) -> str:
    norm = rel_path.replace("\\", "/")
    if norm.startswith("Docs/BossCombatReview/ExistingBossAudit"):
        return "Legacy ExistingBossAudit"
    if norm.startswith("Docs/BossCombatReview/Reference"):
        return "Legacy Combat Reference"
    if norm.startswith("Documentation/AG") or norm.startswith("Documentation/Archive/AG"):
        return "Archived Briefs & Reports"
    if norm.startswith("Documentation/Archive"):
        return "Archived Reviews & Queues"
    if norm.startswith("Documentation/Boss"):
        return "Completed Sub-Queue Audits"
    if norm.startswith("Docs/BossCombatReview/Execution"):
        return "Historical Execution Notes"
    return "Other Documentation"


def find_orphans(root_path: Path, cutoff_timestamp: float | None = None) -> list[dict]:
    root = root_path.resolve()
    if cutoff_timestamp is None:
        # Default: end of 2026-11-04
        cutoff_timestamp = datetime.datetime(2026, 11, 4, 23, 59, 59).timestamp()

    active_corpus = collect_active_corpus(root)
    evidence_dirs = find_evidence_directories(root)

    candidates = []
    for search_dir in ["Documentation", "Docs"]:
        dir_p = root / search_dir
        if not dir_p.is_dir():
            continue
        for p in dir_p.rglob("*"):
            if not p.is_file():
                continue
            ext = p.suffix.lower()
            if ext not in [".md", ".patch", ".txt"]:
                continue

            rel = p.relative_to(root).as_posix()

            # Rule b: Never list raw evidence directories
            p_resolved = p.resolve()
            if p_resolved.parent in evidence_dirs or any(parent in evidence_dirs for parent in p_resolved.parents):
                continue

            # Rule b: Never list recovery copies
            if is_recovery_or_backup(rel):
                continue

            # Rule b: Never list anything modified newer than cutoff
            try:
                if p.stat().st_mtime > cutoff_timestamp:
                    continue
            except Exception:
                continue

            # Never list core active docs
            if rel in ACTIVE_DOC_PATHS:
                continue

            # Check references (by relative path or by filename)
            fname = p.name
            if rel in active_corpus or fname in active_corpus:
                continue

            # Unreferenced candidate
            size = p.stat().st_size
            candidates.append({
                "path": rel,
                "filename": fname,
                "size_bytes": size,
                "category": classify_category(rel),
            })

    return sorted(candidates, key=lambda c: c["path"])


def render_markdown_report(orphans: list[dict]) -> str:
    total_count = len(orphans)
    total_bytes = sum(c["size_bytes"] for c in orphans)
    total_kb = total_bytes / 1024.0

    by_cat = {}
    for c in orphans:
        by_cat.setdefault(c["category"], []).append(c)

    lines = [
        "# CL1 Data-Driven Orphan Documentation Audit",
        "",
        f"**Census:** {total_count} candidate orphan documents ({total_kb:.1f} KB / {total_bytes:,} bytes).",
        "**Filter Contract:** Excluded all raw evidence folders, recovery/backup logs, files modified after 2026-11-04, and files referenced by active docs, scripts, C++ sources, or ledger.",
        "",
        "## Summary by Category",
        "",
        "| Category | Count | Total Size (KB) | Example Paths |",
        "|---|---:|---:|---|",
    ]

    for cat in sorted(by_cat.keys()):
        items = by_cat[cat]
        cat_kb = sum(i["size_bytes"] for i in items) / 1024.0
        sample = ", ".join(Path(i["path"]).name for i in items[:3])
        if len(items) > 3:
            sample += f", ... (+{len(items)-3} more)"
        lines.append(f"| {cat} | {len(items)} | {cat_kb:.1f} | `{sample}` |")

    lines.extend([
        "",
        "## Complete Candidate Pool for Lead Approval (CL2 Git Removal)",
        "",
        "| Relative Path | Size (Bytes) | Category |",
        "|---|---:|---|",
    ])

    for c in orphans:
        lines.append(f"| `{c['path']}` | {c['size_bytes']} | {c['category']} |")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Find orphan documentation files.")
    parser.add_argument("--root", default=".", help="Workspace root directory.")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown.")
    parser.add_argument("--cutoff", type=float, default=None, help="Cutoff mtime timestamp.")
    args = parser.parse_args()

    root = Path(args.root)
    orphans = find_orphans(root, args.cutoff)

    if args.json:
        print(json.dumps(orphans, indent=2))
    else:
        print(render_markdown_report(orphans))


if __name__ == "__main__":
    main()
