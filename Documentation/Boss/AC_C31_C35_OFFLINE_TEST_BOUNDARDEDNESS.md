# AC-C31–C35 — offline suite boundedness and discovery

Date: 2026-11-07. Offline tooling/test work only; no Unreal/build/cook/PIE.

## AC-C31–C32 — 20-second suite wrapper

`Scripts/Tools/run_offline_suite_timed.py` defaults to 20 seconds and accepts only finite positive `--max-seconds`. Before this change it checked elapsed time after `subprocess.run` returned, so a hung suite process could bypass the intended budget. It now passes the selected budget as the subprocess timeout, reports timeout as `OFFLINE_SUITE_TIMING FAIL`, and exits 2; ordinary nonzero unittest exit codes remain preserved. `test_offline_suite_timing_runner.py` now simulates timeout and nonzero exit and verifies the default/override reaches `subprocess.run`.

## AC-C33–C34 — subprocess and cleanup inventory

Current static inventory of `subprocess.run` in `Scripts/Tools/test_*.py`:

| File/call sites | Timeout | Resource scope |
|---|---:|---|
| `test_check_bench_kit.py:103,114` | none | Both inside `TemporaryDirectory`; context cleanup waits for each call to return. |
| `test_parity_tools_isolated_imports.py:14,21` | none | Short `--help` subprocesses; no temporary outputs. |
| `test_round5_experiment_plan.py:68` | none | PowerShell dry run; no temporary outputs. |
| `test_round6_benchmark_report.py:121,124` | none | PowerShell dry runs; no temporary outputs. |
| `test_round6_phase2_intake.py:102` | 10 s | Selected Round 6 intake group; call is inside `TemporaryDirectory`, whose cleanup runs when timeout propagates. |
| `test_queue_w_workflows.py:44` | 30 s | Temporary output root. |
| `test_gate_script.py:64` | 45 s | Temporary project root and generated artifacts. |

At the time of this AC batch, seven calls still lacked per-call bounds; Queue AD-C16–C20 later closed that maintenance via `process_test_support.run_test_subprocess`. The inventory above is retained as the dated AC-C33–C34 snapshot and is superseded by `Documentation/Boss/AD_C16_C20_SUBPROCESS_TIMEOUT_HARDENING.md`. Python `subprocess.run` timeout cleanup covers the direct child; no audited test intentionally daemonizes descendants.

## AC-C35 — focused-player discovery inventory

`python Scripts/Tools/discover_focused_player_tests.py` parsed the five named focused player contract files without importing/executing them and reported **19 methods / 5 groups**: air attack 3, default route 5, DLSS player settings 4, guard counter 3, optional presentation 4. This inventory excludes native Unreal automation and says nothing about test execution.

## Validation

`python -m unittest Scripts.Tools.test_offline_suite_timing_runner Scripts.Tools.test_round6_phase2_intake -q`: **11/11 passed**. The focused discovery command reported 19/5 with no parse/discovery errors. The full offline suite was not run; Unreal/native automation, build, CookCoverage and PIE remain Lead-owned.

