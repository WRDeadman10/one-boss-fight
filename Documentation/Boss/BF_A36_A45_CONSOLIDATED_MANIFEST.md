# BF-A36..A45: Queue BF_AG Batches 8–9 — Shipping/Stage Check & Consolidated Manifest

**Authority:** [`QUEUE_BF_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BF_AG.md), `[X-1883]` (`0` commits, `0` pushes, `0` editor/build calls)

---

## 1. Batch 8 (`BF-A36..BF-A40`) Disposition
- `BF-A36`: **`BLOCKED`** — Lead UHT Shipping reflection dump & `CheckShippingBinary` receipt pending.
- `BF-A37`: **`BLOCKED` (Refresh Needed)** — `Saved/StagedBuilds_Shipping/Windows` remains `2026-11-06 12:06:17` stale stage; refreshed Shipping stage pending Lead run.
- `BF-A38`: **`BLOCKED`** — `1080p / 60 FPS` (`p99 <= 16.67 ms`) packaged RTX 2060 Super telemetry pending Lead run.
- `BF-A39..40`: **COMPLETE** — Full active offline contract suite + `test_check_shipping_guards.py` (`4/4`) + `check_doc_links.py` (`broken_links=0`) PASS; Batch 8 Owner-ready manifest complete.

---

## 2. Batch 9 (`BF-A41..BF-A45`) Disposition & Cross-Queue Audit
- `BF-A41`: **COMPLETE** — Consolidated Owner `git add` checklist (`Group A` Ready Now vs `Group B` Deferred Awaiting `[C-1286+]`, never staging `suite.log > 1 MB` or media):
  - **`Group A` Additions (`QUEUE_BF_AG`):** `BF_A01_A05_BATCH1_RETARGET_SOURCE_AUDIT.md`, `BF_A06_A10_BATCH2_RECEIPT.md`, `BF_A11_A30_DISPOSITIONS_AND_RECHECKS.md`, `BF_A36_A45_CONSOLIDATED_MANIFEST.md`, `QUEUE_BG_AG.md`, `QUEUE_BF_AG_CLOSEOUT.md`, `Scripts/Tools/test_bf_a02_retarget_rootfix_source_contract.py`, `Scripts/Tools/test_bf_a43_cross_queue_contract.py`, plus `BE_A41_A45_CONSOLIDATED_MANIFEST.md` Group A files (`BB_A26_A30` + `BB_A31_A35` updated to `V3`).
  - **`Group B` (Deferred Awaiting Lead `[C-1286+]`):** Lead `retarget_*.py`, `fix_greystone_fit_root_motion.py`, `A_C1285_GREYSTONE_ROOTFIX/`, and Codex `X26` / `BE_X*` / `BF_X*` (`Run_*/` excluding `suite.log > 1 MB`).
- `BF-A42`: **COMPLETE** — `0` pack edits, `0` autonomous commits since `5ae1b2b2`, `0` staged `.png`/`.mp4`/`.wav`.
- `BF-A43`: **COMPLETE** — Cross-queue consistency verified by [`test_bf_a43_cross_queue_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bf_a43_cross_queue_contract.py).
- `BF-A44`: **COMPLETE** — Pre-closeout doc hygiene (`0` broken links).
- `BF-A45`: **COMPLETE** — Authored [`QUEUE_BG_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BG_AG.md) (`BG-A01..BG-A50`).
