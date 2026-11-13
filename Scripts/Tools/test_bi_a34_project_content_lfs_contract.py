import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ONEBOSS_DIR = REPO_ROOT / "Content" / "OneBossFight"
GITATTRIBUTES = REPO_ROOT / ".gitattributes"


class BiA34ProjectContentLfsContractTest(unittest.TestCase):
    def test_gitattributes_tracks_unreal_and_art_binaries_in_lfs(self) -> None:
        text = GITATTRIBUTES.read_text(encoding="utf-8")
        for ext in ("*.uasset", "*.umap", "*.fbx", "*.blend", "*.wav", "*.mp4"):
            self.assertIn(f"{ext} filter=lfs", text, f"Missing LFS pattern: {ext}")

        ptr = subprocess.check_output(
            ["git", "show", "HEAD:Content/OneBossFight/Levels/L_SevarogArena.umap"],
            cwd=REPO_ROOT,
            text=True,
        )
        self.assertIn("https://git-lfs.github.com/spec/v1", ptr)

    def test_project_maps_audio_ui_and_startup_assets_non_zero(self) -> None:
        required = (
            ONEBOSS_DIR / "Levels" / "L_SevarogArena.umap",
            ONEBOSS_DIR / "Levels" / "L_AssetProof.umap",
            ONEBOSS_DIR / "Audio" / "MX_Boss01_Phase1.uasset",
            ONEBOSS_DIR / "Audio" / "MX_Boss01_Phase2.uasset",
            ONEBOSS_DIR / "UI" / "Art" / "T_Boss01_Flask_Full.uasset",
            REPO_ROOT / "Content" / "AdvancedARPGCombat" / "MeleeCombatSystem" / "Blueprints" / "BP_AdvancedGameMode.uasset",
            REPO_ROOT / "Content" / "AdvancedARPGCombat" / "MeleeCombatSystem" / "Blueprints" / "BP_AdvancedGameInstance.uasset",
            REPO_ROOT / "Content" / "AdvancedARPGCombat" / "MeleeCombatSystem" / "UI" / "Fonts" / "Cinzel" / "Cinzel.uasset",
        )
        for path in required:
            self.assertTrue(path.is_file() and path.stat().st_size > 0, f"Missing/empty required asset: {path}")


if __name__ == "__main__":
    unittest.main()
