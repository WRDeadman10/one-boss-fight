# BD-A41..A45 & Batch 9 (`BD-A41..BD-A45`): Packaging Readiness & Owner Commit Manifest

**Authority:** [`QUEUE_BD_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BD_AG.md), `[X-1872]` (`0` commits made, `0` pushes, `0` editor calls)

---

## 1. Batch 9 Status Matrix (`BD-A41..BD-A45`)

| ID | Task | Status | Evidence / Notes |
|---|---|---|---|
| `BD-A41` | Prepare Owner-ready commit manifest (`0` commits performed per `[X-1872]` / `AGENTS.md`) | **COMPLETE** | Group A (Antigravity `BD` docs/tests) vs Group B (deferred `X26`/`BE`/`retarget_*` awaiting `[C-1286]`) listed in Section 2. |
| `BD-A42` | Audit recent `git log -n 12` & working tree for `0` staged/committed `.png`/`.mp4`/`.mp3`/`.wav` media | **COMPLETE** | Verified `0` media matches across `8d096e04`..`5ae1b2b2`; `0` `.png`/`.mp4` in Group A manifest. |
| `BD-A43` | Packaging readiness checklist (`1080p / 60 FPS`, `p99 <= 16.67 ms` RTX 2060 Super budget) | **COMPLETE** | Section 3 below (`DirectoriesToAlwaysCook`, Shipping guards `4/4`, `WITH_EDITORONLY_DATA`, open packaged runtime checks). |
| `BD-A44` | Pre-closeout sync summary (`DECISIONS.md`/`KNOWN_ISSUES.md` closures remain gated on `[C-1286]`) | **COMPLETE** | Verified; zero premature closures written. |
| `BD-A45` | Author [`QUEUE_BE_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BE_AG.md) (`BE-A01..BE-A50`, next 50 tasks) | **COMPLETE** | `10` batches of `5`, prioritized by capture/verdict unblock order. |

---

## 2. Owner-Ready Full Commit Manifest (`0` Commits Performed)

### Group A — Ready-Now Antigravity `QUEUE_BD_AG` Deliverables
- `Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md`
- `Documentation/Boss/BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md`
- `Documentation/Boss/BD_A01_A05_BATCH1_RECEIPT.md`
- `Documentation/Boss/BD_A07_X26_DRYRUN_RECONCILE.md`
- `Documentation/Boss/BD_A12_SEVAROG_S6_S8_DODGE_FAIRNESS.md`
- `Documentation/Boss/BD_A16_A20_BATCH4_RECEIPT.md`
- `Documentation/Boss/BD_A24_GREYSTONE_READINESS_MATRIX.md`
- `Documentation/Boss/BD_A28_A29_SFX_AURA_PREWIRING_CHECK.md`
- `Documentation/Boss/BD_A36_A40_HYGIENE_AND_DRIFT_TRIAGE.md`
- `Documentation/Boss/BD_A41_A45_BATCH9_PACKAGING_MANIFEST.md`
- `Documentation/Boss/QUEUE_BE_AG.md`
- `Documentation/Boss/QUEUE_BD_AG_CLOSEOUT.md`
- `Scripts/Tools/test_bd_a07_x26_dryrun_contract.py`
- `Scripts/Tools/test_bd_a14_sevarog_s1_s8_fairness_contract.py`
- `Scripts/Tools/test_bd_a19_cook_coverage_contract.py`
- `Scripts/Tools/test_bd_a24_greystone_readiness_contract.py`
- `Scripts/Tools/test_bd_a28_sfx_aura_precheck_contract.py`
- `Scripts/Tools/test_bd_a32_evidence_index_contract.py`

### Group B — Deferred Pending Lead `[C-1286]` Acceptance *(DO NOT STAGE YET)*
- `Scripts/Editor/retarget_er_fit_candidate.py`, `Scripts/Editor/retarget_pack_to_greystone.py`, `Claude/A_C1285_GREYSTONE_ROOTFIX/`
- Codex `X26` (`[X-1864]`) + `BE` Batches `1–7` (`[X-1866..X-1873]`: `Source/OneBossFight/*`, `Scripts/Editor/author_sevarog_draft_cards.py`, `Documentation/TASKS.md`, `Documentation/Boss/C1280_X26_*`, `BE_X*`, `Run_*` excluding `suite.log` `> 1 MB`).

---

## 3. `BD-A43` Packaging Readiness Audit (`RTX 2060 Super 1080p / 60 FPS <= 16.67 ms`)

| Surface | Verified Offline Status | Open Packaging / Runtime Gate |
|---|---|---|
| **Cook Roots (`DefaultGame.ini`)** | All `5` `Player/Greystone/*.uasset`, `7` `Data/Sevarog/*.uasset`, planned `S6–S8` cards & `ParagonSevarog` anims covered (`test_bd_a19` `1/1 PASS`) | Repackage & verify cooked tree manifest (`BE` / package stage) |
| **Shipping CVar Compile Guards** | `test_check_shipping_guards.py` **`4/4 PASS`** across all `Source/` (`CVarBossProofSkipInitialWalk` & `CVarBossProofTraceGeometry` fixed) | Lead full Shipping build + smoke launch |
| **Shipping Reflection Surface** | `WITH_EDITORONLY_DATA` guards added by Codex `[X-1870]` (`509/509` Dev suite PASS) | Lead UHT Shipping reflection dump & `CheckShippingBinary` |
| **Art / VFX / Audio Budgets** | Sevarog aura spec capped at `[-220, 220] cm` fixed bounds, `<= 120` sprites; TSR default unchanged (`C-954`); `S1–S8` `"cues": []` | Lead/RTX 2060 Super packaged 1080p `p99 <= 16.67 ms` telemetry capture |
