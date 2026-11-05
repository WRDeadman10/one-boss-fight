# Build failure propagation review (S184)

Rechecked and updated `Scripts/Rebuild.ps1` so compiler and automation failures propagate to the caller and point to retained logs. The wrapper was parsed with the PowerShell AST parser after the edits; it was not executed, and no compiler, Unreal process, or test suite was run.

## Changes

- Build output is captured to a timestamp-and-process-specific file in `$env:TEMP`; the wrapper prints the path on success and failure. It captures `$LASTEXITCODE` immediately after `Build.bat` and exits 1 for a nonzero process code or compiler error text. This covers failures whose output lacks the old `error C` / `: error` pattern.
- The automation log path is process-specific and printed on every run. The wrapper captures `UnrealEditor-Cmd.exe`'s exit code and exits 1 if the process fails, no `Test Completed` rows appear, or the counted successful rows differ from completed rows. The existing completion/success row interpretation is unchanged; the log remains the source for diagnosing individual cases.
- The previous diagnostic-only failed-build branch now exits nonzero. Failures return before editor relaunch.
- S186 further narrowed Rebuild's editor close/force-stop selection to PIDs whose command line identifies this checkout; see `STALE_PROCESS_LOCK_RUNBOOK_AUDIT_S186.md`.

## Verification and limits

`System.Management.Automation.Language.Parser::ParseFile` reported no syntax errors; `git diff --check -- Scripts/Rebuild.ps1` reported no whitespace errors (Git printed only its LF-to-CRLF working-copy notice). Since Build.bat and UnrealEditor-Cmd were not invoked, actual child-process status propagation and log contents still require Lead execution. Acceptance is met by source-level propagation and path reporting; runtime behavior remains unverified.
