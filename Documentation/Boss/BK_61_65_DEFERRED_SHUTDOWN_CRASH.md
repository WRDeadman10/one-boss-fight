# BK-61..65: deferred-refusal shutdown crash (python311.dll) — offline diagnosis

Assigned by X-1990 (lead Codex) to C (implementer), 2026-11-11. Offline only: no Unreal, build, PIE, asset writes or lock use; no edits to the BK-56..60 files claimed in X-1984.

## BK-61 — shutdown/exit sequence (from receipts and scripts)

Run_20261111_090828 `deferred_pie.log`, in order:

1. 09:10:53.238 `[SevarogLive] DEFERRED_TICK_RESULT ... outcome=ActivationRefused ...` with the parity snapshot (driver `pie_sevarog_framework_live.py`, refusal branch after `activate()`): the driver destroys the transient boss, logs the marker, sets `STATE["done"]` and returns. It deliberately does not raise, call `finish()` or unregister its slate callback (driver comment: the Python plugin can fault during callback teardown).
2. The runner (`run_bk56_60_deferred_selection.ps1:142-147`) polls the log every 2 s, sees the marker and leaves the loop; its `finally` (`:150-151`) calls `CloseMainWindow()`, waits 5 s, then `Kill()` if needed.
3. 09:10:53.731 `Window 'OneBossFight - Unreal Editor' being destroyed` → PIE teardown → 09:10:54.023 `Cmd: QUIT_EDITOR` / `Engine exit requested (reason: UUnrealEdEngine::CloseEditor())` → 09:10:54.738 `LogExit: Preparing to exit.`
4. 09:10:56.885 `EXCEPTION_ACCESS_VIOLATION` in `python311.dll`, called from `UnrealEditor-PythonScriptPlugin.dll`, during engine exit; `StaticShutdownAfterError`, `RequestExit(1)`. The crash comes 3.2 s after the close request, before the runner's 5 s `Kill()`, so the kill is not the cause.

Across every retained receipt:

| Receipt | Deferred activation refused | Callback unregistered (`finished:`) | python311 crash at exit |
|---|---|---|---|
| BK_56_60 Run_072640 | yes (raised, `finish()` ran) | yes | yes |
| BK_56_60 Run_073307, 073838, 085921, 090828 | yes (marker, no `finish()`) | no | yes |
| BK2_X26_DRIVER Run_022223 pie_S1 / pie_S6 (same `CloseEditor` exit) | n/a (standalone profile) | yes | no |
| X26 R3/R4 arms | n/a | yes | no |

### Proved
- The crash happens inside the Python plugin during editor exit, after `LogExit: Preparing to exit.`, in 5/5 deferred runs. In every one, the deferred activation was refused.
- The result/refusal marker and snapshot are written before the exit begins in every receipt, so the crash does not lose the evidence (asserted by `test_retained_receipts_log_the_marker_before_editor_exit`).
- The crash does not depend on whether the slate callback was still registered: Run_072640 unregistered it through `finish()` and still crashed. The driver comment's theory (callback teardown) therefore does not explain the crash on its own.
- No non-deferred editor exit through the same `CloseEditor` path crashed (BK2 S1/S6, X26 arms).

### Unknown
- The faulting native frame. Minidumps exist (`Saved/Crashes/UECC-Windows-C784A37F4CF8EE87FB04D19A2721A7D4_0000/UEMinidump.dmp` matches Run_090828's CrashGUID), but this engine install has no `UnrealEditor-PythonScriptPlugin.pdb`, so the stack shows only `UnknownFunction`.
- Which part of the refused deferred path leaves state that faults at Python finalization. Candidates, none proved: (a) the selection/moves subsystem calls on the refusal path (`clear_selected_definition`, `rpg.EncounterDefinition`/`rpg.FrameworkEncounterSelection` console state, `activate_deferred_selection_for_test` refusal, `ReportActivationFailure`); (b) the transient framework boss destroyed from Python inside the same tick as the refusal; (c) Python wrapper objects for GameInstance subsystems that outlive the PIE GameInstance.
- Whether the crash also happens after a successful deferred activation. That needs the BK-59 data gate (X-1991) cleared first.

## BK-62 — refusal/exception path audit

| ID | Finding (file:line) | Effect | Minimal safe correction |
|---|---|---|---|
| F1 | The runner never reads the PIE process exit code (`run_bk56_60_deferred_selection.ps1:149-152`; status at `:178` has no PIE exit field) | A crash at exit (exit 1) is invisible in `status.txt`; it is found only by grepping the log | After `WaitForExit()`, write `PIE_EXIT=$($pieProc.ExitCode)` to a receipt. Keep the marker-based verdict, since a crash after the marker does not void the evidence, but record it |
| F2 | `status.txt` is written only after every check passes (`:178-179`); a refused run throws at `:164` and leaves no machine-readable status, only `lock_result.txt` from `finally` | Refusal receipts are not deterministic; reviewers must parse the raw log | Wrap the body with a `catch` that writes `failure_status.txt` (stage, message, PIE exit code), then rethrow, so the exit code still propagates |
| F3 | The driver refusal branch returns with the slate callback still registered, and PIE ends only when the runner closes the editor | Run by hand without the runner, the editor stays in PIE ticking a no-op callback | Acceptable for the runner. If changed, unregister after the marker; Run_072640 shows this alone does not prevent the crash |

Lock cleanup is sound: `finally` (`:182-191`) removes only locks whose `owner_token` matches, and writes `lock_result.txt` on every path.

## BK-63 — correction

No code edit. F1 and F2 belong in `Scripts/Editor/run_bk56_60_deferred_selection.ps1`, a BK-56..60 file claimed by the lead (X-1984), which X-1990 excludes. Nothing statically justifies changing the driver's refusal branch either: the crash happens with or without the unregister. The patch text for F1/F2 is above, for the lead to apply.

## BK-64 — tests

New file `Scripts/Tools/test_bk61_65_refusal_shutdown_contract.py` (8 cases, read-only: it parses the runner, the driver and the retained receipts, and never launches Unreal or touches assets or locks):
- The refusal marker carries the selection diagnostic and the snapshot, captured before the marker.
- The refusal branch leaves shutdown to the runner (no `finish`, unregister or raise).
- The runner stops polling on the result or error markers, closes then kills, and releases only its own token's locks; `lock_result.txt` is written in `finally`.
- In every retained receipt the marker precedes editor exit.
- In the retained receipts the crash occurs only in refused deferred runs.
- Two `expectedFailure` test-first cases for F1 (PIE exit code recorded) and F2 (failure status written on throw); remove the decorators when the lead applies the fix.

## BK-65 — validation (exact)

- `python -I -m unittest discover -s Scripts/Tools -p "test_bk61_65_refusal_shutdown_contract.py" -v` → `Ran 8 tests ... OK (expected failures=2)`.
- `python -I -m py_compile Scripts/Tools/test_bk61_65_refusal_shutdown_contract.py` → OK.
- Full `discover -p "test_*.py"`: 788 run, failures=12, errors=19, skipped=1, expected failures=2. The baseline without the new file is identical (failures=12, errors=19, skipped=1). The failures are pre-existing (loader import errors such as `test_air_light_receipt`, `test_aq_evidence_freshness`, `test_ar_charge_receipt`, plus `test_validate_encounter_manifest`, `test_optional_tier2_hooks` and others) and unrelated to this batch.
- `git diff --check` on the new file: clean.

Changed files: `Scripts/Tools/test_bk61_65_refusal_shutdown_contract.py` (new) and this report (new). A later locked run is still needed to (1) apply F1/F2 and see `PIE_EXIT` recorded, and (2) find out whether a successful deferred activation also crashes at exit (after X-1991). Symbolizing the minidump would need the engine's editor debug symbols (`UnrealEditor-PythonScriptPlugin.pdb`) to be installed.

## Lead review and receipt hotfix

Codex reviewed C-1304 and accepted BK-61..65. The evidence supports the distinction between a proved editor-exit crash and unknown root cause; the report correctly avoids blaming callback teardown and notes that refusal markers precede shutdown. Codex applied the two narrow runner fixes identified in F1/F2 to lead-owned `Scripts/Editor/run_bk56_60_deferred_selection.ps1`: it writes `pie_exit.txt` after the PIE process is fully closed and includes `PIE_EXIT` in success status; on a caught in-run failure it writes `failure_status.txt` with stage/error/PIE exit, then rethrows while preserving the existing outer `finally` lock cleanup. The two test-first expected failures were enabled. Focused contracts pass 8/8; PowerShell parser and scoped `git diff --check` pass. No Unreal/build/PIE was run; a later locked run is required to verify real receipts on refusal and successful activation.
