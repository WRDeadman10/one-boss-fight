# S37 — Safely author a new encounter definition

This guide covers the opt-in data route. The current default remains the legacy route; authoring a definition does not select it or authorize retiring the fallback.

## Before editing content

1. Start from an approved boss and player source, with stable object paths and package provenance. Do not invent field values to fill an incomplete export.
2. Capture the source/default snapshot and retain its hash. The saved-draft manifest must name the exact definition package, typed values, encounter GUID, phase IDs, and source provenance.
3. Treat legacy defaults and MoveCard-local timings as separate sources. The D5 G044 audit compares typed definition leaves with source-cited native defaults; it does not supply missing MoveCard specs or prove live CDO values.
4. Preserve player leaves as `NOT-COMPARABLE` when the selected TargetOnly route does not configure them onto the player. The current D5 census is 214 MATCH, 0 MISMATCH, and 210 player NOT-COMPARABLE out of 424 leaves; do not present the last group as matching.

## Preflight-to-selection sequence

Use the existing G044 procedure as the template:

1. Run the read-only draft preflight and stop on any refusal or identity mismatch.
2. Write the manifest receipt to a new `Saved/G044` run folder. Never overwrite an existing receipt.
3. Run the offline manifest validator; require package, provenance, and hash validation to pass before asset creation.
4. Create the selection asset only at a new destination; validate its object path and manifest hash afterward.
5. Compare pre/post Content inventories and hashes. Expected change is only the newly created selection package. Preserve the runner command, raw log, result, receipt, and before/after inventory.

The exact project wrapper commands and current G044 field contract are in [`G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md`](G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md). Use a unique output directory for each step. Do not save a transient corruption fixture or alter existing source assets as part of validation.

## Phase, parity, and approval constraints

- C-824 selects `PhaseTwo` as the G044 phase-transition record; the field does not mean the fight starts in phase two.
- Preserve source defaults unless a specific field has source-backed evidence and the relevant owner approval. The S26 allowlist contract requires exact field, value, reason, and owner approval ID.
- Run selected and legacy controls in separate fresh processes with identical driver, seed, settings, inputs, and build/content identities. Preserve both arms and compare valid v2 receipts with source-log hash verification.
- A green manifest comparison or parity pair does not prove Shipping behavior, packaged first-caller behavior, performance, save compatibility, or owner play-test acceptance.
- Keep the production default unchanged and the legacy route available until the owner-listed A7 gates are closed.

Sources: `Documentation/Boss/D5_G044_LEGACY_DEFAULT_AUDIT.md`, `D5_G044_LEGACY_DEFAULTS_EXPECTED.md`, `G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md`, `P15_A7_PARITY_SUMMARY_DRAFT.md`, `Scripts/Tools/compare_manifest_to_legacy_defaults.py`, and C-824/C-852/C-855/C-873/C-876.
