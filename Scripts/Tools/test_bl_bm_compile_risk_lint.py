"""BM-41..45 (C, implementer; lane BM batch 9): pre-compile risk lint for the lane-BL / lane-BM native test files (none compiled yet).

Heuristic, source-only checks for overload/type patterns that commonly fail to compile with FAutomationTestBase, reviewed by hand
(see BM_41_45_COMPILE_RISK_LINT.md). It is NOT a substitute for the engine-lock build. Checks:
  1. TestEqual must not take a bool comparison (`==`, `!=`, `.IsEmpty()`, `IsNearlyEqual`) or a `uint64(...)` operand
     (use TestTrue(a == b) instead);
  2. string comparisons: a TestEqual whose expected value is `FString(...)` must not compare against a bare `TEXT("...")` actual,
     and vice versa (mismatched overloads);
  3. any file using std::numeric_limits includes <limits>;
  4. TestEqual must not compare an integer literal with a floating literal (ambiguous float/double overloads).
"""
import re
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parents[2] / "Source" / "OneBossFight" / "Tests"


def lane_files():
    out = []
    for p in sorted(TESTS.glob("*.cpp")):
        head = p.read_text(encoding="utf-8-sig", errors="replace")[:1500]
        if "lane BL" in head or "lane BM" in head:
            out.append(p)
    return out


def split_args(text, start):
    """Split the call arguments starting after '(' at index start; returns (args, end_index)."""
    depth, args, cur, i, in_str = 0, [], [], start, False
    while i < len(text):
        c = text[i]
        if c == '"' and text[i - 1] != "\\":
            in_str = not in_str
        if not in_str:
            if c in "([{":
                depth += 1
            elif c in ")]}":
                if depth == 0:
                    args.append("".join(cur).strip())
                    return args, i
                depth -= 1
            elif c == "," and depth == 0:
                args.append("".join(cur).strip())
                cur = []
                i += 1
                continue
        cur.append(c)
        i += 1
    return args, i


def test_equal_calls(path):
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for m in re.finditer(r"\bTestEqual\(", text):
        args, _ = split_args(text, m.end())
        yield text.count("\n", 0, m.start()) + 1, args


INT = re.compile(r"^-?\d+$")
FLT = re.compile(r"^-?(\d+\.\d*|\.\d+|\d+\.)(e-?\d+)?f?$")


class CompileRiskLint(unittest.TestCase):
    def setUp(self):
        self.files = lane_files()

    def test_lane_files_found(self):
        self.assertGreaterEqual(len(self.files), 51)

    def test_no_bool_or_uint64_operands_in_test_equal(self):
        hits = []
        for p in self.files:
            for line, args in test_equal_calls(p):
                for a in args[1:3]:
                    if re.search(r"(?<![=!<>])==(?!=)|!=|\.IsEmpty\(\)|IsNearlyEqual|\buint64\(", a):
                        hits.append(f"{p.name}:{line}: {a[:80]}")
        self.assertEqual(hits, [])

    def test_no_string_overload_mismatch(self):
        hits = []
        for p in self.files:
            for line, args in test_equal_calls(p):
                if len(args) >= 3:
                    a, e = args[1], args[2]
                    if (e.startswith("FString(") and a.startswith("TEXT(")) or (a.startswith("FString(") and e.startswith("TEXT(")):
                        hits.append(f"{p.name}:{line}")
        self.assertEqual(hits, [])

    def test_numeric_limits_has_include(self):
        hits = [p.name for p in self.files if "std::numeric_limits" in p.read_text(encoding="utf-8-sig", errors="replace")
                and "#include <limits>" not in p.read_text(encoding="utf-8-sig", errors="replace")]
        self.assertEqual(hits, [])

    def test_no_int_literal_against_float_literal(self):
        hits = []
        for p in self.files:
            for line, args in test_equal_calls(p):
                if len(args) >= 3:
                    a, e = args[1], args[2]
                    if (INT.match(a) and FLT.match(e)) or (FLT.match(a) and INT.match(e)):
                        hits.append(f"{p.name}:{line}: {a} vs {e}")
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
