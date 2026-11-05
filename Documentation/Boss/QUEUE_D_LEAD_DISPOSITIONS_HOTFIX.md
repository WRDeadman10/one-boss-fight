# Queue D Lead dispositions hotfix

Date: 2026-11-03. Scope: implement Claude's C-751 additive dispositions for D50, D54, D57, and D58. This is a focused source/test hotfix; it does not alter the D63 queue task.

## D50 encounter probe and bridge

`Scripts/Editor/pie_boss_encounter.py` now emits `[EncPie] RESULT PASS|FAIL passed/total` and a `SUMMARY checks=... failed=...` line whenever it finishes. A second-wake timeout is now an explicit failed check instead of a silent stall. The existing global timeout and unexpected-error paths produce a FAIL terminal line.

`Scripts/run_in_editor.py` now returns nonzero when the editor task does not reach `completed`, when the encounter probe reports FAIL, or when an encounter probe emits no terminal result. Successful encounter probes print a machine-readable bridge PASS. The PIE probe itself was not run, so the live output and timeout behavior remain unverified by the Lead's next run.

## D54 manifest verifier fixtures

`Scripts/Tools/test_queue_c_tools.py` now has fixtures for duplicate exact entries, a symlink resolving outside the evidence root, and two lexical aliases (`run.log`, `./run.log`). The current verifier rejects the exact duplicate and outside symlink; it accepts both aliases as separate rows. The symlink fixture skips where the host cannot create a symlink.

## D57/D58 proof report fixtures

Fixtures establish that a missing requested identity is printed as `IDENTITY UNKNOWN` and is non-failing, and that `run_completeness_issues` currently accepts repeated RESULT rows when at least one orderly exit marker exists. The latter documents current behavior; it does not impose exactly-once semantics.

## Verification

Ran from `Scripts/Tools`: `python -m unittest test_queue_c_tools test_queue_c_s36_s40` — 24 tests passed, 1 symlink fixture skipped because symlink creation was unavailable. No Unreal Editor, build, or full project suite was run. The initial root-level unittest invocation failed to import the tool modules because that directory is not on its import path; rerunning from `Scripts/Tools` passed.

## Limits

The probe only asserts player input requests, not actual player displacement. The Lead should verify the new bridge PASS/FAIL behavior on the next live run. The alias fixture records current accepted behavior; canonical-path duplicate detection remains unimplemented. Repeated terminal RESULT rows remain accepted by the optional completeness checker.
