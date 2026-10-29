# DD27 C312 in-memory rerun — FAILED (DD27d evidence folder)

One authorized launch; no save flag, retry, toolkit edit, cleanup, build or automation test. Editor process exit=0, 23.263s; helper reports 29 property failures, returns False and logs SystemExit:1. This is FAILURE despite editor exit0 and misleading per-draft print lines.

Exact command is recorded in command.json/run_once.ps1: UnrealEditor-Cmd.exe OneBossFight.uproject -ExecutePythonScript="<AuthoringToolkit>/draft_boss_profiles.py --input-json <AuthoringToolkit>/examples/boss_draft_profiles.json --apply" -unattended -nullrhi -nosound -nosplash -abslog=<DD27d>/editor_raw.log. No --save or other helper flag.

Fresh preflight read all FOUR required pins from the current AuthoringToolkit/evidence_sha256.txt, matched bytes, captured pre-state and required a verified record; wrapper throws before launch on any failure, rehashes all four pins/pre-state and checks processes again. Both snapshots: HEADbc3fe6a, Source212 equal DD26; Content11752 paths/sizes equal and Data16 SHA256 equal; Config/toolkit/binary hashes equal; tracked Content/Config/Source empty. Processes empty before/after. Captured differences outside Saved: {}. Content outside Data is inventoried by path+size, not fully hashed. Saved has 1 new and 3 changed editor-side files; paths and hashes preserved, no cleanup.

Raw log SHA256 `bf7735a30c9104538a8d2c9115b3118ff77ebad065d65d7876d4eb8677b17b68`. DRAFT_APPLY extraction SHA256 `2cba692daed162882450bbfd7fb603bb0761d3ea9cfaac98438e314c91387ec7`. Diagnostic table extraction SHA256 `773c19b6796efbff6a6eb27738c925f0aa37dfdcf4c070a5dd7b8c657d9fa85a`. Warning severity=2, Error severity=7; every Error line quoted below. TraceServer Error0x5 remains within Warning severity.

## Every DRAFT_APPLY line (verbatim)
```
[2026.10.29-13.12.48:052][  2]LogPython: [DRAFT_APPLY] Creating draft asset at '/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft'...
[2026.10.29-13.12.48:093][  2]LogPython: [DRAFT_APPLY] Initialized & verified all 14 typed properties on draft asset: 'DA_Boss_EmberWarden_Draft'
[2026.10.29-13.12.48:094][  2]LogPython: [DRAFT_APPLY] Creating draft asset at '/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_AbyssalRevenant_Draft'...
[2026.10.29-13.12.48:109][  2]LogPython: [DRAFT_APPLY] Initialized & verified all 14 typed properties on draft asset: 'DA_Boss_AbyssalRevenant_Draft'
[2026.10.29-13.12.48:116][  2]LogPython: [DRAFT_APPLY] Creating draft asset at '/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft'...
[2026.10.29-13.12.48:130][  2]LogPython: [DRAFT_APPLY] Initialized & verified all 14 typed properties on draft asset: 'DA_Player_Hero_Draft'
[DRAFT_APPLY] FATAL: 29 property failure(s) detected during in-memory authoring.
```

The helper prints “Initialized & verified all 14 typed properties” for each draft BEFORE inspecting the shared collector. These are not successful whole-draft readbacks: FATAL29 follows and no final SUCCESS/NOT-saved completion line exists. Source draft_boss_profiles.py:818-825 explains this ordering. Do not certify three successful drafts or all22 properties from these printed14 counts.

## Full emitted diagnostic table (verbatim)
```
[2026.10.29-13.12.48:158][  2]LogPython: [DIAGNOSTIC SUMMARY] Collected 29 failure(s) during in-memory apply:

[2026.10.29-13.12.48:169][  2]LogPython: ==========================================================================================

[2026.10.29-13.12.48:179][  2]LogPython: Asset                      Section          Property           Expected       Actual Type  Actual Repr              Error                     

[2026.10.29-13.12.48:190][  2]LogPython: ----------------------------------------------------------------------------------------------------------------------------------------

[2026.10.29-13.12.48:201][  2]LogPython: DA_Boss_EmberWarden_Draft  top              skeleton           /Game/Advance  NoneType     None                     TypeError: RPGBossDefinit 

[2026.10.29-13.12.48:212][  2]LogPython: DA_Boss_EmberWarden_Draft  top              animations         ['/Game/OneBo  NoneType     None                     TypeError: RPGBossDefinit 

[2026.10.29-13.12.48:223][  2]LogPython: DA_Boss_EmberWarden_Draft  fireball         (constructor)      struct instan  NoneType     None                     TypeError: RPGFireballCon 

[2026.10.29-13.12.48:234][  2]LogPython: DA_Boss_EmberWarden_Draft  phase_dependenc  (constructor)      struct instan  NoneType     None                     TypeError: RPGPhaseDepend 

[2026.10.29-13.12.48:246][  2]LogPython: DA_Boss_EmberWarden_Draft  stagger_profile  (constructor)      struct instan  NoneType     None                     TypeError: RPGStaggerProf 

[2026.10.29-13.12.48:257][  2]LogPython: DA_Boss_EmberWarden_Draft  dormant_wake     (constructor)      struct instan  NoneType     None                     TypeError: RPGDormantWake 

[2026.10.29-13.12.48:268][  2]LogPython: DA_Boss_EmberWarden_Draft  bleed            (constructor)      struct instan  NoneType     None                     TypeError: RPGBleedConfig 

[2026.10.29-13.12.48:279][  2]LogPython: DA_Boss_EmberWarden_Draft  look             (constructor)      struct instan  NoneType     None                     TypeError: RPGLookConfig: 

[2026.10.29-13.12.48:290][  2]LogPython: DA_Boss_EmberWarden_Draft  close_clip_swap  (constructor)      struct instan  NoneType     None                     TypeError: RPGCloseClipSw 

[2026.10.29-13.12.48:301][  2]LogPython: DA_Boss_EmberWarden_Draft  death            (constructor)      struct instan  NoneType     None                     TypeError: RPGDeathConfig 

[2026.10.29-13.12.48:312][  2]LogPython: DA_Boss_AbyssalRevenant_D  top              skeleton           /Game/Advance  NoneType     None                     TypeError: RPGBossDefinit 

[2026.10.29-13.12.48:323][  2]LogPython: DA_Boss_AbyssalRevenant_D  top              animations         ['/Game/OneBo  NoneType     None                     TypeError: RPGBossDefinit 

[2026.10.29-13.12.48:334][  2]LogPython: DA_Boss_AbyssalRevenant_D  fireball         (constructor)      struct instan  NoneType     None                     TypeError: RPGFireballCon 

[2026.10.29-13.12.48:346][  2]LogPython: DA_Boss_AbyssalRevenant_D  phase_dependenc  (constructor)      struct instan  NoneType     None                     TypeError: RPGPhaseDepend 

[2026.10.29-13.12.48:357][  2]LogPython: DA_Boss_AbyssalRevenant_D  stagger_profile  (constructor)      struct instan  NoneType     None                     TypeError: RPGStaggerProf 

[2026.10.29-13.12.48:368][  2]LogPython: DA_Boss_AbyssalRevenant_D  dormant_wake     (constructor)      struct instan  NoneType     None                     TypeError: RPGDormantWake 

[2026.10.29-13.12.48:379][  2]LogPython: DA_Boss_AbyssalRevenant_D  bleed            (constructor)      struct instan  NoneType     None                     TypeError: RPGBleedConfig 

[2026.10.29-13.12.48:389][  2]LogPython: DA_Boss_AbyssalRevenant_D  look             (constructor)      struct instan  NoneType     None                     TypeError: RPGLookConfig: 

[2026.10.29-13.12.48:400][  2]LogPython: DA_Boss_AbyssalRevenant_D  close_clip_swap  (constructor)      struct instan  NoneType     None                     TypeError: RPGCloseClipSw 

[2026.10.29-13.12.48:411][  2]LogPython: DA_Boss_AbyssalRevenant_D  death            (constructor)      struct instan  NoneType     None                     TypeError: RPGDeathConfig 

[2026.10.29-13.12.48:422][  2]LogPython: DA_Player_Hero_Draft       top              skeleton           /Game/Advance  NoneType     None                     TypeError: RPGBossDefinit 

[2026.10.29-13.12.48:432][  2]LogPython: DA_Player_Hero_Draft       fireball         (constructor)      struct instan  NoneType     None                     TypeError: RPGFireballCon 

[2026.10.29-13.12.48:443][  2]LogPython: DA_Player_Hero_Draft       phase_dependenc  (constructor)      struct instan  NoneType     None                     TypeError: RPGPhaseDepend 

[2026.10.29-13.12.48:453][  2]LogPython: DA_Player_Hero_Draft       stagger_profile  (constructor)      struct instan  NoneType     None                     TypeError: RPGStaggerProf 

[2026.10.29-13.12.48:464][  2]LogPython: DA_Player_Hero_Draft       dormant_wake     (constructor)      struct instan  NoneType     None                     TypeError: RPGDormantWake 

[2026.10.29-13.12.48:476][  2]LogPython: DA_Player_Hero_Draft       bleed            (constructor)      struct instan  NoneType     None                     TypeError: RPGBleedConfig 

[2026.10.29-13.12.48:487][  2]LogPython: DA_Player_Hero_Draft       look             (constructor)      struct instan  NoneType     None                     TypeError: RPGLookConfig: 

[2026.10.29-13.12.48:498][  2]LogPython: DA_Player_Hero_Draft       close_clip_swap  (constructor)      struct instan  NoneType     None                     TypeError: RPGCloseClipSw 

[2026.10.29-13.12.48:509][  2]LogPython: DA_Player_Hero_Draft       death            (constructor)      struct instan  NoneType     None                     TypeError: RPGDeathConfig 

[2026.10.29-13.12.48:520][  2]LogPython: ==========================================================================================

[2026.10.29-13.12.48:541][  2]LogPython: 
[DRAFT_APPLY] FATAL: 29 property failure(s) detected during in-memory authoring.
```

Diagnostic limitation: the frozen helper's print_summary_table (:525-537) slices Asset/Section/Property/Expected/Actual Type/Actual Repr/Error columns to fixed widths (25/15/17/13/11/23/25 characters). The complete table AS EMITTED is preserved, but original long expected values, actual repr and exception messages cannot be recovered from this run. No untruncated dump was written by the helper. I did not reconstruct missing details, alter the helper, or launch again. The label `(constructor)` is assigned around the whole create_struct_instance call (:715-718), so it does not distinguish constructor failure from an inner property-conversion/setter exception.

Observed categories: both boss drafts have top-level skeleton and animations TypeError rows; player has skeleton TypeError; all three have eight struct-section `(constructor)` TypeError rows (fireball, phase_dependencies [truncated in table], stagger_profile, dormant_wake, bleed, look, close_clip_swap, death). These sum to29. This does not establish a single root cause or an exact failing nested property because the full exceptions were truncated.

EmberWarden input Fields count110 is pinned in the pre-state JSON. The helper source checks count equality and compares each field's canonical values (:791-816), and no fields failure row appears. There is NO explicit numeric Fields-readback log line, however, and the overall draft fails. Therefore “110 rows read back” is source-control-flow inference only, not a directly logged numeric readback witness. No compiler or preflight was run.

## Every Error-severity line (verbatim)
```
[2026.10.29-13.12.48:577][  2]LogPython: Error: Traceback (most recent call last):
[2026.10.29-13.12.48:577][  2]LogPython: Error:   File "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py", line 921, in <module>
[2026.10.29-13.12.48:578][  2]LogPython: Error:     main()
[2026.10.29-13.12.48:578][  2]LogPython: Error:   File "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py", line 917, in main
[2026.10.29-13.12.48:578][  2]LogPython: Error:     sys.exit(0 if success else 1)
[2026.10.29-13.12.48:578][  2]LogPython: Error: SystemExit: 1
[2026.10.29-13.12.48:578][  2]LogEditorPythonExecuter: Error: Python script executed with errors
```

Limits: in-memory creation attempts and collected failures only. No saved asset, complete valid definition, CompileParticipant/preflight/preparation, binding/Ready/activation, gameplay/PIE/package claim. DD27 original guard failure and DD27b missing pre-state finding remain preserved. Await lead's concrete diagnostic/conversion correction and separate release; DD28 staging interface stop X322 remains unresolved.
