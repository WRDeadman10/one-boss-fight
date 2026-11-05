# Codex Brief 08: packaged-build readiness (editor-only code, cook coverage)

From Claude via the owner. Files only; you do NOT run the editor, a build, a package or the game. The machine is busy with packaging and benchmarks (mailbox C-6): run nothing heavy. Claude validates your report by evidence and writes Brief 09.

## Validation of Report 07
Accepted statically (scope, syntax, no new unmatched names, `-Repeat` present, `pie_soak` row added by me). Its runtime check comes after the benchmark runs.

## 1. Why this brief
The first packaging attempt failed: the GAME target did not compile because `RerunConstructionScripts` exists only in editor builds and six call sites used it unguarded (fixed with `#if WITH_EDITOR`; mailbox C-7). The editor build never showed it. Packaging will also show whether assets that C++ loads by `/Game` path are in the cooked build (KI-084). Both classes of problem can be found by reading.

## 2. Deliverables (new files only; no existing file edited)
1. `Documentation/Codex/AUDIT_02.md`: a static audit of `Source/OneBossFight`, `Source/OneBossFight.Target.cs`, `Source/OneBossFightEditor.Target.cs`, `Source/OneBossFight/OneBossFight.Build.cs` and `Config/*.ini` for things that break or misbehave in a PACKAGED game (Development and Shipping), each finding with file:line, a quote, the scenario and a fix:
   a. Editor-only API outside `#if WITH_EDITOR`: `GEditor`, `FEditorDelegates`, anything from `UnrealEd`, `Editor.h`, `EditorSubsystem`, `FEditorFileUtils`, `UEditorEngine`, `AActor::RerunConstructionScripts`, `PostEditChangeProperty`/`PostEditChangeChainProperty` overrides without the guard, `UPROPERTY(meta=(...))` is fine, `#include` of editor headers, module dependencies in `OneBossFight.Build.cs` that are editor-only without `Target.bBuildEditor` conditions.
   b. Code that exists only because of Python or tests (`UFUNCTION`s for drivers, `...ForTest` hooks, `RPGInputTestUtils`, `RPGCombatDebug`): confirm each is harmless or guarded in Shipping (`UE_BUILD_SHIPPING`, `UE_BUILD_TEST`); list the ones that draw, log or tick in Shipping.
   c. Packaging config: `Config/DefaultGame.ini` (`+DirectoriesToAlwaysCook`, `MapsToCook`, packaging settings), `DefaultEngine.ini` (startup map, game mode), `Scripts/Package.ps1` map list: does the cook include everything the game loads at run time (the arena map, the pack's folders the project depends on, the project's own Data, Audio, Boss01 folders)? List folders that C++ or Python-free runtime code loads by path that are NOT covered.
   d. Anything that reads a file outside the packaged content at run time (`FPaths::ProjectDir`, `Saved/`, `Scripts/`, `Documentation/`) and would fail or misbehave in a staged build.
   Rate each of a to d: "no defect found" is valid; state how many files you read (list with line counts).
2. `Scripts/CheckStagedContent.py` (Python 3.10, standard library only, read-only): (i) scans `Source/OneBossFight/**/*.cpp|h` for string literals that are `/Game/...` asset paths (handle `TEXT("...")`, `FSoftObjectPath(TEXT("..."))`, `TSoftObjectPtr` constructors, `LoadObject<...>(..., TEXT("..."))`, class paths with `_C`, and `Package.Asset` forms; strip the `.AssetName` suffix and quote forms); (ii) maps each to a file under `Content/` (`.uasset` or `.umap`) and reports paths that do not exist; (iii) given `--manifest <path>` (default `Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt`, read its real format first: it exists from an older package, quote two lines in your report) reports every referenced asset that is NOT in the manifest, grouped by folder; (iv) prints the counts and exits 1 when anything is missing. It must run on the existing old manifest now (say what it printed) and Claude will run it on the new manifest after packaging: this decides whether KI-084 is closed.
3. `Documentation/Codex/REPORT_08.md`: files written, the audit table (id, severity, file:line, one line), the manifest format with two quoted lines, what the script printed on the old manifest, what could not be verified.

## 3. Rules
No commit or push, no git command that changes the working tree (about 240 uncommitted changes must survive), no editor, build, package or game run; do not delete or move anything under `Saved/StagedBuilds` (packaging may be running there: only READ files and only after checking that they are not growing). Never claim a defect without a quote and a scenario. You may run your Python script and syntax-check.

## 4. Acceptance criteria (Claude checks)
1. Only the three named new files exist; nothing else changed.
2. Each audit finding has file:line and a quote Claude opens; Claude counts how many hold.
3. Claude runs `CheckStagedContent.py` against the new manifest after packaging and compares with the runtime: any asset the script says is missing is checked in the staged build's log.
4. The report lists what could not be verified.

## 5. Report
`Documentation/Codex/REPORT_08.md`. Tell the owner "Report 08 is ready".
