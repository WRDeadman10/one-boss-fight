#!/usr/bin/env python3
"""
test_a6_hardcoded_value_audit.py
Automated test suite verifying the A6 Hardcoded Gameplay Values Audit:
(a) Verifies all 23 hardcoded literal locations exist verbatim on disk.
(b) Verifies Section 2 (Live Framework Code) contains ZERO citations of RPGSevarogDirector.
(c) Verifies file formatting: clean CRLF line endings and zero tabs.
"""

import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
MD_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews/A6_HARDCODED_VALUE_AUDIT.md"

def test_citations_verbatim_on_disk():
    """Verify that every cited file:line exists on disk and contains the verbatim quoted value."""
    print("--- Test 1: Citation Verification on Disk ---")
    assert MD_PATH.exists(), f"Missing audit document: {MD_PATH}"
    content = MD_PATH.read_text(encoding="utf-8")
    
    # Extract table rows with backtick file:line citations
    matches = re.findall(r"^\|\s*`([^`]+):(\d+)`\s*\|\s*`([^`]+)`\s*\|", content, re.MULTILINE)
    assert len(matches) == 23, f"Expected 23 audited citations, found {len(matches)}"
    
    file_cache = {}
    for frel, lnum_str, val in matches:
        lnum = int(lnum_str)
        fpath = REPO_ROOT / frel
        assert fpath.exists(), f"Cited file does not exist: {fpath}"
        
        if fpath not in file_cache:
            file_cache[fpath] = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
            
        lines = file_cache[fpath]
        assert 1 <= lnum <= len(lines), f"Line {lnum} out of range (1..{len(lines)}) for {frel}"
        actual = lines[lnum - 1]
        assert val in actual, f"Value {val!r} not found in {frel}:{lnum}\n  Actual: {actual!r}"
        
    print(f"  [PASS] All {len(matches)} citations verified verbatim on disk across {len(file_cache)} files.")

def test_live_framework_section_purity():
    """Verify that Section 2 (Live Framework Code) contains ZERO citations of RPGSevarogDirector."""
    print("--- Test 2: Live Framework Section Purity ---")
    content = MD_PATH.read_text(encoding="utf-8")
    assert "## 2. Live Framework Code Audit" in content, "Missing Section 2 header"
    assert "## 3. Retired Code Reference" in content, "Missing Section 3 header"
    
    sec2_content = content.split("## 2. Live Framework Code Audit")[1].split("## 3. Retired Code Reference")[0]
    
    # Check that no row in Section 2 cites RPGSevarogDirector
    director_cits = re.findall(r"RPGSevarogDirector", sec2_content)
    assert len(director_cits) == 0, f"Found {len(director_cits)} citations of RPGSevarogDirector in Live Section 2!"
    
    # Count rows in Section 2
    sec2_rows = re.findall(r"^\|\s*`([^`]+):(\d+)`", sec2_content, re.MULTILINE)
    assert len(sec2_rows) == 10, f"Expected 10 rows in Live Section 2, found {len(sec2_rows)}"
    
    print(f"  [PASS] Section 2 verified pure: {len(sec2_rows)} live framework rows, 0 citations of RPGSevarogDirector.")

def test_file_formatting():
    """Verify clean CRLF line endings and zero tabs."""
    print("--- Test 3: Formatting & Hygiene ---")
    raw = MD_PATH.read_bytes()
    assert b"\t" not in raw, f"Tab character found in {MD_PATH}"
    assert b"\r\n" in raw, f"Missing CRLF in {MD_PATH}"
    orphan_lf = raw.replace(b"\r\n", b"").find(b"\n")
    assert orphan_lf == -1, f"Found orphan LF without CR in {MD_PATH} at offset {orphan_lf}"
    print(f"  [PASS] {MD_PATH.name}: clean CRLF, 0 tabs.")

def main():
    print("================================================================================")
    print(" A6 HARDCODED VALUES AUDIT VERIFICATION SUITE")
    print("================================================================================")
    try:
        test_citations_verbatim_on_disk()
        test_live_framework_section_purity()
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
