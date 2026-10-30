#!/usr/bin/env python3
"""
verify_a305_ki147_analysis.py
Offline verification of KI147_ANTIGREED_MISS_ROOT_CAUSE.md.
"""
from pathlib import Path

DOC_PATH = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/KI147_ANTIGREED_MISS_ROOT_CAUSE.md")

REQUIRED_TOKENS = [
    "## 1. Executive Summary: The ONE Root Cause",
    "## 2. Comparative Evidence from Raw Logs",
    "## 3. Mathematical Proof: Chord Cutting vs Thrust Trajectory",
    "## 4. Heading & Arrival Geometry Analysis",
    "## 5. Falsifiable Check for One More PIE Run",
    "## 6. Recommended Engine-Side Solutions",
    "band_f5_run1",
    "band_f5_run2",
    "band_f5_run3",
    "Linear Socket Interpolation",
    "0.072686",
    "43.90 cm GAP",
    "radius = 42.0 cm",
]

CITED_LINES = [
    (Path("Docs/BossCombatReview/Execution/Claude/F6/band_f5_run1/editor_raw.log"), 1674, "position=0.225264"),
    (Path("Docs/BossCombatReview/Execution/Claude/F6/band_f5_run1/editor_raw.log"), 1675, "position=0.29795"),
    (Path("Docs/BossCombatReview/Execution/Claude/F6/band_f5_run2/editor_raw.log"), 1677, "position=0.265285"),
    (Path("Docs/BossCombatReview/Execution/Claude/F6/band_f5_run3/editor_raw.log"), 1669, "position=0.268453"),
    (Path("Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp"), 150, "const double Span=Position-PrevPosition"),
]


def check_crlf(path: Path):
    assert path.is_file(), f"Missing file: {path}"
    raw = path.read_bytes()
    assert b"\r\r\n" not in raw, f"{path}: double CRLF detected"
    assert b"\n" in raw, f"{path}: no newlines detected"
    assert raw.endswith(b"\r\n"), f"{path}: file does not end with CRLF"
    for idx, b in enumerate(raw):
        if b == 0x0A:
            assert idx > 0 and raw[idx - 1] == 0x0D, f"{path}: invalid bare LF at byte {idx}"
    print(f"[OK] {path.name}: pure CRLF, {len(raw):,} bytes")


def main():
    print("================================================================================")
    print(" VERIFYING KI-147 ROOT CAUSE ANALYSIS (ORDER A-304)")
    print("================================================================================")

    check_crlf(DOC_PATH)

    doc_text = DOC_PATH.read_text(encoding="utf-8")
    for tok in REQUIRED_TOKENS:
        assert tok in doc_text, f"Missing required token in analysis doc: {tok}"
        print(f"[OK] Token verified: '{tok[:45]}'")

    for path, line_no, token in CITED_LINES:
        assert path.is_file(), f"Source file missing: {path}"
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        assert line_no <= len(lines), f"Line {line_no} out of range in {path} (total {len(lines)})"
        line_text = lines[line_no - 1]
        assert token in line_text, f"Token '{token}' not found on line {line_no} of {path.name} (found: '{line_text.strip()}')"
        print(f"[OK] Citation {path.name}:{line_no} verified: '{token[:40]}'")

    print("\n================================================================================")
    print(" ALL KI-147 ANALYSIS CITATIONS & SECTIONS 100% VERIFIED OFFLINE")
    print("================================================================================")


if __name__ == "__main__":
    main()
