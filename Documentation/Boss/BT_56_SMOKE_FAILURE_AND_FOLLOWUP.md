# BT-56 Smoke failure and follow-up

Date: 2026-11-16
Run: `Saved/SevarogArenaRoute/Run_20261116_152934_ba15687c`
Receipt: `Saved/SevarogArenaRoute/Run_20261116_152934_ba15687c/acceptance.json`

## Result

The C-1155 Development build and full DD27j suite passed immediately before this run (BT-55: build exit 0, 573/573 tests). The fresh Smoke then returned exit 1 after its 180-second evidence window. The receipt says `accepted=false` and `runtime_acceptance_status=BLOCKED`; BT-56 is closed as a completed failed attempt.

Smoke did make meaningful runtime progress: it observed `rpg.Build=Starter`; the route initialized target health to 800/800 and read it back; the selected framework binding was active; one framework boss spawned; production card decisions occurred and the boss damaged the player. Pack-boss suppression/no montage and zero pack-boss HUD widgets were observed.

Acceptance still fails: runtime boss max health was 250 while the required `sevarog_health_1500` criterion expects 1500. The authoring script labels the currently authored framework profile `F5 fixture` and gives it `boss_max_health=250` and `target_health=800`. The separate O1 owner-approved boss-definition input specifies `Stats.MaxHealth=1500`; whether/how the production framework profile consumes that definition must be traced before changing data. The raw BehaviorTree attack-task tick count remains `BLOCKED_NOT_INSTRUMENTED`; card selection and damage are not a substitute for this counter.

Cleanup passed: `DefaultGame.ini` restored byte-for-byte to SHA-256 `5DE691FCA4E0FA375F6F262FA6BA402FEFA7AB9A0B567AE2146E6823F69EDEC8`, Editor exited, C-1155 locks released 2/2, no asset save or package. No playable build is claimed.

## Next gated batch

BT-57 (Antigravity) audits the selected runtime profile, O1 health wiring, fixture separation, and direct BT-tick evidence source. BT-58 (Codex) reviews that audit. BT-59 (Antigravity) implements only the approved production-profile and telemetry changes while preserving the F5 fixture. BT-60 (Codex) reviews the changes. BT-61 reruns the locked Development build, full suite, and fresh Smoke only after acceptance. The 1500 gate remains unchanged; no profile/tuning values are to be invented.

## Lead source cross-check

The encounter authoring script selects `/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Draft` (`author_framework_encounter_definition.py:22,152,189,195`). The profile authoring labels that asset `F5 fixture` and writes boss max health 250 / target health 800 (`author_sevarog_draft_cards.py:55,63,67`). Native runtime boss health initializes directly from `Dependencies->Profile->BossMaxHealth` (`RPGFrameworkBossCharacter.cpp:185-187`); the O1 boss-definition Stats.MaxHealth is not automatically copied by that code. Separately, `RPGPlayerMovesSubsystem.cpp:825` states raw BehaviorTree attack-task execution is uninstrumented, matching the blocked receipt. Preserve both acceptance gates pending the BT-57 audit and lead decision.

## Lead review note for BT-57 (2026-11-16)
The profile wiring findings are independently confirmed. Two recommendations remain unaccepted pending correction. First, BT-13 (`Documentation/Boss/BT_13_RAW_BT_TICK_EVIDENCE.md`) expressly rejects `began_play=0`, StopLogic, or a suppression-time status snapshot as a substitute for a raw attack-task tick counter; the proposed `IsRunning/GetActiveNode` snapshot cannot establish the historical count unless a source/engine contract proves the tree could not have run before sampling. Keep the acceptance criterion blocked absent genuine execution-path instrumentation. Second, `TargetHealth=800` is currently only sourced from the F5 fixture; it is not an owner-approved production player-health value. BT-57 is back in progress for an audit correction. No code or data implementation is approved yet.
