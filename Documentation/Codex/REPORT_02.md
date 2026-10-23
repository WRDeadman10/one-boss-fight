# Codex Report 02: Gate 4 Runbook and Packaged Log Checker

## Files Written

- `Documentation/GATE4_RUNBOOK.md`
- `Scripts/CheckPackagedLog.ps1`
- `Documentation/Codex/REPORT_02.md`

No existing project file was edited. The optional Brief 01 soak watchdog update was not made.

## Checker Evidence and Patterns

The checker is read-only. It accepts a file or folder for `-CookLog` and `-RuntimeLog`, otherwise selecting the newest UAT text log under `%APPDATA%\Unreal Engine\AutomationTool\Logs` and newest staged runtime log under `Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs`.

| Category | Checker pattern / rationale | Historical evidence |
|---|---|---|
| Missing or unloadable assets (KI-084) | Requires `/Game/`, `.uasset`, asset/package/object context, or `LogLinker`; generic DLL failures are deliberately excluded. | No historical `/Game` asset-load failure was found. Exclusion is grounded by `Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs\OneBossFight.log:2`: `LogWindows: Failed to load 'aqProf.dll' (GetLastError=126)`. That optional profiler DLL is not a cooked asset. The KI-084 detection patterns are therefore unverified on an actual historical asset failure. |
| Error / shader / cook | `Error:`, `LogShaderCompilers: Error`, and Cook/Shader text combined with `error`, `failed`, or `failure`. | No matching historical error, shader failure, or cook failure was found in the supplied archived UAT/runtime logs. These failure patterns are unverified because the old logs are clean in this category. A non-error shader line read was `Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs\OneBossFight.log:741`: `LogShaderLibrary: Display: Using IoDispatcher for shader code library Global. Total 7584 unique shaders.` |
| Own warnings | `LogRPG*: Warning:`. | No `LogRPG*: Warning` line was found in the archived logs; this pattern is unverified against historical warning output. The source category is real: `Source\OneBossFight\Player\RPGCombatDebug.cpp:171` emits `UE_LOG(LogRPGDebug, Warning, ...)`. |
| Shipping debug text | `LogRPGDebug:`, `rpg.Debug`, or `DrawDebugCircle`. | No archived runtime line contained these text markers, so runtime detection is unverified. Source evidence: `Source\OneBossFight\Player\RPGCombatDebug.h:11` documents `rpg.Debug` and `LogRPGDebug`; `Source\OneBossFight\Player\RPGCombatDebug.cpp:533` calls `AddOnScreenDebugMessage`; `Source\OneBossFight\Player\RPGBossShockwave.cpp:163` calls `DrawDebugCircle`. Both implementation sites are guarded by `!UE_BUILD_SHIPPING` (`RPGCombatDebug.cpp:523`, `RPGBossShockwave.cpp:162`). |
| Crash / fatal | `Fatal error:`, `Critical error:`, `LowLevelFatalError`, `Unhandled Exception`, or `Ensure condition failed`. `CrashGUID` is deliberately not treated as fatal. | The staged log has normal startup metadata at `Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs\OneBossFight.log:45`: `LogInit: Session CrashGUID ...`; it is not a crash. No historical fatal marker was found, so the fatal patterns are unverified on a real failure. |

## Static Validation Performed

The PowerShell parser was run against `Scripts/CheckPackagedLog.ps1`, and the checker was run read-only against the archived default UAT/runtime logs. No editor, build, package, game, or PIE run was started.

Observed archived-log output:

```text
PARSER: PASS
Packaged log check (read-only)
Cook/UAT log: C:\Users\Rushit Vaghela\AppData\Roaming\Unreal Engine\AutomationTool\Logs\C+Program+Files+Epic+Games+UE_5.5\Log.txt
Runtime log:  C:\UnrealProject\OneBossFight\Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs\OneBossFight.log
[missing/unloadable assets (KI-084)] 0
  (none)
[Error / shader / cook] 0
  (none)
[LogRPG warnings] 0
  (none)
[Shipping debug text] 0
  (none)
[crash / fatal] 0
  (none)
Result: PASS (blocking categories empty)
CHECKER_EXIT=0
```

The staged runtime log is from 2026-10-18 and contains retired greybox-era content. Its clean checker result does **not** validate the current cooked asset set or close KI-084.

## Runbook Notes and Owner Decisions

- The runbook uses `Scripts\Package.ps1 -Configuration Development` for G4-1/G4-2 and `-Configuration Shipping` for G4-3, matching that script's supported values.
- It uses `RunBenchmark.ps1` at its actual default 1920x1080 arena fight mode and records the runner's five-second discarded warm-up plus 60-second capture.
- `RunVariants.ps1` has a stale `L_Greybox` default while the package script cooks `L_SevarogArena`; the runbook passes `-Map /Game/OneBossFight/Levels/L_SevarogArena` explicitly.
- The owner must decide whether an RTX 3060 proxy result can ever close the RTX 2060 Super requirement. `Documentation/DECISIONS.md:573` still lists that question as open. This runbook labels every 3060 result `proxy` and does not close the target gate from it.

## Not Verified

- No package, staged executable, smoke checklist, benchmark, variant, Shipping build, editor, or PIE was run for this brief.
- The old UAT log is not a fresh cook and the old staged runtime log predates the current content; neither proves KI-084 is fixed.
- The checker has no archived positive sample for cooked-asset failure, shader/cook failure, project warning, Shipping-debug leakage, or fatal crash. Those patterns need validation on future deliberately captured failures or Gate 4 logs.
