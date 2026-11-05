# Framework boss generation reset guide

`RestartEncounter(NewGeneration)` reuses one initialized framework boss after a successful finish or death. It is a generation transition, not a reconstruction of the actor or a reset of every UObject/component in the world. Source: `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:855-872`.

## Preconditions and order

1. `CanRestart` requires initialized, not failed, terminal (`bDead || bSucceeded`) state, and `NewGeneration > GenerationId`; restart also requires the game thread (`RPGFrameworkBossCharacter.h:59`, `.cpp:855-858`).
2. The existing target/controller pair is revalidated for identity, world, liveness, arena, and readable health before mutation (`.cpp:859`, `TargetFault` at `:101-111`). A replacement pawn/controller is not accepted by this API.
3. `Executor->Rearm(NewGeneration)` happens before the boss writes its own `GenerationId` (`:860-861`). Rearm stops the owned montage, asks the move model to close/abort any active token and advance its epoch, clears executor transient playback state, and disables executor ticking (`RPGFrameworkMoveExecutor.cpp:96-107`; `FRPGBossMoveModel::ResetGeneration` in `RPGBossMoveModel.cpp:141-147`). The generation must be strictly greater than the model epoch. The model's monotonic instance identity is not reset.
4. The boss then writes the new generation, snapshots target health, resets attack count and encounter-local behavior state, restores boss health if hittable and posture to profile maximum, resets bleed, and resets selector state (`RPGFrameworkBossCharacter.cpp:861-865`).
5. It returns to the original `WalkStart`, faces the retained target, restores walking, records a new start time and asks the existing controller to walk to the band (`:866-872`).

## State disposition

| Owner/state | Restart disposition | Source / boundary |
|---|---|---|
| Executor / move model | Owned montage stopped; model closes any open windows and emits abort when active; model epoch advances; executor's transient flags, token, pose samples, grab/warp state reset; ticking disabled. | `RPGFrameworkMoveExecutor.cpp:96-107`; `RPGBossMoveModel.cpp:125-147`. Not a new executor. |
| Selector | `Selector.Reset()` clears per-card last-start clocks, recent-repeat history, started count, and cone hysteresis (`LastStartClock=-1`, empty history). Immutable config/candidates remain. | `RPGBossMoveSelector.cpp:85-95`; called at boss `.cpp:865`. |
| Boss/encounter | `AttacksDone`, movement/strafe/stuck/reposition, pending parry reaction, aggro samples/band, fatigue, phase latch/current phase, posture/stagger, combo/LOS/dodge/flask/anti-cheese state, leash and bleed state reset. Boss health refills only when `bHittable`. | `RPGFrameworkBossCharacter.cpp:861-865`. `DecisionSeq` is explicitly monotonic across restarts; do not treat its trace sequence as generation-local (`RPGFrameworkBossCharacter.h:74`). |
| Executor damage counters | `HitsAccepted`, `HitsGuarded`, `HitsParried`, and `AppliedDamage` are lifetime totals and are not cleared by `Rearm`; card-local accepted/parried counts reset on each `StartCard`. | `RPGFrameworkMoveExecutor.h:41-59`; card reset at `.cpp:128`. Interpret log totals across generations accordingly. |
| Player/controller references | Weak `Target` and `TargetController` are retained, not rebound. Validation checks target still belongs to the same controller/world and has readable positive health. `ProofFixture` also remains retained. | `RPGFrameworkBossCharacter.h:65-68`; `.cpp:859`, `:101-111`. |
| Player tags / abilities | Framework code reads `Status.Blocking` at contact and logs observed guard/parry tags in the proof hook; it does not add/remove those tags during boss restart. The player/ability system owns its own tag and input cleanup. | `RPGFrameworkMoveExecutor.cpp:286,408`; `RPGFrameworkBossCharacter.cpp:277-278`. Restart does not restore player health or clear external player state. |
| Proof hooks | Some scheduling cursors reset: target shift, drink, dodge, and player-hit starts/counts reset and their parsed arrays are rebuilt when armed. Bystander and target-fault booleans reset. The guard (`ProofGStart`) and iframe (`ProofIFStart`) sentinels are not reset in `RestartEncounter`; after their hook sets them to `-2`, those hooks remain one-shot for this actor even if the CVar stays enabled. | Reset at `.cpp:864`; hook arming at `:524-556`; guard/iframe sentinels finish at `:279,309`. Test CVars themselves are external process state and are never reset by this method. |
| Spawned bystander | `bBystanderSpawned` resets, so an enabled hook may spawn another bystander in a later generation. No bystander actor handle is retained here for removal. | `RPGFrameworkBossCharacter.cpp:557-562,864`. The actor persists until its own/world lifecycle ends. |

## Operational interpretation

Use a strictly increasing generation for each reused encounter; retain the same target/controller and ensure external player state is ready before calling restart. `encounter_reset` is emitted after transient-state reset and before the new walk request succeeds, so it is not itself proof that the new generation reached the band or started a card. Lifetime damage/contact counters and `DecisionSeq` intentionally span generations. Proof hooks with one-shot sentinels need a fresh boss actor or a separate explicit reset change for repeated experiments; this guide does not alter that behavior.
