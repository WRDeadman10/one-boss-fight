# Queue AL — live Tier 2 and full-fight video (50 tasks)

Run five tasks per batch; send one X receipt per batch, then continue without waiting for Claude's review. Check mailbox each cycle and hotfix rejected work first. Claude owns UE build/PIE/native tests and the engine lock; Codex owns test-first Source, offline tools, and documentation. Label every Source edit `PRODUCTION CHANGE`. Never commit or push. Evidence-dependent rows say `WAITING ON <evidence>` rather than claim success.

| ID | File(s) | Task and acceptance |
|---|---|---|
| AL-C01 | `Source/OneBossFight/Boss/RPGSevarogDirector.*`, `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.*` | Map dormant director hooks, live pack-boss attach path, health and parry signals; write source-backed gap map. |
| AL-C02 | `Source/OneBossFight/Tests/` | Add native tests for Tier 2 off-by-default, <=60% phase threshold, one-shot aura and parry-only recoil before production Source. |
| AL-C03 | `Source/OneBossFight/Boss/` | PRODUCTION CHANGE: implement live pack-boss Tier 2 component or safe director reuse with default aura/recoil references; source test-first. |
| AL-C04 | `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp`, `Source/OneBossFight/Boss/` | PRODUCTION CHANGE: attach only to live pack boss and wire successful player parry, with rpg.Art.Tier2 gate. |
| AL-C05 | `Documentation/Boss/AL_C01_C05_TIER2_SOURCE.md`, `Documentation/TEST_PLAN.md`, `Documentation/KNOWN_ISSUES.md` | Document exact Source contract, unbuilt status, Lead build/native/PIE gates; one five-task receipt. |
| AL-C06 | `Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/pie_full_fight.py` | Inventory FRAME/ACTION/COUNTER/BOSS_DEAD log grammar and 15-fps frame naming; save fixture lines. |
| AL-C07 | `Scripts/Tools/test_make_fight_video.py` | Write failing offline tests for real game-time frame durations, missing frames/markers and subtitle escaping. |
| AL-C08 | `Scripts/Tools/make_fight_video.py` | Implement strict log/frame parser and ffmpeg concat list with game-time durations, including final frame. |
| AL-C09 | `Scripts/Tools/make_fight_video.py` | Emit ASS action subtitles and a reproducible ffmpeg command; no render by default. |
| AL-C10 | `Documentation/Boss/AL_C06_C10_VIDEO_TOOL.md` | Record fixture/tests, sample output and limits; one five-task receipt. |
| AL-C11 | `Scripts/Editor/pie_lead_common.py`, retained fight driver | Map shared helper APIs and retained driver state/setup/finish contract. |
| AL-C12 | `Scripts/Editor/pie_full_fight.py` | Port full-fight driver to shared helper without losing [FullFight] markers or game-time timing. |
| AL-C13 | `Scripts/Editor/pie_full_fight.py` | Preserve below-35-HP refill, slomo 0.5 and 15-fps capture; ER_FIGHT_TIER2=1 toggles cvar. |
| AL-C14 | `Scripts/Editor/test_pie_full_fight_offline.py` | Offline state/grammar tests with no editor import; verify Tier 2 switch default off. |
| AL-C15 | `Documentation/Boss/AL_C11_C15_FIGHT_DRIVER.md` | Diff port against retained driver and mark Lead-only runtime smoke; one five-task receipt. |
| AL-C16 | `Documentation/Boss/FIGHT_VIDEO_REVIEW.md` | Write owner checklist for all seven approved reel items with visible look/timing and tick boxes. |
| AL-C17 | `Documentation/Boss/OWNER_REVIEW_PACK.md` | Cross-check checklist names and clip references against approved reel; keep implementation evidence separate. |
| AL-C18 | `Documentation/Boss/GATE07_ANIMATION_REVIEW.md` | Reconcile four ER montage lengths and motion notes with the owner checklist. |
| AL-C19 | `Documentation/Boss/CONTROLS_STATUS.md` | Add video/visual evidence boundary without claiming post-BUILD-255 PIE. |
| AL-C20 | `Documentation/Boss/AL_C16_C20_OWNER_CHECKLIST.md` | Verify links and trace each checklist row to owner wording; one five-task receipt. |
| AL-C21 | `Source/OneBossFight/Boss/` | Audit Tier 2 component lifetime on boss respawn/reset and aura cleanup. |
| AL-C22 | `Source/OneBossFight/Boss/` | Audit activation after BeginPlay and cvar transition behavior; add test if Source contract needs it. |
| AL-C23 | `Source/OneBossFight/Boss/` | Audit parry event classification against actual pack/adapter event source; avoid guessed hook claims. |
| AL-C24 | `Source/OneBossFight/Tests/` | Add edge tests for zero/max health, repeated threshold crossings and repeated parry event. |
| AL-C25 | `Documentation/Boss/AL_C21_C25_TIER2_LIFETIME.md` | Report static/test outcome and Lead runtime gate; one five-task receipt. |
| AL-C26 | `Scripts/Tools/make_fight_video.py` | Validate timestamp monotonicity and missing/duplicate FRAME indices with explicit errors. |
| AL-C27 | `Scripts/Tools/make_fight_video.py` | Preserve frame-folder paths with spaces and ASS special characters in emitted artifacts. |
| AL-C28 | `Scripts/Tools/test_make_fight_video.py` | Add long/short capture and marker-boundary test cases. |
| AL-C29 | `Scripts/Tools/make_fight_video.py` | Audit ffmpeg concat tail duration and subtitle time base without producing a video. |
| AL-C30 | `Documentation/Boss/AL_C26_C30_VIDEO_EDGE_CASES.md` | Publish exact fixture output and remaining render-only gate; one five-task receipt. |
| AL-C31 | `Scripts/Editor/pie_full_fight.py` | Audit early boss death, player death, timeout and capture cleanup branches. |
| AL-C32 | `Scripts/Editor/pie_full_fight.py` | Verify no imported editor dependency in offline tests and stable route selection. |
| AL-C33 | `Scripts/RunLeadPie.ps1` | Assess an opt-in full-fight route under existing lock/log contract; test dry run before any edit. |
| AL-C34 | `Scripts/Editor/test_pie_full_fight_offline.py` | Test every [FullFight] marker used by video tool, including BOSS_DEAD. |
| AL-C35 | `Documentation/Boss/AL_C31_C35_CAPTURE_INTEGRATION.md` | Record Lead smoke command and no-UE offline validation; one five-task receipt. |
| AL-C36 | `Documentation/KNOWN_ISSUES.md` | Reconcile Tier 2 runtime/current KI-191 with native build and PIE evidence if available. |
| AL-C37 | `Documentation/TEST_PLAN.md` | Keep synthetic/live guard-counter, Tier 2 and full-fight capture gates distinct. |
| AL-C38 | `Documentation/PROJECT_STATE.md` | Refresh current queue/build/capture handoff without rewriting historical receipts. |
| AL-C39 | `Documentation/Boss/CONTROLS_STATUS.md` | Recheck default-wired controls only against new Lead raw receipts, if present. |
| AL-C40 | `Documentation/Boss/AL_C36_C40_GATE_CENSUS.md` | Publish issues/tests/evidence census; one five-task receipt. |
| AL-C41 | `Documentation/Boss/FIGHT_VIDEO_REVIEW.md` | Verify owner checklist maps all seven reel segments to actual capture timestamps if Lead video exists. |
| AL-C42 | `Scripts/Tools/make_fight_video.py` | Inspect Lead first render result/log and hotfix tool only from reproducible failure. |
| AL-C43 | `Source/OneBossFight/Boss/` | Inspect Lead build/native rejection; hotfix Source/tests before next batch if needed. |
| AL-C44 | `Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/` | Audit new full-fight raw log/frame coverage without inventing frames. |
| AL-C45 | `Documentation/Boss/AL_C41_C45_LEAD_REVIEW.md` | Report accepted/rejected evidence and owner action, or WAITING ON Lead; one five-task receipt. |
| AL-C46 | `Documentation/Boss/QUEUE_AL.md` | Census all 50 rows for duplicate work, source ownership and blocked gates. |
| AL-C47 | `Scripts/Tools/`, `Scripts/Editor/` | Run scoped offline tests and link validation; list exact commands and counts. |
| AL-C48 | `Documentation/Boss/FIGHT_VIDEO_REVIEW.md`, `Documentation/Boss/OWNER_REVIEW_PACK.md` | Final owner-facing proof check: media links, approval language, no invented runtime pass. |
| AL-C49 | `Documentation/Boss/AL_C46_C50_HANDOFF.md` | Write final Lead/owner gate handoff with build, PIE, render and package status. |
| AL-C50 | `Documentation/Boss/QUEUE_AL.md`, `Documentation/TASKS.md` | Close completed offline rows only and post final five-task receipt; leave evidence-bound rows open. |

## Progress

- AL-C01–C05: test-first Tier 2 live pack-boss Source and docs authored; PRODUCTION CHANGE, unbuilt. Lead native/PIE acceptance waits for engine lock. See `AL_C01_C05_TIER2_SOURCE.md`.
- AL-C06–C10: video log/frame parser, game-time ffconcat, ASS action subtitles and command file complete offline; isolated tests 4/4. Real render remains Lead/owner verification. See `AL_C06_C10_VIDEO_TOOL.md`.
- AL-C11–C15: full-fight driver ported to `pie_lead_common.py`, preserving game-time/log/capture rules and adding ER_FIGHT_TIER2 opt-in; isolated fake-Unreal tests 4/4. Lead PIE smoke pending. See `AL_C11_C15_FIGHT_DRIVER.md`.
- AL-C16–C20: seven-row owner full-fight checklist, review-pack links, current GATE-07 status and controls boundary complete; broken_links=0. Capture/owner ticks remain open. See `AL_C16_C20_OWNER_CHECKLIST.md`.
- AL-C21–C25: Tier 2 lifetime/parry-source review and one-shot aura latch authored test-first; PRODUCTION CHANGE, unbuilt. KI-191 Lead native/PIE/first-use gates remain. See `AL_C21_C25_TIER2_LIFETIME.md`.
- AL-C26–C30: strict marker/sequence and spaced-path video-tool edges complete; isolated tests 8/8. Real render/time-base check remains Lead/owner evidence. See `AL_C26_C30_VIDEO_EDGE_CASES.md`.
- AL-C31–C35: full-fight driver player-death/missing-pawn abort, cross-tool marker tests and runner two-route dry run complete; isolated tests 6/6, no output/lock side effects. Lead smoke remains. See `AL_C31_C35_CAPTURE_INTEGRATION.md`.
- AL-C36–C40: BUILD-256 485/485 and data-route aura entered as partial KI-191 evidence; full-fight real guard arm/camera issues classified. Lead-only real A4 parry script and camera proposal authored. See `AL_C36_C40_GATE_CENSUS.md`.
- AL-C41–C45: Lead video and BUILD-256 receipts audited; 7326 FRAME markers/PNGs, intentional 7327th encoded terminal frame, first ASS labels aligned, owner checklist remains unticked. See `AL_C41_C45_LEAD_REVIEW.md`.
- AL-C46–C50: 50/50 queue-row census, 14/14 focused offline tests, parry script syntax and broken_links=0; owner pack links full-fight capture with caveat. Handoff leaves PIE/camera/counter/package/owner gates open. See `AL_C46_C50_HANDOFF.md`.
