# Editor Python command inventory (D89)

Date: 2026-11-03. A source-text inventory of all 340 `Scripts/Editor/*.py` files is in [`EDITOR_PYTHON_COMMAND_INDEX_D89.csv`](EDITOR_PYTHON_COMMAND_INDEX_D89.csv). Each row lists parse status, action categories, matching source line numbers, and the literal `replace_existing` flag assignments when found. It supplements the purpose/name index in `Scripts/Editor/README.md`; it is not an execution order.

## Search results

| Category | Files with a match |
|---|---:|
| Asset reads (`load_asset`, asset existence/list/read APIs) | 230 |
| Property or asset-edit APIs (`set_editor_property`, saves, creates, duplicates, rename/consolidate) | 117 |
| Asset import tasks | 20 |
| Direct delete/filesystem removal APIs | 27 |
| Filesystem output patterns | 31 |
| Editor-world/PIE operations | 155 |
| Direct process launch signatures searched | 0 |

These text categories overlap and classify API-shaped source lines, not effective state changes or safe rerun behavior. The 155 world/PIE set includes mixed probes and drivers. The `process_launch` scan targeted Python `subprocess`/`Popen`, `os.system`/`startfile`, and `launch_url`; indirect helpers or native/Blueprint behavior are outside it.

## Asset replacement flags

Twenty files contain an explicit `replace_existing` spelling: 18 set it to `True` (including the reflected setter in `import_arena_meshes.py:39`), `import_boss01_clips_r12.py` sets it to `False` at lines 56–57, and `import_boss01_clips_r14.py` assigns a caller-supplied `replace` value at lines 36–37. The CSV preserves every matching line; some assignments are tuple-packed or use reflected property setters. A true flag signals overwrite/import policy, not a proof that existing references are safe. Before execution, use the detailed collision/referencer reviews S161–S162 and each script's own guards.

## Syntax and scope limits

Python `ast.parse` succeeded for 339 files; `Scripts/Editor/sevarog_pack_02_montages_abilities.py` has an `unexpected indent` at line 215, so its later source remains searchable but its control flow cannot be parsed. No scripts were imported or executed, and no Editor asset, level, file, process, or runtime state was changed. The grep-based inventory can miss computed API names, aliases, reflection, indirect helper effects, and dynamic flags; it does not replace per-script review before execution.
