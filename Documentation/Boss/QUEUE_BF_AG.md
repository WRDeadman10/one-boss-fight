# Queue BF — Antigravity Next 50 Offline Tasks (`BF-A01..BF-A50`)

**Queue Authority:** `BE-A45` continuation of the two-lane 50-task pattern ([`QUEUE_BE_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BE_AG.md))  
**Lane Owner:** Antigravity (`Art / Review / Specs / Docs / Owner-Ready Manifests`; `0` commits / `0` pushes per `AGENTS.md` & `[X-1872]`)

## Execution Rules
1. Work in **batches of 5**, posting one `[A-###]` status message in `Documentation/TEAM_MAILBOX.md` per completed batch.
2. Check `[C-1286+]` verdicts first; execute any newly unblocked capture/review/intake item, mark still-blocked items `BLOCKED (<exact missing input>)`, and never wait idly.
3. **Hard Safety Gates:** `0` remote pushes, `0` autonomous git commits, `0` editor/build slot use, `0` staged `.png`/`.mp4`/`.mp3`/`.wav`, `0` logs `> 1 MB` (`suite.log`), `0` third-party pack edits, `check_doc_links.py` -> `broken_links=0`.

---

## Batch 1 (`BF-A01..BF-A05`): Greystone `_RM` Root-Motion Gate & `[C-1286]` Intake

| ID | Task | Acceptance |
|---|---|---|
| `BF-A01` | Inspect Lead `A_C1285_GREYSTONE_ROOTFIX` `--write` + `P_C1282_GREYSTONE_RM4_*` paired displacement (`84–98 cm` / `215–290 cm`, `<= 10%`) | Doc / `BLOCKED` if pending |
| `BF-A02` | Verify `get_bone_pose_for_time` `root` XY proof across `_RM` ER sequences + re-retargeted `_Grey` pack sequences | Doc + unittest |
| `BF-A03` | Audit `KI-052` `GetMainAnimBP` resolution (`457 -> 0` or Lead disposition) in RM4+ logs | Doc |
| `BF-A04` | Update [`C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md) & [`BD_A24_GREYSTONE_READINESS_MATRIX.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BD_A24_GREYSTONE_READINESS_MATRIX.md) post-`RM4` | Doc |
| `BF-A05` | Batch 1 Owner-ready commit manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 2 (`BF-A06..BF-A10`): `X26` Live PIE Checks & `LevelStart` Tail `41–74`

| ID | Task | Acceptance |
|---|---|---|
| `BF-A06` | Audit Lead live `X26` PIE log vs [`C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md) (`P1/P2`, `S6`, `S7a/b`, `S8a/b`) | Doc / `BLOCKED` if pending |
| `BF-A07` | Author live-verdict regression check verifying saved `S6–S8` & `S1`/`S2` `90–120 cm` logs | Unittest |
| `BF-A08` | Frame-cite `LevelStart` tail (`Frames 41–74`, `2.733–5.000 s`) in [`BC_A10_SEVAROG_STUN_INTRO_FRAME_NOTES.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BC_A10_SEVAROG_STUN_INTRO_FRAME_NOTES.md) | Doc / `BLOCKED` if tail pending |
| `BF-A09` | Intake Codex `QUEUE_BF.md` Batches 1–5 provisional/accepted receipts into Evidence Index | Doc |
| `BF-A10` | Batch 2 Owner-ready commit manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 3 (`BF-A11..BF-A15`): Sevarog `S6..S8` Live Captures & Post-PIE Tuning

| ID | Task | Acceptance |
|---|---|---|
| `BF-A11` | Frame-cite Lead live PIE visual capture sheets for `S6`, `S7` (ground ring/snare), and `S8` (drain cone) | Doc / `BLOCKED` if pending |
| `BF-A12` | Draft `S1–S8` post-PIE tuning delta table (damage, snare scale, `0.200 s x 5` drain, `S1`/`S2` punish margin) | Doc |
| `BF-A13` | Reconcile `S2` live hit/whiff reach once updated `DA_Move_Sevarog_Swing2_Medium` (`90–120 cm`) runs in PIE | Doc |
| `BF-A14` | Update `S1–S8` offline fairness contracts for Lead-approved tuning adjustments | Unittest |
| `BF-A15` | Batch 3 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 4 (`BF-A16..BF-A20`): Accepted Verdicts Doc Sync (`DECISIONS` / `KNOWN_ISSUES` / `TEST_PLAN`)

| ID | Task | Acceptance |
|---|---|---|
| `BF-A16` | Append accepted `[C-1286+]` verdicts (`X26`, `BE`, Greystone `_RM`) into `Documentation/DECISIONS.md` | Doc / `BLOCKED` on `[C-1286+]` |
| `BF-A17` | Close verified `KNOWN_ISSUES.md` items (`BB-A15` 28-texture probe, `SetKeyDown`, `_RM` pelvis bug) | Doc |
| `BF-A18` | Sync `Documentation/TEST_PLAN.md` historical `X31–X35` & `BUILD-297+` checkboxes cleanly | Doc |
| `BF-A19` | Run `test_check_shipping_guards.py` + `test_bd_a19_cook_coverage_contract.py` regression sweep | Unittest |
| `BF-A20` | Batch 4 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 5 (`BF-A21..BF-A25`): Greystone `8`-Slot Review Clip Stitch (`D:/FightVideo/greystone_review/`)

| ID | Task | Acceptance |
|---|---|---|
| `BF-A21` | Validate all `8` Greystone review slot PNGs (`Idle`..`Plunge`, `0` dark frames) on `D:` | Receipt / `BLOCKED` if missing |
| `BF-A22` | Stitch `1080p` Owner review clip via `ffmpeg` on `D:/FightVideo/greystone_review/` (`0` git media) | Receipt on `D:` |
| `BF-A23` | Populate clip timestamps in `C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md` (`0–2` scorecard ready) | Doc |
| `BF-A24` | Update `BD_A24_GREYSTONE_READINESS_MATRIX.md` post-stitch & Owner decision status | Doc |
| `BF-A25` | Batch 5 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 6 (`BF-A26..BF-A30`): Owner SFX & Phase-2 Aura Picks Unlock

| ID | Task | Acceptance |
|---|---|---|
| `BF-A26` | Intake Owner audition picks (`SFX_03` / `SFX_06` Batches `1–9`) and unlock `BB_A05` matrix | Doc / `BLOCKED` on Owner |
| `BF-A27` | Intake Owner Sevarog `4-Move Live Clip` feedback & `BB-A24` aura (`Cand A/B/C`) pick | Doc / `BLOCKED` on Owner |
| `BF-A28` | Prepare Lead-executable `DA_Move_Sevarog_*` cue & `NS_Sevarog_PhaseTwoAura_*` spec (`[-220,220] cm`, `<=120` sprites) | Doc |
| `BF-A29` | Verify selected SFX & aura `/Game/` paths + `DefaultGame.ini` cook coverage | Unittest |
| `BF-A30` | Batch 6 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 7 (`BF-A31..BF-A35`): Evidence Index & Owner Digest V3

| ID | Task | Acceptance |
|---|---|---|
| `BF-A31` | Update [`BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md) through latest `[C-1286+]` & `BF` runs | Doc |
| `BF-A32` | Run [`test_bd_a32_evidence_index_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bd_a32_evidence_index_contract.py) verifying every folder on disk | Unittest |
| `BF-A33` | Refresh [`BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md) (`V3`, Accepted vs Provisional labels) | Draft |
| `BF-A34` | Audit digest claims & links (`0` unverified runtime claims) | Doc check |
| `BF-A35` | Batch 7 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 8 (`BF-A36..BF-A40`): Shipping Binary, UHT Reflection & RTX 2060 Super 60 FPS Audit

| ID | Task | Acceptance |
|---|---|---|
| `BF-A36` | Audit Lead UHT Shipping reflection dump & `CheckShippingBinary` receipt (`BE-X21..X25`) | Doc / `BLOCKED` if unrun |
| `BF-A37` | Audit refreshed `Saved/StagedBuilds_Shipping` manifest (replacing `2026-11-06` stale stage) | Doc / `BLOCKED` if unrun |
| `BF-A38` | Audit `1080p / 60 FPS` (`p99 <= 16.67 ms`) packaged RTX 2060 Super performance receipt | Doc / `BLOCKED` if unrun |
| `BF-A39` | Run full active offline contract suite + `test_check_shipping_guards.py` + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BF-A40` | Batch 8 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 9 (`BF-A41..BF-A45`): Consolidated Owner Commit Manifest & Queue BG

| ID | Task | Acceptance |
|---|---|---|
| `BF-A41` | Build updated Group A (unblocked docs/tests) vs Group B (accepted/deferred Lead+Codex) Owner `git add` checklist | Manifest |
| `BF-A42` | Confirm `0` pack edits & `0` staged `.png`/`.mp4`/`.wav` | Check |
| `BF-A43` | Audit cross-queue contract consistency (`BD`/`BE`/`BF`) | Doc |
| `BF-A44` | Pre-closeout hygiene scan (`TEST_PLAN`, `TASKS`, `PROJECT_STATE`, `DECISIONS`, `KNOWN_ISSUES`) | Check |
| `BF-A45` | Author `Documentation/Boss/QUEUE_BG_AG.md` (next 50 offline tasks) | Posted |

## Batch 10 (`BF-A46..BF-A50`): Closeout

| ID | Task | Acceptance |
|---|---|---|
| `BF-A46` | Audit all `BF-A01..BF-A45` deliverables, contracts, & manifests | Checklist |
| `BF-A47` | Author `Documentation/Boss/QUEUE_BF_AG_CLOSEOUT.md` | Doc |
| `BF-A48` | Sync `PROJECT_STATE.md` / `TASKS.md` if unclaimed & Lead-approved | Doc |
| `BF-A49` | Final offline suite + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BF-A50` | Final Owner-ready closeout manifest (`0` commits) + Batch 10 `[A-###]` receipt | Closeout + post |
