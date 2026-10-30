#!/usr/bin/env python3
"""
verify_a250_witness_plan.py
Offline verification of WITNESS_PLAN_82.md (A-250).
"""

import json
from pathlib import Path

def main():
    print("================================================================================")
    print(" VERIFYING A-250 WITNESS PLAN (82 REQUIREMENTS)")
    print("================================================================================")

    plan_path = Path("Docs/BossCombatReview/Execution/Antigravity/Ledger/WITNESS_PLAN_82.md")
    assert plan_path.is_file(), f"Missing plan file: {plan_path}"

    raw = plan_path.read_bytes()
    assert b"\r\r\n" not in raw, "No double CRLF"
    assert b"\n" in raw, "Must have newlines"
    print(f"[OK] WITNESS_PLAN_82.md raw bytes: {len(raw):,} bytes, clean CRLF")

    # Load canonical requirements
    req_path = Path("Documentation/Boss/Morgott_82_Point_Combat_Reference/requirements.json")
    canonical_reqs = json.loads(req_path.read_text(encoding="utf-8"))
    canonical_ids = {r["id"] for r in canonical_reqs}
    print(f"[OK] Loaded {len(canonical_ids)} canonical requirement IDs from requirements.json")

    # Parse table in WITNESS_PLAN_82.md
    lines = plan_path.read_text(encoding="utf-8").splitlines()
    table_rows = []
    in_table = False
    for line in lines:
        if line.startswith("| Req ID | Title |"):
            in_table = True
            continue
        if in_table and line.startswith("|:---|"):
            continue
        if in_table:
            if not line.startswith("|"):
                in_table = False
                continue
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) == 7:
                table_rows.append(cols)

    print(f"[OK] Parsed {len(table_rows)} requirement rows from Markdown table")
    assert len(table_rows) == 82, f"Expected 82 rows, found {len(table_rows)}"

    # Validate each row
    seen_ids = set()
    for row in table_rows:
        req_id_raw = row[0].replace("*", "")
        assert req_id_raw in canonical_ids, f"Unknown requirement ID: {req_id_raw}"
        assert req_id_raw not in seen_ids, f"Duplicate requirement ID: {req_id_raw}"
        seen_ids.add(req_id_raw)

        # Check fields non-empty
        assert row[1], f"Empty title for {req_id_raw}"
        assert row[2], f"Empty section for {req_id_raw}"
        assert row[3], f"Empty witness step for {req_id_raw}"
        assert row[4], f"Empty witness type for {req_id_raw}"
        assert row[5], f"Empty observable result for {req_id_raw}"
        assert row[6], f"Empty missing gap for {req_id_raw}"

    assert seen_ids == canonical_ids, "Missing some canonical requirement IDs"
    print(f"[OK] All 82 canonical requirement IDs mapped 1:1 without omissions or duplicates")

    # Check that zero requirements are claimed closed/completed
    plan_text = plan_path.read_text(encoding="utf-8")
    for bad_claim in ["completed", "closed", "100% complete", "DONE"]:
        # Only check within table rows
        for row in table_rows:
            assert bad_claim.lower() not in row[3].lower(), f"Forbidden completion claim '{bad_claim}' in step column for {row[0]}"

    print("[OK] Confirmed ZERO completion claims in witness steps")
    print("\n================================================================================")
    print(" WITNESS PLAN 82 VERIFICATION 100% PASS")
    print("================================================================================")

if __name__ == "__main__":
    main()
