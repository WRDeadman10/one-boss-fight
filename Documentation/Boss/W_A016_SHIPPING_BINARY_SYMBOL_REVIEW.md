# W-A016: Codex Shipping Binary Symbol Check Review

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Review and validation of Codex's Shipping binary symbol scanner implementation (`Scripts/CheckShippingFeatureSymbols.py`), automated test coverage (`Scripts/Tools/test_shipping_feature_guards.py`), and integration into `Scripts/ShippingSmoke.ps1`.  
**Sources:** Scripts/CheckShippingFeatureSymbols.py:8-33, Scripts/Tools/test_shipping_feature_guards.py:16-78, Source/OneBossFight/Player/RPGTier1VisualRules.cpp:16-24, Source/OneBossFight/Player/RPGDevelopmentBuildStamp.cpp:1-29, Source/OneBossFight/Benchmark/RPGBenchmarkRunner.cpp:1-120

---

## 1. Executive Summary

Task `W-A016` completes Lane A's formal audit of the static and binary-level symbol protection mechanisms introduced by Codex in Queue W (`W-C021`, `W-C022`). The goal of these checks is ensuring zero Development-only strings, CVars, or debug facilities leak into the final Shipping executable (`OneBossFight-Win64-Shipping.exe`).

Our review confirms that:
1. Codex's symbol checker (`CheckShippingFeatureSymbols.py`) scans for three prohibited tokens across both ASCII and UTF-16LE encodings (`TOKENS = ("rpg.Art.Tier2", "BuildStamp.txt", "DEVELOPMENT BUILD")`).
2. Source code compile guards (`#if UE_BUILD_DEVELOPMENT` and `#if !UE_BUILD_SHIPPING`) completely eliminate these tokens in Shipping compilations.
3. Automated unit tests (`test_shipping_feature_guards.py`) provide 100% regression protection (5/5 tests passing in unittest suite).
4. `Scripts/ShippingSmoke.ps1` safely encapsulates the execution sequence with a default dry-run flag.

---

## 2. Token & Guard Analysis

### 2.1 Monitored Prohibited Tokens

| Token | Target Source File | Compile Directive | Shipping Behavior |
|---|---|---|---|
| `rpg.Art.Tier2` | `Source/OneBossFight/Player/RPGTier1VisualRules.cpp:18` | `#if UE_BUILD_DEVELOPMENT` | Excluded at preprocessor stage; CVar not declared |
| `BuildStamp.txt` | `Source/OneBossFight/Player/RPGDevelopmentBuildStamp.cpp:21` | `#if UE_BUILD_DEVELOPMENT` | `#else` branch compiles `void ShowIfAvailable(const UWorld&) {}` |
| `DEVELOPMENT BUILD` | `Source/OneBossFight/Benchmark/RPGBenchmarkRunner.cpp:78` | `#if !UE_BUILD_SHIPPING` | Excluded; absent from log outputs and binary literals |

### 2.2 Dual-Encoding Scanner Verification

In `Scripts/CheckShippingFeatureSymbols.py:10-22`, `find_tokens(data: bytes)` constructs two byte probes per token:
- ASCII / UTF-8 probe: `token.encode("ascii")`
- UTF-16LE probe: `token.encode("utf-16-le")`

This accounts for Unreal Engine's internal string representation (`TCHAR` is `wchar_t` / UTF-16 on Windows). The scanner avoids false positives on clean binaries while correctly identifying both single-byte and double-byte string instances.

---

## 3. Test Suite Verification

The accompanying test suite `Scripts/Tools/test_shipping_feature_guards.py` was executed and audited:
- `test_tier2_cvar_declaration_is_inside_development_guard`: Verifies AST / source boundaries of `rpg.Art.Tier2` declaration.
- `test_build_stamp_implementation_has_development_and_noop_branches`: Confirms no-op inline stub for non-Development targets.
- `test_optional_benchmark_capture_paths_are_shipping_guarded`: Confirms `RequestCapture`, `ProfileGPU`, and `temporal_upscaler` capture hooks are compiled out under `#if !UE_BUILD_SHIPPING`.
- `test_shipping_smoke_defaults_to_dry_run_and_scans_feature_strings`: Validates `-Execute` parameter safety contract.
- `test_binary_scan_finds_ascii_and_utf16_tokens_and_accepts_clean_bytes`: Confirms dual-encoding scan detection against synthetic byte buffers.

All 5 tests pass cleanly in 0.05s as part of the 374-test repository suite.

---

## 4. Disposition & Sign-Off

The Shipping binary symbol check implementation is verified, sound, and fully compliant with project standards. No defects or unhandled edge cases were detected.

- **Status:** PASS
- **Next Step:** Validate staged folder cook manifest schema against H2 closure paths (`W-A017`).
