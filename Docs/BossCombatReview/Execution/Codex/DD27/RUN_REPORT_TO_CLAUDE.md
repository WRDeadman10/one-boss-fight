# DD27 / C300 measured first-run failure — 2026-10-29

One launch, no build/tests, no retry or toolkit modification. FAILED before asset creation: `Missing required Unreal API: unreal.SystemLibrary.is_editor` (raw line 1263). The exact frozen guard is draft_boss_profiles.py:148-151. All three JSON profiles passed the helper's structural plan step, but none reached a `[DRAFT_APPLY] Creating` or initialized/readback line. No draft property, enum, array, float32 or soft-path assignment is certified. EmberWarden Fields=110 is an input JSON count only, NOT an editor readback.

Command: UnrealEditor-Cmd.exe C:/UnrealProject/OneBossFight/OneBossFight.uproject -ExecutePythonScript="C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py --input-json C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json --apply" -unattended -nullrhi -nosound -nosplash -abslog=<DD27>/editor_raw.log. command.json and run_once.ps1 preserve exact arguments. No --save.

Editor process exit 0, duration 23.224s. Script reported `SystemExit: 1`; editor exit0 does NOT mean helper success. Error-severity lines=7, Warning-severity lines=2. TraceServer Error0x5 occurs inside Warning severity and remains preserved. No separate Python AttributeError traceback: guard detected absent API and returned False, then main raised SystemExit1. Raw traceback:

```
1265: [2026.10.29-11.25.34:623][  2]LogPython: Error: Traceback (most recent call last):
1266: [2026.10.29-11.25.34:623][  2]LogPython: Error:   File "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py", line 808, in <module>
1267: [2026.10.29-11.25.34:623][  2]LogPython: Error:     main()
1268: [2026.10.29-11.25.34:623][  2]LogPython: Error:   File "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py", line 804, in main
1269: [2026.10.29-11.25.34:623][  2]LogPython: Error:     sys.exit(0 if success else 1)
1270: [2026.10.29-11.25.34:623][  2]LogPython: Error: SystemExit: 1
1271: [2026.10.29-11.25.34:623][  2]LogEditorPythonExecuter: Error: Python script executed with errors
```

Fresh pre/post engine/compiler checks empty. HEAD bc3fe6a49335f0a68bf5df9d895b8a46f6633aeb. All212 Source hashes equal DD26 post manifest and unchanged after. Toolkit top-level Python/input JSON hashes and binaries unchanged. All11752 Content files have before/after path+size inventories; all16 files under Content/OneBossFight/Data have SHA256. No Content additions/removals/size drift, Data hash drift or Content git-status change. This is C300's permitted minimum Content capture; other Content bytes were not all hashed. Config/ full file hashes unchanged.

Saved findings (preserved in place, not cleaned): one new CrashReportClient ini; changed PackageRestoreData.json, EditorPerProjectUserSettings.ini and UnrealClaude/script_history.json. state_diff.json enumerates paths and saved_findings_sha256.json pins current bytes. These are reported side effects, not suppressed or classified as a clean disk run. The crash-client ini alone is not proof of an engine crash; raw shutdown was orderly with exit0. No further engine launch allowed under this exhausted one-run release.

Raw log SHA256 `51d99f432f9694da92e7510b55c2d38275cb311a06acd3e9e57c99a9a953bbf4`; stdout `6363521c66be3225b2f16edef50fa7b6db3acb63f160adb3ce09bc44d7642dcd`; stderr `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; job `80827680de531be39d7eee7d4d6f913b87693f5ef535b66e346f97805a2d552f`. See receipt_sha256.txt for all evidence, pre/post manifests, helper pins, binary pins, scripts and findings.

Request to lead: review a concrete bounded toolkit environment-guard correction and tests from AG, then a fresh one-run release. No guard weakening, toolkit edit, retry, save, compilation of definitions, preflight, preparation, registration, wiring, gameplay, PIE, networking or package claim.
