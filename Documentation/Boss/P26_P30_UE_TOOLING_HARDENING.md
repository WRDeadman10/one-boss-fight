# Queue P26–P30 — UE Python and authoring pipeline hardening

## P26 — shared Unreal Python value adapters

Added `Scripts/Editor/ue_editor_values.py` with path conversion (`get_path_name`, `export_text`, `to_string`, and soft-path repr fallback), reflected `UClass` ancestry comparison, UE `Array` handling, nested struct JSON conversion including `export_text` field-name recovery, finite-number refusal, and GUID word formatting. Explicit engine-module injection keeps the helper importable in offline fixtures.

## P27–P28 — consumers and mock fidelity

The four G044 editor scripts now call the common helpers for definition readback, class checks, object/soft-object paths, and GUID text: `verify_g044_draft_inputs.py`, `write_g044_manifest_receipt.py`, `create_g044_encounter_definition.py`, and `validate_g044_encounter_selection.py`. The offline fixture `Scripts/Tools/test_ue_editor_values.py` covers the observed API shapes: UE Array, SoftObjectPath whose repr is `{}` but `export_text()` contains the path, nested reflected structs, child `UClass`, and `Guid` exposed as four signed 32-bit properties. C-836 F1 found that `stable_value()` still returned the raw `SoftObjectPath('/Game/...')` export string for a nested path. It now emits `{"object_path": "/Game/..."}`, matching the current BUILD-214 live G044 receipt at `Saved/G044/encounter_manifest.json`, field `definitions.boss.bleed.proc_effect` (and `proc_sound`). F2 fixed the stale manifest-validator fixture by giving it a SHA-256-shaped `source_snapshot_sha256` and asserting absence is rejected. Full offline discovery: 122 tests pass, 1 skipped. Claude still owns the live P27 step 1+5 receipt equality check; the local source change alone does not claim that acceptance.

## P29 — C2 AnimBlueprint compile receipt (Lead-run)

The existing read-only dispatcher and validator are `Docs/BossCombatReview/Execution/Claude/C2_RUNTIME/select_and_validate.py` and `Docs/BossCombatReview/Execution/Codex/C2/validate_selected_anim_blueprint.py`. Run only after confirming the Editor is idle and there is no engine lock; use a fresh evidence directory:

```powershell
$out = Join-Path (Get-Location).Path ('Docs/BossCombatReview/Execution/Claude/B_Codex_P29_C2_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
$env:C2_RUNTIME_TARGET = '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint'
$env:C2_EDITOR_LOG_PATH = Join-Path $out 'editor_raw.log'
& 'Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1' `
  -Script (Resolve-Path 'Docs/BossCombatReview/Execution/Claude/C2_RUNTIME/select_and_validate.py').Path `
  -OutDir $out -Task 'P29_C2_AnimBlueprint_compile_receipt' -NullRhi 0 -PyCmd 0
```

Expected: `[C2_VALIDATE_BOSS]` receipt has `ok=true`, `compiled=true`, `saved=false`, selected asset path/class, and newly captured `[Compiler]` records (or an explicit empty list). The receipt/log must refer to this fresh `abslog`; do not infer a current receipt from the older C2 run.

## P30 — second non-Polearm C3 dry run (Lead-run)

Prepared `Docs/BossCombatReview/Execution/Claude/C3/p30_sword_style_update_dry.json`, using the recorded Sword asset paths and `update_existing_style` because `SwordCombatStyle` already has six table rows. It is a configuration/validator dry run; it does not create a new catalog weapon and must not be applied. The exact editor invocation is:

```powershell
$out = Join-Path (Get-Location).Path ('Docs/BossCombatReview/Execution/Claude/B_Codex_P30_SWORD_DRY_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
& 'Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1' `
  -Script (Resolve-Path 'Scripts/Editor/run_c3_sword_dry_config.py').Path `
  -OutDir $out -Task 'P30_Sword_style_update_dry_run' -NullRhi 0 -PyCmd 0
```

Expected: `[NEWWEAPON_VALIDATION]` has no errors, `[NEWWEAPON_PLAN]` contains the three existing Sword row kinds, `[NEWWEAPON_END]` says `written=[]` and `dry_run=true`, and the package snapshots match. No `--apply` argument is permitted.

## P29/P30 limits

Both are prepared for Claude's Editor run and are not accepted until the fresh logs/result records meet the expected criteria. Codex did not launch Unreal or save assets. Python offline tests and diff checks do not replace the required live Editor receipts.
