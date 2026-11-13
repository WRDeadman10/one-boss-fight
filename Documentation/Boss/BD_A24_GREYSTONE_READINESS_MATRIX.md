# BD-A24 & Batch 5 (`BD-A21..BD-A25`): Greystone Switch Readiness Matrix

**Authority:** [`QUEUE_BD_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BD_AG.md), `[X-1872]` (`0` commits made, `0` pushes, `0` editor calls)

---

## 1. Batch 5 Status Matrix (`BD-A21..BD-A25`)

| ID | Task | Status | Disposition / Missing Input |
|---|---|---|---|
| `BD-A21` | Validate captured frames under `D:/FightVideo/greystone_review/` (`8` slots) | **`BLOCKED`** | `D:/FightVideo/greystone_review/` absent on disk; awaits `_RM` re-retarget & Lead visual capture. |
| `BD-A22` | Stitch `1080p` Owner review clip via `ffmpeg` on `D:` | **`BLOCKED`** | Depends on `BD-A21` captured PNGs. |
| `BD-A23` | Cross-link stitched clip timestamps in [`C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md) | **`BLOCKED`** | Depends on `BD-A22` clip timestamps. |
| `BD-A24` | Verify `BP_GreystoneERPlayer` notify readback + root-motion + review readiness matrix | **COMPLETE** | Verified Section 2 below & [`test_bd_a24_greystone_readiness_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bd_a24_greystone_readiness_contract.py). |
| `BD-A25` | Prepare Owner-ready Batch 5 file manifest (`0` commits made) | **COMPLETE** | Section 3 below. |

---

## 2. `BD-A24` Greystone Switch Technical Gate Matrix *(Fail-Closed Until Every Gate PASS)*

| Gate | Requirement | Current Verified State | Disposition |
|---|---|---|---|
| **G0 Repo Reproducibility** | `~312 MB` local pack exclusion policy (`DECISIONS.md:460-462`) | Local packs verified; `BC-A25` / `BD-A19` cook roots include `/Game/OneBossFight/Player/Greystone` (`DefaultGame.ini:49`) | **CLOSED (`[C-1261]`)** |
| **Blind Visual Score** | Fit-test candidate score | Candidate_A (`Greystone`) `47/48` (`97.9%`, `0` zeroes) | **PASS (`[C-1227]`)** |
| **Child BP & Wrapper Notify Readback** | `BP_GreystoneERPlayer` + `4` `_Fit_Greystone` montages match source notifies after save/reload | `B_C1286_GREYSTONE_RM`: recreated on `*_Fit_GreystoneRM` (`SAVED_COUNT=5`, readback `0`, `replace_write pass=True`, `[C-1289]`) | **PASS (`[C-1289]`)** |
| **Materials & Textures Probe** | Minimal Paragon dependency audit (`BB-A15` / `BD-A03..04`) | `17` slots / `15` unique materials + `28` resolved textures (`0` foreign leakage; `BD_A03_A04_GREYSTONE_TEXTURES_RECONCILE.md`) | **ACCEPTED (`[C-1286]`)** |
| **Warm-Up Key-Injection Driver** | `SetKeyDown` Enhanced Input warm-up before first dodge (`[C-1283]`) | `pie_greystone_root_motion.py` verified via AST contract `test_pie_greystone_root_motion_warmup_contract.py` (`2/2 PASS`) | **PASS (`[C-1283]`)** |
| **IK Retarget Root-Chain Output** | `Root -> Root` `GLOBALLY_SCALED` + `Saved/ERFitRM_20261111_023747.json` proof | `A_C1285` full-editor write (`FIX_editor pass=True`), backstep `180.81 cm` root / `1.57 cm` pelvis (`root_ratio=1.15346`) | **PASS (`[C-1288]`)** |
| **Root-Motion Backstep PIE Gate** | Scaled band `97–113 cm`, `<= 10%` after `/ root_ratio` (`[C-1289]` Decision 1) | `P_C1282_GREYSTONE_RM4_*`: Greystone `99.35 cm` (`5/5` in `98.03–100.20`), `99.35 / 1.15346 = 86.13` vs Mannequin `83.83` (`+2.75%`) | **PASS (`[C-1289]`)** |
| **Root-Motion Quick Roll PIE Gate** | Pack `_Grey` roll sequences re-retargeted (`BK-1`); scaled `248–334 cm` / `<= 10%` | RM4 `_Grey` roll still `0.00 cm` (`4/5` completed + trial `5` `MONTAGE_NOT_OBSERVED`); awaits Codex `BK-1` | **OPEN (Fail-Closed until `BK-1`)** |
| **`KI-052` Linked-Layer Warning** | `457` `GetMainAnimBP` `"Accessed None"` warnings in `ABP_*Layer_Grey` | Recorded in `C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md` (`[C-1284]`); unresolved | **OPEN (Fail-Closed)** |
| **Owner `8`-Slot Clip Sign-Off** | Review `D:/FightVideo/greystone_review/` clips (`Idle`..`Plunge`) + explicit Owner approval | Scheduled after `BK-1` per `[C-1289]` Decision 3 | **OPEN (Default remains Mannequin)** |

---

## 3. Owner-Ready Batch 5 File Manifest (`BD-A25`)

Antigravity deliverables ready for Owner review/commit (`0` commits made per `[X-1872]`):
- `Documentation/Boss/BD_A24_GREYSTONE_READINESS_MATRIX.md`
- `Scripts/Tools/test_bd_a24_greystone_readiness_contract.py`
