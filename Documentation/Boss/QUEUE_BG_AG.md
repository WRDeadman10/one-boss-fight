# Queue BG — Antigravity Next 50 Offline Tasks (`BG-A01..BG-A50`)

**Queue Authority:** `BF-A45` continuation of the two-lane 50-task pattern ([`QUEUE_BF_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BF_AG.md))  
**Lane Owner:** Antigravity (`Art / Review / Specs / Docs / Owner-Ready Manifests`; `0` commits / `0` pushes per `AGENTS.md` & `[X-1872]`)

## Execution Rules
1. Work in **batches of 5**, posting one `[A-###]` status message in `Documentation/TEAM_MAILBOX.md` per completed batch.
2. Check `[C-1286+]` verdicts first; execute any newly unblocked capture/review/intake item, mark still-blocked items `BLOCKED (<exact missing input>)`, and keep working without idling.
3. **Hard Safety Gates:** `0` remote pushes, `0` autonomous git commits, `0` editor/build slot use, `0` staged `.png`/`.mp4`/`.mp3`/`.wav`, `0` logs `> 1 MB` (`suite.log`), `0` third-party pack edits, `check_doc_links.py` -> `broken_links=0`.

---

## Batch 1 (`BG-A01..BG-A05`): Greystone `_RM` Live Gate & `[C-1286+]` Intake

| ID | Task | Acceptance |
|---|---|---|
| `BG-A01` | Inspect Lead `Saved/ERFitRM_*.json` + `P_C1282_GREYSTONE_RM4_*` paired displacement (`84–98 cm` / `215–290 cm`, `<= 10%`) | Doc / `BLOCKED` if pending |
| `BG-A02` | Verify re-retargeted `GreystonePack` `_Grey` roll root XY after Lead runs `retarget_pack_to_greystone.py` | Doc + unittest |
| `BG-A03` | Audit `KI-052` `GetMainAnimBP` resolution status in RM4+ logs | Doc |
| `BG-A04` | Sync [`C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md) & [`BD_A24_GREYSTONE_READINESS_MATRIX.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BD_A24_GREYSTONE_READINESS_MATRIX.md) post-`RM4` | Doc |
| `BG-A05` | Batch 1 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 2 (`BG-A06..BG-A10`): `X26` Live PIE Checks & `LevelStart` Tail `41–74`

| ID | Task | Acceptance |
|---|---|---|
| `BG-A06` | Audit Lead live `X26` PIE log vs [`C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md) (`P1/P2`, `S6`, `S7a/b`, `S8a/b`) | Doc / `BLOCKED` if pending |
| `BG-A07` | Author live-verdict regression verifying saved `S6–S8` & `S1`/`S2` `90–120 cm` logs | Unittest |
| `BG-A08` | Frame-cite `LevelStart` tail (`Frames 41–74`, `2.733–5.000 s`) in [`BC_A10_SEVAROG_STUN_INTRO_FRAME_NOTES.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BC_A10_SEVAROG_STUN_INTRO_FRAME_NOTES.md) | Doc / `BLOCKED` if tail pending |
| `BG-A09` | Intake latest Codex `QUEUE_BF` Batches `4–10` (`BF-X16..X50`) into Evidence Index | Doc |
| `BG-A10` | Batch 2 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 3 (`BG-A11..BG-A15`): Sevarog `S6..S8` Live Captures & Post-PIE Tuning

| ID | Task | Acceptance |
|---|---|---|
| `BG-A11` | Frame-cite Lead live PIE visual capture sheets for `S6`, `S7`, and `S8` | Doc / `BLOCKED` if pending |
| `BG-A12` | Draft `S1–S8` post-PIE tuning delta table | Doc |
| `BG-A13` | Reconcile `S2` live hit/whiff reach once updated `DA_Move_Sevarog_Swing2_Medium` (`90–120 cm`) runs in PIE | Doc |
| `BG-A14` | Update `S1–S8` offline fairness contracts for Lead-approved tuning deltas | Unittest |
| `BG-A15` | Batch 3 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 4 (`BG-A16..BG-A20`): Accepted Verdicts Doc Sync (`DECISIONS` / `KNOWN_ISSUES` / `TEST_PLAN`)

| ID | Task | Acceptance |
|---|---|---|
| `BG-A16` | Append accepted `[C-1286+]` verdicts (`X26`, `BE`, `BF`, Greystone `_RM`) into `Documentation/DECISIONS.md` | Doc / `BLOCKED` on verdicts |
| `BG-A17` | Close verified `KNOWN_ISSUES.md` items (`BB-A15`, `SetKeyDown`, `_RM` pelvis bug) | Doc |
| `BG-A18` | Sync `Documentation/TEST_PLAN.md` historical `X31–X35` & `BUILD-297+` checkboxes | Doc |
| `BG-A19` | Run `test_check_shipping_guards.py` + `test_bd_a19_cook_coverage_contract.py` sweep | Unittest |
| `BG-A20` | Batch 4 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 5 (`BG-A21..BG-A25`): Greystone `8`-Slot Review Clip Stitch (`D:/FightVideo/greystone_review/`)

| ID | Task | Acceptance |
|---|---|---|
| `BG-A21` | Validate all `8` Greystone review slot PNGs (`Idle`..`Plunge`, `0` dark frames) on `D:` | Receipt / `BLOCKED` if missing |
| `BG-A22` | Stitch `1080p` Owner review clip via `ffmpeg` on `D:/FightVideo/greystone_review/` (`0` git media) | Receipt on `D:` |
| `BG-A23` | Populate clip timestamps in `C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md` (`0–2` scorecard ready) | Doc |
| `BG-A24` | Update `BD_A24_GREYSTONE_READINESS_MATRIX.md` post-stitch & Owner decision status | Doc |
| `BG-A25` | Batch 5 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 6 (`BG-A26..BG-A30`): Owner SFX & Phase-2 Aura Picks Unlock

| ID | Task | Acceptance |
|---|---|---|
| `BG-A26` | Intake Owner audition picks (`SFX_03` / `SFX_06` Batches `1–9`) and unlock `BB_A05` matrix | Doc / `BLOCKED` on Owner |
| `BG-A27` | Intake Owner Sevarog `4-Move Live Clip` feedback & `BB-A24` aura (`Cand A/B/C`) pick | Doc / `BLOCKED` on Owner |
| `BG-A28` | Prepare Lead-executable `DA_Move_Sevarog_*` cue & `NS_Sevarog_PhaseTwoAura_*` spec (`[-220,220] cm`, `<=120` sprites) | Doc |
| `BG-A29` | Verify selected SFX & aura `/Game/` paths + `DefaultGame.ini` cook coverage | Unittest |
| `BG-A30` | Batch 6 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 7 (`BG-A31..BG-A35`): Evidence Index & Owner Digest V4

| ID | Task | Acceptance |
|---|---|---|
| `BG-A31` | Update [`BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md) through latest runs | Doc |
| `BG-A32` | Run [`test_bd_a32_evidence_index_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bd_a32_evidence_index_contract.py) verifying every folder on disk | Unittest |
| `BG-A33` | Refresh [`BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md) (`V4`, Accepted vs Provisional) | Draft |
| `BG-A34` | Audit digest claims & links (`0` unverified runtime claims) | Doc check |
| `BG-A35` | Batch 7 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 8 (`BG-A36..BG-A40`): Shipping Binary, UHT Reflection & RTX 2060 Super 60 FPS Audit

| ID | Task | Acceptance |
|---|---|---|
| `BG-A36` | Audit Lead UHT Shipping reflection dump & `CheckShippingBinary` receipt | Doc / `BLOCKED` if unrun |
| `BG-A37` | Audit refreshed `Saved/StagedBuilds_Shipping` manifest | Doc / `BLOCKED` if unrun |
| `BG-A38` | Audit `1080p / 60 FPS` (`p99 <= 16.67 ms`) packaged RTX 2060 Super perf receipt | Doc / `BLOCKED` if unrun |
| `BG-A39` | Run full active offline contract suite + `test_check_shipping_guards.py` + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BG-A40` | Batch 8 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 9 (`BG-A41..BG-A45`): Consolidated Owner Commit Manifest & Queue BH

| ID | Task | Acceptance |
|---|---|---|
| `BG-A41` | Build updated Group A (unblocked docs/tests) vs Group B (accepted/deferred Lead+Codex) Owner `git add` checklist | Manifest |
| `BG-A42` | Confirm `0` pack edits & `0` staged `.png`/`.mp4`/`.wav` | Check |
| `BG-A43` | Audit cross-queue contract consistency (`BE`/`BF`/`BG`) | Doc |
| `BG-A44` | Pre-closeout hygiene scan (`TEST_PLAN`, `TASKS`, `PROJECT_STATE`, `DECISIONS`, `KNOWN_ISSUES`) | Check |
| `BG-A45` | Author `Documentation/Boss/QUEUE_BH_AG.md` (next 50 offline tasks) | Posted |

## Batch 10 (`BG-A46..BG-A50`): Closeout

| ID | Task | Acceptance |
|---|---|---|
| `BG-A46` | Audit all `BG-A01..BG-A45` deliverables, contracts, & manifests | Checklist |
| `BG-A47` | Author `Documentation/Boss/QUEUE_BG_AG_CLOSEOUT.md` | Doc |
| `BG-A48` | Sync `PROJECT_STATE.md` / `TASKS.md` if unclaimed & Lead-approved | Doc |
| `BG-A49` | Final offline suite + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BG-A50` | Final Owner-ready closeout manifest (`0` commits) + Batch 10 `[A-###]` receipt | Closeout + post |
