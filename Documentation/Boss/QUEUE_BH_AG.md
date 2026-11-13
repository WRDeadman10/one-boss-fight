# Queue BH — Antigravity Residual 50 Offline Tasks (`BH-A01..BH-A50`)

**Queue Authority:** Owner-Directed Interim Lead Assignment `[X-1889]` (`2026-11-11`, following [`QUEUE_BG_AG_CLOSEOUT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BG_AG_CLOSEOUT.md))  
**Lane Owner:** Antigravity (`Art / Media / Audio / Asset Integrity / Docs / Owner-Ready Manifests`)  
**Zero-Overlap Scope Rule (`[X-1889]`):** Does NOT duplicate Codex [`QUEUE_BF.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BF.md) C++/validator/suite engineering; carries all Lead/Owner-only gates explicitly as `BLOCKED (<missing input>)`; `0` autonomous git commits, `0` pushes, `0` editor/build/runtime/asset operations, `0` staged media, `broken_links=0`.

---

## Batch 1 (`BH-A01..BH-A05`): `D:/FightVideo/` Media Archive & Antigravity JSON Integrity

| ID | Task | Acceptance |
|---|---|---|
| `BH-A01` | Audit `D:/FightVideo/SFX_audition/` audio/manifest files against `SFX_03_AUDITION_MANIFEST.md` & `SFX_06_BATCH3_AUDITION_MANIFEST.md` (existence + non-zero bytes) | Audit table |
| `BH-A02` | Verify `D:/FightVideo/sevarog_live/Sevarog_4Moves_Live_Review.mp4` & `D:/FightVideo/sevarog_frames/_sheets/*.png` non-zero sizes (`S1..S8`, `Stun_*`, `Death_front`, partial `LevelStart`) | Audit table |
| `BH-A03` | Offline Python contract validating `D:/FightVideo/` clip/sheet presence & `0` repo git tracking leakage | Unittest |
| `BH-A04` | Inspect `Docs/BossCombatReview/Execution/Antigravity/` JSON manifests (`MoveCards/`, `Ledger/`) read-only for valid JSON & provenance alignment | Receipt |
| `BH-A05` | Prepare Batch 1 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 2 (`BH-A06..BH-A10`): Sevarog Signature Sheet (`S3`/`S4`/`S7`/`S8` & `Swing3`/`Speedburst`) Visual Anchor Notes

| ID | Task | Acceptance |
|---|---|---|
| `BH-A06` | Inspect `Subjugation_sheet.png` (`S7`) & `Soul_Siphon_sheet.png` (`S8`, `15 Hz`) read-only to document visual stamp/aperture anchor sites (`weapon_r` ground stamp, left-hand drain cone posture) | Doc |
| `BH-A07` | Inspect `Swing3_Slow_sheet.png` (`S3`) & `Speedburst_sheet.png` (`S4`, `15 Hz`) read-only for swing-trail socket span (`weapon_r` -> `root_weapon_end_r`) & camera clearance | Doc |
| `BH-A08` | Offline contract test verifying `BH-A06`/`A07` cited socket/clip identities match `author_sevarog_draft_cards.py` | Unittest |
| `BH-A09` | Carry `LevelStart` tail (`Frames 41–74`) & `D:/FightVideo/greystone_review/` captures as `BLOCKED` (awaiting Lead engine slot) | `BLOCKED` |
| `BH-A10` | Prepare Batch 2 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 3 (`BH-A11..BH-A15`): SFX Batch `1–9` Asset Byte-Size & Option `A/B/C` Mapping Check

| ID | Task | Acceptance |
|---|---|---|
| `BH-A11` | Verify every `/Game/` `SoundCue` & `DialogueWave` cited in `BB_A11_A13`, `BB_A14`, & `SFX_05..SFX_12` resolves to non-zero `.uasset` size on disk | Receipt |
| `BH-A12` | Cross-check `BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md` vs `SFX_03`/`SFX_06` confirming `1:1` option A/B/C cue lookup readiness | Doc |
| `BH-A13` | Offline unittest verifying non-zero SFX/voice `.uasset` bytes on disk & zero `SFX_02` shorthand regressions | Unittest |
| `BH-A14` | Carry Owner audition picks & `BB-A24` aura pick as `BLOCKED` (awaiting Owner reply) | `BLOCKED` |
| `BH-A15` | Prepare Batch 3 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 4 (`BH-A16..BH-A20`): Paragon Material/Texture On-Disk Closure & Authored Greystone SHA-256 Check

| ID | Task | Acceptance |
|---|---|---|
| `BH-A16` | Verify all `15` Greystone unique materials + `26` `Characters/Global/` textures (`BD-A03..04`) + `39` `Heroes/Greystone/Textures/` files exist physically (`> 0` bytes, `0` git-tracked) | Receipt |
| `BH-A17` | Compare current `Content/OneBossFight/Player/Greystone/*.uasset` (`5` authored files) SHA-256 against `Claude/B_C1280_GREYSTONE2/evidence_sha256.txt` | Receipt |
| `BH-A18` | Offline contract test asserting bit-exact SHA-256 parity on the `5` authored Greystone project assets (`0` silent drift) | Unittest |
| `BH-A19` | Carry Lead `_RM` re-retarget (`ERFitRM_*.json`), `RM4`, `KI-052`, & live `X26` PIE as `BLOCKED` (awaiting Lead `[C-1286+]`) | `BLOCKED` |
| `BH-A20` | Prepare Batch 4 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 5 (`BH-A21..BH-A25`): Niagara VFX Disk Footprint & `DefaultEngine.ini` / `DefaultGame.ini` Graphics Audit

| ID | Task | Acceptance |
|---|---|---|
| `BH-A21` | Inventory `Content/OneBossFight/VFX/*.uasset` & cross-check `BB_A24` Sevarog Phase-2 aura spec (`[-220,220] cm`, `<=120` sprites) | Doc |
| `BH-A22` | Audit `Config/DefaultEngine.ini` & `Config/DefaultGame.ini` ensuring TSR default preserved (`C-954`) and zero debug/test CVars forced on | Doc |
| `BH-A23` | Offline contract test asserting TSR default & cook roots unchanged in `Config/*.ini` | Unittest |
| `BH-A24` | Carry `NS_Sevarog_PhaseTwoAura_*` live authoring as `BLOCKED` (awaiting Owner pick & Lead slot) | `BLOCKED` |
| `BH-A25` | Prepare Batch 5 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 6 (`BH-A26..BH-A30`): Evidence Oversized-Log (`> 1 MB`) & Index Integrity Audit

| ID | Task | Acceptance |
|---|---|---|
| `BH-A26` | Scan `Docs/BossCombatReview/Execution/` for all files `> 1 MB` (`suite.log`, `abslog`) and publish an Owner commit exclusion guard list | Doc |
| `BH-A27` | Update [`BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md) with any newly landed Codex `QUEUE_BF` Batches `5–10` runs (`PROVISIONAL`) | Doc |
| `BH-A28` | Offline contract asserting recent commits `8d096e04..5ae1b2b2` & Group A manifest hold `0` files `> 1 MB` or media | Unittest |
| `BH-A29` | Carry Lead UHT Shipping dump, refreshed Shipping stage, & RTX 2060 Super `60 FPS` telemetry as `BLOCKED` | `BLOCKED` |
| `BH-A30` | Prepare Batch 6 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 7 (`BH-A31..BH-A35`): Lead/Owner Unblock Sequencing Brief & Owner Digest `V5`

| ID | Task | Acceptance |
|---|---|---|
| `BH-A31` | Draft single-page chronological Lead + Owner unblock execution brief (`RM4` -> `_Grey` retarget -> `8`-slot clip -> `X26` live PIE -> Owner picks -> Shipping stage) | Doc |
| `BH-A32` | Refresh [`BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md) (`V5`) with concise 1-minute decision summary (`0` unverified claims) | Draft |
| `BH-A33` | Re-run [`test_bd_a32_evidence_index_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bd_a32_evidence_index_contract.py) + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BH-A34` | Carry `DECISIONS.md` / `KNOWN_ISSUES.md` / `TEST_PLAN.md` final verdict updates as `BLOCKED` (`[C-1286+]`) | `BLOCKED` |
| `BH-A35` | Prepare Batch 7 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 8 (`BH-A36..BH-A40`): `Content/OneBossFight/` Inventory & Active Offline Verification Sweep

| ID | Task | Acceptance |
|---|---|---|
| `BH-A36` | Inventory all project `.uasset` folders under `Content/OneBossFight/` (`Data`, `Player`, `VFX`, `Audio`, `Poise`, `UI`) vs `.gitignore` rules | Doc |
| `BH-A37` | Cross-link audit across `Documentation/Boss/B*_A*.md` confirming `0` orphaned Queue `BC..BH` docs | Doc |
| `BH-A38` | Re-run `test_check_shipping_guards.py` across latest Source tree (`4/4 PASS` expected) | Test receipt |
| `BH-A39` | Run full active offline contract suite + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BH-A40` | Prepare Batch 8 Owner-ready manifest (`0` commits) + post `[A-###]` | Receipt + post |

## Batch 9 (`BH-A41..BH-A45`): Consolidated Owner Commit Prep & Zero-Overlap Check

| ID | Task | Acceptance |
|---|---|---|
| `BH-A41` | Build consolidated Group A (Antigravity `BD`–`BH`) vs Group B (deferred Lead+Codex) Owner `git add` checklist (`0` commits) | Manifest |
| `BH-A42` | Verify `0` third-party pack edits & `0` staged `.png`/`.mp4`/`.wav`/`.mp3` | Check |
| `BH-A43` | Audit zero task overlap between `QUEUE_BH_AG.md` & `QUEUE_BF.md` | Check |
| `BH-A44` | Carry `PROJECT_STATE.md` / `TASKS.md` post-verdict sync as `BLOCKED` (`[C-1286+]`) | `BLOCKED` |
| `BH-A45` | Hold next queue creation unless Lead/Owner explicitly authorizes (no unapproved duplicate queue) + post Batch 9 receipt | Receipt + post |

## Batch 10 (`BH-A46..BH-A50`): Closeout

| ID | Task | Acceptance |
|---|---|---|
| `BH-A46` | Audit all `BH-A01..BH-A45` deliverables, SHA checks, unit tests, & `BLOCKED` tags | Checklist |
| `BH-A47` | Author `Documentation/Boss/QUEUE_BH_AG_CLOSEOUT.md` | Doc |
| `BH-A48` | Confirm `0` commits / `0` pushes / `0` editor or asset operations throughout Queue `BH` | Check |
| `BH-A49` | Final active offline contract suite + `check_doc_links.py` (`broken_links=0`) | Test receipt |
| `BH-A50` | Post Batch 10 closeout `[A-###]` receipt cleanly | Closeout + post |
