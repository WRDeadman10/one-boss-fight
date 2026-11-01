#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_generate_not_yet_census.py

Tests generate_not_yet_census.py:
1. Verifies that all 10 entries pass validation on disk.
2. Mutation tests: asserts that validation fails when:
   - file does not exist
   - line number is past EOF
   - quote does not match line content
   - no-code entry lacks 'no code: ' prefix
"""

import sys
import unittest
from pathlib import Path
from copy import deepcopy

# Import generator module
REV_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REV_DIR))
import generate_not_yet_census as gen

class TestNotYetCensus(unittest.TestCase):
    def test_live_metadata_all_pass(self):
        """Current live metadata passes all disk verifications."""
        gen.validate_census_metadata()

    def test_mutation_nonexistent_file(self):
        """Fails when cited file does not exist."""
        saved = deepcopy(gen.CENSUS_METADATA)
        try:
            gen.CENSUS_METADATA["BOSS-MOV-006"]["cite"]["file"] = "Source/NonExistentFile.cpp"
            with self.assertRaises(AssertionError) as ctx:
                gen.validate_census_metadata()
            self.assertIn("Cited file does not exist", str(ctx.exception))
        finally:
            gen.CENSUS_METADATA = saved

    def test_mutation_line_past_eof(self):
        """Fails when cited line is past EOF."""
        saved = deepcopy(gen.CENSUS_METADATA)
        try:
            gen.CENSUS_METADATA["BOSS-MOV-006"]["cite"]["line"] = 99999
            with self.assertRaises(AssertionError) as ctx:
                gen.validate_census_metadata()
            self.assertIn("past EOF", str(ctx.exception))
        finally:
            gen.CENSUS_METADATA = saved

    def test_mutation_quote_mismatch(self):
        """Fails when quote is not in cited line."""
        saved = deepcopy(gen.CENSUS_METADATA)
        try:
            gen.CENSUS_METADATA["BOSS-MOV-006"]["cite"]["quote"] = "NonExistentQuoteString"
            with self.assertRaises(AssertionError) as ctx:
                gen.validate_census_metadata()
            self.assertIn("Quote mismatch", str(ctx.exception))
        finally:
            gen.CENSUS_METADATA = saved

    def test_mutation_missing_no_code_prefix(self):
        """Fails when uncited entry does not begin with 'no code: '."""
        saved = deepcopy(gen.CENSUS_METADATA)
        try:
            gen.CENSUS_METADATA["BOSS-AWR-006"]["explanation"] = "missing prefix"
            with self.assertRaises(AssertionError) as ctx:
                gen.validate_census_metadata()
            self.assertIn("Missing 'no code: ' prefix", str(ctx.exception))
        finally:
            gen.CENSUS_METADATA = saved

    def test_generation_runs_cleanly(self):
        """Main generator runs to completion and produces markdown."""
        ret = gen.main()
        self.assertEqual(ret, 0)
        self.assertTrue(gen.OUTPUT_MD.exists())
        with open(gen.OUTPUT_MD, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("## 2. Complete 10-Row NOT YET Census Table", content)
        self.assertEqual(content.count("| **BOSS-"), 10)

if __name__ == "__main__":
    unittest.main()
