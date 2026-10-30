#!/usr/bin/env python3
"""
verify_a297_dashboard_and_design.py
Offline verification of Documentation/TASKS.md Dashboard and F6B_RESET_AND_PHASE_DATA_DESIGN.md.
Updated per Lead Review C-419 with strict assertion of 6 factual corrections.
"""
from pathlib import Path

TASKS_PATH = Path("Documentation/TASKS.md")
DESIGN_PATH = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/F6B_RESET_AND_PHASE_DATA_DESIGN.md")

REQUIRED_DASHBOARD_TOKENS = [
    "Track A (Data-Driven Boss Platform - 7 tasks)",
    "Track B (83 Requirements - 82 Framework Rows)",
    "Tracks C & D (Editor Tools & Reference Boss - 10 tasks)",
    "Framework Delivery Slices Proved (F1 to F6a)",
    "SavedProductionPreflight",
    "Source/OneBossFight/Player/RPGBossMoveCard.h",
    "Source/OneBossFight/Player/RPGBossMoveModel.h",
    "full2_raw.log",
    "grade_f3d_log.py",
    "KI-146",
    "grade_f5_log.py",
    "INJECTED hits",
    "grade_f6a_log.py",
    "c1_full_raw.log:3956",
    "Display: **** TEST COMPLETE. EXIT CODE: 0 ****",
    "Open Owner Decisions",
    "KI-143",
]

FORBIDDEN_DASHBOARD_TOKENS = [
    "cycle2_attempt1",
    "Dodge Invariant",
    "dodge_run1",
    "final_f5_run1",
    "c1_full_raw.log:1286-1300",
]

REQUIRED_DESIGN_TOKENS = [
    "## 1. Executive Summary & Purpose",
    "## 2. Framework Boss Generation Reset Semantics",
    "## 3. Trigger Authority: Fixture Call vs Player",
    "## 4. Witness Log Lines & Requirement Mapping",
    "## 5. Minimal Phase Authority Data Fields for Profile",
    "## 6. Honest Unknowns & UNVERIFIED Items",
    "PhaseThresholdFractions",
    "PhaseTransitionMontages",
    "PhaseTransitionDurationSeconds",
    "bPhaseTransitionRequiresNeutral",
    "RestartEncounterForTest",
    "BOSS-EXE-001",
    "BOSS-DEF-001",
    "[UNVERIFIED - Blend-Out Tail on Transition Montages]",
]

CITED_LINES = [
    (Path("Source/OneBossFight/Player/RPGDamageResolver.cpp"), 42, "if (ProviderGeneration)"),
    (Path("Source/OneBossFight/Player/RPGBossRules.h"), 77, "if (F.bPhaseTwo) { return ETransitionResult::AlreadyDone; }"),
    (Path("Source/OneBossFight/Player/RPGBossEncounter.cpp"), 313, "++Generation;"),
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
    print(" VERIFYING A-297 DASHBOARD UPDATE (C-419 CORRECTIONS) & F6B DESIGN")
    print("================================================================================")

    check_crlf(TASKS_PATH)
    check_crlf(DESIGN_PATH)

    tasks_text = TASKS_PATH.read_text(encoding="utf-8")
    for tok in REQUIRED_DASHBOARD_TOKENS:
        assert tok in tasks_text, f"Missing required dashboard token in TASKS.md: {tok}"
        print(f"[OK] TASKS.md dashboard verified: '{tok[:45]}'")

    for tok in FORBIDDEN_DASHBOARD_TOKENS:
        assert tok not in tasks_text, f"Forbidden legacy/erroneous token found in TASKS.md: {tok}"
        print(f"[OK] Forbidden token absent: '{tok}'")

    design_text = DESIGN_PATH.read_text(encoding="utf-8")
    for tok in REQUIRED_DESIGN_TOKENS:
        assert tok in design_text, f"Missing required design token in F6B doc: {tok}"
        print(f"[OK] F6B design verified: '{tok[:45]}'")

    for path, line_no, token in CITED_LINES:
        assert path.is_file(), f"Source file missing: {path}"
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        assert line_no <= len(lines), f"Line {line_no} out of range in {path} (total {len(lines)})"
        line_text = lines[line_no - 1]
        assert token in line_text, f"Token '{token}' not found on line {line_no} of {path.name} (found: '{line_text.strip()}')"
        print(f"[OK] Citation {path.name}:{line_no} verified: '{token[:40]}'")

    print("\n================================================================================")
    print(" ALL DASHBOARD ENTRIES, F6B DESIGN SECTIONS & CITATIONS 100% VERIFIED OFFLINE")
    print("================================================================================")


if __name__ == "__main__":
    main()
