import hashlib
from pathlib import Path
import tempfile
import unittest
from verify_bundle import EvidenceError, parse_receipt, verify_receipt, summarize_automation, parse_job_record

HERE = Path(__file__).resolve().parent


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="owned_fixture_", dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.payload = self.root / "payload.txt"
        self.payload.write_bytes(b"evidence\r\n")
        self.sha = hashlib.sha256(self.payload.read_bytes()).hexdigest()
        self.receipt = self.root / "receipt.txt"

    def test_both_receipt_formats_and_spaces(self):
        self.receipt.write_text(self.sha + " *payload.txt\n")
        self.assertTrue(verify_receipt(self.receipt, self.root, self.root)["all_verified"])
        self.payload.rename(self.root / "has spaces.txt")
        self.receipt.write_text(self.sha + " 10 has spaces.txt\n")
        self.assertTrue(verify_receipt(self.receipt, self.root, self.root)["all_verified"])

    def test_hash_and_size_drift(self):
        self.receipt.write_text(self.sha + " 99 payload.txt\n")
        self.assertFalse(verify_receipt(self.receipt, self.root, self.root)["all_verified"])
        self.receipt.write_text("0" * 64 + " *payload.txt\n")
        self.assertFalse(verify_receipt(self.receipt, self.root, self.root)["all_verified"])

    def test_missing_is_not_success(self):
        self.receipt.write_text(self.sha + " *missing.txt\n")
        self.assertEqual(verify_receipt(self.receipt, self.root, self.root)["checks"][0]["status"], "missing")

    def test_path_escape_and_absolute_rejected(self):
        for name in ["../outside.txt", "/absolute.txt", "C:\\outside.txt", "\\\\server\\share"]:
            self.receipt.write_text(self.sha + " *" + name + "\n")
            with self.subTest(name=name), self.assertRaises(EvidenceError):
                verify_receipt(self.receipt, self.root, self.root)

    def test_canonical_duplicate_rejected(self):
        self.receipt.write_text(self.sha + " *payload.txt\n" + self.sha + " *./payload.txt\n")
        with self.assertRaisesRegex(EvidenceError, "Duplicate"):
            verify_receipt(self.receipt, self.root, self.root)

    def test_malformed_and_empty_receipts(self):
        for text in ["", "# comment", "not a receipt", self.sha + " *"]:
            with self.subTest(text=text), self.assertRaises(EvidenceError):
                parse_receipt(text)

    def test_log_duplicate_failures_and_warning_text(self):
        self.payload.write_text(
            "Test Completed. Result={Success} Name={A} Path={Suite.A}\n"
            "Test Completed. Result={Fail} Name={A} Path={Suite.A}\n"
            "LogTrace: Warning: embedded Error: text is still warning severity\n"
            "LogTest: Error: actual severity\n")
        result = summarize_automation(self.payload, self.root)
        self.assertEqual((result["completed"], result["unique"]), (2, 1))
        self.assertEqual(result["failures"], ["Suite.A"])
        self.assertEqual(result["duplicate_completions"], ["Suite.A"])
        self.assertEqual((result["warning_severity_lines"], result["error_severity_lines"]), (1, 1))

    def test_job_requires_single_explicit_exit(self):
        self.payload.write_text("start date\nend date exit 6 seconds 9\n")
        self.assertEqual(parse_job_record(self.payload, self.root)["exit_code"], 6)
        self.payload.write_text("maybe passed\n")
        with self.assertRaises(EvidenceError):
            parse_job_record(self.payload, self.root)
        self.payload.write_text("end date exit 0 seconds 1\nend date exit 0 seconds 2\n")
        with self.assertRaises(EvidenceError):
            parse_job_record(self.payload, self.root)


if __name__ == "__main__":
    unittest.main()
