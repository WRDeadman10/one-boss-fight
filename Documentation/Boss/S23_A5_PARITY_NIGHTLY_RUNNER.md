# Queue S23 — A5 parity nightly runner

`Scripts/RunA5ParityNightly.ps1` provides a dry-run list by default and executes only when `-Execute` is supplied. It schedules all 31 registered pairs sequentially through `Scripts/RunA5ParityPair.ps1`; each pair runner launches a fresh Editor process for the legacy arm and another for the selected-data arm. The A4 low-sweep pair routes through its dedicated `run_a4_parity_and_quit.py`; the other 30 use the A5 runner.

## Owner commands

Set one unused output path, then review the exact 31 pair commands without launching the Editor:

```powershell
$outRoot = 'Saved\A5ParityNightly\Nightly-YYYYMMDD-HHMMSS'
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunA5ParityNightly.ps1 -OutRoot $outRoot
```

After reviewing the list and handing the Editor to the runner, execute the same command with `-Execute`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunA5ParityNightly.ps1 -OutRoot $outRoot -Execute
```

`OutRoot` must not already exist. The script writes `summary.md` after each pair and at completion; failures remain rows in the table and the script continues through the remaining pairs before returning a nonzero exit. Each child pair retains its arm logs under its own output directory. The pair harness enforces its registered minimum check count and stops on a failing arm.

Offline acceptance: A5 registration tests pass 17/17; both PowerShell scripts parse without errors; the dry-run prints 31 pair commands and creates no output directory. Codex did not execute the Editor, PIE, or any live pair.

Queue V-C026 added `Scripts/Tools/test_a5_nightly_runner.py` for the fixed 31-unique-driver schedule, default dry-run and no-overwrite guard, and `Scripts/Tools/diff_a5_nightly_reports.py` to compare complete 31-row nightly summaries. A fresh dry-run still prints all 31 commands and does not create the requested output directory. See `V_C026_C029_OFFLINE_TOOLS.md` for report comparison limits.
