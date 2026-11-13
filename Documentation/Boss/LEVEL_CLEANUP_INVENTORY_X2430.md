# Level cleanup inventory and target layout (X-2429 / X-2430 / X-2431)

C (implementer), 2026-11-13. **Read-only.** No map was moved, deleted or saved by C.

**Method:**
- every project `.umap` under `Content/OneBossFight` was checked;
- text references were searched by filename across Source, Scripts, Config and Documentation;
- asset references were checked by an **exact package-path byte match** (`/Game/OneBossFight/.../<Name>` not followed by an identifier character) across every `.uasset` and `.umap` in `Content/`. The first prefix-substring pass over-counted, because `L_SevarogFrameworkProof` is a prefix of the other proof map names;
- git tracking came from `git ls-files`.

This is a static scan. Codex's Asset Registry referencer census (zero package referencers for the proof levels) agrees.

## Findings

| Group | Count | Untracked | Meaning |
|---|---|---|---|
| `Levels/L_SevarogArena` | 1 | 0 | **The playable map.** `GameDefaultMap` and `EditorStartupMap` (`DefaultEngine.ini`), 2 source files, 62 scripts, 145 docs |
| `Levels/L_AssetProof` | 1 | 0 | `build_asset_proof_map.py`, an AG content contract and a dirty AG test name it. **Keep** |
| Proof maps named by code | 5 | 4 | Only `report_owner_cleanup_referencers.py` names them: the earlier P35 owner-cleanup census, an unrun read-only list |
| Proof maps cited only in docs (evidence) | 57 | 5 | Referenced by queue reports and receipts as proof fixtures |
| Proof maps referenced **nowhere** | 20 | 0 | No asset, code, config, script or doc names them |

**No asset references any proof map** (exact-match asset references are 0 for all 82). The reverse is true: the proof maps reference `L_SevarogArena`, because they were made from it.

The 20 maps referenced nowhere:
- `L_SevarogFrameworkProofAggroSwitchR13`, `...AWR007B`, `...FatigueR15A6`, `...GuardChipR7`
- `...FAG5_Close250`, `...FAG5_Gap700`, `...FAG5_Medium375`, `...FAG5_Melee100`
- `...MOV001_R150`, `...MOV001_R300`, `...MOV001_R700`
- `...ParryRecoveryA4`, `...ParryRecoveryR9`, `...ParryRecoveryR9P`, `...ParryRecoveryR9Q`
- `...StrafeEdgeR3c`, `...TelegraphScaleR11`, `...WarpEaseR1`, `...YawConeR5`, `...YawConeR6A8`

Their companion `DA_Sevarog_*` proof profiles are separate assets and are not part of this map list.

## Recommendation

1. **Do not move `L_SevarogArena`.** Its `/Game/OneBossFight/Levels/` path is hard-coded in config, 2 source files and 62 scripts. Codex's editor rename returned false, and a move needs a task-specific C-1155 runner plus a coordinated path update. The risk is high and the value small. **Proposed target tree: treat `Levels/` as the maps folder**, keeping `L_SevarogArena` and `L_AssetProof` there, and remove the empty `Maps/` folder (it holds no files today). If the owner insists on the name `Maps/`, that is a separate locked task with a path-update batch.
2. **Proof maps, in order of safety (owner approval, editor closed):**
   - **(a)** The 20 referenced nowhere: safe deletion candidates, all git-tracked, so recoverable from history. Use Codex's 83 hash-verified rollback copies as the manifest.
   - **(b)** The 9 untracked (4 code-named, 5 docs-only): local captures that are not in git. **Deleting them is permanent.** Ask the owner explicitly, or keep them.
   - **(c)** The 57 docs-only: evidence fixtures. Keep them in place, or archive them only together with the reports that cite them. Do not delete.
   - **(d)** The 5 named by the P35 census script: keep until that census is either run or retired.
3. **How to delete (ENG):** with the editor closed, delete through the Editor's delete workflow under a C-1155 runner, so redirectors and registry state stay consistent, then reload and check that no referencer appears. Do not use a raw filesystem delete while any editor is open.

## Status

- `Content/OneBossFight/Levels/NewFolder` (X-2431) **does not exist on disk**. It was probably only a Content Browser virtual folder, so nothing needs removing.
- Owner decisions needed: approve (a); decide on (b); confirm keeping `Levels/` as the maps folder.
