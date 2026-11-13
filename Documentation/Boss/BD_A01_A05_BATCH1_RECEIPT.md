# QUEUE_BD_AG Batch 1 Receipt (`BD-A01`..`BD-A05`)

**Authority:** Interim Lead Assignment `[X-1872]` (`2026-11-11`), [`QUEUE_BD_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BD_AG.md)  
**Policy Compliance:** `0` git commits made (`[X-1872]` / `AGENTS.md`: Owner commits), `0` remote pushes, `0` editor/build usage, `0` media staged.

---

## 1. Batch 1 Task Status Table

| ID | Task | Status | Evidence / Missing Input |
|---|---|---|---|
| `BD-A01` | Inspect Lead `P_C1282_GREYSTONE_RM2_*` / Run 4 paired displacement (`84–98 cm` / `215–290 cm`, `<= 10%`) | **`BLOCKED`** | `A_C1285_GREYSTONE_ROOTFIX` exists on disk, but Lead Run 4 (`P_C1282_GREYSTONE_RM4_*`) & Claude verdict are still pending (Claude back `02:31` IST). |
| `BD-A02` | Author offline contract check reconciling paired RM summary metrics | **`BLOCKED`** | Depends on `BD-A01` Run 4 metrics. |
| `BD-A03` | Inspect refreshed `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json` (`28` resolved textures) | **COMPLETE** | Verified in [`BD_A03_A04_GREYSTONE_TEXTURES_RECONCILE.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BD_A03_A04_GREYSTONE_TEXTURES_RECONCILE.md) (`5ae1b2b2`). |
| `BD-A04` | Reconcile `28` resolved `unique_textures` & `Characters/Global/` keep-list vs `C1259` | **COMPLETE** | Covered by [`test_bd_a03_greystone_textures_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bd_a03_greystone_textures_contract.py) (`1/1 PASS`, `5ae1b2b2`). |
| `BD-A05` | Prepare Owner-ready Batch 1 file list / receipt (`0` commit made) | **COMPLETE** | This receipt (`Documentation/Boss/BD_A01_A05_BATCH1_RECEIPT.md`). |

---

## 2. Owner-Ready File Manifest (Stage Only When Owner Chooses to Commit)

Prior Batch 1 work (`BD-A03`, `BD-A04`, `C-1284`/`C-1285`) was already locally committed prior to `[X-1872]` in `5ae1b2b2`. New un-committed Batch 1 file:
- `Documentation/Boss/BD_A01_A05_BATCH1_RECEIPT.md` *(replaces local commit per `[X-1872]` / `AGENTS.md` Owner-commit rule)*
- *Excluded (in-flight / unaccepted by Lead):* `Scripts/Editor/retarget_*.py`, `Source/OneBossFight/*` (`X26` / `BE`), `Documentation/TASKS.md`, `Docs/BossCombatReview/Execution/*/suite.log` (`> 1 MB`).
