# Queue V C071–C075 — encounter authoring and optional policy fields

Status: C071 partial (second encounter asset absent); C072 synthetic worked example validates; C073 cannot claim legacy MATCH from current evidence; C074 optional group rules implemented; C075 reference updated here. No Unreal Editor or asset save was performed.

## C071 — repeatability baseline for a second encounter

The current source-backed audit of `Saved/G044/encounter_manifest.json` reproduces the D5 result: 424 leaves, 214 MATCH, 0 MISMATCH, 210 NOT-COMPARABLE. This shows the comparator is deterministic on the current G044 manifest, but it does not satisfy “second encounter”: there is only one saved encounter-selection asset, `Content/OneBossFight/Data/DA_Sevarog_G044_Encounter.uasset`. `DA_Boss_AbyssalRevenant_Draft.uasset` exists as an AuthoringPreview draft, but it has no complete field manifest and no distinct encounter-selection asset binding it to a player/root. Do not duplicate the EmberWarden receipt and label it a second authored encounter. Lead/Editor authoring of the second complete definition is still required before a true second-route dry-run can be claimed.

## C072 — one-field intentional-tuning worked example

Synthetic-only validation changed `definitions.boss.stats.max_health` from the source-backed 2000 to 1999, recomputed the canonical manifest digest, and ran the manifest validator: PASS. The source audit found exactly one MISMATCH at that field. A one-row allowlist with `TEST-ONLY-NONAPPROVAL` structurally cleared the exact-path/value/reason/ID gate. This demonstrates the mechanics only; the placeholder ID is explicitly not owner approval and cannot authorize gameplay tuning. No saved manifest or asset was changed.

## C073 — seven ParrySlowMotion leaves: no legacy MATCH witness

`Scripts/Tools/legacy_defaults_g044.json` currently has no `ParrySlowMotion` rules, and the saved 424-leaf G044 receipt has no `parry_slow_motion` group. The native values at `RPGEncounterBinding.h:51–57` are documented in source as the C-903 design proposal defaults, not measured prior legacy values. Therefore there are no seven current D5 rows to audit as MATCH; adding “legacy” values from the proposal and calling them parity would invent a baseline. Keep this task open until a prior legacy witness or an explicit accepted source-default comparison policy exists.

## C074 — optional group all-or-none validation

`Scripts/Tools/validate_encounter_manifest.py` now allows the additive `parry_slow_motion` group to be absent for schema-1 compatibility. If present, it must contain exactly seven fields and all seven matching typed provenance paths; explicit null, partial values/provenance, wrong types, nonfinite numbers, and out-of-domain values fail validation. Native domains mirror `RPGParrySlowMotionConfigRules::Validate` in `RPGEncounterBinding.h`. New focused fixtures cover legacy absence, complete group, missing member, partial provenance, explicit null and invalid range. The group is optional and a no-op unless a later authored receipt opts in.

## C075 — encounter-definition field reference

The new `parry_slow_motion` group belongs on a participant definition as:

| JSON field | Typed source path | Type | Native proposed default | Runtime bounds |
|---|---|---|---:|---|
| `perfect_enabled` | `ParrySlowMotion.bPerfectEnabled` | boolean | `true` | — |
| `perfect_scale` | `ParrySlowMotion.PerfectScale` | number | `0.30` | 0.05–1.0; `<1.0` when enabled |
| `perfect_seconds` | `ParrySlowMotion.PerfectSeconds` | number | `0.35` | `(0, 5]` seconds |
| `normal_enabled` | `ParrySlowMotion.bNormalEnabled` | boolean | `false` | — |
| `normal_scale` | `ParrySlowMotion.NormalScale` | number | `0.50` | 0.05–1.0; `<1.0` when enabled |
| `normal_seconds` | `ParrySlowMotion.NormalSeconds` | number | `0.20` | `(0, 5]` seconds |
| `cooldown_seconds` | `ParrySlowMotion.CooldownSeconds` | number | `0.60` | [0, 30] seconds |

These are native proposed defaults from `Source/OneBossFight/Player/RPGEncounterBinding.h:51–57`; they are not serialized-asset evidence, a historical legacy baseline, or owner-approved tuning. A custom group must carry one provenance entry for each exact typed source path. The group is not yet present in the canonical G044 manifest; no asset was rewritten as part of this validator/doc change.
