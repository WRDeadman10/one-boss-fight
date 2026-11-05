# Editor asset collision and overwrite audit (S162)

Static scan of `Scripts/Editor` found asset creation/import calls in 52 scripts (70 call sites for `create_asset`, `duplicate_asset`, `import_asset_tasks`, or `new_level`). This audit records the collision policy visible in source. It does not infer Unreal's behavior when an unguarded factory call hits an existing package. Do not run a script with an unresolved destination collision.

## Explicit import replacement

These import tasks set `replace_existing=True`; they overwrite/import over existing destination content according to Unreal's import path. Some also save explicitly; others leave `save=False` and save later. Inspect the script's precise source and import settings before use:

| Scripts | Evidence |
|---|---|
| `build_boss01_materials.py`, `import_boss01.py`, `import_audio.py` | `replace_existing` and, where used, `replace_existing_settings` (`build_boss01_materials.py:31-37`; `import_boss01.py:18-25`; `import_audio.py:16-24`). |
| `import_all_builds.py`, `import_arena_meshes.py` | Explicit replace flag (`import_all_builds.py:28-48`; `import_arena_meshes.py:35-57`). |
| `import_ui_art.py`, `import_shiva_shrine.py`, `import_corpse_statue.py`, `place_gate_frame.py` | Explicit replacement; UI/shrine/statue set `save=False` and save separately (`import_ui_art.py:11-24`; `import_shiva_shrine.py:8-20`; `import_corpse_statue.py:8-20`; `place_gate_frame.py:12-29`). |
| `review_report10.py`, `review_report11.py`, `review_report12.py`, `review_report13.py`, `review_report13c.py`, `test_death_ue.py`, `test_import_skm.py` | Import task replacement flags are true (`review_report10.py:18-25`; `review_report11.py:24-31`; `review_report12.py:30-37`; `review_report13.py:43-50`; `review_report13c.py:14-26`; `test_death_ue.py:8-22`; `test_import_skm.py:10-28`). These are scratch/probe imports; do not infer that the output is disposable without checking its path and references. |
| `make_flipbook_materials.py`, `make_remains_material.py` | Texture import replacement flags are true; scripts then create or update material assets (`make_flipbook_materials.py:18-22,34-40,88-94`; `make_remains_material.py:15-22,39-49`). |

`import_boss01.py` deletes existing animation destinations before importing; `retarget_pack_to_greystone.py` deletes the old IK rig/retargeter before recreating them. See [S161 deletion audit](EDITOR_ASSET_DELETION_AUDIT_S161.md). `import_boss01_clips_r12.py:44-59` skips existing clips and has both replace flags false. `import_boss01_clips_r14.py:29-40,58-74` reimports an existing clip in place only after `find_package_referencers_for_asset` reports none; otherwise it leaves the existing asset untouched.

## Reuse, refuse, and recreate policies

- **Load and reuse when the target exists; otherwise create:** `build_boss01_materials.py:115-128,205-216`; `dress_arena.py:90-107`; `hide_grey_builtin_weapons.py:7-12`; `make_flipbook_materials.py:30-40,85-94`; `make_remains_material.py:39-49`; `setup_input_fix.py:44-52`; `setup_m3_content.py:104-115,317-324`; `setup_m4_content.py:246-256`; `setup_m5_content.py:82-91`; `setup_m7_arena.py:35-43`. These scripts may subsequently edit and save the loaded asset in place, so “reuse” does not mean “leave its existing contents unchanged.”
- **Return unchanged or refuse if present:** `make_combat_catalog.py:18-26` returns the existing object; `make_abi_test_catalog.py:31-35` explicitly refuses an existing fixture path; `make_death_montage.py:7-18`, `make_gate_rune_material.py:7-12`, and `make_weapon_table.py:10-22` leave an existing asset untouched. `make_scratch_route_a.py:20-37` refuses existing info and reuses its scratch tree; `make_typed_abi_fixtures.py:40-52,69-74` preflights fixture destinations; `make_typed_abi_uncooked_item.py:10-16` refuses an existing target.
- **Reuse existing by code path:** `make_polish_materials.py:15-22` and `update_arena_v2.py:9-39` load an existing path instead of creating it, then edit/save it; `sevarog_pack_07_bolt_impact.py:12-15` returns the loaded existing output or duplicates only when absent. `fix_grey_layers_1.py:5-9` duplicates the temporary root-level base only when that target is missing.
- **Delete, then recreate:** `rpg_content_lib.py:23-28`, `setup_m3_content.py:92-98`, `setup_m4_content.py:98-103`, `setup_m7_beam_materials.py:26-41`, `sevarog_pack_01_proxy.py:14-18`, `sevarog_pack_02_montages_abilities.py:102-106,150-156,223-229`, `sevarog_pack_03_info_style_pawn.py:20-26`, `sevarog_pack_05_parity.py:27-46`, and `sevarog_pack_05b_death_style.py:21-48` use the destructive replacement paths recorded in S161. Existing assets are not protected by reference checks.

## In-place edits after a collision-safe lookup

Several scripts deliberately load existing assets and then modify/save them. Their collision behavior is reuse, but their content effect is an in-place edit:

- `build_boss01_materials.py:115-128,205-216` loads existing material assets and rebuilds their graphs/parameters; this is not a no-op rerun.
- `dress_arena.py:90-112`, `make_flipbook_materials.py:30-40,85-94`, `make_remains_material.py:39-49`, `setup_input_fix.py:44-52`, `setup_m3_content.py:104-115,317-324`, `setup_m4_content.py:246-256`, `setup_m5_content.py:82-91`, and `setup_m7_arena.py:35-43` load existing outputs or create when absent; later statements may update existing content.
- `make_close_montages.py:35-57` leaves existing montages unchanged unless `REBUILD` is enabled; with rebuild enabled, it edits the existing montage in place.
- `sevarog_pack_08_turn.py:13-35` and `sevarog_pack_09_charge.py:13-24` create only when absent, then later configure existing ability/style assets. Their title/docstring no-delete policy does not imply a no-edit rerun.

## Remaining operational limits

The 52 matching scripts and 70 call sites were inventoried; categories above record inspected collision branches and the caller-selected import policy. Where a generated path has no documented per-script policy, this report deliberately does not infer Unreal factory behavior: resolve the exact target before executing it. For importers with `replace_existing=True`, replacement is intentional. Import replacement can keep an asset path while changing its contents, so downstream reference continuity is not proof that dependent behavior remains correct. The `Scripts/Editor/README.md` usage boundary points users to this map and the deletion audit before reruns.

The `Scripts/Editor/README.md` safety section is the usage boundary: all these scripts can mutate content, each must be read before execution, and referenced assets must not be deleted and recreated. This audit makes the per-script collision policy and unknown cases discoverable; it does not make unsafe scripts safe.
