# Death and remains

The pack-facing death path is `URPGBossDeath`; the native proof boss has its own simpler terminal transition. The two paths should not be treated as equivalent.

## Pack boss

`URPGBossDeath::BeginDeath` captures the skeletal mesh transform and preloads the remains assets before applying the pack death transition (`Source/OneBossFight/Player/RPGBossDeath.cpp:360-375`). When the death flow reaches its terminal point, it spawns the remains actor at the captured transform if the world is not tearing down (`:121-124`). Reset is refused while death remains active, preserving the remains and the dying actor's final state (`RPGBossEncounter.cpp:303-310`). An accepted later encounter reset removes existing remains (`RPGBossEncounter.cpp:310`).

`ARPGBossRemains` owns the static mesh/materials and optional Niagara burst; its tick applies the form/dissolve curve over the configured duration (`RPGBossRemains.cpp:45-54,89-120,132-155`). `rpg.RemainsFormSeconds` controls the form duration with a positive floor (`:21-27,132-138`).

## Native proof boss

`ARPGFrameworkBossCharacter::Die` is idempotent, stops movement, aborts the executor and phase/stagger clips, then emits a `BossDefeated` result (`RPGFrameworkBossCharacter.cpp:874-884`). The implementation does not spawn `ARPGBossRemains`; a native boss death animation/remains presentation is outside this path. `Fail` is a separate error terminal that stops movement and playback and logs an error token (`:885-892`).
