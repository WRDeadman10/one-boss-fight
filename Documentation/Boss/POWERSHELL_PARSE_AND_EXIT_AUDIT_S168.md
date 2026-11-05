# PowerShell syntax and exit-code audit (S168)

Static review of PowerShell scripts under `Scripts`. Each `.ps1` file was parsed with `System.Management.Automation.Language.Parser.ParseFile`; no script body was executed. Follow-up inspection of native process wrappers was also read-only.

## Parse result

- Files parsed: 19 `.ps1` scripts.
- Parser failures: 1.

| File:line:column | Parser message | Source | Proposed correction |
|---|---|---|---|
| `Scripts/PlayDevBuild.ps1:16:61` | Variable reference is not valid: `:` was not followed by a valid variable name character. | `throw "No Development build at $Exe: run ..."` | Use `${Exe}:` in the interpolated string, or format with `-f`. The current script cannot parse until corrected. |

## Native child-process exit-code risks

These are source-level risks; the wrappers were not run.

| File:lines | Current handling | Risk / suggested handling |
|---|---|---|
| `Scripts/Rebuild.ps1:31-34` | Captures Build.bat output and searches it for `error C` or `: error`; it does not capture/check `$LASTEXITCODE`. | A nonzero Build.bat exit without matching text can proceed as if the build succeeded. Capture `$LASTEXITCODE` immediately after the invocation and fail on nonzero as well as diagnostics. |
| `Scripts/Rebuild.ps1:38-45` | Runs UnrealEditor-Cmd for automation, then counts matching log rows; only reports when no tests finished. | The engine process exit code is not checked, and zero or partial test rows do not force failure. Preserve exit code and make missing/incomplete test evidence an explicit nonzero result. |
| `Scripts/RunBenchmark.ps1:48-49` | Waits for the packaged process and prints its exit code. | A nonzero game exit is displayed but not propagated; callers may treat a failed run as success if benchmark output exists. Return/fail on nonzero before summarizing. |
| `Scripts/RunEditorScript.ps1:19-33` | Waits or kills the editor and prints `$proc.ExitCode`; it does not exit with that code. | Python/editor failure can be lost to the caller. Exit with the process code after separately handling intended stop-pattern termination. |
| `Scripts/PlayDevBuild.ps1:20` | Starts the game detached without `-PassThru`/`-Wait`. | This is an intentional launcher; it cannot report the later game exit code. Keep this distinct from a verification wrapper. |

## Checked propagation examples

- `Scripts/Package.ps1:34-43` checks `$LASTEXITCODE` immediately after `RunUAT BuildCookRun` and throws on nonzero.
- `Scripts/MakeBenchKit.ps1:27-30,54-55` handles robocopy's documented success range (`< 8`) and fails on tar's nonzero exit.
- `Scripts/PackagedSmoke.ps1:93-105,115-119` captures checker `$LASTEXITCODE` and bases its verdict/exit status on it.

## Disposition

S168 acceptance is partially met: all 19 `.ps1` files were parsed, the syntax error is identified, and the principal child-process propagation gaps are listed. No scripts were changed or executed; no build, Unreal Editor, runtime, or tests were run.
