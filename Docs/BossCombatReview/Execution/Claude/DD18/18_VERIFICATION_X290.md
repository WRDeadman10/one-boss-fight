# DD17/DD18 serialized verification (Codex X-290), run 2026-10-28

Executed by Claude (sole engine operator). Frozen 191 Source files, no Source/Content/Config edit, no git operation, no PIE, no non-editor build. Everything below was read from the raw logs in `run_2026-10-28/`. Not accepted until Codex reviews it.

## Safety before (run_2026-10-28/pre_*)
- HEAD 79d55906d155574a0c308b33d4442f4a7acbf8b9; no Unreal/UBT/MSBuild/compiler process (a Codex headless process existed, untouched, not an engine process).
- Live Source 191 files, byte-equal to `post_c246_correction_full_tree_manifest_sha256.txt` (diff empty); pins 24/24, dependency pins (after C247) all OK, 14/14 candidate assets, 7/7 default catalog assets; no Content/Config change in git status.
- DLL 3009ff5fb38cf9d4f5f08cbfc6ed930c8d4718f636ce7bf036f5e835571aa585, exe 5495fb88c31c1546a01329165d4bbe697671176dd263ee46f57ff2e3c9c34b65.

## Build (one editor build, editor not running)
- `build_dd18.cmd` (Build.bat OneBossFightEditor Win64 Development -WaitMutex): exit 0, 15 s, 9 actions: compile of RPGBossWorldPreparation.cpp, RPGBossPreparationRegistry.cpp, RPGBossWorldInputCompiler.cpp and the three new/changed test units (WorldPreparation, WorldInput compiler, PreparationRegistry), then lib, dll, metadata. UHT NOT invoked (no UHT line in the log). 0 `warning C`, 0 error lines; UBT `Warning:` lines only (Visual Studio compiler not preferred; UnrealClaude/Niagara plugin dependency). "Invalidating makefile (source file added)" and the adaptive-build exclusion list are in the log. First attempt, no retry, no fix round.
- DLL eeade... -> `eea8f85dca0a43cd62ae298917ce901f267fc16ce8c9c15cf5537b5e3bd4d831` (was 3009ff5f...); exe 5495fb88... NOT rebuilt. Log sha256 74d5331c7971ad32ba242200314bd848e1936f0a54cfce142ebbf5847744e193. Source manifest after the build identical to before.

## Focused runs (UnrealEditor-Cmd, -unattended -nullrhi -nosound -nosplash, serial)
| Filter | Found | Result | exit | seconds | Error lines | ensure/fatal/unsupported lines | Warning lines | log sha256 |
|---|---|---|---|---|---|---|---|---|
| OneBossFight.Binding.WorldInput | 3 | 3 Success (ContentRejections, InputRejections, PositiveGameInstance) | 0 | 47 | 0 | 0 | 19 | c2723894...0c40 |
| OneBossFight.Binding.WorldPreparation | 4 | 4 Success (LateInvalidAndCollision, PositiveAndAbort, Refusals, SecondPreparation) | 0 | 24 | 0 | 0 | 19 | 1ee82f81...9db0 |
| OneBossFight.Binding.PreparationRegistry | 3 | 3 Success (AdmissionAndConflicts, Lifetime, ReleaseAndTokens) | 0 | 24 | 0 | 0 | 19 | 47b61291...6f5c |
GIsCriticalError=0 in each. The WorldPreparation and PreparationRegistry runs each contain ONE `LogRPGPreparation` cleanup line (the real name-collision case, Preparation.AllocationFailed[slot=BossTwo][component=RPGBossEncounter]); the WorldInput run has none.

## Full suite (run because all three focused groups were clean)
- `OneBossFight`: Found 129 (119 + exactly the ten new paths, counted from the run), 129 Success, 0 other result, exit 0, 28 s, GIsCriticalError=0, 0 Error lines, 0 ensure/fatal/unsupported lines, 63 Warning lines. Log sha256 a4f2418184748173acf896bd5be81ed55df26114440161759863b57e9927c7e3.
- Membership (`full_dd18_completed_paths.txt`): 129 unique completed paths; every one of the 119 DD16 paths present (0 missing), `OneBossFight.Content.CookCoverage` among them; the only new paths are the ten WorldInput (3), WorldPreparation (4) and PreparationRegistry (3) tests; every path appears exactly twice as `Path={...}` in the log; no filter, no skipped result.
- Warnings: 63 vs 60 in the DD16 full run. Masked comparison (`warnings_vs_dd16_diff.txt`): the only difference is THREE extra `LogPackageName: Warning: GetLocalFullPath called on FPackagePath ... which has an unspecified header extension, and the path does not exist` lines (VF_RandomNoise_01_90 once, ML_Dark_Leather02_Brown_3 twice), the same category as six such lines already in the DD16 run (nine now). By log order they follow `PreparationRegistry.AdmissionAndConflicts` (one block) and `Catalog.Diagnostics` (one block); I did not isolate the cause (retired Greystone skip-package imports of the real default catalog assets are logged just before). Not an error severity line; recorded, not explained.

## After
- Source manifest identical to the pre-run manifest (191 files); pins 24/24 and dependency pins OK, candidates and catalog assets OK; HEAD unchanged; exe untouched; no engine/build process left; no git operation.

## Not done / open (unchanged from X-290 limits)
Quarantine, mid-stage drift, re-entry and worker-thread destruction stay source-only/unexecuted; transient definitions and hand manifest rows are not authored asset provenance; collision retries reuse destroyed, uncollected objects (observed, not a collected-name claim); no cold-load claim (not every asset observed unloaded); no registration, BeginPlay of managed consumers, context publication, Ready, legacy suppression, startup/target/reset wiring, PIE, duel/networking, gate, package or Shipping. The game-instance Init created the game-instance subsystems without an observed error. Nothing committed.
