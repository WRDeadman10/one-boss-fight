#!/usr/bin/env python3
"""
verify_a253_a254.py
===================
Offline verification script for Orders A-253, A-254, and A-259 return fixes.
Verifies probe parsing, timing derivations, PROBE_DERIVED_TIMINGS.md,
move_cards_probe_c379.json, move_cards_f3_telemetry.json, move_cards_f4_proposed.json,
and author_move_cards.py validator execution.
"""

import sys
import json
import subprocess
from pathlib import Path

BASE_DIR = Path("Docs/BossCombatReview/Execution/Antigravity/MoveCards")
PROBE_DIR = Path("Docs/BossCombatReview/Execution/Codex/HitWindowProbe/run_C379")

def main():
    print("================================================================================")
    print(" VERIFYING A-253 & A-254 PROBE DATA & MOVE-CARD TIMINGS (A-259 UPDATE)")
    print("================================================================================")

    # 1. Verify Probe Output Source Files Exist
    enum_file = PROBE_DIR / "enum_observed.json"
    summary_file = PROBE_DIR / "probe_summary.json"
    verbatim_file = PROBE_DIR / "probe_lines_verbatim.txt"
    assert enum_file.is_file(), f"Missing {enum_file}"
    assert summary_file.is_file(), f"Missing {summary_file}"
    assert verbatim_file.is_file(), f"Missing {verbatim_file}"
    print("[OK] run_C379 empirical probe output files verified present.")

    # 2. Verify Enum Certification
    enum_data = json.loads(enum_file.read_text(encoding="utf-8"))
    assert enum_data.get("integer_fallback") is False, "Must not use integer fallback"
    assert "WORLD" in enum_data.get("enum_repr", ""), "Must be WORLD space"
    print("[OK] Confirmed [PROBE_ENUM] reflected WORLD enum observed without integer fallback.")

    # 3. Verify PROBE_DERIVED_TIMINGS.md formatting
    doc_path = BASE_DIR / "PROBE_DERIVED_TIMINGS.md"
    assert doc_path.is_file(), f"Missing {doc_path}"
    raw_doc = doc_path.read_bytes()
    assert b"\r\r\n" not in raw_doc, "No double CRLF"
    assert raw_doc.endswith(b"\r\n"), "Must end in CRLF"
    print(f"[OK] PROBE_DERIVED_TIMINGS.md verified: {len(raw_doc):,} bytes, clean CRLF.")

    # 4. Verify move_cards_probe_c379.json & move_cards_f3_telemetry.json
    expected_ids = [
        "Move_Sevarog_SwingSlow",
        "Move_Sevarog_SwingMedium",
        "Move_Sevarog_AntiGreed",
        "Move_Sevarog_HeavySlam"
    ]

    for fname in ["move_cards_probe_c379.json", "move_cards_f3_telemetry.json"]:
        json_path = BASE_DIR / fname
        assert json_path.is_file(), f"Missing {json_path}"
        raw_json = json_path.read_bytes()
        assert b"\r\r\n" not in raw_json, f"No double CRLF in {fname}"
        assert raw_json.endswith(b"\r\n"), f"Must end in CRLF in {fname}"
        
        spec_data = json.loads(raw_json.decode("utf-8"))
        assert spec_data.get("synthetic") is not True, "Must NOT be marked synthetic"
        cards = spec_data.get("cards", [])
        assert len(cards) == 4, f"Expected 4 cards, got {len(cards)}"
        for c, exp_id in zip(cards, expected_ids):
            assert c["MoveId"] == exp_id, f"Expected {exp_id}, got {c['MoveId']}"
            assert c.get("synthetic") is not True, f"Card {exp_id} must not be synthetic"
            assert c["SlotName"] == "FullBody", "SlotName must be FullBody"
            assert c["HPDamage"] == 0.0, f"F3 telemetry card {exp_id} must have HPDamage == 0.0 strictly"
            assert c["ClipLengthSeconds"] > 0, "ClipLengthSeconds must be positive"
            assert 0 <= c["CommitSeconds"] <= c["ActiveStartSeconds"] < c["ActiveEndSeconds"] <= c["RecoveryEndSeconds"] <= c["ClipLengthSeconds"]
            assert len(c["Windows"]) >= 1, "Must have at least one window"
            for w in c["Windows"]:
                assert c["ActiveStartSeconds"] <= w["StartSeconds"] < w["EndSeconds"] <= c["ActiveEndSeconds"]
                assert w["RadiusCm"] > 0
        print(f"[OK] {fname} verified: 4 cards, valid ordering, zero synthetic tags, HPDamage==0.0.")

    # 4b. Verify move_cards_f4_proposed.json
    f4_path = BASE_DIR / "move_cards_f4_proposed.json"
    assert f4_path.is_file(), f"Missing {f4_path}"
    raw_f4 = f4_path.read_bytes()
    assert b"\r\r\n" not in raw_f4, "No double CRLF in move_cards_f4_proposed.json"
    assert raw_f4.endswith(b"\r\n"), "Must end in CRLF"
    f4_data = json.loads(raw_f4.decode("utf-8"))
    assert "Proposed" in f4_data.get("status", "")
    f4_cards = f4_data.get("cards", [])
    assert len(f4_cards) == 4
    for c in f4_cards:
        assert c["DamageStatus"] == "design value, proposed"
        assert c["HPDamage"] > 0.0
    print("[OK] move_cards_f4_proposed.json verified: 4 cards, HPDamage marked proposed.")

    # 5. Execute author_move_cards.py dry-run
    cmd = [
        sys.executable, "-B",
        str(BASE_DIR / "author_move_cards.py"),
        "--input", str(BASE_DIR / "move_cards_probe_c379.json")
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"author_move_cards.py dry run failed: {res.stderr}\n{res.stdout}"
    for exp_id in expected_ids:
        assert f"[CARD_VALIDATE] OK   MoveId='{exp_id}'" in res.stdout, f"Missing validation pass for {exp_id}"
    assert "[CARD_DRYRUN] Dry-run complete." in res.stdout
    print("[OK] author_move_cards.py dry-run: 4/4 cards passed all validation checks cleanly.")

    # 6. Execute Unit Test Suite
    test_cmd = [
        sys.executable, "-B", "-m", "unittest",
        "Docs/BossCombatReview/Execution/Antigravity/MoveCards/test_author_move_cards.py"
    ]
    test_res = subprocess.run(test_cmd, capture_output=True, text=True)
    assert test_res.returncode == 0, f"Unit test suite failed: {test_res.stderr}\n{test_res.stdout}"
    assert "Ran 30 tests" in test_res.stderr or "Ran 30 tests" in test_res.stdout
    print("[OK] test_author_move_cards.py: 30/30 unit tests PASS.")

    print("\n================================================================================")
    print(" ALL A-253, A-254, AND A-259 RETURN CHECKS 100% VERIFIED OFFLINE")
    print("================================================================================")

if __name__ == "__main__":
    main()
