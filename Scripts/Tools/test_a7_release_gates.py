import contextlib
import io
import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import a7_release_gates as gates


def checklist(root: Path):
    entries = []
    for gate_id in sorted(gates.EXPECTED_IDS):
        source = root / "source.md"
        entries.append({"id": gate_id, "title": gate_id, "status": "OPEN", "owner": "Lead",
                        "evidence_sources": ["source.md"], "close_with": "retain proof", "closure_evidence": []})
    return {"schema": gates.SCHEMA, "policy": {"J049_shipping_selector": "A", "A7_legacy_retirement": "B"},
            "gates": entries}


class A7ReleaseGateTests(unittest.TestCase):
    def test_valid_open_checklist(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source.md").write_text("evidence source", encoding="utf-8")
            self.assertEqual(gates.validate_checklist(checklist(root), root), [])

    def test_closed_gate_without_evidence_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source.md").write_text("evidence source", encoding="utf-8")
            value = checklist(root)
            value["gates"][0]["status"] = "CLOSED"
            issues = gates.validate_checklist(value, root)
            self.assertTrue(any("CLOSED without closure evidence" in issue for issue in issues))

    def test_closed_gate_requires_existing_safe_evidence_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source.md").write_text("source", encoding="utf-8")
            value = checklist(root)
            value["gates"][0]["status"] = "CLOSED"
            value["gates"][0]["closure_evidence"] = ["../outside.md"]
            issues = gates.validate_checklist(value, root)
            self.assertTrue(any("escapes project root" in issue for issue in issues))

    def test_closed_gate_with_existing_evidence_is_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source.md").write_text("source", encoding="utf-8")
            (root / "closeout.md").write_text("closure evidence", encoding="utf-8")
            value = checklist(root)
            value["gates"][0]["status"] = "CLOSED"
            value["gates"][0]["closure_evidence"] = ["closeout.md"]
            self.assertEqual(gates.validate_checklist(value, root), [])

    def test_policy_and_gate_set_are_fixed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source.md").write_text("source", encoding="utf-8")
            value = checklist(root)
            value["policy"]["A7_legacy_retirement"] = "A"
            self.assertTrue(any("J049=A and A7=B" in issue for issue in gates.validate_checklist(value, root)))

    def test_report_lists_each_gate_without_percentage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text = gates.render_report(checklist(root))
            self.assertIn("A7-SHIPPING-SELECTOR", text)
            self.assertIn("A7-SELECTION-RECOVERY", text)
            self.assertIn("no aggregate completion percentage", text)

    def test_cli_suppresses_report_for_invalid_checklist(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source.md").write_text("source", encoding="utf-8")
            value = checklist(root)
            value["gates"][0]["status"] = "CLOSED"
            path = root / "gates.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                with mock.patch.object(sys, "argv", ["a7_release_gates.py", str(path), "--project-root", str(root), "--report"]):
                    code = gates.main()
            self.assertEqual(code, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("report not generated", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
