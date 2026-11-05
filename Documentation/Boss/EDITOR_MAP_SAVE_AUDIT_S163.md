# Editor map save audit (S163)

Static review of world load/create/save calls in `Scripts/Editor/*.py`. No Unreal Editor, map asset, or runtime was opened or changed for this audit. A map path in source is not proof that the asset is unreferenced; saving a world to an existing destination can replace that package.

## Finding: wrong destination can overwrite the arena map

`Scripts/Editor/sevarog_pack_04_level.py` originally declared `DST_NAME = "L_SevarogPack"` and asserted that world was open, but saved it to the existing `L_SevarogArena` package. Lead confirmed the mismatch and directed a hotfix. The script now checks both the open world's name and outermost package path against `/Game/OneBossFight/Levels/L_SevarogPack` before modifying actors, then passes that asserted package path to `save_map`. The script was not run; the `get_outermost().get_name()` behavior and resulting asset save still need Lead's Editor-side validation. The declared `SRC` remains `L_Greybox`; the duplicate/open step is external, so this source-level review cannot establish what was actually duplicated.

## Create/recreate paths

| Script and lines | Static behavior | Safety conclusion |
|---|---|---|
| `Scripts/Editor/build_asset_proof_map.py:15,146-150,172` | Creates `/Game/OneBossFight/Levels/L_AssetProof`; explicitly deletes that map first if it exists, then creates and saves a replacement. | Destructive rerun; no referencer check. Cross-reference [S161 deletion audit](EDITOR_ASSET_DELETION_AUDIT_S161.md). |
| `Scripts/Editor/setup_m1_content.py:19,104-110,137,147-148` | Builds `L_Greybox` and `L_Benchmark` under `/Game/OneBossFight/Levels`. `build_level` deletes an existing target, calls `new_level`, then saves the current level; the `new_level` result is not checked. | Destructive rerun of either existing map; no referencer check. Cross-reference S161. |

Neither path demonstrates a fresh, non-colliding destination on rerun. Choose a new unused package path or verify references before any destructive rerun.

## Explicit same-map saves

- `Scripts/Editor/arena_use_pack_boss.py:13,28` checks that the current world is `L_SevarogArena` and saves it back to that same path. This is an intentional in-place edit with a name guard, not a new destination.
- `Scripts/Editor/sevarog_pack_09_charge.py:51-58` adds a benchmark runner only when the current world name is `L_SevarogArena`, then saves to that same path. This is also an in-place edit, not a copy.
- `Scripts/Editor/setup_m3_content.py:22,333-342` loads and saves `L_Greybox`; `setup_m4_content.py:20,289-310` loads and saves `L_Greybox`; `setup_m6_content.py:10-23` loads and saves `L_Greybox`. These are explicit in-place mutations. The scripts do not create a separate map destination.
- `Scripts/Editor/setup_m7_arena.py:22,66-68,112` sequentially loads `L_SevarogArena` and `L_Greybox`, edits their arena actors, and calls `save_dirty_packages(True, True)` for each. This is a same-map content edit; the save call is package-wide and the script does not verify the loaded map identity after loading.

## Saves that depend on the current editor world

These save the current/dirty level without checking a map package path in the save call: `atmosphere.py:165` and `dress_arena.py:456` (their module docstrings direct use with `L_SevarogArena`); `finish_statue_import.py:12`, `save_gate_frame.py:7`, and `save_shrine.py:6`. The latter three have no current-map identity guard, so a wrong map open can be saved along with the intended asset work. `apply_arena_art_fix.py:3,47` declares `L_SevarogArena` but its save is `save_dirty_packages(True, True)` and no explicit level load/identity guard appears in the script. `apply_perfect_arena.py:79`, `fix_grey_default_layer.py:14`, `move_grey_abps.py:26`, `reset_component_materials.py:31`, `tune_arena_visuals.py:42`, and `update_arena_v2.py:3,83` also use package-wide dirty saves; the first five lack a map-path check in the inspected save flow. Treat these as editor-state-dependent and verify the open world and dirty package set before running.

`pie_pack_demo.py:10,112` loads the pack demo map but contains no map save call. It is not a map authoring path in this scan.

## Scope and disposition

The scan found a concrete destination mismatch in `sevarog_pack_04_level.py`, two delete-before-recreate map builders with no referencer checks, in-place map edits, and current-world/package-wide save scripts without consistent map identity guards. Therefore S163 acceptance is **not met**: source does not establish safe new destinations or protection of referenced source maps. This is static source evidence only; package references and actual save outcomes were not inspected in Unreal. Consult [S161](EDITOR_ASSET_DELETION_AUDIT_S161.md) for deletion call details and [S162](EDITOR_ASSET_OVERWRITE_AUDIT_S162.md) for asset collision behavior.
