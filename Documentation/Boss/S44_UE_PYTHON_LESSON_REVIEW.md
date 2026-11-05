# Queue S44 — UE Python lesson review

Read-only audit of today's 46 `Scripts/Editor/*.py` files plus the current C-791 proof/content scripts. The inventory scan checked for E-prefixed Unreal enum access, apparent integer coercion of enum fields, map-path `load_asset` calls, `get_path_name()` package comparisons, and save/map-save calls. No suspicious E-prefixed enum or literal map-load pattern was found. The save/call sites and path comparisons were then reviewed in the seven focused scripts below. One unsafe save order was corrected; this report does not claim any script was run in Unreal.

## Fix

- `Docs/BossCombatReview/Execution/Codex/F_AG2_AG3_COM004/create_distinct_outcome_content.py`: moved the duplicated profile's first `save_loaded_asset(profile)` from before `new_level` and the map/fixture setup assertions to immediately before `save_map`, after the profile, game-mode, map, fixture references, spawn, and navigation checks. This applies C-791 lesson 5: perform setup assertions before the first explicit save. Destinations remain refuse-if-exists; no existing asset or map was loaded as a map.

## Audit results

| Script | C-791 lessons checked | Result |
|---|---|---|
| `create_distinct_outcome_content.py` | UENUM name/member/value, package path split, GameMode `get_name`, map lookup, first-save order | Correct enum API (`RPGBossComboOutcome`, uppercase members, `.value`), package component comparison, `get_name`, no map `load_asset`; save order fixed as above |
| `make_strafe_stuck_static_blocker_sel008.py` | path/class comparisons, map handling, pre-save assertions | Correct package-path split and `get_name`; full map setup uses `new_level`, not `load_asset`; all geometry/reference/mobility/collision assertions precede `save_map` |
| `Scripts/Editor/create_g044_encounter_definition.py` | class/path handling, pre-save assertions | Uses `is_expected_class`/`ue_path`; validates dependencies, manifest, and all record fields before its sole save; not a map script |
| `Scripts/Editor/apply_g044_d5_legacy_defaults.py` | UENUM name/value, save order | Uses the corrected `RPGBossDeathMode` name; source/digest/allowlist/backup and in-memory checks precede the first save; no enum-to-int cast |
| `Scripts/Editor/update_g044_boss_health_and_manifest.py` | object path and save order | Loads only named data assets; validates receipt, source hashes, selection refs, backups, and in-memory health before first save; later checks are post-save integrity checks |
| `Scripts/Editor/pie_player_death_reset.py` | map/enum hazards | Loads an input action asset only; does not load a map or author/save assets; integer conversions are for generation/count values, not UENUMs |
| `Scripts/Editor/pie_selection_refusal.py` | map/path handling | Loads a data definition, keeps corruption on a transient object, and does not load/save a map or compare a package path to a full object path |

No UE Python interpreter, Editor, PIE, asset save, or build was run for this audit. Post-fix review verified the first explicit profile save follows the map setup assertions in source order.
