# C320 DD27f in-memory authoring — FAILED, stop/no fix/no retry

DD29 verification was completed/reported as X-328 BEFORE this launch; fresh preflight verified four actual toolkit receipt entries, DD29final216Source/DLL4e3580fd/EXE, HEADbc3fe6a, Content11752 path+size/Data16hashes, Config/status/process snapshots. C321 ENGINE_LOCK acquired exclusively and recorded, no existing lock bypass. Exact command/arguments in command.json/run_once.ps1: draft_boss_profiles.py --input-json examples/boss_draft_profiles.json --apply, same headless flags -unattended -nullrhi -nosound -nosplash. No --save or additional helper flag. ONE launch, no toolkit/profile/Source fix, retry, build, test, asset save or cleanup.

Editor process exit=0, elapsed=20.229s, helper SystemExit:1;9failures. Raw editor SHA256 `db3a231b4c2e6a32b5a77af6c2d965028df03cd432aa848e7499747d19ff39a1`. Error severity=7; Warning severity=17. No complete-draft SUCCESS. Three in-memory creation attempts each report19properties set/3failed. Exact per-draft and Fields witnesses below. EmberWarden now has a DIRECT110of110readback witness, distinct from overall authoring success (which failed).

## All tagged DRAFT_APPLY lines (full continuation text is also preserved in all_draft_apply_blocks.txt)
```
[2026.10.29-15.04.16:727][  2]LogPython: [DRAFT_APPLY] Creating draft asset at '/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft'...
[2026.10.29-15.04.17:791][  2]LogPython: [DRAFT_APPLY] fields rows read back: 110 of 110 expected
[2026.10.29-15.04.17:815][  2]LogPython: [DRAFT_APPLY] Draft asset 'DA_Boss_EmberWarden_Draft': 19 properties set, 3 failed
[2026.10.29-15.04.17:825][  2]LogPython: [DRAFT_APPLY] Creating draft asset at '/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_AbyssalRevenant_Draft'...
[2026.10.29-15.04.17:849][  2]LogPython: [DRAFT_APPLY] fields rows read back: 0 of 0 expected
[2026.10.29-15.04.17:857][  2]LogPython: [DRAFT_APPLY] Draft asset 'DA_Boss_AbyssalRevenant_Draft': 19 properties set, 3 failed
[2026.10.29-15.04.17:868][  2]LogPython: [DRAFT_APPLY] Creating draft asset at '/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft'...
[2026.10.29-15.04.17:887][  2]LogPython: [DRAFT_APPLY] fields rows read back: 0 of 0 expected
[2026.10.29-15.04.17:889][  2]LogPython: [DRAFT_APPLY] Draft asset 'DA_Player_Hero_Draft': 19 properties set, 3 failed
[2026.10.29-15.04.18:097][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_EmberWarden_Draft fireball fireball_ability expected='/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C' actual_type=NoneType actual_repr=None exception=TypeError: RPGFireballConfig: Failed to convert type 'Name' to property 'FireballAbility' (SoftClassProperty) for attribute 'fireball_ability' on 'RPGFireballConfig'
[2026.10.29-15.04.18:117][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_EmberWarden_Draft phase_dependencies immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'
[2026.10.29-15.04.18:128][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_EmberWarden_Draft stagger_profile immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'
[2026.10.29-15.04.18:139][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_AbyssalRevenant_Draft fireball fireball_ability expected='/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C' actual_type=NoneType actual_repr=None exception=TypeError: RPGFireballConfig: Failed to convert type 'Name' to property 'FireballAbility' (SoftClassProperty) for attribute 'fireball_ability' on 'RPGFireballConfig'
[2026.10.29-15.04.18:161][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_AbyssalRevenant_Draft phase_dependencies immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'
[2026.10.29-15.04.18:171][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_AbyssalRevenant_Draft stagger_profile immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'
[2026.10.29-15.04.18:182][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Player_Hero_Draft fireball fireball_ability expected='/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C' actual_type=NoneType actual_repr=None exception=TypeError: RPGFireballConfig: Failed to convert type 'Name' to property 'FireballAbility' (SoftClassProperty) for attribute 'fireball_ability' on 'RPGFireballConfig'
[2026.10.29-15.04.18:204][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Player_Hero_Draft phase_dependencies immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'
[2026.10.29-15.04.18:215][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Player_Hero_Draft stagger_profile immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'
[DRAFT_APPLY] FATAL: 9 property failure(s) detected during in-memory authoring.
```

## Full untruncated failure details, including multiline exception continuations
```
[DIAGNOSTIC SUMMARY DETAILS (UNTRUNCATED)]
[2026.10.29-15.04.18:097][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_EmberWarden_Draft fireball fireball_ability expected='/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C' actual_type=NoneType actual_repr=None exception=TypeError: RPGFireballConfig: Failed to convert type 'Name' to property 'FireballAbility' (SoftClassProperty) for attribute 'fireball_ability' on 'RPGFireballConfig'
  TypeError: NativizeProperty: Cannot nativize 'Name' as 'FireballAbility' (SoftClassProperty)
    TypeError: NativizeClass: Cannot nativize 'Name' as 'Class' (allowed Class type: 'Object')
      TypeError: NativizeObject: Cannot nativize 'Name' as 'Object' (allowed Class type: 'Class')
[2026.10.29-15.04.18:117][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_EmberWarden_Draft phase_dependencies immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'

[2026.10.29-15.04.18:128][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_EmberWarden_Draft stagger_profile immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'

[2026.10.29-15.04.18:139][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_AbyssalRevenant_Draft fireball fireball_ability expected='/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C' actual_type=NoneType actual_repr=None exception=TypeError: RPGFireballConfig: Failed to convert type 'Name' to property 'FireballAbility' (SoftClassProperty) for attribute 'fireball_ability' on 'RPGFireballConfig'
  TypeError: NativizeProperty: Cannot nativize 'Name' as 'FireballAbility' (SoftClassProperty)
    TypeError: NativizeClass: Cannot nativize 'Name' as 'Class' (allowed Class type: 'Object')
      TypeError: NativizeObject: Cannot nativize 'Name' as 'Object' (allowed Class type: 'Class')
[2026.10.29-15.04.18:161][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_AbyssalRevenant_Draft phase_dependencies immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'

[2026.10.29-15.04.18:171][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Boss_AbyssalRevenant_Draft stagger_profile immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'

[2026.10.29-15.04.18:182][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Player_Hero_Draft fireball fireball_ability expected='/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C' actual_type=NoneType actual_repr=None exception=TypeError: RPGFireballConfig: Failed to convert type 'Name' to property 'FireballAbility' (SoftClassProperty) for attribute 'fireball_ability' on 'RPGFireballConfig'
  TypeError: NativizeProperty: Cannot nativize 'Name' as 'FireballAbility' (SoftClassProperty)
    TypeError: NativizeClass: Cannot nativize 'Name' as 'Class' (allowed Class type: 'Object')
      TypeError: NativizeObject: Cannot nativize 'Name' as 'Object' (allowed Class type: 'Class')
[2026.10.29-15.04.18:204][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Player_Hero_Draft phase_dependencies immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'

[2026.10.29-15.04.18:215][  2]LogPython: [DRAFT_APPLY][FAILURE] DA_Player_Hero_Draft stagger_profile immunity_effect expected='/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C' actual_type=NoneType actual_repr=None exception=RuntimeError: asset does not exist or did not load: '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C'

[2026.10.29-15.04.18:225][  2]LogPython: ==========================================================================================

[2026.10.29-15.04.18:248][  2]LogPython: 
[DRAFT_APPLY] FATAL: 9 property failure(s) detected during in-memory authoring.
```

Observed failures per draft: fireball.fireball_ability TypeError (Name cannot convert to SoftClassProperty); phase_dependencies.immunity_effect and stagger_profile.immunity_effect RuntimeError (the generated-class path does not exist or did not load through the chosen API). Source RPGEncounterBinding.h:92,106,128 declares ALL THREE as TSoftClassPtr<UObject>. This establishes a soft-CLASS distinction in the remaining failures; it does not prove whether the immunity API's existence check or load failed. The package file's disk presence was already verified in the offline count artifact, so do not call that proof the class object is loadable, or call the package absent. Collector actual_type=NoneType/actual_repr=None is what the failure record stores, not a fresh readback of the rejected property's default. No guessed correction applied.

## Every Error-severity line
```
[2026.10.29-15.04.18:272][  2]LogPython: Error: Traceback (most recent call last):
[2026.10.29-15.04.18:272][  2]LogPython: Error:   File "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py", line 1025, in <module>
[2026.10.29-15.04.18:272][  2]LogPython: Error:     main()
[2026.10.29-15.04.18:272][  2]LogPython: Error:   File "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py", line 1021, in main
[2026.10.29-15.04.18:272][  2]LogPython: Error:     sys.exit(0 if success else 1)
[2026.10.29-15.04.18:272][  2]LogPython: Error: SystemExit: 1
[2026.10.29-15.04.18:272][  2]LogEditorPythonExecuter: Error: Python script executed with errors
```

Post-state: zero captured drift outside Saved={}; Source216 exact DD29 final, toolkit/input and binaries unchanged; HEADbc3fe6a, tracked Content/Config/Source status same (existing accepted uncommitted Source changes retained). Content11752paths/sizes and Data16hashes unchanged,Config hashes unchanged; no new .uasset/.umap under Content. These are the required minimum inventory/hash checks; other Content bytes were not all hashed. Saved1newCrashReportClient ini+3changed files pinned/preserved; no cleanup. No engine/compiler after. C321 own lock is released only after evidence freeze/STOP; lock record retained in the bundle.

Limits: attempted in-memory creation and partial readback only. No asset saved, full valid authored definition, CompileParticipant/preflight/preparation/registration/Ready/startup/gameplay/PIE/package claim. All prior failed runs and DD27b missing-pre-state finding remain. C320 path-count reconciliation is in the DD29 report:27actualassetpaths+1previewdirectory, all package files present, multiple differences versus A214's table. Await exact lead correction and fresh release. Idle, ready for engine lane after this failure report; no further engine task inferred.
