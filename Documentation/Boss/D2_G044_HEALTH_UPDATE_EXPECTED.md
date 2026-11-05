# D2 — G044 boss health parity update

**Status:** Lead-run update PASS (C-847); Codex did not run Editor or modify Content. Lead reports the player package is unchanged, the G044 selection hash now matches the refreshed manifest, and byte-verified backups were created. Codex validated the actual post-update fixture and live receipt after fixing the strict validator.

## Change and safety boundary

The approved source is `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft`. Change only `Stats.MaxHealth`, from the witnessed BUILD-219 value `1500.0` to the shipped legacy value `2000.0`. Keep `DA_Player_Hero_Draft_V3`, selection identity/references/phase, and the phase/config records intact. Refresh the receipt and `DA_Sevarog_G044_Encounter.stable_manifest_hash` so selection remains valid.

`Scripts/Editor/update_g044_boss_health_and_manifest.py` is the single Lead-run Editor script. Before its first package save it checks the exact old health, receipt digest and provenance package hashes, selection class/references/phase/hash, reflected classes, and backup destination. It writes byte-verified backups of the boss draft, player draft, G044 selection package, and current manifest to a unique `Saved/G044/backups/C840_D2_<uuid>/` directory. It then sets and reads back 2000.0, saves the boss draft, regenerates the canonical manifest from the saved package bytes, verifies the new receipt value/hash, updates and reads back the selection hash, saves the selection, and atomically replaces the receipt. It logs the old/new health and package/manifest hashes plus backup index hash.

The package hash in the receipt is only knowable after Unreal serializes the modified draft. Therefore the script performs all input and backup assertions before the first package save, then validates the saved boss and regenerated receipt before the next package save. If a later save fails, preserve the backups and report the failed stage; do not retry over the same run evidence.

## Health assertion/fixture census

The update script intentionally requires the saved draft and current manifest to report exactly 1500.0 before applying this one-way correction; it regenerates the manifest at 2000.0. The active authoring input `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json:22` already records `DA_Boss_EmberWarden_Draft.MaxHealth = 2000.0`.

The active `test_authoring_core.py` has **no test asserting that the Ember Warden draft must remain at 1500**. Its remaining literal 1500 values are generic test data, enumerated here so they are not mistaken for stale G044 expectations:

- `test_finite_floats` (line 507): accepted positive numeric sample for the float validator.
- `test_camelcase_dict_raises_key_error` (line 2293): wrong-case fixture field; failure is about `MaxHealth` key mapping.
- `test_min_and_max_speed_domain_rules` (line 4031): a speed-domain boundary sample (`MinSpeed`).
- `test_old_code_dict_assignment_raises_type_error` (line 6007): generic typed-struct assignment input.
- `test_new_code_struct_instance_assignment_succeeds` (lines 6023, 6049): generic struct round-trip and canonicalization sample.
- `test_diagnostic_failure_collector_collects_without_stopping` (lines 6113, 6133): expected/actual values in a diagnostic collector fixture.

Superseded profile copies, manifests, and evidence remain historical and are not inputs to the D2 script.

## Expected output

- Boss draft readback: `Stats.MaxHealth 1500.0 -> 2000.0`.
- Boss package hash changes; player draft package hash remains unchanged.
- G044 selection references and `PhaseTwo` remain unchanged; only its `stable_manifest_hash` changes to the new receipt digest.
- `Saved/G044/encounter_manifest.json` validates against the newly saved source package hashes and reports boss `stats.max_health: 2000.0`.
- A unique backup directory contains hash-verified source copies and `backup_index.json`.
- No map, production default, player definition, or other boss-definition field is changed.

## Exact Lead command

From the project root in PowerShell, after confirming no Editor process or engine lock is active:

```powershell
$wrap = (Resolve-Path 'Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1').Path
$out = Join-Path (Get-Location) 'Docs/BossCombatReview/Execution/Claude/C840_D2_HEALTH'
if (Test-Path $out) { throw "Preserve existing evidence; choose a new output directory: $out" }
& $wrap -Script (Resolve-Path 'Scripts/Editor/update_g044_boss_health_and_manifest.py').Path -OutDir $out -Task 'C840-D2-G044-health-parity' -NullRhi 1
if ($LASTEXITCODE -ne 0) { throw 'D2 health correction failed; preserve logs and backups' }
```

Then run the offline manifest validator and the approved six-pair parity suite. The script does not execute either.

## Completed run record (C-847)

Claude reports the raw run in `Docs/BossCombatReview/Execution/Claude/C840_D2_HEALTH/`: boss package SHA-256 changed `ba05a8aa…` → `806d8747…`; player package SHA-256 stayed `30cdd6b0…`; manifest SHA-256 changed `2f03e958…` → `4bcf1a63…`; selection `stable_manifest_hash` is `4bcf1a63…`; backup index is under `Saved/G044/backups/C840_D2_37d12b9c…/`. Receipt diff is limited to MaxHealth, the boss package/manifest hashes and tracker provenance fields. Claude caught and fixed the `stable_value(value, unreal, where)` helper call during this run.

Codex then updated `Scripts/Tools/validate_encounter_manifest.py` to recognize the exact tracker provenance contract. The D2 fixture and live `Saved/G044/encounter_manifest.json` both pass the validator with `--project-root .`, including package/evidence byte hashes.
