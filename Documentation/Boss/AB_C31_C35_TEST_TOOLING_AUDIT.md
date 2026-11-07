# Queue AB-C31–C35 — focused test discovery, subprocess, report-path, and queue validation

Status: complete locally, 2026-11-07. Offline tools only; no Unreal build, editor, PIE, package, or asset operation.

## AB-C31 — deterministic focused player-contract discovery

Added `Scripts/Tools/discover_focused_player_tests.py`. It parses (does not import or execute) five named offline contract files, sorts group/test/path/line rows, and prints a stable tab-separated or JSON summary. Missing, unparseable, or test-empty files fail closed. Current scan: **19 test methods across five groups** (air attack 3, default route 5, DLSS settings 4, guard counter 3, optional presentation 4). Fixture tests verify ordering/repeatability and malformed/missing inputs. This is a focused offline Python inventory; it does not enumerate native UE automation.

## AB-C32 — Python test subprocess timeout and cleanup audit

Static inventory of `Scripts/Tools/test_*.py` found ten `subprocess.run` call sites and no `Popen` calls:

| File:line | Timeout | Context / cleanup |
|---|---:|---|
| `test_check_bench_kit.py:103,114` | none | CLI checks inside `TemporaryDirectory`; synchronous `run` waits, but a hung child delays directory cleanup indefinitely. |
| `test_parity_tools_isolated_imports.py:14,21` | none | `--help` smoke checks; synchronous, no temporary resources, but no hang bound. |
| `test_queue_w_workflows.py:44` | 30 s | PowerShell dry-run; output root is a `TemporaryDirectory`; timeout is bounded. |
| `test_round5_experiment_plan.py:68` | none | PowerShell dry-run; synchronous and has no timeout. |
| `test_round6_benchmark_report.py:121,124` | none | Two PowerShell dry-runs; no timeout. |
| `test_round6_phase2_intake.py:102` | none | CLI runs inside `TemporaryDirectory`; synchronous, no timeout. |
| `test_gate_script.py:64` | 45 s | New end-to-end Gate fixture with temporary root containing spaces; bounded and receipt/artifacts are contained in that temporary root. |

Finding: the eight pre-existing unbounded calls exercise short `--help`, fixture CLI, or dry-run commands, but a regression could hang the suite. Recommend adding conservative per-call timeouts; `subprocess.run` has no orphan process handle to manage after normal return, and its timeout path kills/waits for the child. No process tree is intentionally left running by these tests.

## AB-C33 — Gate.ps1 path-with-spaces regression

Extended `test_gate_script.py` with a temporary project root named `One Boss Fight Gate ...`, harmless stubs for the build/offline/Shipping/doc commands, and a real `Gate.ps1` run. The receipt reports all five steps passed; the Shipping stub receives the staged executable path as one argument despite spaces. The fixture is bounded at 45 seconds and all generated files live under `TemporaryDirectory`. `test_gate_script.py`: **4/4 PASS**.

## AB-C34 — generated report path assumptions

Scanned current `AA_*.md`, `AB_*.md`, `QUEUE_AA.md`, and `QUEUE_AB.md` for drive-letter absolute paths and Unix home paths. No absolute workspace/user/temp paths occur in generated AA/AB reports. The sole source match is `QUEUE_AA.md:15`, where a fixed reference-tree exclusion and D-drive bench-kit boundary are explicit safety constraints from the binding queue instructions, not stale report output. New discovery and validator outputs use repository-relative paths and no machine-specific root.

## AB-C35 — AA/AB five-task queue validator

Added `Scripts/Tools/validate_queue_batches.py` and fixture tests. It rejects missing, duplicate, unexpected, or out-of-order IDs; requires ten ordered AB headings with five task rows each; checks AA-C01..C50 ordering in ten consecutive groups and confirms X- receipt rows close groups 1–8 (AA-C45 builds Queue AB and AA-C50 closes the lane). Current AA and AB queues both validate at 50 task IDs. Fixtures cover valid queues plus duplicate, missing-ID, and malformed-group cases. Tests: **3/3 PASS**.

## Validation and limits

- `python Scripts/Tools/validate_queue_batches.py`: AA-C PASS (50 rows), AB-C PASS (50 rows).
- `python Scripts/Tools/discover_focused_player_tests.py`: 19 focused tests, five groups, no discovery issues.
- Focused tests: `test_gate_script.py` 4/4, `test_validate_queue_batches.py` 3/3, `test_discover_focused_player_tests.py` 2/2.
- No full offline suite or Unreal/native automation was run in this batch.
