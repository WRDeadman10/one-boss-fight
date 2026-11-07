# Queue AC AC-C06–AC-C10 — player attack montage lifecycle audit

Mailbox reviewed through C-980. Static Source/test review only; no Unreal, PIE, build, or tests run by Codex.

## AC-C06 — death interruption ownership

- `URPGDodgeTiming` is attached to pack player pawns (`RPGPlayerMovesSubsystem.cpp:871-888`). Its `EndPlay` restores temporary ability arrays and resets the guard window, but does not stop an animation montage (`RPGDodgeTiming.cpp:40-47`). No death-state callback appears in this component.
- `URPGAttackTracker` monitors a boss's move montage and ends boss attack-instance bookkeeping at zero boss health (`RPGAttackTracker.cpp:378-397`); it is registered only under `IsPackBoss` (`RPGPlayerMovesSubsystem.cpp:783-786`). It is not evidence for player attack cleanup.
- The reviewed source has no explicit player-death -> stop-player-attack-montage hook. This is a coverage gap, not proof that the pack death ability fails to replace/stop the montage. `URPGBossStagger::StartRiposteClips` separately stops all montages on the player mesh when starting riposte (`RPGBossStagger.cpp:576-598`); that is a specific interruption, not general death handling.

## AC-C07 — reset and rebind

- `URPGBossEncounter::ResetEncounter` stops montages on the boss character mesh (`RPGBossEncounter.cpp:328-403`), then broadcasts reset. The player subsystem waits for a possessed player and attaches components to that pawn (`RPGPlayerMovesSubsystem.cpp:368-383, 430+`).
- No reviewed reset call targets the player's `UAnimInstance` to stop an active player attack montage. This does not establish whether every live reset keeps or replaces the player pawn, nor whether pack code independently cancels the montage.
- `URPGDodgeTiming::EndPlay` restores temporary arrays, but a surviving component/pawn does not take that teardown path just because the boss resets.

## AC-C08 — temporary ability-array backup lifetime

- Optional air attacks and GuardCounter use `ApplyMontageArrayOverride` on the specified ability arrays (`RPGDodgeTiming.cpp:477-481, 497-515, 529-540`). It first restores any prior backup, then stores weak ability references and serialized arrays. Empty arrays are skipped (`:563-621`).
- The component ticks the restore check. The snapshot is restored when the override montage is observed playing or after a one-second fallback (`RPGDodgeTiming.cpp:65-68, 423, 649-677`). EndPlay also restores (`:40-45`); invalid weak ability pointers are skipped (`:635-643`).
- This supports normal start, timeout, subsequent override, and component teardown at source level. It does not prove array restoration under death/reset in a live run. No defect confirmed statically.

## AC-C09 — test and probe coverage

- Native automation asserts the optional fields default to null (`RPGAutomationTests.cpp:1192-1195`). Focused Python wiring checks inspect source contracts (`test_air_attack_wiring_contract.py:13-14`, `test_guard_counter_wiring_contract.py:12,34`).
- No reviewed native/offline test drives a player's active attack montage through player death, encounter reset, pawn replacement/rebind, or component teardown. Lead's air-restore probe covers air attack then grounded R1/R2 only; C-978 reports that sequence on both routes.
- The C-980 movement fix is separate from this lifecycle gap; earlier moving-dodge results are invalid pending corrected Lead runs.

## AC-C10 — minimal Lead observation matrix

| Scenario | Setup and observation | Evidence to retain | Claim boundary |
|---|---|---|---|
| Player death during active attack | On both routes, trigger a known attack, then kill player before montage completion; record montage name/position before death and through death state. | Build ID, route, health/death tags, pawn/controller IDs, montage start/stop/end, `RPGDodgeTiming` lifetime, raw log | Only the exercised death path |
| Encounter reset during active player montage | Trigger attack and reset; record whether pawn is same/replaced, montage state, input/context and component IDs after reset/rebind. | Reset generation/count, pawn IDs, montage timeline, rebind outcome, raw log | Distinguish boss-mesh reset from player-mesh cleanup |
| Player pawn replacement during reset | Capture old pawn destruction and new possession separately; inspect montage on each surviving mesh and confirm component attach. | Old/new IDs, possession times, component presence, montage state | Do not infer old pawn teardown cleans a surviving pawn |
| Temporary ability-array cleanup | In an approved test build, snapshot arrays before/after normal completion, reset, death and respawn for each optional montage. | Array snapshots, montage, actor/ability IDs, route, cleanup event | Does not imply owner approval or saved assignment |

No gameplay change is proposed. If Lead captures a persisting montage on a surviving player mesh, use that reproduction to scope a targeted fix and native regression test.
