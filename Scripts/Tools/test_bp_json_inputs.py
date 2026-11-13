"""BP-06..09 (C, implementer; Queue BP batch 2) under X-2295: in-process unit tests only.

No subprocess, no CLI or main() execution, no real project paths. Each test imports the tool module (import-time safety is
proven by cli_static_contract) and calls its loader or summarize function on files inside a TemporaryDirectory. The only
paths touched are that temp folder and the read-only source files of the four tools (parsed by the static checks).
"""
import ast
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_g2_selection_refusal_expected as g2  # noqa: E402
import check_move_card_ids as move_ids  # noqa: E402
import cli_static_contract  # noqa: E402
import round6_benchmark_report as round6  # noqa: E402
import summarize_parity_set as parity  # noqa: E402
from json_input import JsonInputError  # noqa: E402

TOOLS = ("check_g2_selection_refusal_expected", "check_move_card_ids", "round6_benchmark_report", "summarize_parity_set")


class Temp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def put(self, name, data: bytes):
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def assert_named(self, func, path, fragment):
        with self.assertRaises(JsonInputError) as caught:
            func(path)
        self.assertIn(str(path), str(caught.exception))
        self.assertIn(fragment, str(caught.exception))


class Bp06G2Sheet(Temp):
    def test_valid_sheet_and_bom(self):
        valid = b'{"cases": ["c"], "required_log_tokens": ["T"]}'  # X-2298: empty lists are now a schema error
        self.assertEqual(g2.load_sheet(self.put("s.json", valid))["cases"], ["c"])
        self.assertEqual(g2.load_sheet(self.put("b.json", b"\xef\xbb\xbf" + valid))["cases"], ["c"])

    def test_malformed_and_wrong_shape(self):
        self.assert_named(g2.load_sheet, self.put("bad.json", b"{not json"), "malformed JSON")
        self.assert_named(g2.load_sheet, self.put("arr.json", b"[1]"), "expected top-level dict")
        self.assert_named(g2.load_sheet, self.dir / "missing.json", "cannot read input")


class X2298G2SheetSchema(Temp):
    """X-2298: element types are validated before set(); malformed valid-JSON sheets are named JsonInputErrors."""

    def test_valid_sheet(self):
        sheet = g2.load_sheet(self.put("ok.json", b'{"cases": ["a", "b"], "required_log_tokens": ["T1"]}'))
        self.assertEqual(sheet["cases"], ["a", "b"])

    def test_malformed_sheets(self):
        cases = {
            "unhashable case": (b'{"cases": [{}], "required_log_tokens": ["T"]}', "cases[0] must be a string"),
            "list element": (b'{"cases": ["a"], "required_log_tokens": [["T"]]}', "required_log_tokens[0] must be a string"),
            "number element": (b'{"cases": ["a", 1], "required_log_tokens": ["T"]}', "cases[1] must be a string"),
            "duplicate strings": (b'{"cases": ["a", "a"], "required_log_tokens": ["T"]}', "cases contains duplicate"),
            "duplicate tokens": (b'{"cases": ["a"], "required_log_tokens": ["T", "T"]}', "required_log_tokens contains duplicate"),
            "missing cases": (b'{"required_log_tokens": ["T"]}', "cases must be a nonempty list"),
            "empty tokens": (b'{"cases": ["a"], "required_log_tokens": []}', "required_log_tokens must be a nonempty list"),
            "string not list": (b'{"cases": "a", "required_log_tokens": ["T"]}', "cases must be a nonempty list"),
        }
        for label, (data, fragment) in cases.items():
            with self.subTest(case=label):
                self.assert_named(g2.load_sheet, self.put(f"{label}.json".replace(" ", "_"), data), fragment)

    def test_audit_never_sees_unhashable_elements(self):
        """The TypeError path from X-2298: audit() set()s the lists; load_sheet must have rejected bad elements first."""
        with self.assertRaises(JsonInputError):
            g2.load_sheet(self.put("u.json", b'{"cases": [[1]], "required_log_tokens": ["T"]}'))


class X2298MoveCardsKey(Temp):
    """X-2298: an object export must have an explicit "cards" list; {} or {"other": 1} is no longer a clean empty export."""

    def test_object_without_cards_is_rejected(self):
        for label, data in (("empty", b"{}"), ("other", b'{"other": 1}')):
            with self.subTest(case=label):
                self.assert_named(move_ids.load_cards, self.put(f"{label}.json", data), 'no "cards" key')

    def test_cards_must_be_a_list(self):
        self.assert_named(move_ids.load_cards, self.put("dict.json", b'{"cards": {"MoveId": "A"}}'), "expected cards to be a list")

    def test_explicit_empty_cards_list_is_allowed(self):
        self.assertEqual(move_ids.load_cards(self.put("e.json", b'{"cards": []}')), [])


class Bp07MoveCardIds(Temp):
    def test_list_and_object_exports(self):
        self.assertEqual(len(move_ids.load_cards(self.put("l.json", b'[{"MoveId": "A"}]'))), 1)
        self.assertEqual(len(move_ids.load_cards(self.put("o.json", b'{"cards": [{"MoveId": "B"}]}'))), 1)

    def test_malformed_and_wrong_shape(self):
        self.assert_named(move_ids.load_cards, self.put("bad.json", b"[1,"), "malformed JSON")
        self.assert_named(move_ids.load_cards, self.put("num.json", b"5"), "expected top-level dict/list")
        self.assert_named(move_ids.load_cards, self.put("strs.json", b'["A"]'), "cards[0] must be an object")


class Bp08Round6Receipt(Temp):
    def test_load_and_validate_chain(self):
        value = round6.load_receipt(self.put("r.json", b'{"schema": "x"}'))
        self.assertTrue(round6.validate(value), "shape problems stay validate()'s job (exit 2 INVALID)")

    def test_malformed(self):
        self.assert_named(round6.load_receipt, self.put("bad.json", b'{"a": '), "malformed JSON")
        self.assert_named(round6.load_receipt, self.put("deep.json", b"[" * 200000), "nesting is too deep")


class Bp09ParitySummary(Temp):
    def test_malformed_report_marks_the_pair_invalid(self):
        good = b'{"status": "PASS", "exit_code": 0, "issues": []}'
        for driver in parity.DRIVERS:
            self.put(f"{driver}_x/parity_report.json", good)
        bad = self.put(f"{parity.DRIVERS[1]}_x/parity_report.json", b"{broken")
        array = self.put(f"{parity.DRIVERS[2]}_x/parity_report.json", b"[]")
        result = parity.summarize(self.dir, "_x")
        rows = {row["driver"]: row for row in result["pairs"]}
        self.assertEqual(rows[parity.DRIVERS[0]]["status"], "PASS")
        self.assertEqual(rows[parity.DRIVERS[1]]["status"], "INVALID")
        self.assertIn(str(bad), rows[parity.DRIVERS[1]]["issues"][0])
        self.assertEqual(rows[parity.DRIVERS[2]]["status"], "INVALID")
        self.assertIn(str(array), rows[parity.DRIVERS[2]]["issues"][0])
        self.assertEqual((result["passed"], result["failed_or_missing"]), (3, 2), "malformed reports count as failures")

    def test_missing_report_unchanged(self):
        result = parity.summarize(self.dir, "_none")
        self.assertTrue(all(row["status"] == "MISSING" for row in result["pairs"]))


class StaticMainHandling(unittest.TestCase):
    """main() is not executed; its source must route loader errors to json_input.fail (exit 2, named, no traceback)."""

    def test_mains_catch_json_input_error(self):
        for tool in TOOLS[:3]:
            with self.subTest(tool=tool):
                tree = ast.parse((HERE / f"{tool}.py").read_text(encoding="utf-8"))
                main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
                handlers = [h for n in ast.walk(main) if isinstance(n, ast.Try) for h in n.handlers]
                self.assertTrue(any(isinstance(h.type, ast.Name) and h.type.id == "JsonInputError"
                                    and any(isinstance(c, ast.Call) and getattr(c.func, "id", "") == "fail"
                                            for c in ast.walk(h)) for h in handlers))
                self.assertNotIn("json.loads(", ast.unparse(main), "raw json.loads replaced by the loader")

    def test_tools_still_satisfy_the_static_contract(self):
        for tool in TOOLS + ("round6_phase2_intake",):
            with self.subTest(tool=tool):
                ok, reason = cli_static_contract.analyse(HERE / f"{tool}.py")
                self.assertTrue(ok, reason)


if __name__ == "__main__":
    unittest.main()
