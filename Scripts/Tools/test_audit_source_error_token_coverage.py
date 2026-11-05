import tempfile
import unittest
from pathlib import Path

from audit_source_error_token_coverage import render, scan


class SourceErrorTokenCoverageTests(unittest.TestCase):
    def test_inventory_links_error_tokens_to_literal_test_references(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, tests = root / "Source", root / "Tests"
            source.mkdir()
            tests.mkdir()
            (source / "Example.cpp").write_text(
                'Error = TEXT("Example.BadInput: detail");\n'
                'OutError = TEXT("Example.WrongThread");\n'
                'const TCHAR* Name = TEXT("NotAnError.Token");\n'
                '// Error = TEXT("Comment.Only");\n', encoding="utf-8")
            (tests / "ExampleTests.cpp").write_text(
                'TestEqual(TEXT("token"), Error, FString(TEXT("Example.BadInput")));\n', encoding="utf-8")
            rows = scan(source, tests)
            self.assertEqual({"Example.BadInput", "Example.WrongThread"}, set(rows))
            self.assertEqual(["Example.BadInput"], [k for k, v in rows.items() if v["tests"]])
            report = render(rows)
            self.assertIn("NO LITERAL TEST REFERENCE — coverage unresolved", report)
            self.assertIn("does not prove the test reaches", report)


if __name__ == "__main__":
    unittest.main()
