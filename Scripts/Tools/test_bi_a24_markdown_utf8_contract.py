import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "Documentation"


class BiA24MarkdownUtf8ContractTest(unittest.TestCase):
    def test_all_documentation_markdown_files_decode_strictly_as_utf8(self) -> None:
        md_files = sorted(DOCS_DIR.rglob("*.md"))
        self.assertGreaterEqual(len(md_files), 1230)
        offenders = []
        for md_path in md_files:
            raw = md_path.read_bytes()
            if b"\x00" in raw or raw.startswith((b"\xff\xfe", b"\xfe\xff")):
                offenders.append((md_path.relative_to(REPO_ROOT).as_posix(), "utf16_or_nul"))
                continue
            try:
                raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                offenders.append((md_path.relative_to(REPO_ROOT).as_posix(), str(exc)))
        self.assertEqual(offenders, [], f"Non-UTF8 markdown files found: {offenders}")


if __name__ == "__main__":
    unittest.main()
