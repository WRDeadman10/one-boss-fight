# BT-72 Full-Mode Route Runner Timeout Bounding & Safe Auto-Cleanup Report

- **Date:** 2026-11-17
- **Task ID:** BT-72
- **Category:** Runner safety & automation hardening
- **Status:** Complete / Verified

## 1. Context & Motivation
During BT-71 execution (`[X-2567]`), the Full-mode route acceptance runner was started without a timeout deadline. When desktop UI capture was denied by Windows permissions, the runner remained blocked in its poll loop indefinitely while holding dual C-1155 engine locks and the temporary arena route configuration on disk. Manual intervention was required to close the Editor main window before the runner could safely restore configuration and release locks (`[X-2568]`).

## 2. Implementation Summary
In `Scripts/Editor/run_sevarog_arena_route_acceptance.ps1`:
1. **Validated Parameter:**
   - Added `[ValidateRange(1, 86400)][int]$FullTimeoutSeconds = 3600` to the script `param()` block.
   - Enforces a positive integer timeout bounded between 1 second and 24 hours (86,400s), defaulting to 3,600s (1 hour).
2. **Execution Loop Bounding & Race Prevention:**
   - Computed `$deadline = if ($Mode -eq 'Smoke') { [DateTime]::UtcNow.AddSeconds(900) } else { [DateTime]::UtcNow.AddSeconds($FullTimeoutSeconds) }`.
   - In polling loop:
     * When `$receipt` is found, the runner inspects `[IO.File]::GetLastWriteTimeUtc($receipt)`. If `$receiptWriteTime -gt $deadline`, `$hasTimedOut = $true` is set, preventing late receipts from passing.
     * When `$editorProcess.HasExited` is observed, the runner inspects `$exitTime`. If `$exitTime -gt $deadline`, `$hasTimedOut = $true` is set.
     * If `[DateTime]::UtcNow -ge $deadline`, `$hasTimedOut = $true` is set and loop breaks.
   - Following loop exit, if `$hasTimedOut` is true, the runner throws an unconditional fail-closed `TIMEOUT` exception (`if ($hasTimedOut)`), ensuring no late receipt or late exit bypasses timeout classification.
3. **Graceful Owned Editor Teardown:**
   - Following loop exit on timeout, runner invokes `$editorProcess.CloseMainWindow()` on the runner's owned Editor process (with a 30-second graceful wait period).
   - If the owned process cannot exit, an exception is thrown and locks are intentionally retained for manual recovery, preventing unsafe release while an orphaned instance runs.
   - Never interacts with or terminates unrelated Editor instances (`$otherEditorsStillRunning`).
4. **Fail-Closed Outcome & Clean Teardown:**
   - On timeout, runner throws:
     `throw "TIMEOUT: full-mode driver timed out at $FullTimeoutSeconds seconds"`
   - Catch block classifies the result as `TIMED_OUT`.
   - Finally block restores `Config/DefaultGame.ini` byte-for-byte from original backup, asserts SHA256 match, and cleanly releases both C-1155 atomic locks.
   - No acceptance receipt is emitted (`result=TIMED_OUT`).

## 3. Touched Paths & Hashes
- `Scripts/Editor/run_sevarog_arena_route_acceptance.ps1`
  - SHA256: `5DF121989AA43A6D07B42C9451EFE027155C0B12B0087F0C5890EEACB5E74A3E`
- `Scripts/Tools/test_c1619_route_build_runner_contract.py`
  - SHA256: `39D63E834F1AEBAEB6CDEEB8DB4D9136A02A53E9D429BA39C392F585EFBA706E`
- `Documentation/PROJECT_STATE.md`
  - SHA256: `A68BF2661868B0725D076CDF2096A1F00AA19A4CBB194030CED5C2A8B2D52056`
- `Documentation/TASKS.md`
  - SHA256: `0865026DE8EE8DE99EE22957F83A4E97A89E153110877BF0161C6EC1ADC73451`
- `Documentation/Boss/BT_72_FULL_MODE_RUNNER_TIMEOUT_BOUND_REPORT.md`
  - This document.

## 4. Verification & Contracts
- PowerShell Abstract Syntax Tree (AST) validation: `SYNTAX_VALID` (0 parse errors).
- `python Scripts/Tools/test_c1619_route_build_runner_contract.py`: **22/22 PASS** (covers FullTimeoutSeconds, default 3600s, receipt timestamp deadline check, and unconditional timeout rejection).
- `python Scripts/Tools/test_c1619_sevarog_arena_route_contract.py`: **29/29 PASS**.
- `python -m unittest Scripts/Tools/test_author_production_framework_profile_contract.py`: **15/15 PASS**.
- `python Scripts/Tools/check_doc_links.py`: **broken_links=0**.
- Strictly source-only: 0 builds, 0 Unreal Editor launches, 0 PIE runs executed, 0 asset/config changes, 0 git commits/pushes.
