"""BP-26..30 queued scope (X-2305/X-2307): encoding matrix for line-oriented (log / Markdown) readers.

In-process only under X-2295: no main(), CLI or subprocess. Temp files only.
  1. text_input.read_text_input matrix: plain, UTF-8 BOM, UTF-16 LE/BE with BOM, UTF-16 without BOM, invalid UTF-8
     (strict vs replace), CRLF/CR universal newlines identical to Path.read_text, unreadable path.
  2. scan_doc_citations.scan_all_va_docs on a temp folder: a UTF-16 or invalid-UTF-8 doc becomes an UNREADABLE finding
     instead of being silently skipped/mangled (the former errors="ignore").
  3. Static: the four converted reader sites call read_text_input with their documented policy.
Paths touched: a TemporaryDirectory and the four tools' source files (read/parsed only).
"""
import ast
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scan_doc_citations  # noqa: E402
from text_input import TextInputError, read_text_input  # noqa: E402

TEXT = "### [C-1] Claude -> Codex, 2026-11-13 00:00\nline é漢\r\nthird\rend\n"


class Temp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def put(self, name, data: bytes):
        path = self.dir / name
        path.write_bytes(data)
        return path


class EncodingMatrix(Temp):
    def test_plain_utf8_equals_path_read_text(self):
        path = self.put("plain.md", TEXT.encode("utf-8"))
        self.assertEqual(read_text_input(path), path.read_text(encoding="utf-8"))
        self.assertEqual(read_text_input(path, errors="replace"), path.read_text(encoding="utf-8", errors="replace"))

    def test_utf8_bom_is_stripped(self):
        path = self.put("bom.md", b"\xef\xbb\xbf" + TEXT.encode("utf-8"))
        text = read_text_input(path)
        self.assertTrue(text.startswith("### [C-1]"), "the first-line header is no longer hidden behind U+FEFF")
        self.assertEqual(text, self.put("p.md", TEXT.encode("utf-8")).read_text(encoding="utf-8"))
        self.assertTrue(path.read_text(encoding="utf-8").startswith("﻿"), "the former decode kept the BOM")

    def test_utf16_always_fails_closed(self):
        cases = {"le_bom": TEXT.encode("utf-16"), "be_bom": b"\xfe\xff" + TEXT.encode("utf-16-be"),
                 "le_no_bom": TEXT.encode("utf-16-le")}
        for label, data in cases.items():
            for policy in ("strict", "replace"):
                with self.subTest(case=label, policy=policy):
                    path = self.put(f"{label}.log", data)
                    with self.assertRaises(TextInputError) as caught:
                        read_text_input(path, errors=policy)
                    self.assertIn(str(path), str(caught.exception))
                    self.assertIn("UTF-16", str(caught.exception))

    def test_invalid_utf8_strict_vs_replace(self):
        path = self.put("bad.log", b"ok\nbad \xff\xfe\xfa byte\n")
        with self.assertRaises(TextInputError) as caught:
            read_text_input(path)
        self.assertIn(f"{path}: invalid UTF-8 at byte 7", str(caught.exception))
        self.assertEqual(read_text_input(path, errors="replace"), path.read_text(encoding="utf-8", errors="replace"))

    def test_unreadable_and_bad_policy(self):
        with self.assertRaises(TextInputError) as caught:
            read_text_input(self.dir / "missing.md")
        self.assertIn("cannot read input", str(caught.exception))
        with self.assertRaises(ValueError):
            read_text_input(self.put("x.md", b"x"), errors="ignore")


class ScanDocCitations(Temp):
    def test_undecodable_docs_become_findings(self):
        self.put("V_A1_ok.md", b"Sources: see report\nPlain line\n")
        utf16 = self.put("V_A2_utf16.md", "Sources: x\n".encode("utf-16"))
        bad = self.put("V_A3_bad.md", b"text \xff here\n")
        results = scan_doc_citations.scan_all_va_docs(self.dir)
        self.assertEqual(results["V_A2_utf16.md"][0][1], "UNREADABLE")
        self.assertIn(str(utf16), results["V_A2_utf16.md"][0][2])
        self.assertEqual(results["V_A3_bad.md"][0][1], "UNREADABLE")
        self.assertIn(str(bad), results["V_A3_bad.md"][0][2])


class StaticCallSites(unittest.TestCase):
    EXPECTED = {"evidence_summary": "replace", "mailbox_decision_digest": "strict", "mailbox_open_items": "strict",
                "scan_doc_citations": "strict"}

    def test_reader_sites_use_the_helper_with_documented_policy(self):
        for tool, policy in self.EXPECTED.items():
            with self.subTest(tool=tool):
                calls = [n for n in ast.walk(ast.parse((HERE / f"{tool}.py").read_text(encoding="utf-8")))
                         if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "read_text_input"]
                self.assertEqual(len(calls), 1)
                given = [k.value.value for k in calls[0].keywords if k.arg == "errors"]
                self.assertEqual(given[0] if given else "strict", policy)


if __name__ == "__main__":
    unittest.main()
