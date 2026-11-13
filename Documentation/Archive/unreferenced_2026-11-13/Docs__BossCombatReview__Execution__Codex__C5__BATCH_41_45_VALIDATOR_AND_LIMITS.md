# Queue F-C C5 tasks 41–45: evidence, unresolved gaps, and read-only validator

`weapon_parameter_coverage.json` now records four explicit unresolved gaps: pack Blueprint graph/montage timing cannot be verified offline; native typed catalog compilation needs startup; binary property/name evidence is not runtime execution evidence; and the slot index/table path are structural constants rather than per-weapon fields.

`validate_weapon_inventory.py` verifies manifest shape, unique field names, allowed classifications, all required C3 schema mappings, nonempty consumers/validator rules, and repository-contained evidence paths. It emits a JSON report with entry/mapping counts and explicit `assets_written=false` / `source_written=false`; it has no asset or source write path.

`test_validate_weapon_inventory.py` covers valid full coverage, missing mapping, invalid classification, missing evidence, and read-only behavior. The CLI reports 25 fields, 21 mapped, 4 structural/pack-only, 4 unresolved gaps, and no diagnostics. The five pure-Python tests pass 5/5. The C5 audit reopen suite also passes 8/8 after its stale source-line window was corrected. No Content assets, C++ source, Unreal Editor, PIE, or build were touched/run.
