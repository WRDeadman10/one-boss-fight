#!/usr/bin/env python3
"""D3_findings_table.py - Generates Markdown summary tables from measured combat ledgers.

Reads D3_MEASURED_LEDGER.json, extracts all filled entries, computes phase durations
in frames and seconds, and formats a clean Markdown findings table including ledger priority,
confidence levels, and camera/observability notes.

Run: python -I D3_findings_table.py [path_to_ledger.json]
"""

import json
import os
import sys

DEFAULT_LEDGER = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "Claude", "D3", "D3_MEASURED_LEDGER.json"
    )
)
FPS = 59.9401

MEASUREMENT_FIELDS = [
    "t_W_orig", "t_W_combat", "t_C_orig", "t_C_combat",
    "t_A_orig", "t_A_combat", "t_E_orig", "t_E_combat",
    "t_R_orig", "t_R_combat", "t_RE_orig", "t_RE_combat",
    "W_frame", "C_frame", "A_frame", "E_frame", "R_frame", "RE_frame",
    "evidence_pngs", "confidence"
]


def is_entry_filled(entry):
    """Returns True if entry has measurement fields populated."""
    return not all(entry.get(f) is None for f in MEASUREMENT_FIELDS)


def compute_entry_metrics(entry, fps=FPS):
    """Computes frame deltas and timing in seconds for a filled entry."""
    W = entry["W_frame"]
    C = entry["C_frame"]
    A = entry["A_frame"]
    E = entry["E_frame"]
    R = entry["R_frame"]
    RE = entry["RE_frame"]

    windup_f = A - W
    active_f = E - A
    recovery_f = RE - E
    tail_f = RE - R
    total_f = RE - W

    windup_s = round(windup_f / fps, 4)
    active_s = round(active_f / fps, 4)
    recovery_s = round(recovery_f / fps, 4)
    tail_s = round(tail_f / fps, 4)
    total_s = round(total_f / fps, 4)

    return {
        "priority": entry.get("priority", 0),
        "ref_id": entry["ref_id"],
        "orig_id": entry["ref_to_original"],
        "attack_family": entry.get("attack_family", ""),
        "confidence": entry.get("confidence", "unknown"),
        "notes": entry.get("notes", ""),
        "W": W, "C": C, "A": A, "E": E, "R": R, "RE": RE,
        "windup_f": windup_f, "windup_s": windup_s,
        "active_f": active_f, "active_s": active_s,
        "recovery_f": recovery_f, "recovery_s": recovery_s,
        "tail_f": tail_f, "tail_s": tail_s,
        "total_f": total_f, "total_s": total_s,
    }


def generate_markdown_table(ledger_data, fps=FPS):
    """Generates Markdown table string from ledger data."""
    entries = ledger_data.get("entries", [])
    filled = [e for e in entries if is_entry_filled(e)]
    if not filled:
        return "No measured clips populated in ledger.\n"

    rows = [compute_entry_metrics(e, fps=fps) for e in filled]

    lines = []
    lines.append("| Ledger priority | Reference ID | Original Move ID | Key Frames (W/C/A/E/R/RE) | Windup | Active | Recovery | Total | Confidence | Camera & Observation Notes |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for r in rows:
        frames_str = f"W={r['W']} C={r['C']} A={r['A']} E={r['E']} R={r['R']} RE={r['RE']}"
        windup_str = f"{r['windup_s']:.4f}s ({r['windup_f']}f)"
        active_str = f"{r['active_s']:.4f}s ({r['active_f']}f)"
        recovery_str = f"{r['recovery_s']:.4f}s ({r['recovery_f']}f)"
        total_str = f"{r['total_s']:.4f}s ({r['total_f']}f)"
        clean_notes = r["notes"].replace("|", "\\|").replace("\r", " ").replace("\n", " ")

        line = f"| {r['priority']} | `{r['ref_id']}` | `{r['orig_id']}` | {frames_str} | {windup_str} | {active_str} | {recovery_str} | {total_str} | **{r['confidence']}** | {clean_notes} |"
        lines.append(line)

    return "\n".join(lines) + "\n"


def main():
    ledger_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LEDGER
    if not os.path.exists(ledger_path):
        print(f"Error: Ledger file '{ledger_path}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(ledger_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    table_md = generate_markdown_table(data, fps=FPS)
    print(table_md)


if __name__ == "__main__":
    main()
