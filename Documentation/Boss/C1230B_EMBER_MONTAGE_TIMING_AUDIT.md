# C-1230b — Ember montage timing annotation audit

## Implementation

Added the Editor-only `EmberMontageTimingAudit` commandlet and an editor automation contract. The commandlet scans every `UAnimMontage` below `/Game/OneBossFight/Boss01/Animations`, loads each montage read-only, and compares `URPGANS_BossMoveTiming` entries with matching native `URPGAttackTracker` rows (`MontagePath` or `OptionalTrackerMontagePath`). It uses the shared runtime annotation collector/validator, reporting invalid rows, duplicate MoveIds, unmatched tracker rows, and field differences. Time differences greater than 0.02 seconds are mismatches; branch bounds are compared only for branch-stage rows. It reports absent optional annotations as `MISSING` without failing while annotation use remains opt-in. It never dirties or saves an asset.

Run with:

```powershell
UnrealEditor-Cmd.exe OneBossFight.uproject -run=EmberMontageTimingAudit -DD27jManifestHash=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec -unattended -nosound -nosplash -nullrhi
```

The editor module now depends on the runtime module and AssetRegistry. `Validate` and `CollectAnnotations` are exported from the runtime module so the editor-only audit can use the same validation path as tracking.

## Verification

- Editor automation: `OneBossFight.Editor.EmberMontageTimingAudit.Comparison` covers matching data, the 0.02-second threshold, boolean differences, and numeric differences.
- Actual read-only scan: 6 Ember montages; 4 expected missing annotations (A1, A2, A3a, A3b); 2 non-tracker montages (DeathLegend, ParryRecoil); mismatch=0, duplicate=0, invalid=0.
- Development `OneBossFightEditor` build: PASS.
- Full `Automation RunTests OneBossFight`: PASS 496/496, exit 0, pinned `DD27jManifestHash=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- C-1155 engine rules followed: both lock files acquired/released; `-nosound`; no PIE or capture. No assets were saved or edited.

Evidence is in `Docs/BossCombatReview/Execution/Codex/C1230B_EMBER_TIMING_AUDIT/`. No commit or push.
