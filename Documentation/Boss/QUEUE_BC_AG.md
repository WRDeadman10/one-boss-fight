# Queue BC — Antigravity Next 50 Offline Tasks (`BC-A01..BC-A50`)

**Queue Authority:** `BB-A45` continuation of the two-lane 50-task pattern (`[C-1267]`, `Documentation/Boss/QUEUE_BB.md`)  
**Lane Owner:** Antigravity (`Art / Review / Specs / Docs / Local Verified Commits`)  
**Preceding Queue:** [`Documentation/Boss/QUEUE_BB.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BB.md) (`BB-A01..A50` completed)  

## Execution Rules
1. Work in **batches of 5**, posting one `[A-###]` status message in `TEAM_MAILBOX.md` (`Scripts/MailboxPost.ps1`) per completed batch.
2. **Never wait for review:** check `[C-###]` verdicts at the start of the next batch, fix any HOTFIX first, and proceed immediately; mark tasks `BLOCKED (missing Lead capture/input)` cleanly rather than stopping.
3. **Hard Safety Gates:** `0` remote push (`git push` forbidden), `0` staged media (`.png`, `.mp4`, `.mp3`, `.wav`), `0` pack edits (`/Game/AdvancedARPGCombat/`, `/Game/ParagonGreystone/`, `/Game/ParagonSevarog/`), and `check_doc_links.py` -> `broken_links=0` before every commit/post.
4. Never commit unaccepted Codex/Lead files until `[C-###]` ACCEPTED is posted in `TEAM_MAILBOX.md`.

---

## Batch 1 (`BC-A01..BC-A05`): C-1269a Wrapper Spec & Greystone Probe Unblock

| ID | Task | Acceptance |
|---|---|---|
| `BC-A01..A02` | Read `URPGMontageWrapperLibrary::CreateRetargetWrapper` (once landed from Codex `C-1269a`) and author offline contract test verifying package allowlist (`/Game/OneBossFight/Player/Greystone/`), exact source-notify copy rule, and zero pack mutations | Doc + unittest |
| `BC-A03` | Inspect Lead-run `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json` (after `[C-1270]` `BB-A15` executes) and reconcile minimal material/texture set vs `C1259_GREYSTONE_SOURCE_INVENTORY.md` | Doc / `BLOCKED` if probe unrun |
| `BC-A04` | Local commit of accepted `BB-A45..A50` / Batch 1 deliverables (0 media, 0 push) | Commit receipt |
| `BC-A05` | Sync `BB-A09..A10` Stun/Intro/Death capture status and verify Lead capture input readiness | Doc |

## Batch 2 (`BC-A06..BC-A10`): Sevarog Full-Clip Trace Cross-Check & Contact Refinement

| ID | Task | Acceptance |
|---|---|---|
| `BC-A06..A08` | Cross-check Lead `C-1265b` full-clip trace distances (`Swing1_Medium` & `Swing2_Medium`) against `C1265C_SEVAROG_SWING1_SWING2_FRAME_CROSSCHECK.md` frame-by-frame to recommend exact contact windows & selector `MaxRangeCm` | Doc / `BLOCKED` if trace missing |
| `BC-A09` | Offline validator test asserting every recommended `S1..S5` contact window remains `Commit <= Start < End <= RecoveryEnd` within probe clip lengths | Unittest |
| `BC-A10` | Frame-cite `Stun_Start`, `Stun_Loop`, `Stun_End`, `LevelStart_Montage`, `Death_front` once `D:/FightVideo/sevarog_frames/` sheets arrive (`BLOCKED` cleanly if still uncaptured) | Doc |

## Batch 3 (`BC-A11..BC-A15`): Sevarog Signature Cards (`S6..S8`) Data Prep

| ID | Task | Acceptance |
|---|---|---|
| `BC-A11..A13` | Draft doc-only `DA_Move_Sevarog_{Ultimate,Subjugation,SoulSiphon}` field tables (timings, sockets, cooldowns, ranges) referencing `BB_A06_A08_SIGNATURE_MARKS_REFINED.md` + `BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md` | Doc |
| `BC-A14` | Author offline JSON/table schema check validating `S6..S8` draft bounds and opt-in `FRPGBossCue.Sound=nullptr` default | Unittest |
| `BC-A15` | Document `Subjugation` snare/rupture and `Soul_Siphon` channel/heal module gap matrix against shared `FRPGBossMoveCardSpec` | Doc |

## Batch 4 (`BC-A16..BC-A20`): Doc Sync & Batch 1–3 Local Commit

| ID | Task | Acceptance |
|---|---|---|
| `BC-A16..A18` | Append `DECISIONS.md` entries for `C-1269a`, `C-1270`, and any post-`C-1269` Lead verdicts | Doc |
| `BC-A19` | Sync `KNOWN_ISSUES.md` with `X06..X10` Lead verification & `C-1265b` trace findings | Doc |
| `BC-A20` | Local commit of accepted `BC-A06..A19` work (0 media, 0 unaccepted files, 0 push) | Commit receipt |

## Batch 5 (`BC-A21..BC-A25`): Greystone Clip Stitch & Scorecard Prep

| ID | Task | Acceptance |
|---|---|---|
| `BC-A21..A23` | Validate `D:/FightVideo/greystone_review/` captured frames (when Lead runs `BB-A03` list) and stitch owner clip via verified ffmpeg command on `D:` (never staged) | Receipt / `BLOCKED` if frames missing |
| `BC-A24` | Prepare pre-populated `C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md` scoring sheet linked to the `D:` clip timestamps | Doc |
| `BC-A25` | Author offline contract test verifying Greystone ER wrapper asset paths (`/Game/OneBossFight/Player/Greystone/`) and cook-root inclusion in `DefaultGame.ini` | Unittest |

## Batch 6 (`BC-A26..BC-A30`): SFX & Phase-2 Aura Pre-Wiring Checks

| ID | Task | Acceptance |
|---|---|---|
| `BC-A26..A28` | Re-verify all SFX Batch 1–9 + `BB-A11..A14` cue/dialogue asset existence on disk & update `BB_A05` blocked matrix with any newly arrived Owner reel picks | Doc + unittest |
| `BC-A29` | Draft Sevarog Phase-2 Niagara parameter & fixed-bounds authoring spec for the Owner-chosen `BB-A24` aura candidate (spec only) | Doc |
| `BC-A30` | Audit `DirectoriesToAlwaysCook` coverage for all planned Sevarog & Greystone project assets (`Saved/CookCoverage` offline cross-check) | Doc |

## Batch 7 (`BC-A31..BC-A35`): Evidence Indexing & Owner Digest Refresh

| ID | Task | Acceptance |
|---|---|---|
| `BC-A31..A33` | Extend `BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md` with all post-`C-1269` Lead/Codex evidence folders (`C1269+` builds/PIEs) | Doc |
| `BC-A34..A35` | Refresh `BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md` (decision-first, held for Lead) with Greystone/Sevarog status | Draft |

## Batch 8 (`BC-A36..BC-A40`): Repo & Test Plan Hygiene

| ID | Task | Acceptance |
|---|---|---|
| `BC-A36..A38` | Audit `Documentation/TEST_PLAN.md` and `Documentation/TASKS.md` for duplicate headers, stale open boxes, and orphaned doc links | Doc |
| `BC-A39..A40` | Run full offline `Scripts/Tools` unittest smoke + `check_doc_links.py` (`broken_links=0`) | Test receipt |

## Batch 9 (`BC-A41..BC-A45`): Accepted Commits & Next Queue Authoring

| ID | Task | Acceptance |
|---|---|---|
| `BC-A41..A44` | Stage & commit all Lead-accepted Source/Content/Docs/Evidence logs (0 media, 0 push) | Commit receipt |
| `BC-A45` | Author `Documentation/Boss/QUEUE_BD_AG.md` (next 50 offline tasks) | Posted |

## Batch 10 (`BC-A46..BC-A50`): Closeout

| ID | Task | Acceptance |
|---|---|---|
| `BC-A46..A50` | Author `QUEUE_BC_AG_CLOSEOUT.md`, sync `PROJECT_STATE.md` / `TASKS.md`, commit closeout docs cleanly, and post Batch 10 receipt | Closeout + post |
