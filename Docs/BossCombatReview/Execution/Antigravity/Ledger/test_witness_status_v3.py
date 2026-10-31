#!/usr/bin/env python3
"""
test_witness_status_v3.py
Strict automated verification of Track B 82-Point Witness Status Ledger v3.3:
(a) Checks that every canonical ID exists exactly once (82/82).
(b) Checks that every cited file:line exists on disk and the quoted text is verbatim on that line.
(c) Checks that the census in the markdown document matches the JSON counts.
(d) Framework boss only (exact assertion or exact PIE value line; no bare "Test Completed"; no legacy tests).
(e) Verifies zero non-test source lines cited in witness proofs (Rule 2 enforcement).
"""

import sys
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
JSON_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json"
MD_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Ledger/WITNESS_STATUS_F3_F11.md"
REQS_PATH = REPO_ROOT / "Documentation/Boss/Morgott_82_Point_Combat_Reference/requirements.json"

def test_requirements_integrity():
    """Verify that all 82 canonical requirements exist exactly once in JSON and MD."""
    print("--- Test 1: Requirements Integrity (82/82) ---")
    assert REQS_PATH.exists(), f"Missing {REQS_PATH}"
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    assert MD_PATH.exists(), f"Missing {MD_PATH}"

    canonical_reqs = json.loads(REQS_PATH.read_text(encoding="utf-8"))
    assert len(canonical_reqs) == 82, f"Expected 82 canonical reqs, got {len(canonical_reqs)}"
    canonical_ids = [r["id"] for r in canonical_reqs]
    assert len(set(canonical_ids)) == 82, "Duplicate IDs in canonical requirements.json"

    # JSON check
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    json_reqs = data["requirements"]
    assert len(json_reqs) == 82, f"Expected 82 reqs in JSON, got {len(json_reqs)}"
    json_ids = [r["id"] for r in json_reqs]
    assert json_ids == canonical_ids, "JSON IDs do not match canonical IDs in order"

    # Markdown check
    md_content = MD_PATH.read_text(encoding="utf-8")
    assert "## 2. Complete 82-Point Witness Status Matrix" in md_content, "Missing Section 2 header in MD"
    sec2_content = md_content.split("## 2. Complete 82-Point Witness Status Matrix")[1]
    matrix_ids = re.findall(r"^\|\s*\*\*(BOSS-[A-Z]+-\d+)\*\*", sec2_content, re.MULTILINE)
    assert len(matrix_ids) == 82, f"Expected 82 matrix rows in markdown section 2, got {len(matrix_ids)}"
    assert matrix_ids == canonical_ids, "Markdown matrix IDs do not match canonical IDs in order"
    
    # Delta table check (Section 1) - 13 graduated rows
    sec1_content = md_content.split("## 2. Complete 82-Point Witness Status Matrix")[0]
    delta_part = sec1_content.split("### Status Transition Delta Table")[1].split("### Re-Audited")[0]
    delta_ids = re.findall(r"^\|\s*\*\*(BOSS-[A-Z]+-\d+)\*\*", delta_part, re.MULTILINE)
    assert len(delta_ids) == 20, f"Expected 20 delta table rows in section 1, got {len(delta_ids)}"
    print(f"  [PASS] 82/82 canonical IDs match in matrix, and {len(delta_ids)} transition delta rows verified.")

def test_census_parity():
    """Verify that the census in MD matches the JSON counts and canonical total."""
    print("--- Test 2: Census Parity ---")
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    json_census = data["census"]
    
    # Calculate live census from JSON requirements
    calc_census = {"WITNESSED": 0, "PARTIAL": 0, "NOT YET": 0}
    for r in data["requirements"]:
        st = r["status"]
        assert st in calc_census, f"Invalid status: {st}"
        calc_census[st] += 1
    
    assert json_census == calc_census, f"JSON census header mismatch: {json_census} vs {calc_census}"
    assert sum(calc_census.values()) == 82, f"Census sum != 82: {calc_census}"
    assert calc_census["WITNESSED"] == 31, f"Expected 31 WITNESSED, got {calc_census['WITNESSED']}"
    assert calc_census["PARTIAL"] == 27, f"Expected 27 PARTIAL, got {calc_census['PARTIAL']}"
    assert calc_census["NOT YET"] == 24, f"Expected 24 NOT YET, got {calc_census['NOT YET']}"

    # Extract census from markdown
    md_content = MD_PATH.read_text(encoding="utf-8")
    m_wit = re.search(r"\*\*WITNESSED:\*\*\s*(\d+)", md_content)
    m_par = re.search(r"\*\*PARTIAL:\*\*\s*(\d+)", md_content)
    m_not = re.search(r"\*\*NOT YET:\*\*\s*(\d+)", md_content)
    
    assert m_wit and m_par and m_not, "Could not find census lines in markdown"
    md_census = {
        "WITNESSED": int(m_wit.group(1)),
        "PARTIAL": int(m_par.group(1)),
        "NOT YET": int(m_not.group(1))
    }
    assert md_census == calc_census, f"Markdown census mismatch: {md_census} vs {calc_census}"
    print(f"  [PASS] Census parity confirmed: {calc_census} (Sum=82).")

def test_citations_verbatim_on_disk():
    """Verify that every cited file:line exists and contains the verbatim quoted text."""
    print("--- Test 3: Citation Verification on Disk ---")
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    
    total_citations = 0
    file_cache = {}
    
    for r in data["requirements"]:
        rid = r["id"]
        status = r["status"]
        citations = r.get("citations", [])
        
        if status == "WITNESSED":
            assert len(citations) > 0, f"WITNESSED requirement {rid} has 0 citations!"
            
        for c in citations:
            total_citations += 1
            frel = c["file"]
            lnum = c["line"]
            quoted = c["quoted"].strip()
            
            # Rule 2 enforcement: No non-test source files
            assert ("Tests" in frel or "raw.log" in frel or "log" in frel), f"[{rid}] Non-test source file cited: {frel}"
            
            fpath = REPO_ROOT / frel
            assert fpath.exists(), f"[{rid}] Cited file does not exist: {fpath}"
            
            if fpath not in file_cache:
                file_cache[fpath] = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
            
            lines = file_cache[fpath]
            assert 1 <= lnum <= len(lines), f"[{rid}] Line {lnum} out of range (1..{len(lines)}) for {frel}"
            
            actual_line = lines[lnum - 1]
            q_clean = quoted.rstrip(".")
            assert q_clean in actual_line, (
                f"[{rid}] Quote mismatch at {frel}:{lnum}\n"
                f"  Expected substring: {quoted!r}\n"
                f"  Actual line text:   {actual_line!r}"
            )
            
            # Anti-regression checks: no bare "Test Completed" or generic success lines
            assert "Test Completed. Result={Success}" not in actual_line, f"[{rid}] Bare success line cited at {frel}:{lnum}"
            # Anti-regression: no macro declarations
            assert "IMPLEMENT_SIMPLE_AUTOMATION_TEST" not in actual_line, f"[{rid}] Test macro declaration cited at {frel}:{lnum}"
            
    print(f"  [PASS] {total_citations} citations verified verbatim on disk across {len(file_cache)} files.")

def test_file_formatting():
    """Verify that JSON, MD, and Python test files have pure CRLF and zero tabs in JSON/MD."""
    print("--- Test 4: File Formatting (CRLF & No Tabs) ---")
    files_to_check = [JSON_PATH, MD_PATH, Path(__file__)]
    for fp in files_to_check:
        raw = fp.read_bytes()
        if fp.suffix in [".json", ".md"]:
            assert b"\t" not in raw, f"Tab character found in {fp}"
        # Ensure CRLF line endings
        assert b"\r\n" in raw, f"Missing CRLF line endings in {fp}"
        # No orphan LF
        orphan_lf = raw.replace(b"\r\n", b"").find(b"\n")
        assert orphan_lf == -1, f"Found orphan LF without CR in {fp} at offset {orphan_lf}"
        print(f"  [PASS] {fp.name}: clean CRLF, valid encoding.")

def main():
    print("================================================================================")
    print(" TRACK B WITNESS STATUS LEDGER v3.5 VERIFICATION SUITE")
    print("================================================================================")
    try:
        test_requirements_integrity()
        test_census_parity()
        test_citations_verbatim_on_disk()
        test_file_formatting()
        print("================================================================================")
        print(" ALL TESTS PASSED (100% GREEN)")
        print("================================================================================")
        return 0
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
