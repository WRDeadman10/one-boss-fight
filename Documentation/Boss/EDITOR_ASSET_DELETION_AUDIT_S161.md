# Editor asset deletion audit (S161)

Static scan of maintained `Scripts/Editor` Python files for `EditorAssetLibrary.delete_asset` and `delete_directory`. No editor command was run. Of 22 `delete_asset` call sites and three directory removals, only `fix_grey_layers_2.py` checks package referencers before deletion. Existence checks and target naming do not establish that an asset has no referencers.

## Referencer-guarded deletion

- `Scripts/Editor/fix_grey_layers_2.py:19-22` queries `find_package_referencers_for_asset(TEMP, False)` and deletes only when the returned list is empty. This is the only audited call with an explicit referencer check. Its safety still depends on the query result representing all relevant package references at execution time.

## Destructive calls: treat as unsafe without manual reference review

The following calls delete an existing asset or delete all assets in a directory without querying referencers. The scripts' comments, `does_asset_exist` guards, generated-looking names, and load checks do not substitute for a reference check. These scripts are not endorsed for rerun against referenced content; manually inspect references and preserve or choose a fresh destination before execution.

| Script and lines | Target / behavior | Guard actually present |
|---|---|---|
| `boss_pose_reset.py:9-11` | `SK_Boss01_Body` failed import | Existence only; “nothing references it” is a comment assertion. |
| `build_asset_proof_map.py:145-150` | Existing `LEVEL_PATH` map | Existence only before deleting and recreating the map. |
| `cleanup_review11.py:4-11`, `cleanup_review12.py:5-12`, `cleanup_review13.py:5-12` | Every asset in `_Review11`, `_Review12`, `_Review13`, then directory | Directory existence and scratch-path scoping; no per-asset referencer query. Docstrings claim no references but do not enforce it. |
| `import_boss01.py:56-60` | Existing imported boss animation clips | Existence only; clips may be dependencies of montages or other assets. |
| `retarget_pack_to_greystone.py:43-57` | Generated IK rig and retargeter in `DEST` | Existence only; no referencer query before recreation. |
| `rpg_content_lib.py:23-28` | Any caller-supplied `recreate(path, ...)` destination | Existence only in the shared helper; callers inherit this unsafe replacement behavior. |
| `setup_m1_content.py:104-110` | Existing generated level map | Existence only before `new_level`. |
| `setup_m3_content.py:92-97`, `setup_m4_content.py:98-102` | Any caller-supplied asset destination | Existence only in each `recreate` helper. |
| `setup_m7_beam_materials.py:26-30` | Named material in generated folder | Existence only. |
| `setup_m7_roll.py:69-74` | Existing target sequence before rename | Existence only; no reference check before deleting the destination. |
| `sevarog_pack_01_proxy.py:14-17` | Existing weapon proxy | Existence only. |
| `sevarog_pack_02_montages_abilities.py:102-106,150-156,223-229` | Existing montage/duplicated asset destinations | Existence only before replacement. |
| `sevarog_pack_03_info_style_pawn.py:20-25` | Existing duplicated asset destination | Existence only. |
| `sevarog_pack_05_parity.py:27-34`, `sevarog_pack_05b_death_style.py:21-28` | Existing duplicate destinations when loadable | Successful `load_asset` only; neither helper queries referencers. |

The three `delete_directory` calls are part of the cleanup scripts above and follow their asset loops. Each cleanup script must be treated as destructive because its loop has no referencer check and its docstring is not a runtime safeguard.

## Scan boundary

This count covers maintained files under `Scripts/Editor`, not archived copies under `Docs/` or the semantics of Unreal Editor's reference collector. It is a source review, not an execution or asset-registry proof. See S162 for the separate save/overwrite collision audit.
