from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = (ROOT / "Scripts/Editor/run_bk7_shipping_pipeline.ps1").read_text(encoding="utf-8")
RECEIPT = (ROOT / "Scripts/Tools/verify_bk7_shipping_receipt.py").read_text(encoding="utf-8")


class BK7ShippingRunnerContract(unittest.TestCase):
    def test_default_is_preflight_only_and_build_requires_explicit_switch(self):
        self.assertIn("[switch]$Execute", RUNNER)
        self.assertIn("if (!$Execute) { $preflight | ConvertTo-Json -Depth 5; exit 0 }", RUNNER)

    def test_refuses_editor_and_either_c1155_lock_before_execution(self):
        self.assertIn("Get-Process UnrealEditor*", RUNNER)
        self.assertIn("ENGINE_LOCK.json", RUNNER)
        self.assertIn("C-1155 engine lock exists", RUNNER)
        self.assertLess(RUNNER.index("C-1155 engine lock exists"), RUNNER.index("if (!$Execute)"))

    def test_refuses_overwrite_and_requires_supplied_reflection_command(self):
        self.assertIn("refusing overwrite", RUNNER)
        self.assertIn("no reflection command is guessed", RUNNER)
        self.assertIn("ReflectionDumpExecutable @ReflectionDumpArguments", RUNNER)

    def test_binary_and_feature_scans_are_wired_to_the_staged_executable(self):
        self.assertIn("CheckShippingBinary.py", RUNNER)
        self.assertIn("CheckShippingFeatureSymbols.py", RUNNER)
        self.assertIn("$shippingExe.FullName", RUNNER)

    def test_receipt_verifier_binds_artifacts_to_build_and_refuses_smoke_claim(self):
        self.assertIn('artifact.get("build_id") != receipt["build_id"]', RECEIPT)
        self.assertIn('receipt["shipping_smoke"] != "NOT_RUN"', RECEIPT)


if __name__ == "__main__":
    unittest.main()
