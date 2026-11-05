# Queue X X-C021-X-C024 — Round 6 kit readiness audit

Date: 2026-11-06. Static inspection of the transferred Round 6 kit and repository tooling. No game, Editor, benchmark, build, or package was run.

## X-C021 — required kit files

Ran `python Scripts/Tools/check_bench_kit.py --kit-root C:/BenchTransfer/R6/OneBossFight_BenchKit --include-development`: **FAIL**, 110 files / 7,540,732,206 bytes, empty required files 0, PDB files 0. Missing exact paths: `Scripts/PackagedRunLog.psm1`, `Scripts/Tools/check_bench_kit.py`. `BUILD_INFO.txt` lacks both required lines: `Package build ID: OBF-(SHIPPING|DEVELOPMENT)-...` and `Executable SHA-256: <64 lowercase hex>`. The checker does not classify general extra files; it only reports PDB extras, and found none. No additional path is asserted to be an invalid extra by the checker.

## X-C022 — staged executable and telemetry identity

`BUILD_INFO.txt` records executable size 148,816,896 bytes, matching the staged Shipping game binary `Saved/StagedBuilds/Windows/OneBossFight/Binaries/Win64/OneBossFight-Win64-Shipping.exe`; it has no generated build ID or SHA-256, so this size match is not executable identity proof. The two root launcher hashes differ: Shipping `Saved/StagedBuilds/Windows/OneBossFight.exe` = `47fc7d33…`; Development `Saved/StagedBuilds_Development/Windows/OneBossFight.exe` = `cb526bdf…`. The Shipping inner game binary SHA-256 is `3bb85ac2…`; `BUILD_INFO` does not state which executable is covered by a hash.

Compared kit `Scripts/` files against checkout copies:

| Path | Result |
|---|---|
| `Scripts/PackagedSmoke.ps1` | DIFFERENT (kit `df01f485…`, checkout `94d77cd3…`) |
| `Scripts/round6_experiments.json` | DIFFERENT (kit `c90fbefd…`, checkout `2e27c66c…`) |
| `Scripts/RunPerfExperiments.ps1` | DIFFERENT (kit `1b6127fc…`, checkout `5ff0d800…`) |
| `Scripts/BenchKit_Collect.ps1`, `BenchmarkEncounterSelection.psm1`, `CheckPackagedLog.ps1`, `CheckShippingBinary.py`, `round5_experiments.json`, `RunBenchmark.ps1`, `SummarizeBenchmark.py` | BYTE-IDENTICAL |
| `Scripts/PackagedRunLog.psm1`, `Scripts/Tools/check_bench_kit.py` | Missing from kit |

No version/commit stamp ties the differing telemetry files to the staged binaries. This is an identity/provenance gap; the observed differences alone do not establish which copy is intended.

## X-C023 — receipt schema vs operator README

The transferred README at lines 88-92 requires four measured metrics, CVar map, actual upscaler, active-mode log line, primary fraction upper bound, AA method, and `predicted_gpu_saving_ms` with its cited source. The validator covers the metrics, CVar map, upscaler, fraction, AA method and generic active DLSS line (`Scripts/Tools/round6_benchmark_report.py:32-79`); it has no citation field/check. However, `V_C002_C005_ROUND6_INTAKE.md:19` specifies that the source may be in the receipt author's accompanying notes. The current fixture omits it (`test_round6_benchmark_report.py:12-38`) and passes 9/9; this is an ambiguity between README and intake wording, not a demonstrated false pass if accompanying notes are the source of record. Resolve whether the citation must be machine-readable in the JSON or retained in the accompanying report.

For Phase 2, validator accepts `mode="best"` and only checks that copied active log text contains `Creating NGX DLSS Feature`; it does not bind the parsed concrete mode token to a separately recorded, owner-accepted `BestDlssMode` (`round6_benchmark_report.py:55-67`). The line itself can show an actual mode, but the schema does not prove that it is the accepted selection. Keep the selected mode explicit in the receipt or its linked intake record and validate it against the log. These are contract gaps, not evidence that any Round 6 result exists.

## X-C024 — stop controls and failure retention

`RunPerfExperiments.ps1` fails closed on wrong selected route, missing result, failed fight, virtual/remote GPU, active-upscaler/fraction mismatch, missing or wrong Phase 1 DLSS mode log, unknown CVar, anchor drift above 5%, and Phase 1 p99 regression above 5%; it also refuses Phase 2 absent both acceptance switches. These guard paths throw and stop the series while preserving completed result folders.

**Retention gap:** `RunBenchmark.ps1` throws on process timeout or nonzero exit at lines 53-59, before it discovers the run folder and copies the rotated global `OneBossFight.log` into that folder at lines 62-76. Thus failed-run logs are not copied alongside per-run evidence by this script; they remain in a shared stage/local log location that a later run may rotate. RunPerfExperiments stops after the first failing run, which reduces immediate overwrite risk but does not provide durable per-run failure retention. The failure-folder guarantee is incomplete for process-level failures.

## Disposition

X-C021/X-C022 confirm the current kit is not identity-ready and has two required script absences plus three stale telemetry-file copies. X-C023 confirms missing source/mode binding in the receipt validator. X-C024 confirms the named stop gates but finds process-failure log retention incomplete. No kit contents or source files were changed.
