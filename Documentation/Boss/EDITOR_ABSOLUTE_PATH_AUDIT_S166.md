# Editor script absolute-path audit (S166)

Static scan of script files under `Scripts/Editor` for former-user absolute paths (`<drive>:\Users\...`). No scripts were run or changed. The suggestions below are proposals, not applied fixes.

## Reusable path base

For scripts under `Scripts/Editor`, define `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. Pass `str(PROJECT_ROOT / Path(...))` to APIs that require strings; keep `Path` values for Python file I/O. For a sibling script, prefer `Path(__file__).resolve().with_name("name.py")`.

## Findings

- Found 28 former-user absolute-path occurrences in 20 editor scripts. `Scripts/Editor/sample_deps.py` includes one external sample-content input and a machine-specific temp output that need explicit configuration.

| File:line | Current path (first 60 chars) | Proposed repo-relative/configurable alternative |
|---|---|---|
| `Scripts/Editor/debug_atmos.py:5` | `C:\Users\winss\Documents\Unreal Projects\OneBossFight\Saved\` | `PROJECT_ROOT / r"Saved/debug.txt"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/debug_atmos.py:5` | `C:\Users\winss\Documents\Unreal Projects\OneBossFight\Saved\` | `PROJECT_ROOT / r"Saved/debug.txt"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/export_assets_text.py:5` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Saved/` | `PROJECT_ROOT / r"Saved/asset_text"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/export_greystone.py:8` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Characters/Greystone.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/export_mannequin.py:8` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/SKM_CombatMannequin.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/export_paragon_skins.py:11` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Characters"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/export_quinn.py:8` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/SKM_Quinn.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/fix_sev_montage_refs.py:6` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Script` | `Path(__file__).resolve().with_name("sevarog_pack_02_montages_abilities.py")`. |
| `Scripts/Editor/import_all_builds.py:10` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Characters/Builds/SKM_Samurai.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/import_all_builds.py:11` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Characters/Builds/SKM_IndianYoddha.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/import_all_builds.py:12` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Characters/Builds/SKM_MedievalWarrior.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/import_all_builds.py:13` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Characters/Builds/SKM_Viking.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/import_all_builds.py:14` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Characters/Builds/SKM_IndianGoddess.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/import_all_builds.py:15` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Characters/Builds/SKM_GirlWarrior.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/import_arena_meshes.py:10` | `c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Environment"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/inspect_boss_montages.py:39` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Saved/` | `PROJECT_ROOT / r"Saved/bt_exampleboss.t3d"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/sample_deps.py:8` | `C:\Users\winss\Documents\Unreal Projects\DarkRuinsMegascansS` | External dependency: take `--sample-root` or `DARK_RUINS_SAMPLE_CONTENT`; no repo-relative equivalent is evidenced. |
| `Scripts/Editor/sample_deps.py:9` | `C:\Users\winss\Documents\Unreal Projects\OneBossFight\Conten` | `PROJECT_ROOT / r"Content"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/sample_deps.py:10` | `C:\Users\winss\AppData\Local\Temp\claude\C--Users-winss-Docu` | `Path(tempfile.gettempdir()) / "onebossfight/sample_closure.json"` (or caller-supplied output). |
| `Scripts/Editor/set_view.py:8` | `C:\Users\winss\Documents\Unreal Projects\OneBossFight\Saved\` | `PROJECT_ROOT / r"Saved/view.txt"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/sevarog_pack_02b_toggle_only.py:2` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Script` | `Path(__file__).resolve().with_name("sevarog_pack_02_montages_abilities.py")`. |
| `Scripts/Editor/sevarog_pack_05_parity.py:12` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Script` | `Path(__file__).resolve().with_name("sevarog_pack_02_montages_abilities.py")`. |
| `Scripts/Editor/sevarog_pack_05b_death_style.py:6` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Script` | `Path(__file__).resolve().with_name("sevarog_pack_02_montages_abilities.py")`. |
| `Scripts/Editor/sevarog_pack_08_turn.py:7` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Script` | `Path(__file__).resolve().with_name("sevarog_pack_02_montages_abilities.py")`. |
| `Scripts/Editor/sevarog_pack_09_charge.py:7` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Script` | `Path(__file__).resolve().with_name("sevarog_pack_02_montages_abilities.py")`. |
| `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:9` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Script` | `Path(__file__).resolve().with_name("sevarog_pack_02_montages_abilities.py")`. |
| `Scripts/Editor/test_import_skm.py:4` | `C:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/Characters/Builds/SKM_Roundtrip_Test.fbx"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |
| `Scripts/Editor/verify_arena_meshes.py:31` | `c:/Users/winss/Documents/Unreal Projects/OneBossFight/Import` | `PROJECT_ROOT / r"Import/verify_output.txt"`, where `PROJECT_ROOT = Path(__file__).resolve().parents[2]`. |

## Notes

- All occurrences rooted at the former project directory `C:\Users\winss\Documents\Unreal Projects\OneBossFight` can be based on `PROJECT_ROOT`; the table gives each exact relative tail and source line.
- `sample_deps.py:8` points to a separate Dark Ruins sample project, not to a path inside this repository. The repo-relative replacement is not established; make it an explicit input and fail clearly if absent. Its `TARGET` at `:9` should be `PROJECT_ROOT / "Content"`; its machine-specific temp output at `:10` should use `tempfile.gettempdir()` or a caller-provided output path.
- `generate_project_art.py` paths under `.gemini/antigravity/brain` and fixed system installation paths such as `C:\Program Files` were not in this `Scripts/Editor` scan; this audit does not claim repository-wide path cleanup.
- Scripts using `Path(__file__)` already can derive the root without embedding the owner profile. Keep source and output paths distinct when replacing absolute paths, especially import/export scripts.

## Disposition

S166 acceptance is met as an audit/proposal: every former-user path occurrence in scope has an exact line and a repo-relative or configurable replacement. No source path was edited; no tests, Editor, build, or runtime were run.
