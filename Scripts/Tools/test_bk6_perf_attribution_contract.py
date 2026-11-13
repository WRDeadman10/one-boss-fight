from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXECUTOR = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp").read_text(encoding="utf-8")
COUNTERS = (ROOT / "Source/OneBossFight/Boss/RPGFrameworkPerfAttribution.h").read_text(encoding="utf-8")
SCHEMA = (ROOT / "Documentation/Boss/framework_perf_attribution.schema.json").read_text(encoding="utf-8")


class FrameworkPerfAttributionContract(unittest.TestCase):
    def test_default_off_and_development_only(self):
        self.assertIn('CVarRPGFrameworkPerfAttribution(TEXT("rpg.Perf.FrameworkAttribution"), 0', EXECUTOR)
        self.assertIn("#if !UE_BUILD_SHIPPING\nstatic TAutoConsoleVariable<int32> CVarRPGFrameworkPerfAttribution", EXECUTOR)
        self.assertIn("const double FrameworkTickStart = bMeasureFrameworkTick ? FPlatformTime::Seconds() : 0.0", EXECUTOR)

    def test_scope_exit_records_early_return_paths_only_when_enabled(self):
        self.assertIn("ON_SCOPE_EXIT", EXECUTOR)
        self.assertIn("if (bMeasureFrameworkTick)", EXECUTOR)
        self.assertIn("RecordFrameworkPerfTick", EXECUTOR)

    def test_gpu_is_explicitly_not_component_attributed(self):
        self.assertIn("gpu_component_ms=NA gpu_attribution=unavailable", EXECUTOR)
        self.assertIn("category=executor_tick_inclusive_cpu", EXECUTOR)
        self.assertIn('"gpu_component_attributed": {"const": false}', SCHEMA)

    def test_counter_math_is_saturating_and_ignores_invalid_samples(self):
        self.assertIn("!FMath::IsFinite(Milliseconds) || Milliseconds < 0.0", COUNTERS)
        self.assertIn("MAX_uint64 - TotalMicroseconds", COUNTERS)
        self.assertIn("Samples < MAX_uint64", COUNTERS)


if __name__ == "__main__":
    unittest.main()
