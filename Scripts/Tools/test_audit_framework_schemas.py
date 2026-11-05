"""Synthetic duplicate-schema and regex-looseness fixtures."""
import unittest

from audit_framework_schemas import duplicate_schema_keys, index_problems, numeric_permissiveness_witness, table_token_counts


class FrameworkSchemaAuditTests(unittest.TestCase):
    def test_index_duplicate_counts_are_detected(self):
        table = "| `RESULT` | outcome |\n| `RESULT` | repeated row |\n"
        self.assertEqual(index_problems(table_token_counts(table), {"RESULT", "ERROR"}), (["RESULT"], ["ERROR"]))

    def test_exact_duplicate_is_reported(self):
        source = 'SCHEMAS = {\n    "same": r"^x=\\d+$",\n    "same": r"^x=\\d+$",\n}\n'
        self.assertEqual(duplicate_schema_keys(source), [("same", "exact duplicate", 2, 3)])

    def test_conflicting_duplicate_is_reported_separately(self):
        source = 'SCHEMAS = {\n    "same": r"^x=\\d+$",\n    "same": r"^x=[^ ]+$",\n}\n'
        self.assertEqual(duplicate_schema_keys(source), [("same", "conflicting duplicate", 2, 3)])

    def test_permissive_schema_gets_concrete_malformed_witness(self):
        witness = numeric_permissiveness_witness(r"^rate=[^\s]+$", "rate=0.5")
        self.assertEqual(witness, "rate=NOT_A_NUMBER")

    def test_strict_numeric_pattern_has_no_permissive_witness(self):
        witness = numeric_permissiveness_witness(r"^rate=-?\d+(?:\.\d+)?$", "rate=0.5")
        self.assertIsNone(witness)


if __name__ == "__main__":
    unittest.main()
