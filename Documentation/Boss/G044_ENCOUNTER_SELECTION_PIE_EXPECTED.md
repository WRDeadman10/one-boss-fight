# G044 — opt-in encounter-definition PIE expected sheet

**Status:** ready for Claude's authorized headless run (C-824). The selection remains opt-in; no map/default is changed.

## Selected phase meaning

`InitialBossPhase` is a legacy/misleading field name: it identifies the phase-transition record to configure, while the fight starts in the boss's implicit base phase. `MakePhasesClusterPlan(SelectedPhaseId)` reads the selected record's `EntryHealthFraction`, `SpeedMultiplier`, `RateMultiplier`, and `AttackMultiplier` (`RPGBossPhasesClusterAdapters.cpp:236ff`). The authorized draft has only `PhaseTwo`, and the validated DD27j compile selected that exact record (`F3a/full2_raw.log`, `run_C339/dd27j_lines_verbatim.txt`). Therefore G044 uses `PhaseTwo`; this is a source-backed selection, not a new phase or production behavior change.

## Authorized source assets and safety

- Boss definition: `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft`.
- Player definition: `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3`.
- Claude authorized these saved drafts in C-821. Receipt provenance records each package path, `.uasset` SHA-256 and the DD27j evidence path/hash; it does not use the incomplete CDO snapshot.
- `Scripts/Editor/verify_g044_draft_inputs.py` is the first read-only step. It loads both assets, logs actual/expected reflected class and every one of the 22 consumed fields, hashes the packages and DD27j evidence, and refuses if class, field, required value, phase or evidence is missing. It writes/saves nothing.
- The only new Content asset is `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter`. `create_g044_encounter_definition.py` refuses if this path exists, validates dependencies and receipt before creation, verifies every selection property before its sole save, and does not modify either source draft, the map or production defaults.
- `create_g044_typed_definitions.py` remains in the repository but is excluded from this run order.

## Exact headless run order

Run each command from the project root in PowerShell. Use a distinct output directory per step; the wrapper refuses an active engine process or `ENGINE_LOCK.json`, launches `UnrealEditor-Cmd.exe` headless with `-unattended -nosound -nullrhi`, and retains command, raw log, result and before/after state. Stop on a nonzero exit or any `[G044DraftPreflight] REFUSED`.

**C-824 decision:** use `PhaseTwo` as the selected phase-transition record. The read-only preflight reports listed phase IDs; the receipt writer refuses an unlisted selected phase before creating the receipt. Claude owns the headless run and PIE. The field name is clarified in `RPGBossEncounterDefinition.h` and does not imply that the fight starts in PhaseTwo.

```powershell
$wrap = (Resolve-Path 'Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1').Path
$base = Join-Path (Get-Location) 'Docs/BossCombatReview/Execution/Claude/G044_PLAN_V2_READY'
if (Test-Path $base) { throw "Preserve existing run evidence; choose a new reviewed output root instead of overwriting: $base" }

# 1. Read-only class/field/package/evidence preflight; no writes.
$out = Join-Path $base '01_preflight'
& $wrap -Script (Resolve-Path 'Scripts/Editor/verify_g044_draft_inputs.py').Path -OutDir $out -Task 'G044-draft-preflight' -NullRhi 1
$result = Get-Content (Join-Path $out 'result.json') | ConvertFrom-Json
if ($result.exit_code -ne 0 -or $result.timed_out) { throw 'G044 draft preflight failed; stop' }

# 2. Write the Saved/G044 receipt only, based on existing drafts.
$out = Join-Path $base '02_manifest'
& $wrap -Script (Resolve-Path 'Scripts/Editor/write_g044_manifest_receipt.py').Path -OutDir $out -Task 'G044-write-manifest' -NullRhi 1
$result = Get-Content (Join-Path $out 'result.json') | ConvertFrom-Json
if ($result.exit_code -ne 0 -or $result.timed_out) { throw 'G044 manifest writer failed; stop' }

# 3. Offline receipt/draft-byte/DD27j-byte validation.
python -I Scripts/Tools/validate_encounter_manifest.py Saved/G044/encounter_manifest.json --project-root (Get-Location).Path
if ($LASTEXITCODE -ne 0) { throw 'G044 offline manifest validation failed; stop' }

# 4. Create the one new selection asset; refuse if it already exists.
$out = Join-Path $base '03_selection_create'
& $wrap -Script (Resolve-Path 'Scripts/Editor/create_g044_encounter_definition.py').Path -OutDir $out -Task 'G044-create-selection' -NullRhi 1
$result = Get-Content (Join-Path $out 'result.json') | ConvertFrom-Json
if ($result.exit_code -ne 0 -or $result.timed_out) { throw 'G044 selection creation failed; stop' }

# 5. Read-only selection and receipt validation.
$out = Join-Path $base '04_selection_validate'
& $wrap -Script (Resolve-Path 'Scripts/Editor/validate_g044_encounter_selection.py').Path -OutDir $out -Task 'G044-validate-selection' -NullRhi 1
$result = Get-Content (Join-Path $out 'result.json') | ConvertFrom-Json
if ($result.exit_code -ne 0 -or $result.timed_out) { throw 'G044 selection validation failed; stop' }
```

The Editor wrapper writes its own run receipts under the output directory. The offline validator must pass before selection creation. Preserve all logs and compare the wrapper's pre/post Content inventory: only the new selection package may be added; existing definition package hashes must remain unchanged.

## Control and selected route

1. Run once with `rpg.EncounterDefinition` empty in `L_SevarogArena`; retain baseline log and actor/component census.
2. Opt in with the exact value `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter`. Require one boss/player census, selected binding participants matching those actors, `ActivatedRegisteredSubset reason=ActivationWorld.RegisteredSubset`, a clean terminal state, and no activation HardError/fallback token.
3. After successful selected startup, run the selected H019 respawn/rebind driver and separate refusal cases. Clear the CVar afterward. No production default or map change is authorized.

| Refusal case | Expected token | Required observed state |
|---|---|---|
| Startup with no local possessed player or duplicate local players | `EncounterSelection.Census` | HardError; selected boss disabled; no legacy boss bundle; independent player setup remains. |
| Rebind candidate missing after reset | `EncounterActivation.RebindPlayerMissing` | Boss disabled; active binding released; replacement player's independent setup retained. |
| Rebind candidate misses reset-broadcast deadline | `EncounterActivation.RebindTimeout` | Boss disabled; active binding released; independent player setup retained. |
| Two rebind candidates create ambiguous census | `EncounterActivation.RebindAmbiguousPlayer` | Boss disabled; no active binding or legacy boss bundle; both players' independent setup remains. |

These tokens are source/automation expectations, not PIE evidence. Preserve failed attempts and report mismatches as FAIL or INCONCLUSIVE; do not turn refusal into PASS. Record build/content identities, raw logs, CVar, actor census and exact terminal outcomes.
