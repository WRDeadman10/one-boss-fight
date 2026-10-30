# C361.1 / DD27k FAILED at Hero production dependency check

Exactly accepted test path change promoted byte-for-byte (b77aabf6->830340be), Source219 stable, no other Source change. Four saved assets and manifest file cd088e39 verified from actual files. HEAD6ef433edf6cbf4813ff9db666fff6bc1bad9ddac, allowed C360 delta recorded in baseline.json (none at this run). Exclusive C321lock, fresh pre/post; one build exit0/13.733s,3knownwarnings, no error or visible UHT invocation. Build/raw SHA256 246efed6cf4a6b6eb94e6c40ce99bdef846c1cfee36a90f662b88044620715e2.

ONE focused AuthoredDraft run exit255 (cached handle captured; EXIT_NONZERO, not timeout),1finished0passed1failed, 24.817s. Saved EmberWarden productioncompile ready1/output1. Saved HeroV2 now has4Fields but ready0/output0: required skeleton/animation dependencies missing. The exact missing member is UNKNOWN: current compiler diagnostic combines null skeleton OR empty animation list. No live property probe or inference substituting a cause. Twelve-plan preflight DID NOT RUN; no plan lines emitted. Old assertion text says zero rows, but actual logged fields=4; existing test text left unchanged under exact one-path-only release.

Raw SHA256 912a388e09c04bdfbb7291e918fe5cdb1d06595ad8e0c876ebe5720cde01139b; Error3,Warning13 severity. All errors/warnings/tagged lines verbatim below and separate files. No expected-error filtering/fix/retry/definition mutation/synthetic fallback/fullsuite. Four savedassetSHA unchanged; Content11756paths/sizes/Data20hashes/Config/Source219/toolkit stable, only released DLL/PDB changed; final binaries match post-build hashes. Non-Data Content bytes not all hashed. Saved1new+1changed pinned, no removed; postprocess empty. NewDLL 432fb1f8d5c54fde9f0f39bf0bc1c41c73828c5a4df7db37146fdf5e72d082c9, EXE unchanged. No pack/git/asset write. Lock release after evidence freeze. C361.2 independent inventory release is next only after this evidence is frozen; it does not retry or fix this test.

## Every DD27j line

```
[2026.10.30-05.53.52:590][601]LogAutomationController: [DD27j] loaded boss=/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft.DA_Boss_EmberWarden_Draft player=/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V2.DA_Player_Hero_Draft_V2 manifest=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec phase=PhaseTwo
[2026.10.30-05.53.52:590][601]LogAutomationController: [DD27j] stage=BossCompile ready=1 output=1
[2026.10.30-05.53.52:590][601]LogAutomationController: [DD27j] stage=HeroCompile ready=0 output=0 fields=4
```

## Every test Error line

```
[2026.10.30-05.53.52:590][601]LogAutomationController: Error: Test Completed. Result={Fail} Name={SavedProductionPreflight} Path={OneBossFight.Binding.AuthoredDraft.SavedProductionPreflight}
[2026.10.30-05.53.52:590][601]LogAutomationController: Error: required skeleton/animation dependencies missing [C:\UnrealProject\OneBossFight\Source\OneBossFight\Tests\RPGBossAuthoredDraftPreflightTests.cpp(124)]
[2026.10.30-05.53.52:590][601]LogAutomationController: Error: Expected 'saved Hero production compile; zero rows answered by actual compiler' to be true. [C:\UnrealProject\OneBossFight\Source\OneBossFight\Tests\RPGBossAuthoredDraftPreflightTests.cpp(125)]
```

## Every test Warning line

```
LogCore: Warning: UTS: Unreal Trace Server process returned an error (0x00006005)
[2026.10.30-05.53.38:336][  0]LogUnrealClaude: Warning: === UnrealClaude BUILD 20260107-1450 THREAD_TESTS_DISABLED ===
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_22.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_20.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_38.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_37.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_25.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_23.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_26.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_24.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_35.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_36.
[2026.10.30-05.53.45:746][  1]LogNavigation: Warning: FNavigationOctree::AddNode: Empty bounds, ignoring InstancedStaticMeshComponent /Game/OneBossFight/Levels/L_SevarogArena.L_SevarogArena:PersistentLevel.RPGArenaDressing_0.InstancedStaticMeshComponent_39.
```
