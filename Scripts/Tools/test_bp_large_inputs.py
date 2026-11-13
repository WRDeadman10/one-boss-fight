"""BP-41..44 (C, implementer; Queue BP batch 9) under X-2295: bounded synthetic large inputs with exact output parity.

No main(), CLI or subprocess; no wall-clock or memory thresholds (X-2312). Every input is generated so its correct result
is known by construction, and the in-process core is checked against that exact expectation at roughly 10-20 MB.
Covered cores (all pure functions already exercised at small size): log_failures.find_failures,
mailbox_stats.party_day_counts, list_todo_markers.marker_lines, check_line_endings.line_ending_counts,
compare_framework_tokens.count (file), text_input.read_text_input (file) and json_input.load_json (file).
Paths touched: a TemporaryDirectory only.
"""
import collections
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_line_endings  # noqa: E402
import compare_framework_tokens  # noqa: E402
import json_input  # noqa: E402
import list_todo_markers  # noqa: E402
import log_failures  # noqa: E402
import mailbox_stats  # noqa: E402
import text_input  # noqa: E402

LINES = 200_000  # ~10-20 MB per synthetic text below


class LargeTextCores(unittest.TestCase):
    def test_find_failures_on_a_large_log(self):
        rows = [f"[{i:06d}] Error: boom {i}" if i % 997 == 0 else f"[{i:06d}] info line with some payload text"
                for i in range(LINES)]
        found = log_failures.find_failures("\n".join(rows))
        expected = [(i + 1, rows[i]) for i in range(0, LINES, 997)]
        self.assertEqual(found, expected)

    def test_party_day_counts_on_a_large_mailbox(self):
        parts, expected = [], collections.Counter()
        for i in range(LINES // 4):
            party = "CXA"[i % 3]
            day = f"2026-11-{(i % 28) + 1:02d}"
            parts.append(f"### [{party}-{i}] Someone -> Someone else, {day} 10:00\nbody line {i}\nmore body\n")
            expected[(party, day)] += 1
        self.assertEqual(mailbox_stats.party_day_counts("".join(parts)), expected)

    def test_marker_lines_on_a_large_source(self):
        rows = [f"// TODO item {i}" if i % 1009 == 0 else f"int value_{i} = {i};" for i in range(LINES)]
        self.assertEqual(list_todo_markers.marker_lines("\n".join(rows)), [(i + 1, rows[i]) for i in range(0, LINES, 1009)])

    def test_line_ending_counts_on_large_bytes(self):
        data = b"a\r\n" * 3_000_000 + b"b\n" * 2_000_000 + b"c\r" * 1_000
        self.assertEqual(check_line_endings.line_ending_counts(data), (3_000_000, 2_000_000, 1_000))
        self.assertIsNone(check_line_endings.line_ending_counts(b"\0" + data))


class LargeFileReaders(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_framework_token_count_on_a_large_log(self):
        path = self.dir / "big.log"
        expected = collections.Counter()
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            for i in range(LINES):
                token = ("hit", "decision", "RESULT")[i % 3]
                stream.write(f"[FrameworkProof] {token} instance={i}\nnoise line {i}\n")
                expected[token] += 1
        self.assertEqual(compare_framework_tokens.count(path), expected)

    def test_read_text_input_on_a_large_bom_file(self):
        body = "".join(f"line {i} é漢\r\n" for i in range(LINES))
        path = self.dir / "big_bom.md"
        path.write_bytes(b"\xef\xbb\xbf" + body.encode("utf-8"))
        text = text_input.read_text_input(path)
        self.assertEqual(text, body.replace("\r\n", "\n"))
        self.assertEqual(text.count("\n"), LINES)

    def test_load_json_on_a_large_document(self):
        value = {"cards": [{"MoveId": f"M{i}", "Windows": [{"BakedSamples": list(range(5))}]} for i in range(LINES // 2)]}
        path = self.dir / "big.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        loaded = json_input.load_json(path, dict)
        self.assertEqual(len(loaded["cards"]), LINES // 2)
        self.assertEqual(loaded["cards"][-1]["MoveId"], f"M{LINES // 2 - 1}")
        self.assertEqual(loaded, value)


if __name__ == "__main__":
    unittest.main()
