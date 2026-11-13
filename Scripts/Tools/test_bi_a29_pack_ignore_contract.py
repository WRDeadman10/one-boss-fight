import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

IGNORED_PACK_DIRS = (
    "Content/ParagonGreystone/",
    "Content/ParagonGrux/",
    "Content/ParagonSevarog/",
    "Content/ParagonSteel/",
    "Content/AdvancedARPGCombat/",
    "Content/BeamPack/",
    "Content/BloodPack/",
    "Content/Deadly_Ruins/",
    "Content/Essential_Foosteps_SK/",
    "Content/Free_Spells/",
    "Content/Mage/",
    "Content/MS/",
    "Content/MSPresets/",
    "Content/RealisticSwordSoundEffects/",
    "Content/Vefects/",
    "Content/UnrealClaude/",
)


class BiA29PackIgnoreContractTest(unittest.TestCase):
    def test_zero_third_party_pack_files_tracked_or_dirty(self) -> None:
        tracked = subprocess.check_output(["git", "ls-files", "Content/"], cwd=REPO_ROOT, text=True).splitlines()
        leaked = [p for p in tracked if any(p.startswith(prefix) for prefix in IGNORED_PACK_DIRS)]
        self.assertEqual(leaked, [], f"Ignored third-party pack files leaked into git tracking: {leaked}")

        dirty = subprocess.check_output(
            ["git", "status", "--porcelain", "Content/"], cwd=REPO_ROOT, text=True
        ).splitlines()
        dirty_packs = [
            line for line in dirty if any(prefix in line for prefix in IGNORED_PACK_DIRS)
        ]
        self.assertEqual(dirty_packs, [], f"Third-party packs modified/staged: {dirty_packs}")


if __name__ == "__main__":
    unittest.main()
