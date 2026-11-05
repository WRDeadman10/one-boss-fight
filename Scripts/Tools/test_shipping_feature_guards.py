from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "Scripts/CheckShippingFeatureSymbols.py"
SPEC = importlib.util.spec_from_file_location("check_shipping_feature_symbols", CHECKER_PATH)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class ShippingFeatureGuardTests(unittest.TestCase):
    def test_tier2_cvar_declaration_is_inside_development_guard(self) -> None:
        source = (ROOT / "Source/OneBossFight/Player/RPGTier1VisualRules.cpp").read_text(encoding="utf-8")
        start = source.index("#if UE_BUILD_DEVELOPMENT")
        end = source.index("#endif", start)
        self.assertIn('TEXT("rpg.Art.Tier2")', source[start:end])

    def test_build_stamp_implementation_has_development_and_noop_branches(self) -> None:
        source = (ROOT / "Source/OneBossFight/Player/RPGDevelopmentBuildStamp.cpp").read_text(encoding="utf-8")
        self.assertTrue(source.lstrip().startswith("// Copyright"))
        self.assertIn("#if UE_BUILD_DEVELOPMENT", source)
        self.assertIn('TEXT("BuildStamp.txt")', source)
        self.assertIn("#else", source)
        self.assertIn("void ShowIfAvailable(const UWorld&) {}", source)

    def test_optional_benchmark_capture_paths_are_shipping_guarded(self) -> None:
        source = (ROOT / "Source/OneBossFight/Benchmark/RPGBenchmarkRunner.cpp").read_text(encoding="utf-8")
        blocks: list[str] = []
        guarded = []
        active = False
        depth = 0
        for line in source.splitlines():
            directive = line.strip()
            if directive == "#if !UE_BUILD_SHIPPING":
                if depth == 0:
                    active = True
                    guarded = []
                depth += 1
                continue
            if directive.startswith("#if ") or directive.startswith("#ifdef ") or directive.startswith("#ifndef "):
                if active:
                    guarded.append(line)
                depth += 1
                continue
            if directive == "#endif":
                depth -= 1
                if active and depth == 0:
                    guarded.append("")
                    blocks.append("\n".join(guarded))
                    active = False
                continue
            if active:
                guarded.append(line)
        joined = "\n".join(blocks)
        for token in ("RequestCapture", "ProfileGPU", "temporal_upscaler"):
            self.assertIn(token, joined)

    def test_shipping_smoke_defaults_to_dry_run_and_scans_feature_strings(self) -> None:
        script = (ROOT / "Scripts/ShippingSmoke.ps1").read_text(encoding="utf-8")
        self.assertIn("[switch]$Execute", script)
        self.assertIn("if (-not $Execute)", script)
        self.assertIn("RunBenchmark.ps1", script)
        checker = ast.parse((ROOT / "Scripts/CheckShippingFeatureSymbols.py").read_text(encoding="utf-8"))
        tokens = next(node.value for node in ast.walk(checker)
                      if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "TOKENS" for t in node.targets))
        self.assertEqual(ast.literal_eval(tokens), ("rpg.Art.Tier2", "BuildStamp.txt", "DEVELOPMENT BUILD"))

    def test_binary_scan_finds_ascii_and_utf16_tokens_and_accepts_clean_bytes(self) -> None:
        self.assertEqual(CHECKER.find_tokens(b"clean shipping image"), [])
        self.assertIn("rpg.Art.Tier2", CHECKER.find_tokens(b"prefix rpg.Art.Tier2 suffix"))
        self.assertIn("BuildStamp.txt", CHECKER.find_tokens("BuildStamp.txt".encode("utf-16-le")))


if __name__ == "__main__":
    unittest.main()
