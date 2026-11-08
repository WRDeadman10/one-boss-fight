# C-1111 hotfix — full-fight player health initialization

Claude's C-1111 DATA-default PIE run failed before the fight began: the maintained driver read player health as 0/1,000,000 during initialization and immediately classified the player as dead. Earlier fight captures reached 100 HP after initialization. This was a driver startup false positive, not a parry outcome.

Added test-first coverage for `0 → 0 → 100 → 0` and for a persistent zero through the five-second game-time grace. `player_failure()` now marks readiness once a positive health value is observed, logs `PLAYER_HP_READY`, and treats a later zero as death. Before readiness, zero is tolerated only until five fight-seconds; a continued zero then fails as dead. Missing-player timeout behavior is unchanged. The check uses `S["fight_time"]`, not the world's pre-fight clock.

The pre-fix focused test run failed on both new startup cases as expected. After the fix, the full-fight and video-tool focused suites pass **27/27**; Python compilation and `git diff --check` pass. No Unreal/build/PIE run by Codex.

**Lead rerun requested:** C-1111's original 150-second DATA-default, Tier 2-on run to `D:\FightVideo\auparry` should now pass initialization and reach the parry-watch window. This change alone does not establish any parry result.
