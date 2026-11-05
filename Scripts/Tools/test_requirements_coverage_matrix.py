import csv
import json
import os
import unittest


class TestRequirementsCoverageMatrix(unittest.TestCase):
    """
    Validates the 82-requirement combat coverage matrix against witness_status_v3.json
    and confirms that all mapped native automation tests point to real C++ source files.
    """

    def setUp(self):
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.csv_path = os.path.join(self.repo_root, "Documentation", "Boss", "requirements_automation_coverage_matrix.csv")
        self.ledger_path = os.path.join(self.repo_root, "Docs", "BossCombatReview", "Execution", "Antigravity", "Ledger", "witness_status_v3.json")

    def test_matrix_file_exists(self):
        self.assertTrue(os.path.exists(self.csv_path), f"CSV matrix missing at {self.csv_path}")

    def test_ledger_exists(self):
        self.assertTrue(os.path.exists(self.ledger_path), f"Ledger missing at {self.ledger_path}")

    def test_all_82_requirements_mapped(self):
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            ledger_data = json.load(f)
        ledger_req_ids = [r["id"] for r in ledger_data.get("requirements", [])]
        self.assertEqual(len(ledger_req_ids), 82, "Ledger must contain exactly 82 canonical requirements")

        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            csv_rows = list(reader)

        self.assertEqual(len(csv_rows), 82, f"CSV must contain exactly 82 rows, found {len(csv_rows)}")
        csv_req_ids = [row["RequirementID"] for row in csv_rows]

        self.assertEqual(set(ledger_req_ids), set(csv_req_ids), "CSV requirement IDs must match canonical ledger")

    def test_schema_and_source_file_existence(self):
        expected_fields = ["RequirementID", "Section", "Title", "PrimaryAutomationTest", "SourceFile", "CoverageType", "Status"]

        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.assertEqual(reader.fieldnames, expected_fields, "CSV header columns mismatch")

            for row in reader:
                req_id = row["RequirementID"]
                for field in expected_fields:
                    val = row.get(field, "").strip()
                    self.assertTrue(len(val) > 0, f"Empty field '{field}' for {req_id}")

                source_file_rel = row["SourceFile"]
                source_file_abs = os.path.join(self.repo_root, source_file_rel)
                self.assertTrue(os.path.exists(source_file_abs), f"Referenced source file does not exist: {source_file_rel} for {req_id}")

                coverage_type = row["CoverageType"]
                self.assertIn(coverage_type, ["NativeUnit", "NativeAdapter", "NativeIntegration", "AutomationGate"])

                status = row["Status"]
                self.assertIn(status, ["Covered", "Witnessed", "GateEnforced"])


if __name__ == "__main__":
    unittest.main()
