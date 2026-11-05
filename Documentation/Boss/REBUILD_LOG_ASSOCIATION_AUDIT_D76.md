# Rebuild log association audit (D76)

Date: 2026-11-03. Read-only trace of `Scripts/Rebuild.ps1` process invocations and log path construction; no build or Unreal process was launched.

| Stage | Wrapper / child | Raw log name | Association and overwrite risk |
|---|---|---|---|
| Build | `Rebuild.ps1` launches `Build.bat`; `$PID` belongs to the wrapper PowerShell process, not the Build.bat/MSBuild child. | `%TEMP%\obf_build_<yyyyMMdd_HHmmss>_<wrapper-PID>.log` | Timestamp plus wrapper PID strongly identifies invocation. Same-PID invocation within the same second can collide; low probability, no exclusive-create/uniqueness retry. Captured complete output is written after child exit. |
| Automation | `Rebuild.ps1 -Tests` launches `UnrealEditor-Cmd.exe`; `$PID` again names the wrapper. | `%TEMP%\obf_tests_<wrapper-PID>.log` passed as `-abslog`. | One wrapper PID distinguishes concurrent invocations, but PID reuse across later sessions can overwrite the prior file. No timestamp or unique suffix. |
| Editor relaunch | `Start-Process UnrealEditor.exe` only when tests/build pass and `-NoRelaunch` is absent. | No explicit raw log path here. | Editor owns its normal log selection; this rebuild wrapper does not associate a relaunch log with its own invocation. |

The wrapper checks native Build.bat status and compiler error text before proceeding. In `-Tests` mode it also records UnrealEditor-Cmd exit status and rejects nonzero status, zero completed tests, or any completed row not marked Success. A failed/incomplete test invocation exits 1 while retaining the log path in its diagnostic. No process ID from the native child is written into log metadata; the association is by wrapper PID/path and timestamp for the build stage.

The artifacts are raw logs in `%TEMP%`, not a permanent invocation manifest. PID reuse and same-second timestamp collision are the documented overwrite risks. No log was opened, generated, or refreshed by this audit.
