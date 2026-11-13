"""BK-79 (C, implementer; X-1996): synthetic tests for validate_pending_definition_inputs.py.

In-memory manifests and temp files only; no editor, no asset loads. The real BK-76 manifest is checked schema-only
(no --verify-sources), so the test never hashes the .uasset it cites.
"""
import copy
import hashlib
import importlib.util
import io
import contextlib
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validate_pending_definition_inputs", HERE / "validate_pending_definition_inputs.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
REAL = HERE.parents[1] / "Documentation/Boss/BK76_SEVAROG_DEFINITION_INPUTS_PENDING.json"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def cite(text="value = 1", path="Docs/source.txt"):
    return {"path": path, "scope": "excerpt", "line": 2, "excerpt": text, "sha256": sha(text)}


def row(field, status="SOURCE_BACKED_AWAITING_OWNER", value=1.0, kind="float", **extra):
    base = {"field_path": field, "type": kind, "units": "u", "status": status, "value": value,
            "citations": [cite()], "note": "synthetic"}
    base.update(extra)
    return base


def manifest():
    rows = []
    for field in sorted(V.REQUIRED_FIELDS):
        if field.endswith("PhaseId"):
            rows.append(row(field, status="SOURCE_BACKED", value="Phase_1", kind="name"))
        elif "Multiplier" in field or "Regen" in field:
            rows.append(row(field, status="OWNER_DECISION_REQUIRED", value=None, candidate=1.0, candidate_note="identity"))
        elif field == "Stats.MaxHealth":
            rows.append(row(field, value=1500.0))  # X-2058: native floor is > 1.0 (RPGBossStatsAdapters.cpp:95)
        else:
            rows.append(row(field))
    return {"schema": V.SCHEMA, "manifest_state": "PENDING", "authoring_evidence": False, "executable": False, "rows": rows}


def find(m, field):
    return next(r for r in m["rows"] if r["field_path"] == field)


class PendingManifestTests(unittest.TestCase):
    def assertRefused(self, m, needle, **kwargs):
        result = V.validate(m, **kwargs)
        self.assertFalse(result["valid"])
        self.assertTrue(any(needle in e for e in result["errors"]), (needle, result["errors"]))

    # --- positive ---
    def test_supported_and_pending_rows_validate(self):
        result = V.validate(manifest())
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["counts"]["OWNER_DECISION_REQUIRED"], 5)
        self.assertIn("Stats.PostureRegenRate", result["owner_decisions_required"])

    def test_real_bk76_manifest_validates_schema_only(self):
        result = V.validate(json.loads(REAL.read_text(encoding="utf-8")))
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(sorted(result["owner_decisions_required"]), sorted([
            "Stats.PostureRegenDelay", "Stats.PostureRegenRate", "Phases[Phase_1].SpeedMultiplier",
            "Phases[Phase_1].RateMultiplier", "Phases[Phase_1].AttackMultiplier"]))

    def test_verify_sources_accepts_matching_excerpt_and_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Docs").mkdir()
            (root / "Docs/source.txt").write_text("header\nvalue = 1\n", encoding="utf-8")
            (root / "Docs/blob.bin").write_bytes(b"abc")
            m = manifest()
            find(m, "Stats.MaxHealth")["citations"].append({"path": "Docs/blob.bin", "scope": "file", "sha256": hashlib.sha256(b"abc").hexdigest()})
            result = V.validate(m, root=root, verify_sources=True)
            self.assertTrue(result["valid"], result["errors"])

    # --- tampering / provenance ---
    def test_tampered_excerpt_hash_is_refused(self):
        m = manifest()
        find(m, "Stats.MaxHealth")["citations"][0]["excerpt"] = "value = 2"
        self.assertRefused(m, "does not match its excerpt text")

    def test_tampered_file_hash_is_refused_with_verify_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Docs").mkdir()
            (root / "Docs/source.txt").write_text("value = 1\n", encoding="utf-8")
            (root / "Docs/blob.bin").write_bytes(b"changed")
            m = manifest()
            find(m, "Stats.MaxHealth")["citations"].append({"path": "Docs/blob.bin", "scope": "file", "sha256": hashlib.sha256(b"abc").hexdigest()})
            self.assertRefused(m, "file sha256 differs", root=root, verify_sources=True)

    def test_excerpt_missing_from_source_and_missing_file_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Docs").mkdir()
            (root / "Docs/source.txt").write_text("header\nsomething else\n", encoding="utf-8")
            self.assertRefused(manifest(), "excerpt no longer matches cited line", root=root, verify_sources=True)
            m = manifest()
            find(m, "Stats.MaxHealth")["citations"] = [cite(path="Docs/absent.txt")]
            self.assertRefused(m, "does not exist", root=root, verify_sources=True)

    def test_missing_citation_is_refused(self):
        m = manifest()
        find(m, "Stats.MaxPosture")["citations"] = []
        self.assertRefused(m, "at least one citation")
        m = manifest()
        del find(m, "Stats.PostureRegenDelay")["citations"]
        self.assertRefused(m, "missing keys")

    def test_bad_citation_shapes_are_refused(self):
        cases = {"absolute path": dict(path="C:/x.txt"), "parent path": dict(path="../x.txt"),
                 "short sha": dict(sha256="abc"), "bad scope": dict(scope="url"), "empty excerpt": dict(excerpt="  "),
                 "bad line": dict(line=0)}
        for label, change in cases.items():
            with self.subTest(label):
                m = manifest()
                find(m, "Stats.MaxHealth")["citations"][0].update(change)
                self.assertFalse(V.validate(m)["valid"])

    # --- premature approval / promotion ---
    def test_premature_approval_statuses_are_refused(self):
        for status in ("APPROVED", "OWNER_APPROVED", "AUTHORED"):
            with self.subTest(status):
                m = manifest()
                find(m, "Stats.PostureRegenDelay").update(status=status, value=6.0)
                self.assertRefused(m, "cannot approve or promote")

    def test_owner_decision_row_with_a_value_is_refused(self):
        m = manifest()
        find(m, "Phases[Phase_1].SpeedMultiplier")["value"] = 1.0
        self.assertRefused(m, "premature promotion refused")

    def test_manifest_cannot_claim_evidence_or_executability_or_promotion(self):
        for key, value, needle in (("authoring_evidence", True, "not authoring evidence"), ("executable", True, "not asset data"),
                                   ("manifest_state", "APPROVED", "must be PENDING"), ("schema", "other/v1", "schema must be")):
            with self.subTest(key):
                m = manifest()
                m[key] = value
                self.assertRefused(m, needle)

    def test_conflicting_unknown_top_level_approval_claim_is_refused(self):
        m = manifest()
        m["approval_status"] = "APPROVED"
        self.assertRefused(m, "unknown top-level keys (possible conflicting approval claims)")

    # --- schema ---
    def test_row_schema_rules(self):
        m = manifest(); m["rows"] = [r for r in m["rows"] if r["field_path"] != "Stats.MaxHealth"]
        self.assertRefused(m, "required fields missing: Stats.MaxHealth")
        m = manifest(); m["rows"].append(copy.deepcopy(find(m, "Stats.MaxHealth")))
        self.assertRefused(m, "duplicate field_path")
        m = manifest(); find(m, "Stats.MaxHealth")["value"] = "1500"
        self.assertRefused(m, "float value must be a number")
        m = manifest(); find(m, "Stats.MaxHealth")["value"] = None
        self.assertRefused(m, "needs a value")
        m = manifest(); find(m, "Stats.MaxHealth")["candidate"] = 2.0
        self.assertRefused(m, "must not also carry a candidate")
        m = manifest(); find(m, "Stats.MaxHealth")["surprise"] = 1
        self.assertRefused(m, "unknown keys")
        self.assertRefused({"schema": V.SCHEMA, "manifest_state": "PENDING", "authoring_evidence": False, "executable": False, "rows": []}, "non-empty list")

    # --- CLI and read-only contract ---
    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            good, bad = Path(tmp) / "good.json", Path(tmp) / "bad.json"
            good.write_text(json.dumps(manifest()), encoding="utf-8")
            broken = manifest(); broken["authoring_evidence"] = True
            bad.write_text(json.dumps(broken), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(V.main([str(good)]), 0)
                self.assertEqual(V.main([str(bad)]), 1)

    def test_validator_is_read_only(self):
        source = (HERE / "validate_pending_definition_inputs.py").read_text(encoding="utf-8")
        for forbidden in ("write_text", "write_bytes", "open(", "subprocess", "import unreal", "unlink", "rename", "mkdir"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
