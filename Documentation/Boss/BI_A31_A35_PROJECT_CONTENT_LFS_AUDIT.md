# BI-A31..BI-A35: Project Content (`Audio/`, `Boss01/`, `Environment/`, `UI/`, `Input/`, `Levels/`) & Git LFS Audit

**Authority:** [`QUEUE_BI_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BI_AG.md) Batch 7 (`BI-A31..BI-A35`)  
**Contract Gate:** [`Scripts/Tools/test_bi_a34_project_content_lfs_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a34_project_content_lfs_contract.py)  
**Scope:** Strictly read-only disk, `.gitattributes`, & `DefaultEngine.ini` resolution audit (`0` edits, `0` commits).

---

## 1. `BI-A31..BI-A32`: `.gitattributes` LFS Coverage & Non-Character Content Integrity

- [`.gitattributes`](file:///C:/UnrealProject/OneBossFight/.gitattributes) tracks all Unreal binary & source art formats under Git LFS (`*.uasset`, `*.umap`, `*.blend`, `*.fbx`, `*.tga`, `*.png`, `*.wav`, `*.ogg`, `*.mp3`, `*.mp4`, etc.). Verified sample `git show HEAD:` pointers confirm `git-lfs.github.com/spec/v1` on `L_SevarogArena.umap` & `MX_Boss01_Phase1.uasset`.

| `Content/OneBossFight/<Folder>` | Assets (`.uasset`/`.umap`) | Combined Size (Bytes) | Zero-Byte Files | `git status` |
|---|---:|---:|---:|---|
| `Audio/` (`MX_Boss01_Phase1/2.uasset`) | `2` | `55,926,203` | `0` | Clean |
| `Boss01/` | `77` | `40,682,384` | `0` | Clean |
| `Environment/` | `26` | `2,961,214` | `0` | Clean |
| `UI/` (`Art/T_Boss01_Flask_*`, `T_Boss01_Icon_*`) | `7` | `190,471` | `0` | Clean |
| `Input/` | `14` | `43,903` | `0` | Clean |
| `Levels/` (`L_AssetProof.umap`, `L_SevarogArena.umap`) | `2` | `624,161` | `0` | Clean |
| `Poise/` | `1` | `6,757` | `0` | Clean |
| `Data/` | `32` | `275,333` | `0` | Clean |

---

## 2. `BI-A33..BI-A35`: `DefaultEngine.ini` & Cinzel UI Font Resolution

- `Content/OneBossFight/Levels/L_SevarogArena.umap` (`521,613` B): **VERIFIED** (`DefaultEngine.ini` `GameDefaultMap` & `EditorStartupMap`).
- `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_AdvancedGameMode.uasset` (`61,747` B) & `BP_AdvancedGameInstance.uasset` (`316,017` B): **VERIFIED**.
- `Content/AdvancedARPGCombat/MeleeCombatSystem/UI/Fonts/Cinzel/` (`Cinzel.uasset`, `Cinzel-Regular.uasset`, `Cinzel-Bold.uasset`, `Cinzel-Black.uasset`): **`4/4` VERIFIED** (`DefaultGame.ini` AlwaysCook).
- Enforced offline by [`test_bi_a34_project_content_lfs_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a34_project_content_lfs_contract.py).
