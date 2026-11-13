# Queue BC Batch 2: X06–X10 Sevarog proof audit

## Evidence inventory (X06)

Read-only inventory of the Codex proof folders; raw logs were not opened for this task. Selected status receipts have SHA-256 hashes below.

| Evidence folder | Receipt files and SHA-256 |
|---|---|
| `Docs/BossCombatReview/Execution/Codex/C1256A_SPAWN_BRIDGE/` | `build_suite_status.txt` — `5A58B062C2601B94E0DC50BD068A9B657A25DBB0F5550AD0D1A6351D67014DC8`; `pie_self_test_status.txt` — `460994D1D24E2BBA1B8BC949CC42A2EA474CBC62327255699B985513D3A54815` |
| `Docs/BossCombatReview/Execution/Codex/C1258A_RANGE_RETRY/` | `build_status.txt` — `FF18CF881F837718A05F8D17A057ABFE29F4823CBCC7E78AAA5DEC5FB670C7B2`; `nav_failure_baseline_status.txt` — `B7EBD3C927DD4A4BA065568E220BA9998328D1C70304AE9553C6416FC6DFC2BA`; `pie_self_test_status.txt` — `2B65A6BDFD4BEBF9279A260ABB45AD22DC5FF78BCCEE50778268FF1FC630093C` |
| `Docs/BossCombatReview/Execution/Codex/C1262A_SEVAROG_DIAG/` | `build_status.txt` — `AAF9EE998A553DD5C618ECA8FC24A6B40A924B2586DA218C40439C91260A4680`; `pie_live_status.txt` — `00121EACF7A9B4A05944B1BBFD12AB394BC71C835DB524AF2908442246FEE9B0` |

The actual C-1262a directory is `C1262A_SEVAROG_DIAG`. A prior X40 checklist draft used a nonexistent longer directory name; this batch corrected `NEW_BOSS_CHECKLIST.md` and the X36–X40 audit report. `C1256A` reports spawn plus one S1 start; `C1258A` reports S1–S3 test starts and keeps general nav unresolved; `C1262A` reports four primary cards plus S4 whiff → S5, with S1/S2 contact still open. These are the scopes stated in the existing status reports, not a fresh raw-log verification.

## Authoring manifest cross-check (X07)

C-1254 accepts five named cards (`Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow`, `Speedburst`, and standalone `Swing1_FAST_v2`), the framework profile, and an unselected definition under `/Game/OneBossFight/Data/Sevarog/`. `Scripts/Editor/author_sevarog_draft_cards.py:17–21` has the matching five asset names; `:64–65,353–370` pins the S4 whiff → S5 `Swing1_Medium` edge. C-1254's accepted margins are S1/S2 +0.303 s (0.300 required), S3 +0.603 s, and S4 forward counterplay +0.086 s. The code's `CARD_FIELD_SOURCES` table at `:93–137` attributes each authored field. No per-field saved-asset reread was done in this batch; C-1254's authoring receipt remains the authority for that run.

## Driver and lifecycle audit (X08–X09)

- The PIE driver checks required cards and bridge methods (`pie_sevarog_framework_live.py:64–109`), refuses a missing/failed transient spawn and profile initialization (`:138–175`), checks requested distance against the selected card's band (`:191–218`), and invokes exact test card starts (`:490–508`). The C++ spawn API refuses invalid class/world and marks the actor transient; initialization requires standalone, same-world authorized target/profile state (`RPGFrameworkBossCharacter.cpp:64–104`). The test-only initial-walk bypass is explicitly scoped and non-Shipping (`RPGFrameworkBossCharacter.cpp:145–158`).
- Narrow cleanup risk: after successful init, a missing controller triggers a raised driver error (`pie_sevarog_framework_live.py:178–188`) without an explicit `boss.destroy_actor()` at that branch. The PIE shutdown path normally destroys transient actors, but the driver could explicitly destroy the actor before raising. This is a bounded test-driver hygiene risk, not a production behavior defect.
- The executor's pure watchdog rule has native cases for recovery-dominant and clip/blend-tail budgets plus invalid inputs (`RPGFrameworkRuntimeTests.cpp:501–514`). Executor startup and timeout use that rule (`RPGFrameworkMoveExecutor.cpp:150–152,193–196`). `RestartEncounter` checks `CanRestart` and game-thread status (`RPGFrameworkBossCharacter.cpp:988–991`), but this search found no focused automation for repeated full lifecycle restart/teardown; that transition remains a coverage gap, not a source-proven runtime failure.

## X10 checklist update and limits

Updated the evidence link in `NEW_BOSS_CHECKLIST.md` to the actual C-1262a folder. No new runtime, asset, build, or PIE claims were added. No suite run was performed.

Next: continue BC-X11–X15; check Claude feedback at the next cycle, hotfix any bounded rework, and proceed without waiting.
