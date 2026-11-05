# D145 — performance capture provenance audit

Date: 2026-11-03  
Scope: retained benchmark summaries referenced by `Documentation/PERFORMANCE_LOG.md`; read-only inventory and field comparison. No benchmark, Editor, Unreal, or build was run.

## Retained summary inventory

Scanned 59 JSON summaries across `Documentation/PerfCaptures/` (20 legacy captures), `Saved/bench_return/r1/` (5 Gate 4 captures), and `Saved/bench_return/r2/` (34 experiment captures). All 59 parse as JSON objects. The summary files include a map field (three distinct map names across the inventory), engine version, build configuration, GPU and driver, CPU, RAM, OS, resolution, timing window, and measured frame statistics.

| Provenance field | JSON coverage | Finding |
|---|---:|---|
| Scene/map | 59/59 | `map` is present; values include `L_Benchmark`, `L_Greybox`, and `L_SevarogArena`. Treat this as the recorded scene identifier, not proof of the loaded package contents. |
| Build configuration | 59/59 | Present as `Development` or `Shipping`; this is not a unique build identity. |
| Engine version | 59/59 | Present and consistent at UE 5.5.4 build `40574608`. |
| Machine/host name | 0/59 | **UNKNOWN in every summary JSON.** The r1 and r2 bundle-level `system_info.txt` files record `GANPATIGAMERBOI`, but are collection-level context, not a field linked into each summary. The 20 legacy `Documentation/PerfCaptures` summaries have no adjacent system-info file. |
| Interactive session | 0/59 | **UNKNOWN in every summary JSON.** r1/r2 collection files show console sessions; that does not add a per-summary session field. |
| Unique build ID / binary hash | 0/59 | **UNKNOWN in every summary JSON.** `build_configuration` does not identify the exact executable or compiled Source/content state. |
| Hardware details | 59/59 | GPU, both GPU driver strings, CPU, RAM, OS and resolution are recorded in each JSON. |

The 2026-10-23 Remote Desktop section of `PERFORMANCE_LOG.md` cites its Remote Display Adapter and RDP session from the retained run narrative, but its `summary.json` is not in the scanned 59-file set. The 2026-10-24 valid packaged run's r1 bundle has five per-run summaries and a bundle-level system snapshot. The 2026-10-25 r2 folder likewise has per-run summaries and one bundle-level system snapshot. The source writer `Source/OneBossFight/Benchmark/RPGBenchmarkRunner.cpp:364-379` writes the map, configuration, engine and hardware fields listed above; it does not write host/session/build identity. `Scripts/SummarizeBenchmark.py:44-79` displays only label, GPU, performance metrics and target status; it does not show map, configuration, host, session, or build identity and does not fail on their absence.

## Acceptance and limits

Missing machine, session, and unique build identity are explicitly recorded here as **UNKNOWN**, rather than inferred from the current hardware table or neighboring runs. Scene/map is captured in the JSON. Bundle-level `system_info.txt` supports the documented r1/r2 PC and console context, but cannot prove every run's package identity or session continuity on its own. Raw frame CSVs exist for the r1/r2 runs; the 20 legacy `Documentation/PerfCaptures` entries retain summary JSON only. The first `baseline_defaults` run is already documented as console-only with its raw summary missing. This audit does not upgrade any result's validity or claim a build/source hash binding.
