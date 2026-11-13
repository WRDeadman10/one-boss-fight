# BE-A01..A05: Queue BE_AG Batch 1 — Root-Motion Fix Dry-Run Audit

**Authority:** [`QUEUE_BE_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BE_AG.md), `[X-1878]` (`0` commits, `0` pushes, `0` editor/build calls)  
**Verified Dry-Run Source:** `Docs/BossCombatReview/Execution/Claude/A_C1285_GREYSTONE_ROOTFIX/fix_dryrun.log`, `fix_dryrun_status.txt`

---

## 1. Batch 1 Task Disposition (`BE-A01..BE-A05`)

| ID | Task | Status | Evidence / Missing Input |
|---|---|---|---|
| `BE-A01` | Inspect Lead `A_C1285_GREYSTONE_ROOTFIX` write + `P_C1282_GREYSTONE_RM4_*` paired displacement | **`BLOCKED`** | Only `FIX_dryrun exit=0` exists (`pre/post_content_dryrun.txt = 0 bytes`); live `--write` & `RM4` run still pending Lead execution. |
| `BE-A02` | Verify `AnimationLibrary.get_bone_pose_for_time` `root` XY probe metrics | **PARTIAL (`Dry-Run Verified`, `_RM` Outputs `BLOCKED`)** | `fix_dryrun.log:1155-1164` proves source `AN_ER_Backstep_Mixamo_V2` (`root_xy_cm=156.75`, `pelvis_xy_cm=1.36`) and pinpoints `<RetargetTranslationMode.NONE: 0>` on `RTG_ERFit_Greystone` (`test_be_a02_rootfix_dryrun_contract.py`); live `_RM`/`_Grey` outputs await Lead `--write`. |
| `BE-A03` | Verify `KI-052` `GetMainAnimBP` (`457` warnings) resolution in RM4+ logs | **`BLOCKED`** | Awaits Lead RM4+ live PIE logs. |
| `BE-A04` | Update `C1257C` checklist & `BD_A24` readiness matrix with `[C-1286]` gate verdict | **`BLOCKED`** | Awaits Lead `[C-1286]` verdict. |
| `BE-A05` | Prepare Batch 1 Owner-ready file manifest (`0` commits) | **COMPLETE** | `Documentation/Boss/BE_A01_A05_BATCH1_RM_DRYRUN_AUDIT.md`, `Scripts/Tools/test_be_a02_rootfix_dryrun_contract.py`. |

---

## 2. Dry-Run Evidence Summary (`fix_dryrun.log:1152-1164`)

- `AN_ER_Backstep_Mixamo_V2` (`SK_CombatMannequin`): `enable_root_motion=True`, `root_xy_cm=156.75`, `pelvis_xy_cm=1.36`, `length=0.5667`.
- `IK_CombatMannequin` & `IK_Fit_Greystone`: both already contain `(Root, root, root)` chain (`retarget_root=pelvis`).
- `RTG_ERFit_Greystone`: `Root` chain `fk_translation_mode=<RetargetTranslationMode.NONE: 0>` -> `RESULT=PASS dry_run=1 saves=0` (`FIX_dryrun exit=0`).
