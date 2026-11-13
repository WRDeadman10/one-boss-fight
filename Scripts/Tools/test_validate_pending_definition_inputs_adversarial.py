"""BK-83 (C, implementer; X-1998): independent adversarial tests for validate_pending_definition_inputs.py.

Does not modify the validator or its existing tests. All identified defenses are ordinary tests. In-memory manifests and temp files
only; the real manifest is used only as a template (no --verify-sources against the .uasset).
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validate_pending_definition_inputs", HERE / "validate_pending_definition_inputs.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
REAL = json.loads((HERE.parents[1] / "Documentation/Boss/BK76_SEVAROG_DEFINITION_INPUTS_PENDING.json").read_text(encoding="utf-8"))


def fresh():
    return copy.deepcopy(REAL)


def row(m, field):
    return next(r for r in m["rows"] if r["field_path"] == field)


def excerpt_cite(text, line=1, path="Docs/source.txt"):
    return {"path": path, "scope": "excerpt", "line": line, "excerpt": text, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}


def temp_root(lines):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "Docs").mkdir()
    (root / "Docs/source.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return tmp, root


class HeldDefenses(unittest.TestCase):
    def test_path_traversal_variants_are_refused(self):
        for bad in ("Docs\\..\\..\\x.txt", "Docs/../x", "\\\\srv\\share\\x", "C:x.txt", "./../x", "/etc/passwd", ""):
            with self.subTest(bad):
                m = fresh()
                row(m, "Stats.MaxHealth")["citations"][1]["path"] = bad
                self.assertFalse(V.validate(m)["valid"])

    def test_benign_dot_segment_path_is_allowed(self):
        m = fresh()
        cite = row(m, "Stats.MaxHealth")["citations"][1]
        cite["path"] = "Documentation/./DECISIONS.md"
        self.assertTrue(V.validate(m)["valid"])

    def test_source_drift_on_cited_line_is_refused(self):
        tmp, root = temp_root(["header", "value = 1"])
        with tmp:
            m = fresh()
            row(m, "Stats.MaxHealth")["citations"] = [excerpt_cite("value = 1", line=2)]
            for r in m["rows"]:
                if r["field_path"] != "Stats.MaxHealth":
                    r["citations"] = [excerpt_cite("value = 1", line=2)]
            self.assertTrue(V.validate(m, root=root, verify_sources=True)["valid"])
            (root / "Docs/source.txt").write_text("header\nvalue = 2\n", encoding="utf-8")
            self.assertFalse(V.validate(m, root=root, verify_sources=True)["valid"])

    def test_excerpt_on_the_wrong_line_is_refused(self):
        tmp, root = temp_root(["value = 1", "other"])
        with tmp:
            m = fresh()
            for r in m["rows"]:
                r["citations"] = [excerpt_cite("value = 1", line=2)]
            errors = V.validate(m, root=root, verify_sources=True)["errors"]
            self.assertTrue(any("excerpt no longer matches cited line 2" in e for e in errors), errors)

    def test_line_number_shapes_are_refused(self):
        for bad in (0, -1, True, "2", None, 2.0):
            with self.subTest(bad):
                m = fresh()
                row(m, "Stats.MaxHealth")["citations"][1]["line"] = bad
                self.assertFalse(V.validate(m)["valid"])

    def test_unknown_top_level_approval_claims_are_refused(self):
        for key, value in (("approved", True), ("owner_approval", "X-9999"), ("APPROVED", 1)):
            with self.subTest(key):
                m = fresh()
                m[key] = value
                self.assertFalse(V.validate(m)["valid"])

    def test_status_case_and_whitespace_variants_are_refused(self):
        for status in ("approved", "Approved", " SOURCE_BACKED", "SOURCE_BACKED ", "source_backed", "OWNER_DECISION_REQUIRED\n"):
            with self.subTest(repr(status)):
                m = fresh()
                row(m, "Stats.MaxHealth")["status"] = status
                self.assertFalse(V.validate(m)["valid"])

    def test_uppercase_or_padded_hashes_are_refused(self):
        for transform in (str.upper, lambda h: " " + h, lambda h: h[:-1]):
            m = fresh()
            cite = row(m, "Stats.MaxHealth")["citations"][1]
            cite["sha256"] = transform(cite["sha256"])
            self.assertFalse(V.validate(m)["valid"])

    def test_nonlist_rows_and_nonobject_manifest_are_refused(self):
        self.assertFalse(V.validate([])["valid"])
        m = fresh(); m["rows"] = {"a": 1}
        self.assertFalse(V.validate(m)["valid"])

    def test_unhashable_unknown_field_path_is_refused_without_crashing(self):
        m = fresh()
        row(m, "Phases[Phase_1].PhaseId")["field_path"] = ["Owner", "Approval"]
        result = V.validate(m)
        self.assertFalse(result["valid"])
        self.assertTrue(any("field_path must be one of" in error for error in result["errors"]))


class FixedGapRegressions(unittest.TestCase):
    """Cases identified in BK-83; all must now be refused."""

    def test_gap_nonfinite_value_is_refused(self):
        for bad in (float("nan"), float("inf"), float("-inf"), 10 ** 1000):
            m = fresh()
            row(m, "Stats.MaxHealth")["value"] = bad
            self.assertFalse(V.validate(m)["valid"], bad)

    def test_gap_truncated_excerpt_is_refused(self):
        # A fragment such as "0.6" hashes correctly and is a substring of the cited line, so it passes; an excerpt
        # should equal the stripped cited line.
        tmp, root = temp_root(['    "phase_two_fraction": 0.6,'])
        with tmp:
            m = fresh()
            for r in m["rows"]:
                r["citations"] = [excerpt_cite("0.6", line=1)]
            self.assertFalse(V.validate(m, root=root, verify_sources=True)["valid"])

    def test_gap_unknown_field_path_row_is_refused(self):
        m = fresh()
        extra = copy.deepcopy(row(m, "Phases[Phase_1].PhaseId"))
        extra.update(field_path="Owner.Approval", value="yes")
        m["rows"].append(extra)
        self.assertFalse(V.validate(m)["valid"])

    def test_gap_duplicate_json_keys_are_refused_by_the_cli(self):
        text = json.dumps(REAL).replace('"manifest_state": "PENDING"', '"manifest_state": "APPROVED", "manifest_state": "PENDING"', 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.json"
            path.write_text(text, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(V.main([str(path)]), 1)

    def test_gap_candidate_type_is_checked(self):
        for bad in ("six", float("nan"), True, None):
            m = fresh()
            row(m, "Stats.PostureRegenDelay")["candidate"] = bad
            self.assertFalse(V.validate(m)["valid"], bad)


if __name__ == "__main__":
    unittest.main()
