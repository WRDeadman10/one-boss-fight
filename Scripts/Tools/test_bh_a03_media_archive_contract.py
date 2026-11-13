import json
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ANTIGRAVITY_EXEC_DIR = REPO_ROOT / "Docs" / "BossCombatReview" / "Execution" / "Antigravity"

EXPECTED_SFX_REELS = (
    "Batch3_Audition_Reel.mp3",
    "Batch3_Audition_Reel.mp4",
    "Parry_Addendum_Reel.mp3",
    "Parry_Addendum_Reel.mp4",
    "SFX_Audition_Reel.mp3",
    "SFX_Audition_Reel.mp4",
)

EXPECTED_SEVAROG_SHEETS = (
    "Death_front_sheet.png",
    "LevelStart_sheet.png",
    "Soul_Siphon_sheet.png",
    "Speedburst_sheet.png",
    "Stun_End_sheet.png",
    "Stun_Loop_sheet.png",
    "Stun_Start_sheet.png",
    "Subjugation_sheet.png",
    "Swing1_FAST_v2_sheet.png",
    "Swing1_Medium_sheet.png",
    "Swing2_Medium_sheet.png",
    "Swing3_Slow_sheet.png",
    "Ultimate_Swing_120fps_sheet.png",
)


class BhA03MediaArchiveContractTest(unittest.TestCase):
    def test_zero_repo_tracking_leakage_or_staged_media(self) -> None:
        tracked = subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT, text=True).splitlines()
        forbidden_names = {n.lower() for n in EXPECTED_SFX_REELS + EXPECTED_SEVAROG_SHEETS} | {
            "sevarog_4moves_live_review.mp4"
        }
        forbidden_dirs = ("sfx_audition/", "sevarog_frames/", "sevarog_live/")
        leaked = [
            p
            for p in tracked
            if Path(p).name.lower() in forbidden_names or any(d in p.lower() for d in forbidden_dirs)
        ]
        self.assertEqual(leaked, [], f"Off-repo media markers leaked into git tracking: {leaked}")

        staged = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"], cwd=REPO_ROOT, text=True
        ).splitlines()
        staged_media = [p for p in staged if p.lower().endswith((".png", ".mp4", ".wav", ".mp3"))]
        self.assertEqual(staged_media, [], f"Binary media must never be staged: {staged_media}")

    def test_antigravity_execution_jsons_parse_cleanly(self) -> None:
        json_files = sorted(ANTIGRAVITY_EXEC_DIR.rglob("*.json"))
        self.assertGreaterEqual(len(json_files), 90)
        for jf in json_files:
            self.assertGreater(jf.stat().st_size, 0, f"Empty JSON file: {jf}")
            with jf.open("r", encoding="utf-8") as fh:
                json.load(fh)

    def test_offrepo_fightvideo_media_non_zero_when_mounted(self) -> None:
        base = Path("D:/FightVideo")
        if not base.exists():
            self.skipTest("D:/FightVideo drive not mounted on this host")

        sfx_dir = base / "SFX_audition"
        for name in EXPECTED_SFX_REELS:
            p = sfx_dir / name
            self.assertTrue(p.is_file() and p.stat().st_size > 0, f"Missing/empty reel: {p}")

        live_clip = base / "sevarog_live" / "Sevarog_4Moves_Live_Review.mp4"
        self.assertTrue(live_clip.is_file() and live_clip.stat().st_size > 0, f"Missing live clip: {live_clip}")

        sheets_dir = base / "sevarog_frames" / "_sheets"
        for name in EXPECTED_SEVAROG_SHEETS:
            p = sheets_dir / name
            self.assertTrue(p.is_file() and p.stat().st_size > 0, f"Missing/empty sheet: {p}")


if __name__ == "__main__":
    unittest.main()
