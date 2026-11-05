"""Focused fixtures for the documentation link scanner's path/URL boundary."""
import tempfile
import unittest
from pathlib import Path

from check_doc_links import find_broken


class DocLinkScannerFixtures(unittest.TestCase):
    def test_relative_encoded_space_and_fragment_only_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "Documentation"
            (docs / "guides").mkdir(parents=True)
            (docs / "target page.md").write_text("# Present\n", encoding="utf-8")
            (docs / "guides" / "source.md").write_text(
                "[relative](../target%20page.md#not-validated)\n[fragment](#local)\n",
                encoding="utf-8",
            )
            self.assertEqual(find_broken(root), [])

    def test_broken_relative_path_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "Documentation"
            docs.mkdir()
            (docs / "source.md").write_text("[missing](absent%20page.md#section)\n", encoding="utf-8")
            issues = find_broken(root)
        self.assertEqual(len(issues), 1)
        self.assertIn("broken link absent page.md#section", issues[0])

    def test_external_urls_are_skipped_without_network_client_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "Documentation"
            docs.mkdir()
            (docs / "source.md").write_text(
                "[https](https://example.invalid/path)\n[protocol-relative](//example.invalid/path)\n",
                encoding="utf-8",
            )
            self.assertEqual(find_broken(root), [])
        import check_doc_links
        self.assertFalse(hasattr(check_doc_links, "urlopen"))


if __name__ == "__main__":
    unittest.main()
