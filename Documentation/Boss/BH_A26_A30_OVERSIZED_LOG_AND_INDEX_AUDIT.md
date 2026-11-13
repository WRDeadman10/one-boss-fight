# BH-A26..BH-A30: Evidence Oversized-Log (`> 1 MB`) & Index Integrity Audit

**Authority:** [`QUEUE_BH_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BH_AG.md) Batch 6 (`BH-A26..BH-A30`)  
**Index Updated:** [`BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md)  
**Contract Guard:** [`Scripts/Tools/test_bh_a28_oversized_log_guard_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a28_oversized_log_guard_contract.py)

---

## 1. `BH-A26`: Oversized (`> 1 MB`) Untracked Artifacts Under `Docs/BossCombatReview/Execution/`

Full recursive disk scan across `Docs/BossCombatReview/Execution/` vs `git ls-files`:

| Bucket | Count (`> 1,048,576` B) | Commit Policy (`Owner Exclusion Guard`) |
|---|---|---|
| Untracked `suite.log` (`1.05–1.11 MB` across `Claude/B_C1280_GREYSTONE2` + `Codex/{BE_*,BF_*,C1257B_*,C1274_*,C1275A_*,C1280_*}`) | `27` | **EXCLUDE** from `git add` (`AGENTS.md` / `BD-A29` / `BH-A26` `> 1 MB` guard; commit small `status.txt` / `summary` / `readback.log` instead) |
| Untracked `abslog` | `0` | N/A |
| Untracked binary media (`.png` / `.mp4` under `Claude/`) | `13` | **EXCLUDE** from `git add` (`0` repo-committed showcase binaries) |
| Untracked `Codex/WP6Support/node_modules/` binaries/maps | `54` | **EXCLUDE** (`node_modules` dependency cache, never stage) |
| Untracked large `.log` / `.txt` / `.json` / `.csv` / `.fbx` dumps (`pre_state`, `post_state`, etc.) | `1,701` | **EXCLUDE** (`1,770` total untracked `> 1 MB` under `Execution/` after accounting for overlapping categories) |

*(Note: Historical scan of `8d096e04..5ae1b2b2` showed early `03ce5a8a` included two `suite.log`s (`B_C1274_GREYSTONE/suite.log`, `C1269_GREYSTONE_WRAPPER/suite.log`), whereas every commit from `24c1975e..5ae1b2b2` onward (`8` commits) AND all `86+` Antigravity Group A `BD`–`BH` files have `0` files `> 1 MB` and `0` binary media.)*

---

## 2. `BH-A27`..`BH-A30`: Evidence Index Update, Guard Test, Blockers & Batch 6 Manifest

- **`BH-A27` Index Update:** Appended Codex `QUEUE_BF` Batches `5–8` (`BF-X21..X40`, `[X-1888]..[X-1891]` docs-only static audits) to [`BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md) as `PROVISIONAL / STATIC AUDIT`.
- **`BH-A28` Contract Test:** [`test_bh_a28_oversized_log_guard_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a28_oversized_log_guard_contract.py) asserts `0` files `> 1 MB` and `0` binary media across `24c1975e..5ae1b2b2` AND across all Antigravity Group A files (`BD`–`BH`).
- **`BH-A29` (`BLOCKED`):** Lead UHT Shipping dump, refreshed Shipping stage, and RTX 2060 Super `60 FPS` (`p99 <= 16.67 ms`) telemetry remain **`BLOCKED`** (`[C-1286+]`).
- **`BH-A30` Batch 6 Owner-Ready Manifest (`0` commits, `0` media staged):**
  - [`Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md)
  - [`Documentation/Boss/BH_A26_A30_OVERSIZED_LOG_AND_INDEX_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A26_A30_OVERSIZED_LOG_AND_INDEX_AUDIT.md)
  - [`Scripts/Tools/test_bh_a28_oversized_log_guard_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a28_oversized_log_guard_contract.py)
