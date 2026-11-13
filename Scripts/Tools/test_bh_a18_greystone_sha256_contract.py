import hashlib
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GREYSTONE_DIR = REPO_ROOT / "Content" / "OneBossFight" / "Player" / "Greystone"
EVIDENCE_DIR = REPO_ROOT / "Docs" / "BossCombatReview" / "Execution" / "Claude" / "B_C1280_GREYSTONE2"

# Baseline C-1282 (HEAD f97994a7) historical LFS pointer oids, superseded on disk by C-1289 B_C1286_GREYSTONE_RM _RM re-author:
HEAD_C1282_GREYSTONE_SHA256 = {
    "AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone.uasset": "e02670a3920abd8963f0b0eea20aa708c328154931f7a2cea099d8a537142653",
    "AM_ER_Attack_Air_Light_Fit_Greystone.uasset": "45066e059081e262c82b6cb8640f90f678f2167a57d2f16e16a45c71ee45de82",
    "AM_ER_Attack_GuardCounter_Fit_Greystone.uasset": "2506b804e4e127e5016e4e3caacfb27d12c38b8143a48ba5ec4e78bdfe0133cb",
    "AM_ER_Backstep_Mixamo_V2_Fit_Greystone.uasset": "9d9046f5dbf704046b82dafefb36c2d4b8612b1d3777f4518df9be718bcb8cf4",
    "BP_GreystoneERPlayer.uasset": "91a4a63965c5ade63906221d404cdfb341028482c8be7dcc5fff43ca8e644373",
}

EXPECTED_C1289_GREYSTONE_SHA256 = {
    "AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone.uasset": "03103bf33898444aeb8e7f06638abc98e81aaa0611660b5fb4494feaedf22aab",
    "AM_ER_Attack_Air_Light_Fit_Greystone.uasset": "9de01725c181e8251dd8cfb781acb4959f49ea42202d6eba2207125570c00d18",
    "AM_ER_Attack_GuardCounter_Fit_Greystone.uasset": "ca1fdb9b98b0366679707e20da52d2bfe6b5978b84f40cbad35b446dd5815c01",
    "AM_ER_Backstep_Mixamo_V2_Fit_Greystone.uasset": "5b5d531eb804d38f69db2d83c05b352397c1ade9ed79e3a5ea45d9ec9c53d5ab",
    "BP_GreystoneERPlayer.uasset": "44f617eebeb9128c7e0127a07c25fab30fcca3cc6f52878af1702073d670ce24",
}


class BhA18GreystoneSha256ContractTest(unittest.TestCase):
    def test_five_authored_greystone_uassets_match_sha256_and_lfs_head(self) -> None:
        disk_files = sorted(GREYSTONE_DIR.glob("*.uasset"))
        self.assertEqual([p.name for p in disk_files], sorted(EXPECTED_C1289_GREYSTONE_SHA256))
        for path in disk_files:
            digest = hashlib.sha256(path.read_bytes()).hexdigest().lower()
            self.assertEqual(digest, EXPECTED_C1289_GREYSTONE_SHA256[path.name], f"SHA-256 drift on {path.name}")
            lfs_ptr = subprocess.check_output(
                ["git", "show", f"HEAD:{path.relative_to(REPO_ROOT).as_posix()}"],
                cwd=REPO_ROOT,
                text=True,
            )
            self.assertRegex(lfs_ptr, r"oid sha256:[0-9a-f]{64}")
            self.assertTrue(
                f"oid sha256:{digest}" in lfs_ptr or f"oid sha256:{HEAD_C1282_GREYSTONE_SHA256[path.name]}" in lfs_ptr
            )

    def test_c1280_evidence_sha256_manifest_intact(self) -> None:
        manifest = EVIDENCE_DIR / "evidence_sha256.txt"
        self.assertTrue(manifest.is_file())
        rows = [
            line.strip().split()
            for line in manifest.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(rows), 34)
        for expected_sha, rel_name in rows:
            target = EVIDENCE_DIR / rel_name
            self.assertTrue(target.is_file(), f"Missing evidence artifact: {rel_name}")
            actual = hashlib.sha256(target.read_bytes()).hexdigest().lower()
            self.assertEqual(actual, expected_sha.lower(), f"Evidence SHA drift on {rel_name}")


if __name__ == "__main__":
    unittest.main()
