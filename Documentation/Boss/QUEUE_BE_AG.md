# Queue BE — Antigravity Next 50 Offline Tasks (`BE-A01..BE-A50`)

**Queue Authority:** `BD-A45` continuation of the two-lane 50-task pattern ([`QUEUE_BD_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BD_AG.md))  
**Lane Owner:** Antigravity (`Art / Review / Specs / Docs / Owner-Ready Manifests`; `0` commits / `0` pushes per `AGENTS.md` & `[X-1872]`)

## Execution Rules
1. Work in **batches of 5**, posting one `[A-###]` status message in `Documentation/TEAM_MAILBOX.md` per completed batch.
2. Mark any missing-capture / awaiting-Lead-verdict item `BLOCKED (<exact missing input>)` cleanly rather than idling, and execute all unblocked offline tasks.
3. **Hard Safety Gates:** `0` remote pushes, `0` autonomous git commits (`prepare Owner-ready file list/manifest`), `0` staged `.png`/`.mp4`/`.mp3`/`.wav`, `0` logs `> 1 MB` (`suite.log`), `0` third-party pack edits, `check_doc_links.py` -> `broken_links=0`.

---

## Batch 1 (`BE-A01..BE-A05`): Greystone `_RM` Root-Motion Gate Intake (`[C-1285]` Follow-Up)

| ID | Task | Acceptance |
|---|---|---|
| `BE-A01` | Inspect Lead `A_C1285_GREYSTONE_ROOTFIX` + `P_C1282_GREYSTONE_RM4_*` paired Mannequin vs `BP_GreystoneERPlayer_C` metrics (`84–98 cm` / `215–290 cm`, `<= 10%`, `5/5`) | Doc / `BLOCKED` if pending |
| `BE-A02` | Verify `AnimationLibrary.get_bone_pose_for_time` `root` XY probe metrics across `_RM` ER sequences + `_Grey` pack sequences | Doc + unittest |
| `BE-A03` | Re-verify `KI-052` `GetMainAnimBP` `"Accessed None"` resolution status in Lead RM4+ logs (`457 -> 0` or triaged disposition) | Doc |
| `BE-A04` | Update [`C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md) & [`BD_A24_GREYSTONE_READINESS_MATRIX.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BD_A24_GREYSTONE_READINESS_MATRIX.md) with Lead `[C-1286]` gate verdict | Doc |
| `BE-A05` | Prepare Batch 1 Owner-ready commit manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 2 (`BE-A06..BE-A10`): `X26` Live PIE Verification & `BC-A10` `LevelStart` Tail

| ID | Task | Acceptance |
|---|---|---|
| `BE-A06` | Audit Lead live `X26` PIE log against [`C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md) (`X26-P1/P2`, `X26-S6`, `X26-S7a/b`, `X26-S8a/b`) | Doc / `BLOCKED` if PIE pending |
| `BE-A07` | Author offline regression checking live `X26` `[FrameworkProof]` log predicates & `AdditionalPhaseIds` acceptance | Unittest |
| `BE-A08` | Frame-cite `LevelStart` tail (`Frames 41–74`, `2.733–5.000 s`) in [`BC_A10_SEVAROG_STUN_INTRO_FRAME_NOTES.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BC_A10_SEVAROG_STUN_INTRO_FRAME_NOTES.md) once Lead captures full `75`-frame sheet | Doc / `BLOCKED` if tail pending |
| `BE-A09` | Intake Codex `BE` Batch 1–10 (`BE-X01..X50`) accepted verdicts into Evidence Index (`BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md`) | Doc |
| `BE-A10` | Prepare Batch 2 Owner-ready commit manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 3 (`BE-A11..BE-A15`): Sevarog `S6..S8` Live Visuals & Post-PIE Tuning

| ID | Task | Acceptance |
|---|---|---|
| `BE-A11` | Frame-cite Lead live PIE visual capture sheets for `S6`, `S7` (`AreaEffect` ring/snare), and `S8` (`Soul_Siphon` cone) | Doc / `BLOCKED` if pending |
| `BE-A12` | Draft post-PIE tuning delta table across `S1..S8` (damage, snare scale, drain tick cadence, `+0.303 s` `S1`/`S2` punish margin) | Doc |
| `BE-A13` | Reconcile `S1`/`S2` live `90–120 cm` hit vs whiff rates after Lead saves updated cards (`BE-X26..X30`) | Doc |
| `BE-A14` | Update `S1–S8` contract assertions for any Lead-approved post-PIE tuning delta | Unittest |
| `BE-A15` | Prepare Batch 3 Owner-ready manifest + post `[A-###]` | Receipt + post |

## Batch 4 (`BE-A16..BE-A20`): `DECISIONS.md` / `KNOWN_ISSUES.md` / `TEST_PLAN.md` Sync

| ID | Task | Acceptance |
|---|---|---|
| `BE-A16` | Sync `Documentation/DECISIONS.md` with accepted `X26`, `BE`, and Greystone `_RM` verdicts | Doc / `BLOCKED` on verdicts |
| `BE-A17` | Close resolved `KNOWN_ISSUES.md` items (`BB-A15` 28-texture probe, `SetKeyDown` warm-up, `_RM` pelvis bug) after Lead verification | Doc |
| `BE-A18` | Audit `Documentation/TEST_PLAN.md` stale checkboxes (`L155–156` `X31–X35` & `BUILD-297+`) cleanly once Codex claims close | Doc |
| `BE-A19` | Verify `test_check_shipping_guards.py` + `test_bd_a19_cook_coverage_contract.py` remain green across new changes | Unittest |
| `BE-A20` | Prepare Batch 4 Owner-ready manifest + post `[A-###]` | Receipt + post |

## Batch 5 (`BE-A21..BE-A25`): Greystone 8-Slot Review Clip Stitch (`D:/FightVideo/greystone_review/`)

| ID | Task | Acceptance |
|---|---|---|
| `BE-A21` | Validate all `8` Greystone review slot PNGs (`Idle`..`Plunge`, `0` dark frames) on `D:` | Receipt / `BLOCKED` if uncaptured |
| `BE-A22` | Stitch `1080p` Owner review clip on `D:/FightVideo/greystone_review/` via verified `ffmpeg` command (`0` git media) | Receipt on `D:` |
| `BE-A23` | Populate clip timestamps in `C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md` (`0`–`2` scorecard ready) | Doc |
| `BE-A24` | Update `BD_A24_GREYSTONE_READINESS_MATRIX.md` post-stitch & Owner decision status | Doc |
| `BE-A25` | Prepare Batch 5 Owner-ready manifest + post `[A-###]` | Receipt + post |

## Batch 6 (`BE-A26..BE-A30`): Owner SFX & Phase-2 Aura Picks Intake

| ID | Task | Acceptance |
|---|---|---|
| `BE-A26` | Intake Owner audition picks (`SFX_03` / `SFX_06` Batches `1–9`) and unlock `BB_A05` matrix rows | Doc / `BLOCKED` on Owner |
| `BE-A27` | Intake Owner Sevarog `4-Move Live Clip` feedback & `BB-A24` Phase-2 aura pick (`Cand A/B/C`) | Doc / `BLOCKED` on Owner |
| `BE-A28` | Prepare Lead-executable `DA_Move_Sevarog_*` cue & `NS_Sevarog_PhaseTwoAura_*` authoring spec (`0` unpicked assets) | Doc |
| `BE-A29` | Verify `/Game/` cue paths & cook inclusion for selected SFX + aura folders in `Config/DefaultGame.ini` | Unittest |
| `BE-A30` | Prepare Batch 6 Owner-ready manifest + post `[A-###]` | Receipt + post |

## Batch 7 (`BE-A31..BE-A35`): Evidence Index & Owner Digest V2

| ID | Task | Acceptance |
|---|---|---|
| `BE-A31` | Extend `BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md` through latest `BE` / Shipping / PIE receipts | Doc |
| `BE-A32` | Run `test_bd_a32_evidence_index_contract.py` confirming `100%` folder & fail-closed alignment | Unittest |
| `BE-A33` | Refresh `BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md` with decision-first switch/boss readiness | Draft |
| `BE-A34` | Audit digest links & claims (`0` inferred runtime claims) | Doc check |
| `BE-A35` | Prepare Batch 7 Owner-ready manifest + post `[A-###]` | Receipt + post |

## Batch 8 (`BE-A36..BE-A40`): Shipping Package & RTX 2060 Super Perf Receipt Audit

| ID | Task | Acceptance |
|---|---|---|
| `BE-A36` | Audit Lead UHT Shipping reflection dump & `CheckShippingBinary` receipt (`BE-X21..X25`) | Doc / `BLOCKED` if unrun |
| `BE-A37` | Audit `Saved/StagedBuilds_Shipping` manifest & cooked-tree closure against `DefaultGame.ini` | Doc |
| `BE-A38` | Audit `1080p / 60 FPS` (`p99 <= 16.67 ms`) packaged performance receipt vs RTX 2060 Super gate (`DECISIONS.md` 2026-10-20) | Doc / `BLOCKED` if unrun |
| `BE-A39` | Run active offline contract suite + `test_check_shipping_guards.py` + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BE-A40` | Prepare Batch 8 Owner-ready manifest + post `[A-###]` | Receipt + post |

## Batch 9 (`BE-A41..BE-A45`): Consolidated Owner Commit Prep & Next Queue

| ID | Task | Acceptance |
|---|---|---|
| `BE-A41` | Build consolidated Owner-ready `git add` checklist covering all Lead-accepted `BE` / Greystone / Sevarog / Docs files (`0` commits, `0` media, `0` `suite.log`) | Manifest |
| `BE-A42` | Audit working tree & recent history confirming zero pack edits and zero staged media | Check |
| `BE-A43` | Triage any remaining legacy `Scripts/Tools` test skips/failures | Doc |
| `BE-A44` | Pre-closeout doc sync check (`TASKS.md`, `PROJECT_STATE.md`, `DECISIONS.md`, `KNOWN_ISSUES.md`) | Check |
| `BE-A45` | Author `Documentation/Boss/QUEUE_BF_AG.md` (next 50 tasks) | Posted |

## Batch 10 (`BE-A46..BE-A50`): Closeout

| ID | Task | Acceptance |
|---|---|---|
| `BE-A46` | Audit all `BE-A01..BE-A45` deliverables, tests, and manifests | Checklist |
| `BE-A47` | Author `Documentation/Boss/QUEUE_BE_AG_CLOSEOUT.md` | Doc |
| `BE-A48` | Sync `PROJECT_STATE.md` / `TASKS.md` if unclaimed & Lead-approved | Doc |
| `BE-A49` | Final offline suite + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BE-A50` | Final Owner-ready closeout manifest (`0` commits) + Batch 10 `[A-###]` receipt | Closeout + post |
