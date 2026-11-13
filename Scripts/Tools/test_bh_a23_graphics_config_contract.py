import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENGINE_INI = REPO_ROOT / "Config" / "DefaultEngine.ini"
DEFAULT_GAME_INI = REPO_ROOT / "Config" / "DefaultGame.ini"
VFX_DIR = REPO_ROOT / "Content" / "OneBossFight" / "VFX"

EXPECTED_VFX_UASSETS = (
    "NS_Boss_PhaseTwoAura.uasset",
    "NS_Boss_PhaseTwoAura_Boost.uasset",
    "NS_Boss_PhaseTwoAura_BoostLite.uasset",
    "NS_Boss_PhaseTwoAura_BoostLite_Authored.uasset",
    "NS_Boss_ShockwaveRing.uasset",
    "NS_Combat_ParrySpark.uasset",
)


class BhA23GraphicsConfigContractTest(unittest.TestCase):
    def test_default_engine_ini_preserves_tsr_default_and_no_forced_dlss_cvar(self) -> None:
        text = DEFAULT_ENGINE_INI.read_text(encoding="utf-8")
        self.assertIn("GameDefaultMap=/Game/OneBossFight/Maps/L_SevarogArena.L_SevarogArena", text)
        self.assertIn("GameUserSettingsClassName=/Script/OneBossFight.RPGDLSSGameUserSettings", text)
        self.assertNotIn("r.AntiAliasingMethod=", text)
        self.assertNotIn("r.NGX.DLSS.Enable=", text)

    def test_default_game_ini_preserves_required_cook_roots(self) -> None:
        text = DEFAULT_GAME_INI.read_text(encoding="utf-8")
        for root in (
            '+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/VFX")',
            '+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Player/Greystone")',
            '+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Data")',
            '+DirectoriesToAlwaysCook=(Path="/Game/ParagonSevarog")',
        ):
            self.assertIn(root, text, f"Missing required cook root in DefaultGame.ini: {root}")
        self.assertIn("bDefaultToDataStartup=True", text)

    def test_vfx_folder_contains_expected_non_zero_niagara_uassets(self) -> None:
        for name in EXPECTED_VFX_UASSETS:
            asset = VFX_DIR / name
            self.assertTrue(asset.is_file() and asset.stat().st_size > 0, f"Missing/empty VFX asset: {asset}")


if __name__ == "__main__":
    unittest.main()
