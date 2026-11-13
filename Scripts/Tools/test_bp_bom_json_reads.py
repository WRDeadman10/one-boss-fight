"""BP-26..29 (C, implementer; Queue BP batch 6) under X-2295: static + in-process tests only (no tool main()/subprocess).

  1. Static regression guard: no allowlisted tool parses JSON with `json.loads(<path>.read_text(encoding="utf-8"))`; such
     reads now use "utf-8-sig", so a UTF-8 BOM (Windows PowerShell 5.1's default) is accepted instead of raising
     "Unexpected UTF-8 BOM". The untracked verify_bf_x05_selected_route is exempt (preserved per X-2300).
  2. In-process equivalence on temp files: for BOM-free files utf-8-sig decoding is byte-for-byte identical to utf-8, and
     for BOM files json.loads succeeds with the same value; a BOM is never valid JSON content, so no valid file changes meaning.
Paths touched: a TemporaryDirectory and the allowlisted tools' source files (read/parsed only).
"""
import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_bp_cli_smoke as smoke  # noqa: E402

EXEMPT = {"verify_bf_x05_selected_route"}
CONVERTED = {"a7_release_gates": 1, "audit_pie_command": 1, "check_g044_cook_manifest": 1, "compare_encounter_parity": 1,
             "normalize_cook_package_manifest": 1, "normalize_encounter_selection_graph": 1, "proof_report": 1,
             "round4_benchmark_report": 3, "summarize_encounter_cost": 1, "summarize_packaged_metrics": 1,
             "validate_a5_receipt_directory": 3, "validate_encounter_manifest": 1, "verify_bk7_shipping_receipt": 1,
             "verify_encounter_package_graph": 2, "verify_evidence_manifest": 1, "verify_framework_perf_receipt": 1,
             "write_a4_parity_receipt": 1}


def json_read_encodings(tool):
    """Encodings used by json.loads(<x>.read_text(encoding=...)) call sites in the tool."""
    found = []
    for node in ast.walk(ast.parse((HERE / f"{tool}.py").read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "loads" and node.args:
            inner = node.args[0]
            if isinstance(inner, ast.Call) and getattr(inner.func, "attr", "") == "read_text":
                for keyword in inner.keywords:
                    if keyword.arg == "encoding" and isinstance(keyword.value, ast.Constant):
                        found.append(keyword.value.value)
    return found


class StaticGuard(unittest.TestCase):
    def test_no_plain_utf8_json_reads_in_allowlist(self):
        offenders = {tool: enc for tool in smoke.ALLOWLIST if tool not in EXEMPT
                     for enc in [json_read_encodings(tool)] if "utf-8" in enc}
        self.assertEqual(offenders, {})

    def test_converted_sites_are_pinned(self):
        for tool, count in CONVERTED.items():
            with self.subTest(tool=tool):
                self.assertEqual(json_read_encodings(tool).count("utf-8-sig"), count)


class InProcessEquivalence(unittest.TestCase):
    SAMPLES = [{"a": 1}, [1, 2, {"b": "é漢"}], {"nested": {"x": [True, None]}}, "text", 3.5]

    def test_bom_and_plain_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for i, value in enumerate(self.SAMPLES):
                with self.subTest(value=value):
                    raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
                    plain, bom = tmp / f"p{i}.json", tmp / f"b{i}.json"
                    plain.write_bytes(raw)
                    bom.write_bytes(b"\xef\xbb\xbf" + raw)
                    self.assertEqual(plain.read_text(encoding="utf-8-sig"), plain.read_text(encoding="utf-8"))
                    self.assertEqual(json.loads(bom.read_text(encoding="utf-8-sig")), value)
                    with self.assertRaises(json.JSONDecodeError):
                        json.loads(bom.read_text(encoding="utf-8"))  # the former behaviour on a BOM file


if __name__ == "__main__":
    unittest.main()
