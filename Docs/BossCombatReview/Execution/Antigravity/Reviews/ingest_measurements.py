#!/usr/bin/env python3
"""ingest_measurements.py - Ingests and validates reference combat measurement ledgers.

Reads D2_MEASUREMENT_LEDGER.json or measured ledgers, validates timing constraints, frame formulas,
original move ID conventions, and evidence naming, then outputs card-field proposals
mapped to original move IDs.

Validation Rules:
- Frames must be non-null integers.
- Frame order: W < C <= A <= E < R <= RE.
- RecoveryFrames definition: RE - E (active finish to actionable complete).
- RecoveryTailFrames: RE - R (blend-out / recovery marker to actionable).
- Combat time conversion: t_combat == t_orig - 105.0 (within 1 ms).
- Seconds consistency: elapsed seconds from W must match frame delta / 59.9401 (within 1 ms).
- Frame index formula: frame == round((t_orig - 105.0) * 59.9401) + 1.
- Evidence PNGs must follow 'morgott_c0_NNNNN.png' and match the key frames.
- Confidence: must be one of ('high', 'medium', 'low').
- Move ID conventions:
  * Pattern: ^Move_[A-Za-z0-9]+_[A-Za-z0-9_]+$
  * Forbidden reference names: strictly NO Morgott, REF, or Elden in move IDs.
  * Collision check: collides with Content/OneBossFight/FrameworkProof/Cards/<MoveId>.uasset
    unless id_status == 'existing'.
- Partial ledger support (--partial):
  * Entries whose measurement fields are ALL null are listed as 'pending: <ref_id>' and skipped.
  * Entries with SOME fields null or any inconsistency are still refused.
  * Exits 0 only if every filled entry is valid and at least one is filled.
- Rejection: Refuses entries with null, missing, or inconsistent values (default behavior).
- Clean Output: Emitted proposals contain ONLY original move IDs (strictly no REF_* names),
  and carry the 'DESIGN INPUT (measured from owner footage, observation only)' status.

Run: python -I ingest_measurements.py [--partial] <path_to_ledger.json>
"""

import json
import os
import re
import sys

FPS = 59.9401
COMBAT_ZERO = 105.0
TOLERANCE_SECONDS = 0.001  # 1 millisecond tolerance
PNG_PATTERN = re.compile(r"^morgott_c0_(\d{5})\.png$")
MOVE_ID_PATTERN = re.compile(r"^Move_[A-Za-z0-9]+_[A-Za-z0-9_]+$")
FORBIDDEN_NAME_PATTERN = re.compile(r"morgott|ref|elden", re.IGNORECASE)

DEFAULT_CARDS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "Content", "OneBossFight", "FrameworkProof", "Cards")
)

REQUIRED_TIME_FIELDS = [
    "t_W_orig", "t_W_combat", "t_C_orig", "t_C_combat",
    "t_A_orig", "t_A_combat", "t_E_orig", "t_E_combat",
    "t_R_orig", "t_R_combat", "t_RE_orig", "t_RE_combat"
]
REQUIRED_FRAME_FIELDS = ["W_frame", "C_frame", "A_frame", "E_frame", "R_frame", "RE_frame"]
MEASUREMENT_FIELDS = REQUIRED_TIME_FIELDS + REQUIRED_FRAME_FIELDS + ["evidence_pngs", "confidence"]


def is_entry_unfilled(entry):
    """Returns True if ALL measurement fields are None (unfilled template entry)."""
    return all(entry.get(f) is None for f in MEASUREMENT_FIELDS)


def validate_entry(entry, fps=FPS, combat_zero=COMBAT_ZERO, cards_dir=DEFAULT_CARDS_DIR):
    """Validates a single ledger entry. Raises ValueError if invalid."""
    ref_id = entry.get("ref_id", "UNKNOWN")
    orig_id = entry.get("ref_to_original")
    if not orig_id:
        raise ValueError(f"[{ref_id}] Missing 'ref_to_original' mapping.")

    # Rule (2a): Move ID naming regex
    if not MOVE_ID_PATTERN.match(orig_id):
        raise ValueError(f"[{ref_id}] Invalid move ID format '{orig_id}'. Must match '^Move_[A-Za-z0-9]+_[A-Za-z0-9_]+$'.")

    # Rule (2b): Forbidden reference names in move ID
    if FORBIDDEN_NAME_PATTERN.search(orig_id):
        raise ValueError(f"[{ref_id}] Move ID '{orig_id}' contains forbidden reference name (Morgott/REF/Elden).")

    # Rule (2c): Collision check with existing Cards/.uasset unless id_status == 'existing'
    id_status = entry.get("id_status")
    if id_status not in ("proposed_new", "existing"):
        raise ValueError(f"[{ref_id}] Invalid id_status '{id_status}'. Must be 'proposed_new' or 'existing'.")

    if cards_dir and os.path.isdir(cards_dir):
        card_file = os.path.join(cards_dir, f"{orig_id}.uasset")
        if os.path.exists(card_file) and id_status != "existing":
            raise ValueError(f"[{ref_id}] Move ID '{orig_id}' collides with existing card '{card_file}' but id_status is '{id_status}' (must be 'existing').")

    # Rule: Confidence level validation (high|medium|low per C-494)
    confidence = entry.get("confidence")
    if confidence not in ("high", "medium", "low"):
        raise ValueError(f"[{ref_id}] Invalid or missing confidence '{confidence}'. Must be 'high', 'medium', or 'low'.")

    # Check required fields are present and not null
    for tf in REQUIRED_TIME_FIELDS:
        val = entry.get(tf)
        if val is None:
            raise ValueError(f"[{ref_id}] Time field '{tf}' is null or missing.")
        if not isinstance(val, (int, float)):
            raise ValueError(f"[{ref_id}] Time field '{tf}' must be numeric, got {type(val).__name__}.")

    for ff in REQUIRED_FRAME_FIELDS:
        val = entry.get(ff)
        if val is None:
            raise ValueError(f"[{ref_id}] Frame field '{ff}' is null or missing.")
        if not isinstance(val, int) or isinstance(val, bool):
            raise ValueError(f"[{ref_id}] Frame field '{ff}' must be integer, got {type(val).__name__} ({val}).")

    W = entry["W_frame"]
    C = entry["C_frame"]
    A = entry["A_frame"]
    E = entry["E_frame"]
    R = entry["R_frame"]
    RE = entry["RE_frame"]

    # Frame order rule: W < C <= A <= E < R <= RE
    if not (W < C <= A <= E < R <= RE):
        raise ValueError(f"[{ref_id}] Invalid frame order: expected W < C <= A <= E < R <= RE, got W={W}, C={C}, A={A}, E={E}, R={R}, RE={RE}")

    # Check time conversions: t_combat == t_orig - combat_zero
    stages = [("W", W), ("C", C), ("A", A), ("E", E), ("R", R), ("RE", RE)]
    for tag, frame in stages:
        t_orig = entry[f"t_{tag}_orig"]
        t_cbt = entry[f"t_{tag}_combat"]
        expected_cbt = t_orig - combat_zero
        if abs(t_cbt - expected_cbt) > TOLERANCE_SECONDS:
            raise ValueError(f"[{ref_id}] Combat time mismatch for {tag}: t_combat={t_cbt}, expected t_orig - {combat_zero} = {expected_cbt:.4f}")

        # Check frame index formula: frame == round((t_orig - 105.0) * fps) + 1
        expected_frame = round(expected_cbt * fps) + 1
        if frame != expected_frame:
            raise ValueError(f"[{ref_id}] Frame index formula mismatch for {tag}: frame={frame}, expected round({expected_cbt:.4f} * {fps}) + 1 = {expected_frame}")

        # Check seconds from W match frame delta / fps
        expected_dt_from_W = (frame - W) / fps
        actual_dt_from_W = t_orig - entry["t_W_orig"]
        if abs(actual_dt_from_W - expected_dt_from_W) > TOLERANCE_SECONDS:
            raise ValueError(f"[{ref_id}] Time delta mismatch for {tag}: t_{tag} - t_W = {actual_dt_from_W:.4f} s, but frame delta ({frame} - {W}) / {fps} = {expected_dt_from_W:.4f} s")

    # Validate evidence PNGs
    evidence = entry.get("evidence_pngs")
    if not evidence:
        raise ValueError(f"[{ref_id}] Missing 'evidence_pngs'.")
    if isinstance(evidence, str):
        png_list = [p.strip() for p in evidence.split(",") if p.strip()]
    elif isinstance(evidence, list):
        png_list = evidence
    else:
        raise ValueError(f"[{ref_id}] 'evidence_pngs' must be list or comma-separated string.")

    if len(png_list) < 4:
        raise ValueError(f"[{ref_id}] Expected at least 4 evidence PNGs (for W, A, E, RE), got {len(png_list)}.")

    png_frames = set()
    for png in png_list:
        m = PNG_PATTERN.match(png)
        if not m:
            raise ValueError(f"[{ref_id}] Malformed evidence PNG name '{png}'. Must follow 'morgott_c0_NNNNN.png'.")
        png_frames.add(int(m.group(1)))

    for tag, frame in [("W", W), ("A", A), ("E", E), ("RE", RE)]:
        if frame not in png_frames:
            raise ValueError(f"[{ref_id}] Evidence PNG for stage {tag} (frame {frame:05d}) missing from evidence_pngs.")

    return True


def derive_card_proposal(entry, fps=FPS):
    """Derives clean card-field proposal. Strictly no reference names in output."""
    orig_id = entry["ref_to_original"]
    W = entry["W_frame"]
    A = entry["A_frame"]
    E = entry["E_frame"]
    R = entry["R_frame"]
    RE = entry["RE_frame"]

    active_start_sec = round((A - W) / fps, 4)
    active_end_sec = round((E - W) / fps, 4)
    recovery_end_sec = round((RE - W) / fps, 4)

    # Lead Claude Decision (C-492): RecoveryFrames = RE - E (active finish to actionable complete)
    recovery_frames = RE - E
    recovery_tail_frames = RE - R

    confidence = entry.get("confidence")
    return {
        "MoveId": orig_id,
        "Confidence": confidence,
        "ActiveStartSeconds": active_start_sec,
        "ActiveEndSeconds": active_end_sec,
        "RecoveryEndSeconds": recovery_end_sec,
        "WindupFrames": A - W,
        "ActiveFrames": E - A,
        "RecoveryFrames": recovery_frames,
        "RecoveryTailFrames": recovery_tail_frames,
        "TotalAnimationFrames": RE - W,
        "DesignStatus": "DESIGN INPUT (measured from owner footage, observation only)"
    }


def ingest_ledger(ledger_data, fps=FPS, combat_zero=COMBAT_ZERO, cards_dir=DEFAULT_CARDS_DIR, allow_partial=False):
    """Ingests and validates full ledger dictionary. Returns list of card proposals.

    If allow_partial is True:
    - Entries where ALL measurement fields are None are listed as 'pending: <ref_id>' and skipped.
    - Entries with SOME fields null or any inconsistency are still refused.
    - Exits 0 only if every filled entry is valid and at least one is filled.
    """
    entries = ledger_data.get("entries", [])
    if not entries:
        raise ValueError("Ledger contains no entries.")

    proposals = []
    for entry in entries:
        ref_id = entry.get("ref_id", "UNKNOWN")
        if allow_partial and is_entry_unfilled(entry):
            print(f"pending: {ref_id}")
            continue

        validate_entry(entry, fps=fps, combat_zero=combat_zero, cards_dir=cards_dir)
        proposal = derive_card_proposal(entry, fps=fps)
        proposals.append(proposal)

    if allow_partial and len(proposals) == 0:
        raise ValueError("No filled entries found in ledger (all entries pending).")

    # Sanity check: Ensure strictly NO reference names in proposals
    serialized = json.dumps(proposals)
    if "REF_" in serialized or "Morgott" in serialized or "morgott" in serialized or "Elden" in serialized or "elden" in serialized:
        raise ValueError("Sanity check failed: Reference name leaked into card proposals output!")

    return proposals


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    allow_partial = "--partial" in argv
    clean_argv = [a for a in argv if a != "--partial"]

    if len(clean_argv) < 1:
        print("Usage: python -I ingest_measurements.py [--partial] <path_to_ledger.json>")
        sys.exit(1)

    path = clean_argv[0]
    if not os.path.exists(path):
        print(f"Error: Ledger file '{path}' not found.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        proposals = ingest_ledger(data, allow_partial=allow_partial)
        print(f"Successfully validated {len(proposals)} entries.")
        print(json.dumps(proposals, indent=2))
    except ValueError as e:
        print(f"VALIDATION FAILED: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
