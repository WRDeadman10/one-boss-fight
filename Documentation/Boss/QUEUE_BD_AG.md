# Queue BD — Antigravity Next 50 Offline Tasks (`BD-A01..BD-A50`)

**Queue Authority:** `BC-A45` continuation of the two-lane 50-task pattern (`[C-1283]`, `Documentation/Boss/QUEUE_BC_AG.md`)  
**Lane Owner:** Antigravity (`Art / Review / Specs / Docs / Local Verified Commits`)  
**Preceding Queue:** [`Documentation/Boss/QUEUE_BC_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BC_AG.md) (`BC-A01..A50`)  

## Execution Rules
1. Work in **batches of 5**, posting one `[A-###]` status message in `Documentation/TEAM_MAILBOX.md` (`Scripts/MailboxPost.ps1`) per completed batch.
2. Check `[C-###]` verdicts at the start of every cycle, fix any HOTFIX first, and proceed cleanly across unblocked tasks (`BLOCKED` if Lead capture/input is still pending).
3. **Hard Safety Gates:** `0` remote pushes (`git push` forbidden), `0` staged media (`.png`, `.mp4`, `.mp3`, `.wav`), `0` oversized logs (`> 1 MB`, e.g., skip `suite.log`), `0` third-party pack edits (`/Game/AdvancedARPGCombat/`, `/Game/ParagonGreystone/`, `/Game/ParagonSevarog/`), and `check_doc_links.py` -> `broken_links=0` before every commit.
4. Keep Codex-claimed in-flight files (`TASKS.md`, unaccepted Source files under active `[X-###]` claims) unstaged until `[C-###]` ACCEPTED.

---

## Batch 1 (`BD-A01..BD-A05`): Greystone Root-Motion Gate & Fixed `BB-A15` Texture Probe

| ID | Task | Acceptance |
|---|---|---|
| `BD-A01` | Inspect Lead `P_C1282_GREYSTONE_RM2_*` paired Mannequin vs `BP_GreystoneERPlayer_C` backstep/quick-roll logs and verify `<= 10%` pairing + `84–98 cm` / `215–290 cm` (`5/5` each) | Doc / `BLOCKED` if run pending |
| `BD-A02` | Author offline contract check reconciling `P_C1282_GREYSTONE_RM2_*` summary metrics vs `C1257b` thresholds | Unittest |
| `BD-A03` | Inspect refreshed `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json` after Lead reruns fixed `probe_greystone_materials_textures.py` (`_collect_used_textures` MIC walk) | Doc / `BLOCKED` if rerun pending |
| `BD-A04` | Reconcile resolved `unique_textures` and `non_greystone_textures` against `C1259_GREYSTONE_SOURCE_INVENTORY.md` Section 6.2 (`~312 MB` local footprint) and `Characters/Global/` keep-list | Doc |
| `BD-A05` | Local commit of accepted `BC-A46..A50` + Batch 1 deliverables (`0` media, `0` push) and post Batch 1 receipt | Commit + `[A-###]` |

## Batch 2 (`BD-A06..BD-A10`): `BC-A10` `LevelStart` Tail & `X26` Live-Check Intake

| ID | Task | Acceptance |
|---|---|---|
| `BD-A06` | Frame-cite `LevelStart` tail (`Frames 41–74`, `2.733–5.000 s`) once Lead captures full 75-frame sheet under `D:/FightVideo/sevarog_frames/` | Doc / `BLOCKED` if tail pending |
| `BD-A07` | Verify Codex `X26` dry-run & `BUILD` receipt (`AdditionalPhaseIds` `TArray<FName>`, `S6` `90–150 cm`, `S7` AreaEffect, `S8` `0.200 s x 5` ticks) once Lead accepts | Doc |
| `BD-A08` | Audit Lead live PIE log for `X26` against [`C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md) (`X26-P1/P2`, `X26-S6`, `X26-S7a/b`, `X26-S8a/b`) | Doc / `BLOCKED` if PIE pending |
| `BD-A09` | Author offline regression test verifying Lead live `X26` verdict rows match `RPGBossMoveCard.h` bounds and `[FrameworkProof]` log predicates | Unittest |
| `BD-A10` | Local commit of Batch 2 docs/tests (`0` media, `0` push) and post Batch 2 receipt | Commit + `[A-###]` |

## Batch 3 (`BD-A11..BD-A15`): Sevarog `S6..S8` Live Frame Cites & Post-PIE Tuning Table

| ID | Task | Acceptance |
|---|---|---|
| `BD-A11` | Frame-cite Lead live PIE visual capture sheets for `S6` (`Ultimate_Swing_120fps`), `S7` (`Subjugation`), and `S8` (`Soul_Siphon`) telegraph readability | Doc / `BLOCKED` if capture pending |
| `BD-A12` | Audit `S6` (`0.667–0.900 s`), `S7` (`0.750 s` delay / `225 cm` radius), and `S8` (`45°` cone escape) readability & dodge fairness vs player `215–290 cm` quick roll | Doc |
| `BD-A13` | Draft post-PIE tuning adjustment table (if any hitbox, snare `0.55`, drain `8x5`, or `S1`/`S2` `+0.303 s` punish margin needs refinement) | Doc |
| `BD-A14` | Update offline `S1–S8` move-card contract suite if Lead approves any post-PIE timing/damage delta | Unittest |
| `BD-A15` | Local commit of Batch 3 deliverables (`0` media, `0` push) and post Batch 3 receipt | Commit + `[A-###]` |

## Batch 4 (`BD-A16..BD-A20`): `DECISIONS.md` / `KNOWN_ISSUES.md` Sync & Accepted Slice Commits

| ID | Task | Acceptance |
|---|---|---|
| `BD-A16` | Append `DECISIONS.md` entries for Greystone RM gate verdict, `X26` authored card acceptance, and any post-PIE tuning decisions | Doc |
| `BD-A17` | Sync `KNOWN_ISSUES.md` (close/update resolved `BB-A15` texture probe & `SetKeyDown` items cleanly once Lead verifies) | Doc |
| `BD-A18` | Stage & commit accepted Codex `X26` / `BE` Batch deliverables + Lead evidence receipts (`0` media, `0` oversized logs, `0` push) | Commit receipt |
| `BD-A19` | Verify `Config/DefaultGame.ini` cook roots match all newly authored Sevarog `S6–S8` & Greystone `/Game/OneBossFight/` assets | Unittest |
| `BD-A20` | Run offline contract smoke + `check_doc_links.py` and post Batch 4 receipt | Check + `[A-###]` |

## Batch 5 (`BD-A21..BD-A25`): Greystone Owner 8-Slot Review Clip Stitch & Scorecard

| ID | Task | Acceptance |
|---|---|---|
| `BD-A21` | Validate captured frames under `D:/FightVideo/greystone_review/` across all `8` slots (`Idle`..`Plunge`, `0` dark/corrupt frames) | Receipt / `BLOCKED` if frames missing |
| `BD-A22` | Stitch `1080p` Owner review clip on `D:/FightVideo/greystone_review/` using verified `ffmpeg` manifest (never staged in git) | Receipt on `D:` |
| `BD-A23` | Cross-link clip timestamps in [`C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md) | Doc |
| `BD-A24` | Verify `BP_GreystoneERPlayer` notify readback + root-motion + visual review readiness matrix for Owner Sign-Off | Doc |
| `BD-A25` | Local commit of Batch 5 docs (`0` media, `0` push) and post Batch 5 receipt | Commit + `[A-###]` |

## Batch 6 (`BD-A26..BD-A30`): SFX Reel Picks & Sevarog Phase-2 Aura Pre-Wiring

| ID | Task | Acceptance |
|---|---|---|
| `BD-A26` | Intake Owner audition picks for `SFX_03` / `SFX_06` Batches `1–3` & `1–9` (`BB_A05` blocked matrix unlock check) | Doc / `BLOCKED` if Owner picks pending |
| `BD-A27` | Intake Owner review pick for Sevarog `4-Move Live Clip` & `BB-A24` Phase-2 aura candidate (`Cand A/B/C`) | Doc / `BLOCKED` if pending |
| `BD-A28` | Reconcile exact verified `/Game/` sound paths (preventing `SFX_02` shorthand regressions) and prepare card-cue opt-in spec table | Doc + unittest |
| `BD-A29` | Verify `BC_A26_A30_SFX_AURA_COOK_PRECHECK.md` fixed-bounds (`[-220, 220] cm`) & `<= 120` sprite budget against Owner-chosen aura | Doc |
| `BD-A30` | Local commit of Batch 6 docs/tests (`0` media, `0` push) and post Batch 6 receipt | Commit + `[A-###]` |

## Batch 7 (`BD-A31..BD-A35`): Evidence Index & Owner Digest Refresh

| ID | Task | Acceptance |
|---|---|---|
| `BD-A31` | Update [`BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md) with `P_C1282_GREYSTONE_RM2_*`, `X26`, `LevelStart` tail, and all post-`C-1283` runs | Doc |
| `BD-A32` | Verify every `Docs/BossCombatReview/Execution/` run folder referenced in the index is either cleanly committed (small files) or noted as excluded `> 1 MB` | Unittest |
| `BD-A33` | Refresh [`BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md) decision-first (Greystone switch gate, Sevarog full `S1–S8` kit, SFX/aura picks) | Draft |
| `BD-A34` | Audit digest links & claims against committed receipts (`0` unverified runtime claims) | Doc check |
| `BD-A35` | Local commit of Batch 7 docs (`0` media, `0` push) and post Batch 7 receipt | Commit + `[A-###]` |

## Batch 8 (`BD-A36..BD-A40`): Repo & Test Plan Hygiene

| ID | Task | Acceptance |
|---|---|---|
| `BD-A36` | Audit `Documentation/TEST_PLAN.md` (`X31–X35`, `X26`, `BUILD-297+`) once active Codex claims close | Doc |
| `BD-A37` | Audit `Documentation/TASKS.md` & `PROJECT_STATE.md` for stale blockers or duplicate headings | Doc |
| `BD-A38` | Triage legacy `Scripts/Tools/test_*.py` drift from the `653`-test discovery (flagging only true regressions vs retired schema tests) | Doc |
| `BD-A39` | Verify `test_check_shipping_guards.py` passes cleanly across all Source files | Check |
| `BD-A40` | Run active offline contract suite + `check_doc_links.py` (`broken_links=0`) and post Batch 8 receipt | Test receipt |

## Batch 9 (`BD-A41..BD-A45`): Accepted Commits & Next Queue Authoring

| ID | Task | Acceptance |
|---|---|---|
| `BD-A41` | Stage & commit all remaining Lead-accepted `BE` / `X26` / Greystone / Sevarog Source, Content, Docs & small Evidence files (`0` media, `0` push) | Commit receipt |
| `BD-A42` | Verify `git status` clean of Antigravity working leftovers and verify `0` `.png`/`.mp4`/`.wav` staged across recent commits | Check |
| `BD-A43` | Audit packaging readiness checklist (`1080p / 60 FPS, p99 <= 16.67 ms` RTX 2060 Super target prep, zero test-hook leakage) | Doc |
| `BD-A44` | Sync `KNOWN_ISSUES.md` & `DECISIONS.md` final pre-closeout pass | Doc |
| `BD-A45` | Author `Documentation/Boss/QUEUE_BE_AG.md` (next 50 offline tasks in 10 batches) | Posted |

## Batch 10 (`BD-A46..BD-A50`): Closeout

| ID | Task | Acceptance |
|---|---|---|
| `BD-A46` | Audit all `BD-A01..A45` deliverables, contract tests, and commit hashes | Checklist |
| `BD-A47` | Author `Documentation/Boss/QUEUE_BD_AG_CLOSEOUT.md` summarizing completed, verified, and externally gated items | Doc |
| `BD-A48` | Sync `Documentation/PROJECT_STATE.md` & `Documentation/TASKS.md` (only if unclaimed/approved by Lead) | Doc |
| `BD-A49` | Run final offline contract suite + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BD-A50` | Local commit of Queue BD closeout docs (`0` media, `0` push) and post Batch 10 closeout receipt | Closeout + post |
