#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
generate_not_yet_census.py

Generates the exhaustive Track B NOT YET Census Report (Reviews/NOT_YET_CENSUS.md)
by extracting exact IDs, titles, and observables from witness_status_v3.json.
Classifies all 24 NOT YET requirements by Dependency Class, Code Reference, and Engine Cost.
Enforces strict disk citation verification: fails if cited file does not exist, line is past EOF,
or quoted string is not present in that exact line. Unimplemented items use 'no code: <what is missing>'.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
JSON_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json"
OUTPUT_MD = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews/NOT_YET_CENSUS.md"

VALID_DEP_CLASSES = {
    "ENGINE-ONLY",
    "NEEDS ART",
    "NEEDS DESIGN DECISION",
    "NEEDS NEW SYSTEM",
    "PLAYER-SIDE",
}

VALID_COSTS = {"S", "M", "L"}

CENSUS_METADATA = {
    "BOSS-QA-006": {
        "dep_class": "PLAYER-SIDE",
        "cost": "M",
        "cite": None,
        "explanation": "no code: camera framing and lock-on tracking evaluation requires player follow camera / lock-on system testing",
    },
}

def validate_census_metadata():
    """Validates every citation against disk and checks schema rules."""
    for rid, meta in CENSUS_METADATA.items():
        dep = meta["dep_class"]
        cost = meta["cost"]
        cite = meta["cite"]
        exp = meta["explanation"]

        assert dep in VALID_DEP_CLASSES, f"[{rid}] Invalid dep_class: {dep}"
        assert cost in VALID_COSTS, f"[{rid}] Invalid cost: {cost}"

        if cite is None:
            assert exp.startswith("no code: "), f"[{rid}] Missing 'no code: ' prefix: {exp}"
        else:
            file_rel = cite["file"]
            line_no = cite["line"]
            quote = cite["quote"]

            file_abs = REPO_ROOT / file_rel
            assert file_abs.exists(), f"[{rid}] Cited file does not exist: {file_rel}"

            with open(file_abs, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            assert 1 <= line_no <= len(lines), f"[{rid}] Line {line_no} past EOF ({len(lines)}) in {file_rel}"
            actual_line = lines[line_no - 1]
            assert quote in actual_line, f"[{rid}] Quote mismatch in {file_rel}:{line_no}\nExpected: {quote!r}\nActual:   {actual_line!r}"
            assert len(quote) <= 60, f"[{rid}] Quote exceeds 60 chars ({len(quote)}): {quote!r}"

def main():
    print("--- Validating Census Metadata Against Disk ---")
    validate_census_metadata()
    print("  [PASS] All citations and schemas verified on disk.")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    not_yet_reqs = [r for r in data["requirements"] if r["status"] == "NOT YET"]
    n_reqs = len(not_yet_reqs)
    assert n_reqs == 0, f"Expected exactly 0 NOT YET requirements, found {n_reqs}"

    lines_md = []
    lines_md.append(f"# Track B Remaining Requirements Census: {n_reqs} NOT YET Rows\n")
    lines_md.append("**Document Reference:** `Reviews/NOT_YET_CENSUS.md`  ")
    lines_md.append("**Task Reference:** `[C-565]` / `[C-568]` / `[C-617]` / `[C-621]` (Track B Direction Selection Census)  ")
    lines_md.append("**Source Authority:** `witness_status_v3.json` (exact titles and observables)  ")
    lines_md.append(f"**Total Census:** {n_reqs} requirements currently classified as `NOT YET`  \n")
    lines_md.append("---\n")
    lines_md.append("## 1. Executive Summary & Classification Matrix\n")
    lines_md.append("This document records that 0 requirements remain in `NOT YET` (all 24 canonical NOT YET requirements have graduated to WITNESSED).\n")
    lines_md.append("*(Note: As of BUILD-142, all 24 canonical NOT YET requirements are 100% graduated to WITNESSED; NOT YET census is completely empty.)*\n")
    lines_md.append("### Classification Definitions:")
    lines_md.append("- **ENGINE-ONLY:** Pure C++ / runtime rules or hooks; no art or external system dependencies.")
    lines_md.append("- **NEEDS ART:** Requires animations, montages, notify tracks, VFX/SFX, or arena mesh assets.")
    lines_md.append("- **NEEDS DESIGN DECISION:** Requires designer threshold parameters, precedence rules, or pacing formulas.")
    lines_md.append("- **NEEDS NEW SYSTEM:** Requires an entire unbuilt architectural subsystem (AoE sweeps, memory buffers, grab state machines).")
    lines_md.append("- **PLAYER-SIDE:** Depends on player character combat mechanics, input buffers, or counter-attack intake.\n")
    lines_md.append("### Cost Estimate Scale (in Engine Witness Runs):")
    lines_md.append("- **S (Small):** 1-2 runs; a simple log line, query param, or cvar test hook.")
    lines_md.append("- **M (Medium):** 2-4 runs; a new rule struct/method, unit tests, and live PIE proof scenario.")
    lines_md.append("- **L (Large):** 4+ runs; new multi-component system, asset plumbing, and multi-actor interaction harness.\n")
    lines_md.append("---\n")
    lines_md.append(f"## 2. Complete {n_reqs}-Row NOT YET Census Table\n")
    lines_md.append("| ID | Exact Title | Exact Observable | Dependency Class | Code Reference & Reason | Cost |")
    lines_md.append("|:---|:---|:---|:---:|:---|:---:|")

    print(f"=== TRACK B NOT YET CENSUS ({n_reqs} ROWS) ===")
    print(f"{'ID':<14} | {'Title':<28} | {'Dep Class':<22} | {'Cost':<4} | Details")
    print("-" * 110)

    for r in not_yet_reqs:
        rid = r["id"]
        title = r["title"]
        obs = r["observable"]
        meta = CENSUS_METADATA.get(rid)
        assert meta is not None, f"Missing metadata for {rid}"
        dep = meta["dep_class"]
        cost = meta["cost"]
        cite = meta["cite"]
        exp = meta["explanation"]

        if cite:
            f_rel = cite["file"]
            ln = cite["line"]
            q = cite["quote"]
            cell_detail = f"`{f_rel}:{ln}` quote: `{q}`<br>{exp}"
            summary_log = f"{f_rel}:{ln} quote: \"{q}\" — {exp}"
        else:
            cell_detail = exp
            summary_log = exp

        obs_escaped = obs.replace("|", "\\|")
        lines_md.append(f"| **{rid}** | {title} | {obs_escaped} | `{dep}` | {cell_detail} | **{cost}** |")
        print(f"{rid:<14} | {title:<28} | {dep:<22} | {cost:<4} | {summary_log[:70]}")

    lines_md.append("\n---\n")
    lines_md.append("## 3. Census Distribution Breakdown\n")

    dep_counts = {k: 0 for k in sorted(VALID_DEP_CLASSES)}
    cost_counts = {k: 0 for k in sorted(VALID_COSTS)}
    for r in not_yet_reqs:
        meta = CENSUS_METADATA.get(r["id"])
        if meta:
            dep_counts[meta["dep_class"]] = dep_counts.get(meta["dep_class"], 0) + 1
            cost_counts[meta["cost"]] = cost_counts.get(meta["cost"], 0) + 1

    lines_md.append("### By Dependency Class:")
    if n_reqs == 0:
        lines_md.append("- All dependency classes 100% completed (0 requirements remaining).")
    else:
        for dep, count in sorted(dep_counts.items(), key=lambda x: -x[1]):
            lines_md.append(f"- **{dep}:** {count} requirements ({count/24*100:.1f}%)")

    lines_md.append("\n### By Engine Run Cost:")
    if n_reqs == 0:
        lines_md.append("- All engine cost tiers 100% completed (0 requirements remaining).")
    else:
        for cost, count in sorted(cost_counts.items(), key=lambda x: -x[1]):
            lines_md.append(f"- **Cost {cost}:** {count} requirements ({count/24*100:.1f}%)")

    content_str = "\n".join(lines_md) + "\n"
    with open(OUTPUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(content_str)

    print("-" * 110)
    print(f"Successfully generated {OUTPUT_MD} with pure LF ({n_reqs} rows).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
