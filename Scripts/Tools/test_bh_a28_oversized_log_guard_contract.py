import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_LOG_BYTES = 1024 * 1024
MEDIA_EXTS = (".png", ".mp4", ".wav", ".mp3")
AG_GROUP_A_PREFIXES = (
    "Documentation/Boss/BD_",
    "Documentation/Boss/BE_",
    "Documentation/Boss/BF_",
    "Documentation/Boss/BG_",
    "Documentation/Boss/BH_",
    "Documentation/Boss/QUEUE_B",
    "Documentation/Boss/BB_A26",
    "Documentation/Boss/BB_A31",
    "Scripts/Tools/test_bd_",
    "Scripts/Tools/test_be_a",
    "Scripts/Tools/test_bf_a",
    "Scripts/Tools/test_bg_",
    "Scripts/Tools/test_bh_",
)


class BhA28OversizedLogGuardContractTest(unittest.TestCase):
    def test_commits_since_24c1975e_contain_zero_oversized_logs_or_media(self) -> None:
        commits = subprocess.check_output(
            ["git", "rev-list", "03ce5a8a..5ae1b2b2"], cwd=REPO_ROOT, text=True
        ).splitlines()
        self.assertGreaterEqual(len(commits), 8)
        offenders = []
        for commit in commits:
            changed = subprocess.check_output(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit],
                cwd=REPO_ROOT,
                text=True,
            ).splitlines()
            for rel in changed:
                if rel.lower().endswith(MEDIA_EXTS):
                    offenders.append((commit[:8], rel, "media"))
                path = REPO_ROOT / rel
                if path.is_file() and path.stat().st_size > MAX_LOG_BYTES and rel.startswith("Docs/BossCombatReview/"):
                    offenders.append((commit[:8], rel, path.stat().st_size))
        self.assertEqual(offenders, [], f"Oversized log/media in post-03ce5a8a commits: {offenders}")

    def test_antigravity_group_a_working_tree_has_zero_oversized_or_media_files(self) -> None:
        status_lines = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
        ).splitlines()
        offenders = []
        for line in status_lines:
            rel = line[3:].strip().strip('"')
            if not rel.startswith(AG_GROUP_A_PREFIXES):
                continue
            if rel.lower().endswith(MEDIA_EXTS):
                offenders.append((rel, "media"))
            path = REPO_ROOT / rel
            if path.is_file() and path.stat().st_size > MAX_LOG_BYTES:
                offenders.append((rel, path.stat().st_size))
        self.assertEqual(offenders, [], f"Group A manifest contains oversized/media files: {offenders}")


if __name__ == "__main__":
    unittest.main()
