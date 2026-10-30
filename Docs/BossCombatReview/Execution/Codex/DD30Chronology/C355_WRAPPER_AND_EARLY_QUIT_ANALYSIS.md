# C355: new cached-handle wrapper and early QUIT_EDITOR analysis

## 1. New wrapper / actual offline fake-process proof

New Codex/DD30Chronology/run_chronology_v2.ps1, no modification to Antigravity packet. Invoke-CachedHandleProcess reads $proc.Handle immediately after Start-Process -PassThru, before WaitForExit; then Refresh and ExitCode. Bounded180s for future editor lane; timeout stops ONLY the process id it created. A null exit is EXIT_CODE_UNKNOWN, never coerced to success. No engine execution released by C355: main path requires explicit_engine_release.json, actual lead message, own exclusive lock, reviewed preflight and command file, one-use job. Launch mode is deliberately a reviewed input, not blindly inherited.

C355_fake_process/test_exit_capture.ps1 dot-sources FUNCTIONS ONLY and launches two ordinary PowerShell child scripts exiting0/3. Actual exit0 captured0/SUCCESS; exit3 captured3/EXIT_NONZERO; both cached nonzero handles, no timeout. Harness exit0; raw output and observed_exit_codes.json retained. This is real OS child-process evidence, not an Unreal/PIE test. It cannot retroactively recover the old run's null exit code (still UNKNOWN).

## 2. Raw chronology facts

Antigravity/EngineRuns/DD30ChronologyRun1/chronology_raw.log:1248 records REQUEST freshPIE at18:31:10.969 frame2; :1292 PIE_WORLD at18:31:13.899 frame3. :1293 logs the AutomationController ignoring a2.93s delta. :1306 Cmd: QUIT_EDITOR at18:31:13.903 frame3,4ms after PIE_WORLD. No CAPTURE_END, REQUEST QUIT_EDITOR or quit exception driver line occurs in the complete raw file. Full10s window and later gameplay therefore unmeasured. The exact value of the Python driver's elapsed accumulator is NOT printed; AutomationController's2.93s is not proof that the driver's accumulator equals2.93s.

Driver code: tick adds dt at:58, then requests freshPIE:69-70, logs PIE_WORLD:74. Its normal finish/CAPTURE_END is conditional elapsed>=10 at:75-76. finish(:39-55) logs its message and only then registers quit_tick. quit_tick(:15-37) has its own60tick logging guard(:19-23) and120tick fallback. Their absence is consistent with forced earlier shutdown; do not assert a measured elapsed value or blame finish() without a witness.

## 3. The actual engine termination path is available in local Source

UE5.5 PythonScriptPlugin/Private/EditorUtilities/EditorPythonExecuter.cpp:58-81, FExecuterTickable::Tick, after script execution begins checks bIsRunning and !UEditorPythonScriptingLibrary::GetKeepPythonScriptAlive(), then calls RequestExit. :109-125 RequestExit sets bExitRequested, destroys its notification and calls GEngine->HandleDeferCommand(TEXT("QUIT_EDITOR"), *GLog). :144 parses -ExecutePythonScript=. EditorPythonScriptingLibrary.cpp:9 initializes keep-alive to false; :12-19 setter/getter. Driver registers a Slate callback and returns at:78, and never sets keep-alive. EditorServer.cpp:5761-5764 handles QUIT_EDITOR via CloseEditor. Project Scripts/RunEditorScript.ps1:3-4 already documents this -ExecutePythonScript lifetime and uses -ExecCmds py for tick-driven scripts.

Inference, strongly supported by this exact launch/code/log: the command-line Python executor's built-in deferred quit ended the editor after top-level script completion/next execution tick, before the driver's10s finish/deferred quit path. This explains why Cmd:QUIT_EDITOR has no driver REQUEST marker. The earlier A236 UNKNOWN about the C++ callsite is now narrowed by actual local-source inspection above. The raw Cmd line has no issuer stack, so unique runtime attribution among every possible engine/plugin issuer is UNKNOWN; no debugger/trace was run. No need to invoke startup-delta accumulation as a proven cause.

## Limits / next gate

Wrapper correction is implemented and offline-qualified only, not a release to rerun PIE. A later lead packet must choose a supported long-lived startup mode (existing project's ExecCmds py or explicitly reviewed keep-alive handling) and independently verify full CAPTURE_END/quit/exit0 in a new one-use packet. Do not edit/re-run AG's historical attempt or relabel its null exit as0. C354 accepted the early native chronology only; those measured callback/census/first-component routes remain distinct from a10s-window result. C356 fail-closed runtime policy remains binding; no ActivateWorld/wiring change here.
