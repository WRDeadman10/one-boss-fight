# Codex Brief 09: fix the three Shipping findings of AUDIT_02 (small C++ edits, guarded)

From Claude via the owner. You edit the claimed C++ files only; you do NOT run the editor, a build, a package or the game (the machine is running benchmarks). Claude builds, runs the automation tests and the drivers, and validates your report by evidence.

## Validation of Report 08 and a result
Accepted: only the three named files are new; the audit confirmed the six `WITH_EDITOR` guards. Packaging attempt two succeeded (exit 0) and your `CheckStagedContent.py` on the NEW manifest reports 39 of 39 C++-referenced assets present in the staged build (KI-084 closed at manifest level; runtime proof comes with the smoke run). The three Shipping findings are small and real enough to fix now.

## 1. Task
CLAIM and edit exactly these files: `Source/OneBossFight/Player/RPGCombatDebug.h`, `RPGCombatDebug.cpp`, `RPGTraceAudit.h`, `RPGTraceAudit.cpp`, `Source/OneBossFight/Combat/RPGInputTestUtils.h`, `RPGInputTestUtils.cpp`, and create `Documentation/Codex/REPORT_09.md`. Nothing else.
1. A02-1: the Blueprint-callable debug mesh mutators (`RPGCombatDebug.h:83-87` and the bodies near `RPGCombatDebug.cpp:447-451`) must not exist in Shipping: wrap the UFUNCTION declarations and the definitions in `#if !UE_BUILD_SHIPPING` ... `#endif`. UHT parses UFUNCTIONs inside preprocessor blocks only if the macro is a plain `#if`: keep the guard immediately around the whole UFUNCTION + declaration, and use the same condition in the header and the cpp. Check every caller in `Source/` and in `Scripts/Editor/*.py` (Python drivers run in the editor, never in Shipping): list them in the report.
2. A02-2: `URPGTraceAudit` and `URPGCombatDebug` constructors set `PrimaryComponentTick.bCanEverTick = true`. In Shipping they do no tick work: set `bCanEverTick = false` there (`#if UE_BUILD_SHIPPING`), or return early; keep Development and Editor behaviour byte-for-byte the same. Do not change `RPGPlayerMovesSubsystem.cpp` (not claimed): if you think the components should not be created in Shipping, say so in the report with the line.
3. A02-3: `RPGInputTestUtils.cpp:65-70` sets `GEngine->bUseFixedFrameRate = true;` and the VSync cvar without a Shipping guard. Guard the whole test utility body for Shipping (`#if !UE_BUILD_SHIPPING`, the function then returns false or does nothing, matching its return type), and keep the UFUNCTION signatures valid in all configurations (a UFUNCTION must exist the same way in every configuration or be wholly guarded, header and cpp together).
4. In the report: each edit with before and after lines, why UHT and the linker stay happy, every caller found, the configurations you reasoned about (Editor, Development game, Shipping game), and what you could not verify (you cannot compile).

## 2. Rules
No commit or push, no git command that changes the working tree (about 240 uncommitted changes must survive), no editor, build, package or game run. Be conservative: a compile error costs a rebuild. No behaviour change outside Shipping. Never claim the edit compiles.

## 3. Acceptance criteria (Claude checks)
1. Only the claimed files changed. 2. Claude builds the editor target and runs the 28 automation tests and the debug-dependent drivers (`pie_debug_overlay`, `pie_trace_audit`, `pie_damage_path`, `pie_builds`): no change in Development. 3. Claude packages Shipping later and runs `Scripts/CheckPackagedLog.ps1` on its logs.

## 4. Report
`Documentation/Codex/REPORT_09.md`. Tell the owner "Report 09 is ready".
