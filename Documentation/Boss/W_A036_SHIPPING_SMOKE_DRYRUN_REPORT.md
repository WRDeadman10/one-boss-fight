# W-A036: Shipping Smoke Pipeline Dry-Run Audit

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Dry-run execution, plan verification, and symbol check validation for `Scripts/ShippingSmoke.ps1`.  
**Sources:** Scripts/ShippingSmoke.ps1:1-38, Scripts/CheckShippingFeatureSymbols.py:1-33, Scripts/Tools/test_shipping_feature_guards.py:60-78, Documentation/Boss/W_A016_SHIPPING_BINARY_SYMBOL_REVIEW.md:1-55

---

## 1. Executive Summary

Task `W-A036` executes and validates the end-to-end dry-run plan of `Scripts/ShippingSmoke.ps1`. This script encapsulates the full release packaging and smoke verification workflow, executing:
1. Shipping configuration packaging via `Scripts/Package.ps1`.
2. Packaged benchmark smoke execution via `Scripts/RunBenchmark.ps1` (900 s timeout).
3. Post-execution binary symbol scanning via `Scripts/CheckShippingFeatureSymbols.py`.

Our audit confirms that:
- The script defaults to a zero-risk dry run when executed without `-Execute`.
- The planned command lines correctly target the Shipping stage and executable binaries.
- The symbol checker is wired to evaluate `OneBossFight-Win64-Shipping.exe` immediately following benchmark completion.

---

## 2. Dry-Run Output & Plan Audit

Execution of `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/ShippingSmoke.ps1` yielded exit code 0 and emitted the exact three-stage sequence:

```text
[DRY-RUN] & "C:\UnrealProject\OneBossFight\Scripts\Package.ps1" -Configuration Shipping -EngineRoot "C:\Program Files\Epic Games\UE_5.5"
[DRY-RUN] & "C:\UnrealProject\OneBossFight\Scripts\RunBenchmark.ps1" -Label shipping_smoke -StageDir "C:\UnrealProject\OneBossFight\Saved\StagedBuilds\Windows" -TimeoutSeconds 900
[DRY-RUN] & python.exe -I "C:\UnrealProject\OneBossFight\Scripts\CheckShippingFeatureSymbols.py" "C:\UnrealProject\OneBossFight\Saved\StagedBuilds\Windows\OneBossFight\Binaries\Win64\OneBossFight-Win64-Shipping.exe"
```

### 2.1 Parameter Invariants Verified
- **Engine Root:** Points to canonical installed path `C:\Program Files\Epic Games\UE_5.5`.
- **Target Configuration:** Explicitly `Shipping` (never `Development`).
- **Benchmark Timeout:** Clamped at 900 seconds ([`ShippingSmoke.ps1:10`](file:///c:/UnrealProject/OneBossFight/Scripts/ShippingSmoke.ps1#L10)), preventing frozen test runs from locking execution agents.
- **Fail-Fast Error Handling:** `$ErrorActionPreference = 'Stop'` and explicit `$LASTEXITCODE` checks abort execution immediately upon any phase failure.

---

## 3. Automated Test Verification

In `Scripts/Tools/test_shipping_feature_guards.py:63-72`:
- `test_shipping_smoke_defaults_to_dry_run_and_scans_feature_strings`: Verifies AST presence of `-Execute` parameter, dry-run branch, and token definitions.
- Passing 5/5 in unit test suite.

---

## 4. Disposition & Sign-Off

The Shipping smoke pipeline script is verified, safe, and ready for Lead packaging sessions.

- **Status:** PASS
- **Next Task:** Audit removal of PDBs and debug libraries from staged Shipping payload (`W-A037`).
