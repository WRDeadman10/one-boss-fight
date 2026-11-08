# Queue AD-C16–C20 — offline test subprocess timeouts

Date: 2026-11-07. Targeted offline tests only; no full suite, Unreal, native build, PIE, cook, or package run.

## C16–C19 — bounded child calls

Seven child processes that previously had no per-call timeout now use `Scripts/Tools/process_test_support.py::run_test_subprocess`:

| Test source | Count | Bound | Scope |
|---|---:|---:|---|
| `test_check_bench_kit.py:106,117` | 2 | 15 s each | Both remain inside their `TemporaryDirectory` contexts. |
| `test_parity_tools_isolated_imports.py:17,24` | 2 | 15 s each | Keeps isolated `-I` Python invocation. |
| `test_round5_experiment_plan.py:69` | 1 | 30 s | PowerShell dry-run; no game launch. |
| `test_round6_benchmark_report.py:122,125` | 2 | 30 s each | Phase 1 and Phase 2 PowerShell dry-runs; no game launch. |

The shared helper requires a timeout argument and converts `TimeoutExpired` into a failing assertion that includes the command and captured stdout/stderr. It does not swallow nonzero exits or alter existing `check` behavior. Direct-child termination/reaping remains Python `subprocess.run`'s timeout behavior. The two bench-kit temp roots are context-managed, so they clean up as the assertion unwinds.

`test_process_test_support.py` launches a real sleeping child with a 0.05 s limit inside a temporary working directory. It checks that timeout becomes a failure, command/output appear in diagnostics, and the temporary root is gone after context exit. This fixture passed with the four affected test modules.

## C20 — remaining direct-call census

Re-scanned all `Scripts/Tools/test_*.py` direct `subprocess.run` calls. The only remaining direct calls are already bounded:

| File:line | Limit | Scope |
|---|---:|---|
| `test_gate_script.py:64` | 45 s | Temporary project root. |
| `test_queue_w_workflows.py:44` | 30 s | Temporary output root. |
| `test_round6_phase2_intake.py:102` | 10 s | Temporary receipt root. |

The seven converted sites no longer invoke `subprocess.run` directly. No unbounded test-file subprocess call remains in this census. The suite-level wrapper in `run_offline_suite_timed.py` still enforces its configured 20 s default separately from these per-call bounds.

## Validation and disposition

`python -m unittest Scripts.Tools.test_check_bench_kit Scripts.Tools.test_parity_tools_isolated_imports Scripts.Tools.test_round5_experiment_plan Scripts.Tools.test_round6_benchmark_report Scripts.Tools.test_process_test_support -q`: **35 tests passed** in 2.316 s. Full suite not run. `git diff --check` is used for documentation/patch whitespace review; repository line-ending notices are expected. KI-195 is closed based on this callsite census and targeted run.
