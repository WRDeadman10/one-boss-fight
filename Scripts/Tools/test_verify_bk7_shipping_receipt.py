import unittest
import hashlib
import tempfile
from pathlib import Path

from verify_bk7_shipping_receipt import validate


def receipt():
    digest = "a" * 64
    return {
        "receipt_version": 1, "build_id": "build-17", "engine_root": "UE_5.5", "target": "Win64",
        "configuration": "Shipping", "project": "OneBossFight.uproject", "stage_root": "Saved/stage",
        "source_head": "abc123", "dirty_file_count": 0,
        "artifacts": {
            "uat_log": {"build_id": "build-17", "path": "uat.log", "sha256": digest},
            "shipping_executable": {"build_id": "build-17", "path": "game.exe", "bytes": 100, "sha256": digest},
            "reflection_dump": {"build_id": "build-17", "command": "UHTDump.exe", "arguments": ["--shipping"], "path": "uht.log", "sha256": digest},
        },
        "checks": {"buildcookrun_exit": 0, "reflection_dump_exit": 0, "shipping_binary_guard_exit": 0,
                   "feature_symbol_guard_exit": 0, "source_guard_exit": 0},
        "shipping_smoke": "NOT_RUN", "verdict": "PASS",
    }


class BK7ReceiptTests(unittest.TestCase):
    def test_complete_single_build_receipt_passes_structurally(self):
        self.assertEqual(validate(receipt()), [])

    def test_mixed_artifact_build_identity_fails(self):
        data = receipt()
        data["artifacts"]["reflection_dump"]["build_id"] = "build-old"
        self.assertTrue(any("reflection_dump build_id" in issue for issue in validate(data)))

    def test_failure_exit_cannot_claim_pass(self):
        data = receipt()
        data["checks"]["shipping_binary_guard_exit"] = 1
        self.assertTrue(any("verdict must be FAIL" in issue for issue in validate(data)))

    def test_receipt_cannot_claim_smoke(self):
        data = receipt()
        data["shipping_smoke"] = "PASS"
        self.assertTrue(any("does not prove packaged smoke" in issue for issue in validate(data)))

    def test_artifact_hashes_are_recomputed_when_requested(self):
        data = receipt()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index, name in enumerate(("uat_log", "shipping_executable", "reflection_dump")):
                artifact_path = root / f"artifact-{index}.bin"
                artifact_path.write_bytes(f"artifact-{index}".encode())
                artifact = data["artifacts"][name]
                artifact["path"] = str(artifact_path)
                artifact["sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
                if name == "shipping_executable":
                    artifact["bytes"] = artifact_path.stat().st_size
            self.assertEqual(validate(data, verify_files=True), [])
            data["artifacts"]["uat_log"]["sha256"] = "b" * 64
            self.assertTrue(any("uat_log hash mismatch" in issue for issue in validate(data, verify_files=True)))


if __name__ == "__main__":
    unittest.main()
