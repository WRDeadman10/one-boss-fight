# Editor script dry-run boundary audit (D90)

Date: 2026-11-03. Static review of all 340 `Scripts/Editor/*.py` modules for dry-run/what-if switches and their mutation boundaries. No script was run and no flag was changed.

## Source-level gated modes found

| Script | Dry-run control and boundary | Disposition |
|---|---|---|
| `retarget_pack_to_greystone.py:33–34` | `if DRY: ... raise SystemExit` occurs before asset loads used by the retarget operation and before rig/retargeter deletion/creation, batch duplication, rename, JSON write, or save (`:46–93`). | Source-level gate covers the listed mutation calls. Preview only lists selected AnimBlueprints, not every future mutation/output. `DRY=False` is the default; not a CLI flag. |
| `poise_data.py:35–36` | Inside the asset loop, `if DRY: continue` precedes both property writes and `save_loaded_asset` (`:49–53`). | Source-level gate covers the listed per-asset mutations. Registry/object reads still occur. `DRY=False` is the default; not a CLI flag. |
| `repoint_player_refs.py:85–95` | Both `set_editor_property` and `save_loaded_asset` are individually guarded by `if not DRY`; recursive rewriting can mutate only a temporary struct copy before those guards. | Source-level gate covers persistent object writes/saves; reads and temporary computations remain. `DRY=False` is the default; not a CLI flag. |

## Inventory-wide result and limits

The case-insensitive source scan found only those three `DRY` controls; “preview” matches elsewhere refer to animation preview APIs, and no general `--dry-run`/`what-if` CLI convention was found. The other 337 modules have no recognized dry-run gate, so they must be treated as potentially mutating when they call editor/world/filesystem APIs. In all three candidates, dry mode is a source constant that must be changed before execution, not an externally selected command argument. “Gated” here is a source-control-flow review of the enumerated paths, not an executed proof that the editor API has no indirect side effects. The broader operation and line index is `EDITOR_PYTHON_COMMAND_INDEX_D89.csv`; no mutation or runtime test was performed.
