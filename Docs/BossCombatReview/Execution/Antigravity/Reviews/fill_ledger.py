#!/usr/bin/env python3
"""fill_ledger.py - Populates and validates combat measurement ledgers from visual frame milestones.

Given frame markers (W, C, A, E, R, RE), clip ID, and confidence, automatically computes
original timestamps, combat timestamps, and canonical evidence PNG filenames, updates
the output ledger (never mutating the template), and executes ingest validation.

Arithmetic:
  t_*_orig   = round(combat_zero + (frame - 1) / fps, 3)
  t_*_combat = round(t_*_orig - combat_zero, 3)

Validation & Safety:
  - Refuses unknown clip ref_id.
  - Refuses --out path identical to template --ledger.
  - Refuses overwriting an already-filled clip unless --force is passed.
  - Enforces milestone sequence: W < C <= A <= E < R <= RE.
  - Validates confidence against ('high', 'medium', 'low').
  - Runs ingest_measurements.validate_entry and prints derived card proposal.

Usage:
  python -I fill_ledger.py --ledger D2_MEASUREMENT_LEDGER.json \
      --out Docs/BossCombatReview/Execution/Claude/D3/D3_MEASURED_LEDGER.json \
      --clip REF_CurvedSwordCombo_Chain1 \
      --W 447 --C 456 --A 465 --E 472 --R 479 --RE 500 \
      --confidence high --notes "camera: unobstructed track" --evidence auto
"""

import argparse
import copy
import json
import os
import sys

# Ensure local imports work under python -I
sys.path.insert(0, os.path.dirname(__file__))

from ingest_measurements import (
    FPS,
    COMBAT_ZERO,
    DEFAULT_CARDS_DIR,
    validate_entry,
    derive_card_proposal
)

DEFAULT_TEMPLATE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "D2_MEASUREMENT_LEDGER.json")
)
DEFAULT_OUT = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        "..", "..", "Claude", "D3", "D3_MEASURED_LEDGER.json"
    )
)


def compute_stage_timestamps(frame: int, fps: float = FPS, combat_zero: float = COMBAT_ZERO):
    """Computes (t_orig, t_combat) from frame index using canonical D1 formula."""
    t_orig = round(combat_zero + (frame - 1) / fps, 3)
    t_combat = round(t_orig - combat_zero, 3)
    return t_orig, t_combat


def fill_clip_entry(
    entry: dict,
    W: int,
    C: int,
    A: int,
    E: int,
    R: int,
    RE: int,
    confidence: str,
    notes: str = None,
    evidence_mode: str = "auto",
    fps: float = FPS,
    combat_zero: float = COMBAT_ZERO
) -> dict:
    """Fills milestone frames, timestamps, evidence, and confidence into entry dictionary."""
    # Enforce milestone ordering
    if not (W < C <= A <= E < R <= RE):
        raise ValueError(
            f"Invalid frame order: expected W < C <= A <= E < R <= RE, "
            f"got W={W}, C={C}, A={A}, E={E}, R={R}, RE={RE}"
        )

    # Validate confidence
    if confidence not in ("high", "medium", "low"):
        raise ValueError(
            f"Invalid confidence '{confidence}'. Must be 'high', 'medium', or 'low'."
        )

    frames = {"W": W, "C": C, "A": A, "E": E, "R": R, "RE": RE}
    for tag, f in frames.items():
        t_orig, t_combat = compute_stage_timestamps(f, fps=fps, combat_zero=combat_zero)
        entry[f"{tag}_frame"] = f
        entry[f"t_{tag}_orig"] = t_orig
        entry[f"t_{tag}_combat"] = t_combat

    # Evidence filenames
    if evidence_mode == "auto":
        evidence_list = [f"morgott_c0_{f:05d}.png" for f in frames.values()]
        entry["evidence_pngs"] = evidence_list
    elif isinstance(evidence_mode, str):
        entry["evidence_pngs"] = [s.strip() for s in evidence_mode.split(",") if s.strip()]

    entry["confidence"] = confidence
    if notes is not None:
        entry["notes"] = notes

    return entry


def process_ledger_fill(
    ledger_path: str,
    out_path: str,
    clip_id: str,
    W: int,
    C: int,
    A: int,
    E: int,
    R: int,
    RE: int,
    confidence: str,
    notes: str = None,
    evidence: str = "auto",
    force: bool = False,
    fps: float = FPS,
    combat_zero: float = COMBAT_ZERO,
    cards_dir: str = DEFAULT_CARDS_DIR
):
    """Loads ledger, fills entry, executes ingest validation, and writes output."""
    abs_ledger = os.path.abspath(ledger_path)
    abs_out = os.path.abspath(out_path)

    # Safety check: out path cannot mutate template
    if abs_ledger == abs_out:
        raise ValueError(
            f"Safety violation: --out path '{out_path}' is identical to template '{ledger_path}'. "
            f"The template ledger must never be overwritten."
        )

    # Initialize ledger data: load existing out_path if present, else copy from template
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as fp:
            ledger_data = json.load(fp)
    else:
        if not os.path.exists(ledger_path):
            raise FileNotFoundError(f"Template ledger '{ledger_path}' not found.")
        with open(ledger_path, "r", encoding="utf-8") as fp:
            ledger_data = json.load(fp)

    entries = ledger_data.get("entries", [])
    target_entry = None
    for e in entries:
        if e.get("ref_id") == clip_id:
            target_entry = e
            break

    if target_entry is None:
        raise ValueError(f"Clip '{clip_id}' not found in ledger '{ledger_path}'.")

    # Refuse overwriting an already-filled clip unless --force is passed
    if target_entry.get("W_frame") is not None and not force:
        raise ValueError(
            f"Clip '{clip_id}' is already filled in ledger (W={target_entry.get('W_frame')}). "
            f"Pass --force to overwrite."
        )

    # Fill milestone frames and compute arithmetic
    fill_clip_entry(
        entry=target_entry,
        W=W, C=C, A=A, E=E, R=R, RE=RE,
        confidence=confidence,
        notes=notes,
        evidence_mode=evidence,
        fps=fps,
        combat_zero=combat_zero
    )

    # Execute strict ingest validation on updated entry
    validate_entry(target_entry, fps=fps, combat_zero=combat_zero, cards_dir=cards_dir)

    # Ensure output parent directory exists
    out_dir = os.path.dirname(abs_out)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Write out updated ledger with pure CRLF
    content = json.dumps(ledger_data, indent=2) + "\n"
    content = content.replace("\r\n", "\n").replace("\n", "\r\n")
    with open(out_path, "wb") as fp:
        fp.write(content.encode("utf-8"))

    # Derive card proposal
    proposal = derive_card_proposal(target_entry, fps=fps)
    return proposal


def main():
    parser = argparse.ArgumentParser(
        description="Fills combat milestones into measurement ledger and validates card proposal."
    )
    parser.add_argument(
        "--ledger", default=DEFAULT_TEMPLATE,
        help="Path to template ledger JSON (default: D2_MEASUREMENT_LEDGER.json)."
    )
    parser.add_argument(
        "--out", default=DEFAULT_OUT,
        help="Path to destination ledger JSON (must not equal --ledger)."
    )
    parser.add_argument(
        "--clip", required=True,
        help="Reference clip identifier (e.g. REF_CurvedSwordCombo_Chain1)."
    )
    parser.add_argument("--W", type=int, required=True, help="Windup start frame.")
    parser.add_argument("--C", type=int, required=True, help="Cancel window start frame.")
    parser.add_argument("--A", type=int, required=True, help="Active hit start frame.")
    parser.add_argument("--E", type=int, required=True, help="Active hit end frame.")
    parser.add_argument("--R", type=int, required=True, help="Recovery blend start frame.")
    parser.add_argument("--RE", type=int, required=True, help="Recovery complete frame.")
    parser.add_argument(
        "--confidence", required=True, choices=["high", "medium", "low"],
        help="Visual measurement confidence level."
    )
    parser.add_argument("--notes", default=None, help="Camera conditions and observation notes.")
    parser.add_argument(
        "--evidence", default="auto",
        help="Evidence PNG mode: 'auto' (default) or comma-separated filenames."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Permit overwriting an already filled clip entry."
    )
    parser.add_argument("--fps", type=float, default=FPS, help="Frame rate (default: 59.9401).")
    parser.add_argument(
        "--combat-zero", type=float, default=COMBAT_ZERO,
        help="Combat zero offset in seconds (default: 105.0)."
    )

    args = parser.parse_args()

    try:
        proposal = process_ledger_fill(
            ledger_path=args.ledger,
            out_path=args.out,
            clip_id=args.clip,
            W=args.W, C=args.C, A=args.A, E=args.E, R=args.R, RE=args.RE,
            confidence=args.confidence,
            notes=args.notes,
            evidence=args.evidence,
            force=args.force,
            fps=args.fps,
            combat_zero=args.combat_zero
        )
        print(f"SUCCESS: Clip '{args.clip}' filled and validated in '{args.out}'.")
        print("Card Proposal:")
        print(json.dumps(proposal, indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"REFUSAL: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
