"""Offline source contracts for configuration-specific Package.ps1 stage roots."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "Scripts" / "Package.ps1"
BENCH_KIT = ROOT / "Scripts" / "MakeBenchKit.ps1"
SHIPPING_SMOKE = ROOT / "Scripts" / "ShippingSmoke.ps1"
PACKAGED_SMOKE = ROOT / "Scripts" / "PackagedSmoke.ps1"
SHIPPING_CHECK = ROOT / "Scripts" / "CheckShippingBinary.py"


class PackageStageRootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = PACKAGE.read_text(encoding="utf-8")
        cls.bench_kit = BENCH_KIT.read_text(encoding="utf-8")
        cls.shipping_smoke = SHIPPING_SMOKE.read_text(encoding="utf-8")
        cls.packaged_smoke = PACKAGED_SMOKE.read_text(encoding="utf-8")
        cls.shipping_check = SHIPPING_CHECK.read_text(encoding="utf-8")

    def test_default_shipping_and_development_roots_are_distinct(self):
        self.assertIn("if ($Configuration -eq 'Shipping')", self.package)
        self.assertIn("'Saved\\StagedBuilds_Shipping'", self.package)
        self.assertIn("'Saved\\StagedBuilds'", self.package)
        self.assertIn("$OtherDefaultStage", self.package)
        self.assertIn("collides with the other configuration", self.package)

    def test_defaults_match_bench_kit_source_roots(self):
        self.assertIn("Saved\\StagedBuilds_Shipping\\Windows", self.bench_kit)
        self.assertIn("Saved\\StagedBuilds\\Windows", self.bench_kit)
        self.assertNotIn("$ShippingStage = Join-Path $Root 'Saved\\StagedBuilds\\Windows'", self.bench_kit)
        self.assertIn("Saved\\StagedBuilds_Shipping\\Windows", self.shipping_smoke)
        self.assertIn("$PackageStage", self.shipping_smoke)
        self.assertIn("StagedBuilds_Shipping", self.shipping_check)

    def test_bench_kit_explicit_source_overrides_remain_supported(self):
        self.assertIn("[string]$ShippingStage =", self.bench_kit)
        self.assertIn("[string]$DevelopmentStage =", self.bench_kit)
        self.assertIn("if (-not $ShippingStage)", self.bench_kit)
        self.assertIn("if (-not $DevelopmentStage)", self.bench_kit)

    def test_packaged_smoke_default_follows_configuration_and_keeps_override(self):
        self.assertIn("if (-not $ExePath)", self.packaged_smoke)
        self.assertIn("if ($Configuration -eq 'Shipping')", self.packaged_smoke)
        self.assertIn("StagedBuilds_Shipping", self.packaged_smoke)
        self.assertIn("else { 'StagedBuilds' }", self.packaged_smoke)

    def test_explicit_relative_and_absolute_stage_overrides_are_supported(self):
        self.assertIn("[string]$StageDir = ''", self.package)
        self.assertIn("[IO.Path]::IsPathRooted($StageDir)", self.package)
        self.assertIn("[IO.Path]::GetFullPath($StageDir)", self.package)

    def test_parameter_and_stage_validation_precede_uat_invocation(self):
        self.assertLess(self.package.index("[ValidateSet('Development', 'Shipping')]"), self.package.index("& $Uat BuildCookRun"))
        self.assertLess(self.package.index("if (-not (Test-Path $Uat))"), self.package.index("& $Uat BuildCookRun"))
        self.assertLess(self.package.index("$StageDir = [IO.Path]::GetFullPath"), self.package.index("& $Uat BuildCookRun"))
        self.assertLess(self.package.index("$G044CookManifest"), self.package.index("& $Uat BuildCookRun"))

    def test_build_stamp_and_cook_check_remain_configuration_scoped(self):
        self.assertIn("Join-Path $StageDir 'Windows\\OneBossFight\\Saved'", self.package)
        self.assertIn("--configuration $Configuration", self.package)
        self.assertIn('"-stagingdirectory=$StageDir"', self.package)
        self.assertIn("-StageDir $PackageStage", self.shipping_smoke)


if __name__ == "__main__":
    unittest.main()
