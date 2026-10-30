"""
Unit test verifying that evidence_sha256.txt contains no empty lines,
has exactly one CRLF per line, and all entries are well-formed.
"""
import os
import unittest
from pathlib import Path


class TestEvidenceReceipt(unittest.TestCase):
    def setUp(self):
        self.toolkit_dir = Path(__file__).resolve().parent
        self.receipt_path = self.toolkit_dir / "evidence_sha256.txt"

    def test_receipt_exists(self):
        self.assertTrue(self.receipt_path.is_file(), "evidence_sha256.txt must exist on disk")

    def test_receipt_has_no_double_carriage_returns(self):
        raw_bytes = self.receipt_path.read_bytes()
        self.assertNotIn(b"\r\r\n", raw_bytes, "Receipt must not contain \\r\\r\\n double carriage returns")
        self.assertNotIn(b"\n\n", raw_bytes, "Receipt must not contain consecutive newlines")

    def test_receipt_has_no_blank_lines(self):
        text = self.receipt_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertGreater(len(lines), 0, "Receipt must not be empty")
        for i, line in enumerate(lines):
            self.assertTrue(line.strip(), f"Line {i+1} in evidence_sha256.txt is blank/empty")
            parts = line.split()
            self.assertEqual(len(parts), 3, f"Line {i+1} must have format <sha256> <size> <path>: {line}")
            self.assertEqual(len(parts[0]), 64, f"Line {i+1} sha256 hex must be 64 characters: {parts[0]}")
            self.assertTrue(parts[1].isdigit(), f"Line {i+1} size must be an integer: {parts[1]}")

    def test_receipt_line_endings_are_crlf(self):
        raw_bytes = self.receipt_path.read_bytes()
        self.assertTrue(raw_bytes.endswith(b"\r\n"), "Receipt must end with \\r\\n")
        for idx, b in enumerate(raw_bytes):
            if b == 0x0A:  # \n
                self.assertGreater(idx, 0, "First byte cannot be newline")
                self.assertEqual(raw_bytes[idx - 1], 0x0D, f"Byte before \\n at index {idx} must be \\r")


if __name__ == "__main__":
    unittest.main()
