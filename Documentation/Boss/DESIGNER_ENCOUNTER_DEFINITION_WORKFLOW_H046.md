# Designer workflow — typed encounter selection (Queue I I046; refreshes H046)

**Current status (2026-11-04):** opt-in development path only. C-809 approved Step B's broadcast-triggered respawn rebind after BUILD-211 measured the legacy order. The implementation is authored but still needs Claude's build/automation and selected-mode PIE proof. Do not select a production default, edit the arena map, or treat synthetic receipt examples as evidence.

## Prerequisites

1. Use the Lead-approved encounter contract and selection/lifecycle identity: spawn records a pending replacement; the measured reset broadcast triggers old-lease release, exact census, same-selection compilation and reactivation at the broadcast generation. If no reset broadcast arrives within 5 seconds, the selected route raises `EncounterActivation.RebindTimeout`. Source implementation is not runtime proof.
2. Author distinct typed `URPGBossDefinition` assets for boss and player, each with a valid schema/ID, required field manifest, skeleton and animation references. The boss record must contain the chosen initial phase.
3. Create a canonical manifest receipt from approved asset data; verify exact boss/player paths, phase and SHA-256. Do not invent a manifest hash.
4. Confirm every referenced package is included in the target cook and loads in the target binary. A folder cook rule or Editor load is not runtime/cook evidence.

## Safe G044 preparation path

`Scripts/Editor/create_g044_encounter_definition.py` is the current prepared example. It refuses if `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter` already exists. Before its single save call it checks both typed dependencies, schema, IDs, field manifests, skeleton/animation resolution, selected phase, canonical manifest paths/hash, unique GUID, slots and all output readbacks. It creates only that one new encounter selection asset; it does not overwrite, create the dependency definitions, edit a map, or make the asset a default. Claude owns the Editor run. If a prerequisite or assertion fails, stop and correct the prerequisite through its asset owner; do not bypass the refusal. The exact ordered commands, C-791 Python lessons, and current CDO/spec blocker are maintained in `J041_J045_SELECTED_ROUTE_OPERATIONS.md`; the read-only post-create validator is `Scripts/Editor/validate_g044_encounter_selection.py`.

## Selection and refusal

For development builds, use the nonshipping opt-in command only after Claude confirms the asset and runtime prerequisites: `rpg.EncounterDefinition /Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter`. Empty selection preserves the legacy startup path. A selected-path startup or rebind failure is a HardError with an on-screen refusal and no legacy boss fallback; an unsafe cleanup retains its binding/lease for diagnosis. Current Shipping has no approved selector, and product default selection remains owner-gated.

## Review evidence

Record exact package/object paths, typed class/readback, definition IDs, selected phase, manifest receipt/hash, catalog epoch, target binary/content hash, participant actor IDs and generation/reset count, cook evidence, activation outcome/refusal, component census, clean terminal marker and paired legacy/data identity. A passing native test, Editor asset load, or example JSON alone does not prove PIE, package inclusion, Shipping readiness or parity. Expected live run sheet: `G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md`; parity schema and commands: `ENCOUNTER_PARITY_RECEIPTS_H006_H010.md`.
