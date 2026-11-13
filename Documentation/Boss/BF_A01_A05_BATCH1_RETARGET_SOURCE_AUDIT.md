# BF-A01..A05: Queue BF_AG Batch 1 — `_RM` Rootfix Script & Blockers Audit

**Authority:** [`QUEUE_BF_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BF_AG.md), `[X-1883]` (`0` commits, `0` pushes, `0` editor/build calls)

---

## 1. Batch 1 Task Disposition (`BF-A01..BF-A05`)

| ID | Task | Status | Evidence / Missing Input |
|---|---|---|---|
| `BF-A01` | Inspect Lead `A_C1285_GREYSTONE_ROOTFIX` `--write` + `P_C1282_GREYSTONE_RM4_*` paired displacement | **`BLOCKED`** | Only `FIX_dryrun exit=0` exists; Lead live `--write` (`Saved/ERFitRM_*.json`) & `RM4` run still pending. |
| `BF-A02` | Verify `get_bone_pose_for_time` `root` XY probe in source/rootfix pipeline | **PARTIAL (`Script Contract Verified`; Live `_RM`/`_Grey` Outputs `BLOCKED`)** | [`test_bf_a02_retarget_rootfix_source_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bf_a02_retarget_rootfix_source_contract.py) verifies [`fix_greystone_fit_root_motion.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Editor/fix_greystone_fit_root_motion.py) (`:148-198`): `GLOBALLY_SCALED`, `set_retarget_chain_settings`, `get_bone_pose_for_time` XY check, `output_root_xy_cm > 0.5 * source_root_xy_cm`, rollback, and zero pack writes. Live `Saved/ERFitRM_*.json` & `_Grey` sequences await Lead execution. |
| `BF-A03` | Audit `KI-052` `GetMainAnimBP` (`457 -> 0` or disposition) in RM4+ logs | **`BLOCKED`** | Awaits Lead RM4+ live PIE logs. |
| `BF-A04` | Update `C1257C` checklist & `BD_A24` readiness matrix post-RM4 | **`BLOCKED`** | Awaits Lead `RM4` & `[C-1286]` verdict. |
| `BF-A05` | Prepare Batch 1 Owner-ready manifest (`0` commits) | **COMPLETE** | `BF_A01_A05_BATCH1_RETARGET_SOURCE_AUDIT.md`, `test_bf_a02_retarget_rootfix_source_contract.py`. |
