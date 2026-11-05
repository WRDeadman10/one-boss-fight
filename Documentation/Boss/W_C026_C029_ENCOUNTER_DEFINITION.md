# Queue W-C026–W-C029 — encounter schema and tuning fixtures

## W-C026 — strict optional-group members

Added a negative fixture where the participant `parry_slow_motion` object contains an unsupported `future_field`. `validate_encounter_manifest.py` rejects it with the exact token `player parry_slow_motion must contain exactly the seven supported fields`; missing members, explicit null, partial provenance, and invalid domains remain covered. The group stays absent-compatible for schema 1.

## W-C027 — second-encounter baseline check (partial)

Re-ran the source-backed legacy comparison on `Saved/G044/encounter_manifest.json`: 424 leaves, 214 MATCH, 0 MISMATCH, 210 NOT-COMPARABLE. This is still the existing G044 encounter, not a second selection asset. V-C071 records that no second complete encounter selection asset/field manifest is available; I did not clone or mislabel the existing receipt. W-C027's second-encounter acceptance remains with Lead/Editor authoring.

## W-C028 — one-field tuning through validation and parity

Added a fully synthetic test fixture that changes only `definitions.boss.stats.max_health` from the fixture's 2000 to 1999 and recomputes the canonical manifest digest. The manifest validator passes; synthetic legacy/data parity receipts differ at one observable and the comparator reports only `parity mismatch observables`. This demonstrates validator and comparator behavior, not an approved game tuning or a live route.

## W-C029 — encounter selection record fields

`URPGBossEncounterDefinition` stores: `Schema` (int32, defaults to 1), `EncounterInstance` (FGuid), `StableManifestHash` (FString), distinct `BossSlot` and `PlayerSlot` (FName), `InitialBossPhase` (FName phase-transition record), and soft `BossDefinition`/`PlayerDefinition` references (`RPGBossEncounterDefinition.h:16–29`). `ValidateSelectionRecord` enforces schema, valid GUID, distinct nonempty slots, nonempty phase, nonnull distinct definitions, and a 64-character hex manifest hash (`RPGBossEncounterDefinition.cpp:4–25`). The seven-field `parry_slow_motion` optional group is on participant manifest definitions, not a member of this selection-record class; its typed paths/default proposals and runtime bounds remain documented in `V_C071_C075_ENCOUNTER_AUTHORING_AUDIT.md`.

Validation: manifest validator/tuning fixtures pass 20/20. No asset was authored or saved; no Unreal/build run.
