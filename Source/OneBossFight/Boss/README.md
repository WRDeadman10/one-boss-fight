# Boss module

This folder implements the native framework proof boss and its runtime collaborators. Authored profile/card data is compiled before the actor runs; the framework boss owns decision state and delegates card playback to the executor.

## Main files

- `RPGFrameworkBossCharacter` owns health, phase, posture, bleed, target invariants, selector decisions, and terminal/restart transitions (`RPGFrameworkBossCharacter.h:23-60`; implementation `RPGFrameworkBossCharacter.cpp`).
- `RPGFrameworkMoveExecutor` observes montage time and performs card windows, warp, cues, cleanup and locks (`RPGFrameworkMoveExecutor.cpp:175-300,531-596`).
- `RPGFrameworkBossController` owns navigation requests, completion handling, and its walk stop path (`RPGFrameworkBossController.cpp:12-49,51-69`); the boss calls that interface at range-band, leash, reposition, and teardown boundaries (`RPGFrameworkBossCharacter.cpp:229-235,871-880`).
- `RPGFrameworkProofFixture` owns proof-lane fixture authority, target publication, and restart orchestration (`RPGFrameworkProofFixture.cpp:32-59,99-113`). The boss validates fixture authorization during initialization and owns its generation reset implementation (`RPGFrameworkBossCharacter.cpp:57-80,855-869`).
- `RPGSevarogDirector` is the separate pack-specific boss direction path; do not assume its lifecycle or attack source is the framework proof boss.

## Read before changes

Use `Documentation/Boss/ARCHITECTURE_OVERVIEW.md`, `REF_BOSS_CHARACTER.md`, `REF_EXECUTOR.md`, `REF_SELECTOR.md`, and `REF_PROFILE.md`. Runtime proof logs use `[FrameworkProof]` and are summarized by scripts in `Scripts/Tools`. Do not infer live coverage from a source-only test or compile.
