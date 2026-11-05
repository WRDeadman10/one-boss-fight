# Python syntax inventory (S167)

The two unresolved parse failures are tracked separately as KI-170 and KI-171; neither script was executed.

Offline `ast.parse` pass over project Python scripts under `Scripts/`; files were read and parsed, not imported or executed. This is a syntax check only and does not prove Unreal Python API compatibility or runtime behavior.

## Result

- Files discovered: 519.
- Parsed successfully: 517.
- Syntax/encoding failures: 2.

| File | Line:column | Parser message | Source excerpt |
|---|---:|---|---|
| `Scripts/author_brief13_anims.py` | 141:66 | `invalid decimal literal` | `"""Base kneeling pose with sword planted on the floor (tip Z 0‑3 cm)."""` |
| `Scripts/Editor/sevarog_pack_02_montages_abilities.py` | 215:4 | `unexpected indent` | `unreal.EditorAssetLibrary.save_loaded_asset(hs, False)` |

## Disposition

Each listed syntax failure requires source review before the affected script can be executed. Parsing did not rewrite files or create bytecode. No tests, build, Unreal Editor, or runtime was run.
