# Queue X X-C006–X-C009: content-writer audit

Static source review only. The inventory generator was run; no Editor Python asset writer, Unreal, package, or asset operation was executed. Full source-marker inventory: `X_C006_ASSET_WRITER_INVENTORY.md`.

## X-C006 — inventory

`python Scripts/Tools/inventory_editor_asset_writers.py --output Documentation/Boss/X_C006_ASSET_WRITER_INVENTORY.md` scanned 361 Python files under `Scripts/Editor`: 30 classified `creates`, 69 `modifies`, 42 `map_setup`, and 220 `read-only`. The separate first-save audit reports 141 non-read-only heuristic candidates, 80 with a literal save call, 61 with no literal save call, and 34 with at least one assertion/guard marker before the first literal save. These are tool classifications, not a manually confirmed count of actual asset mutations; dynamic helpers/wrappers and map-only probes can cause false positives/negatives.

## X-C007 — path-anchor review

The generated inventory reports source paths and markers, not destination allowlisting. The literal scan identified candidate non-project-path mutations; the following are direct source examples:

| File and lines | Source operation | Disposition |
|---|---|---|
| `Scripts/Editor/air_jump_tuning.py:9-15` | Loads and saves `BP_CombatPlayerCharacter` under `/Game/AdvancedARPGCombat/...`. | Edits the third-party pack in place; outside `/Game/OneBossFight`. |
| `Scripts/Editor/boss_poise_armor.py:10-19` | Loads and saves `BP_ExampleGreatSwordBoss` under `/Game/AdvancedARPGCombat/...`. | Edits third-party pack in place; outside `/Game/OneBossFight`. |
| `Scripts/Editor/copy_sockets_to_greystone.py:8-15` | Writes the destination skeleton under `/Game/ParagonGreystone/...`. | Outside project namespace; legacy asset change. |
| `Scripts/Editor/setup_m7_beam_materials.py:12,28-41` | Deletes/recreates/saves materials under `/Game/BeamPack/Materials`. | Direct third-party namespace mutation. |

These scripts may have historical authorization or dependency reasons not represented in the current task. The source conflicts with V-A036's blanket path-lockdown principle unless an explicit exception is recorded. No changes are proposed/applied in this audit.

## X-C008 — overwrite/delete review

- `Scripts/Editor/rpg_content_lib.py:23-28` documents `recreate()` as replacing an existing asset and calls `delete_asset(path)` before creating its replacement. Its path/metadata arguments are dynamic, and there is no referencer check in this helper.
- `Scripts/Editor/sevarog_pack_02_montages_abilities.py:103-106,151-153,225-228` checks whether output assets exist, deletes those paths, and then creates/duplicates replacements. Existence checks make this repeatable but do not show that referenced assets are safe to remove.
- `Scripts/Editor/import_boss01.py:58-59` deletes an existing clip before reimport to avoid a frame-rate conflict.
- `Scripts/Editor/setup_m7_beam_materials.py:28-30` deletes existing pack materials before replacement.

These are source-level hazards under the repository rule to preserve referenced assets. A call's explicit existence check is not evidence of referencer clearance or owner approval. Treat these as review/authorization candidates; none were executed.

## X-C009 — compare safety report with actual checks

`V_A036_CONTENT_SCRIPT_SAFETY.md:14-25` describes dry-run default, namespace confinement, reference/property validation, and no-delete policy as broad writer standards. Its test, `Scripts/Tools/test_content_script_safety.py:14-17,25-87`, names only two scripts. It checks several Tier 1 text markers and checks `dry_run` plus owner-approval text for the recoil script; it does not establish all four controls for both files, validate every writer/save site, prove namespace safety for all destinations, or verify referencers. The updated tests now strengthen the Tier 1 writer's dry-run and per-save precondition behavior, but do not retroactively provide global enforcement.

## Limits and follow-up

The 36-file no-project-root marker list from the quick scan contains probes and map operators as well as potential writers, so it must not be treated as 36 confirmed unsafe writes. The table above limits findings to direct source evidence. Next useful work is to classify active versus historical scripts, add scoped exceptions for approved pack edits, and add path/overwrite guard tests only where a concrete live writer is still used. Never mass-edit or execute the candidates during this audit.
