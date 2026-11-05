# I003 — typed encounter-definition authoring spec

The Editor creator `Scripts/Editor/create_g044_typed_definitions.py` reads `Saved/G044/typed_definition_specs.py`. That file is an Editor-owned input generated after `export_encounter_definition_sources.py` and reviewed against the reference pack assets. Codex has not run either Editor script and no definition assets were created by this task.

The module exports two dictionaries, `BOSS_SPEC` and `PLAYER_SPEC`. Each has:

- `source_snapshot_sha256`: the lowercase SHA-256 of the retained Editor CDO snapshot used as one source, not a claim of runtime state.
- `field_sources`: exactly one entry for every nested leaf value except fixed `Schema` and the self-provenancing `Fields` array; each entry has a concrete source `path` and `line`.
- `properties`: exactly the 22 public definition fields in `RPGEncounterBinding.h`, with explicit values. No native constructor defaults are copied silently.

Values use JSON-like scalars and lists. Unreal-specific values use one tagged object:

```python
{"$soft_object": "/Game/Package/Asset.Asset"}
{"$soft_class": "/Game/Package/BP_Class.BP_Class_C"}
{"$enum": {"type": "RpgSomeEnum", "value": "MemberName"}}
{"$struct": {"type": "RpgPhaseConfig", "fields": {"phase_id": "PhaseOne"}}}
```

Nested structs and arrays must explicitly provide the full values established by the reflected source readback; every nested leaf has a matching `field_sources` path/line citation. The typed `Fields` array must include nonempty `field_path`, `type`, `source_path`, lowercase SHA-256 `source_sha256`, `source_site`, `origin`, `precedence`, `destination`, `first_read`, and `witness` for each entry. Boss `Phases` must explicitly contain `PhaseOne`; the player phase record and all other values must come from its reviewed source spec.

The creator resolves every soft reference and checks both target paths before creating either package. It creates only the two new package paths, reads every top-level property back, then saves both; it never overwrites or edits the pack Blueprints, proof profile, map, or G044 selection. If any required source value is unknown, the spec must not be filled with a C++ default or a guessed Greystone identity.
