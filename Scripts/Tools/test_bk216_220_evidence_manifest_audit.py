"""BK-216..220 (C, implementer; X-2066): source-only adversarial audit of Scripts/Tools/verify_evidence_manifest.py.

The verifier is NOT modified. Held defences are ordinary tests; confirmed gaps are pinned as expectedFailure tests
whose docstring states the fail-closed rule, for the lead's hotfix cycle. Synthetic packs in throwaway OS temp
directories only (as the existing verifier suite does); no real evidence file is read or changed; no Unreal/build/PIE.
"""
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("verify_evidence_manifest_bk216", HERE / "verify_evidence_manifest.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Pack:
    """A throwaway evidence pack: files dict {name: bytes}, manifest written raw (text) or from a dict."""

    def __init__(self, files=None, manifest=None, raw=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name, data in (files or {}).items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.manifest = self.root / "evidence_manifest.json"
        self.manifest.write_text(raw if raw is not None else json.dumps(manifest), encoding="utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.tmp.cleanup()

    def verify(self, **kwargs):
        return M.verify(self.manifest, **kwargs)


A = b"evidence-a"
GOOD = {"schema": 1, "files": [{"file": "a.txt", "sha256": sha(A), "bytes": len(A)}]}


class HeldDefences(unittest.TestCase):
    def test_good_pack_passes(self):
        with Pack({"a.txt": A}, GOOD) as pack:
            self.assertEqual(pack.verify(require_bytes=True, strict_membership=True), [])

    def test_bk216_malformed_json_and_wrong_shape_are_invalid(self):
        for raw in ("not json", "[]", '{"schema": 2, "files": []}', '{"schema": 1, "files": {}}', '{"files": []}'):
            with self.subTest(raw=raw), Pack({}, raw=raw) as pack:
                self.assertTrue(pack.verify())

    def test_bk217_traversal_absolute_and_symlink_escape(self):
        outside = tempfile.NamedTemporaryFile(delete=False)
        outside.write(b"x"); outside.close()
        try:
            for name in ("../x.txt", "sub/../../x.txt", outside.name):
                with self.subTest(name=name), Pack({}, {"schema": 1, "files": [{"file": name, "sha256": sha(b"x")}]}) as pack:
                    self.assertTrue(any("unsafe path" in i for i in pack.verify()))
        finally:
            os.unlink(outside.name)

    def test_bk218_hash_size_and_missing_file(self):
        cases = ({"file": "a.txt", "sha256": sha(b"other")}, {"file": "a.txt", "sha256": sha(A), "bytes": 3},
                 {"file": "missing.txt", "sha256": sha(A)})
        for entry in cases:
            with self.subTest(entry=entry), Pack({"a.txt": A}, {"schema": 1, "files": [entry]}) as pack:
                self.assertTrue(pack.verify())

    def test_bk219_duplicate_names_unlisted_members_and_bad_entries(self):
        with Pack({"a.txt": A}, {"schema": 1, "files": [GOOD["files"][0], GOOD["files"][0]]}) as pack:
            self.assertTrue(any("duplicate file entry" in i for i in pack.verify()))
        with Pack({"a.txt": A, "extra.txt": b"e"}, GOOD) as pack:
            self.assertTrue(any("unlisted pack member" in i for i in pack.verify(strict_membership=True)))
        for entry in ({"file": 1, "sha256": sha(A)}, {"file": "a.txt"}, "a.txt", None):
            with self.subTest(entry=entry), Pack({"a.txt": A}, {"schema": 1, "files": [entry]}) as pack:
                self.assertTrue(pack.verify())

    def test_bk218_source_reference_binding(self):
        receipt = json.dumps({"source_log": "run.log", "source_log_sha256": sha(b"log")}).encode()
        files = {"run.log": b"log", "receipt.json": receipt}
        listed = {"schema": 1, "files": [{"file": n, "sha256": sha(d)} for n, d in files.items()]}
        with Pack(files, listed) as pack:
            self.assertEqual(pack.verify(verify_source_references=True), [])
        unlisted = {"schema": 1, "files": [{"file": "receipt.json", "sha256": sha(receipt)}]}
        with Pack(files, unlisted) as pack:
            self.assertTrue(any("not listed" in i for i in pack.verify(verify_source_references=True)))


class ConfirmedGaps(unittest.TestCase):
    """E1-E8 from this audit, fixed in BK-221..225 (X-2068); each former gap is now a passing regression."""
    def test_gap_e1_duplicate_json_keys_are_refused(self):
        """E1 (BK-216, :31): json.loads keeps the LAST duplicate key, so {"files":[<bad entry>], "files":[]} verifies an
        empty list and PASSES. Rule: parse with an object_pairs_hook that refuses duplicate keys."""
        raw = '{"schema": 1, "files": [{"file": "missing.txt", "sha256": "%s"}], "files": []}' % ("0" * 64)
        with Pack({}, raw=raw) as pack:
            self.assertTrue(pack.verify())

    def test_gap_e2_non_finite_constants_are_refused(self):
        """E2 (BK-216, :31): NaN / Infinity are accepted anywhere (e.g. an unknown key). Rule: parse_constant that
        raises, as validate_owner_approval_envelope.loads_strict does."""
        raw = '{"schema": 1, "files": [{"file": "a.txt", "sha256": "%s"}], "note": NaN}' % sha(A)
        with Pack({"a.txt": A}, raw=raw) as pack:
            self.assertTrue(pack.verify())

    def test_gap_e3_schema_must_be_the_integer_1(self):
        """E3 (BK-216, :34): `data.get("schema") != 1` accepts True and 1.0 (True == 1 == 1.0). Rule: require
        type(schema) is int and schema == 1."""
        for schema in (True, 1.0):
            with Pack({"a.txt": A}, dict(GOOD, schema=schema)) as pack:
                self.assertTrue(pack.verify(), schema)

    def test_gap_e4_empty_file_list_does_not_pass(self):
        """E4 (BK-219): {"schema":1,"files":[]} verifies nothing and prints PASS. Rule: an evidence manifest must list
        at least one file (or the caller states that an empty pack is acceptable)."""
        with Pack({}, {"schema": 1, "files": []}) as pack:
            self.assertTrue(pack.verify())

    def test_gap_e5_one_file_listed_twice_under_different_spellings(self):
        """E5 (BK-219, :50): duplicate detection compares the raw string, so "a.txt" and "./a.txt" (and, on Windows,
        "A.TXT") list the same file twice and pass. Rule: deduplicate on the resolved path (os.path.normcase)."""
        entries = [{"file": "a.txt", "sha256": sha(A)}, {"file": "./a.txt", "sha256": sha(A)}]
        with Pack({"a.txt": A}, {"schema": 1, "files": entries}) as pack:
            self.assertTrue(any("duplicate" in i for i in pack.verify()))

    def test_gap_e6_entry_hash_must_be_lowercase_hex(self):
        """E6 (BK-218, :63): the entry hash is compared case-insensitively and never shape-checked, while
        source_log_sha256 must be lowercase 64-hex (:98). Rule: entry sha256 must match [0-9a-f]{64} exactly."""
        with Pack({"a.txt": A}, {"schema": 1, "files": [{"file": "a.txt", "sha256": sha(A).upper()}]}) as pack:
            self.assertTrue(pack.verify())

    def test_gap_e7_unknown_keys_are_refused(self):
        """E7 (BK-219): unknown top-level and entry keys are ignored, so a typo ("sha_256") or an unrelated claim
        ("verdict": "PASS") passes silently. Rule: exact key sets (top: schema, files; entry: file, sha256[, bytes])."""
        manifest = {"schema": 1, "verdict": "PASS", "files": [dict(GOOD["files"][0], verdict="PASS")]}
        with Pack({"a.txt": A}, manifest) as pack:
            self.assertTrue(pack.verify())

    def test_gap_e8_bytes_must_be_an_integer_not_a_bool(self):
        """E8 (BK-218, :61): without --require-bytes, "bytes": true equals 1 and passes for a 1-byte file. Rule: when
        present, bytes must be a non-negative int (type(x) is int)."""
        with Pack({"one.txt": b"1"}, {"schema": 1, "files": [{"file": "one.txt", "sha256": sha(b"1"), "bytes": True}]}) as pack:
            self.assertTrue(pack.verify())


if __name__ == "__main__":
    unittest.main()
