# G044 plan v2 — authorized saved drafts

**State:** ready for Claude's headless Editor run; no run performed by Codex. The owner-authorized source choice in C-821 supersedes the old CDO-snapshot prerequisite. `DA_Boss_EmberWarden_Draft` is the re-skinned pack great-sword boss and `DA_Player_Hero_Draft_V3` is the latest saved hero draft.

**C-823 addendum:** Claude's headless preflight now confirms the boss draft lists only `PhaseTwo`. Production requires a nonempty, explicit boss phase ID and requires that exact ID to be present in the saved definition; it does not select an implicit first phase. `PhaseTwo` is the only currently listed candidate, but Codex has not assigned it as the encounter's initial phase. Do not run receipt/selection creation until Claude decides whether `PhaseTwo` is the intended initial selection or requires a production change. The preflight remains read-only and now logs rather than hardcodes the selected phase. Nested reflected structs now use `export_text()` for actual values; class checks use Unreal class paths/`is_child_of`, including writer, creator and validator paths.

## Inputs and provenance

| Role | Package path | Current package SHA-256 |
|---|---|---|
| Boss | `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft` | `ba05a8aa93fec66526c59bf12f51bb824103f67860bdee16efcdd5217d6a3e2b` |
| Player | `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3` | `30cdd6b0864ca3e23ddaf500bb7e31f2cc6942c5c18cf94147388cf885f4f8b3` |

DD27j evidence is `Docs/BossCombatReview/Execution/Claude/F3a/full2_raw.log`, SHA-256 `39b2c7df37d2b332de4655211b3dfa5b5bba3373fcaa825d2cce9951cf478927`. At line 1719 it names both exact object paths; lines 1720–1722 report boss compile, hero compile and preflight as ready with output. This is compile/preflight evidence only; it does not establish saved package identity or G044 selection/PIE success. The scripts hash the current files at run time and the offline validator compares bytes to the receipt.

## Prepared pipeline

1. `Scripts/Editor/verify_g044_draft_inputs.py`: read-only first step. Loads both drafts, logs the actual class alongside the expected `URPGBossDefinition` class, logs all 22 consumed authored fields, refuses a missing/empty required field, and prints package and DD27j evidence hashes. It does not write assets or files. Its phase readback is informational pending the Lead's initial-phase decision.
2. `Scripts/Editor/write_g044_manifest_receipt.py`: records both saved draft object paths, all consumed field readbacks, each package SHA-256 and the DD27j evidence path/hash to `Saved/G044/encounter_manifest.json`; exclusive-create prevents overwriting an existing receipt.
3. `Scripts/Tools/validate_encounter_manifest.py`: offline canonical-digest, schema, draft provenance, in-project path and package/evidence byte validation.
4. `Scripts/Editor/create_g044_encounter_definition.py`: creates only the new `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter`; refuses if it exists and performs all dependency/receipt/readback assertions before its single save. Existing boss/player assets and map/defaults are not written.
5. `Scripts/Editor/validate_g044_encounter_selection.py`: read-only final selection and manifest validation.

`Scripts/Editor/create_g044_typed_definitions.py` remains available for the older snapshot workflow but is intentionally omitted from this run. The expected sheet `Documentation/Boss/G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md` contains the exact PowerShell commands using `Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1`, the offline validator invocation, stop conditions and subsequent control/selected-route evidence. That wrapper is the project's headless owner/Lead path; do not use `Scripts/run_in_editor.py` here.

## Static review and limits

The receipt writer and selection scripts use C-821's exact saved draft paths. The manifest validator compares receipt package paths to readback object paths and checks both source file hashes and the DD27j log hash. Static review also hardened malformed `asset_path` handling so a non-string produces a clean validation error instead of an attribute exception. No editor, tests, build, asset save or PIE run was performed by Codex. Claude's wrapper run must confirm actual reflected fields/classes and reject on any mismatch before receipt/selection creation. C-823's explicit phase-choice gate supersedes the earlier run-ready status above.
