# Restart and lifecycle audit (Queue C S41–S45)

Read-only source audit. No C++ or runtime behavior was changed.

## S41: boss state across generations

`InitializeProof` establishes stable identity, resolved dependencies, target/controller, arena origin, initial health, executor, and `WalkStart` (`RPGFrameworkBossCharacter.cpp:66–98`). `RestartEncounter` is allowed only after death or clean success, never after failure, and requires an increasing generation (`RPGFrameworkBossCharacter.h:59`; `.cpp:855–865`).

| State class | Fields / behavior | Evidence |
|---|---|---|
| Stable for the boss session | `bInitialized`, profile/dependencies, encounter id, target/controller, `WalkStart`, `ArenaOrigin`; the last two remain fixed to the first setup. `DecisionSeq` is explicitly monotonic and intentionally not reset. | `RPGFrameworkBossCharacter.cpp:66–98,855–865`; `.h:76–79`; selector sequence `.cpp:455`. |
| Reset for a new generation | generation, expected target HP, attack budget, boss health if hittable, posture/stagger/bleed, phase and selector memory, combo, reposition/strafe/leash, aggro/dodge/flask histories, fatigue, and the listed target-hit/dodge/drink/shift test-hook progress. | `.cpp:862–865`. |
| Cumulative by Lead decision | Executor `HitsAccepted`, `HitsGuarded`, `HitsParried`, and `AppliedDamage` survive `Rearm`; `Rearm` resets per-card playback state but not those counters (`RPGFrameworkMoveExecutor.cpp:96–104`; `.h:58–59`). C-714 confirms lifetime-total semantics. | `DECISIONS.md`, “FrameworkProof RESULT counter scope”; F8 restart evidence cited in `RESULT_COUNTER_SCOPE_S6_S7.md`. |
| Test-hook reset gap | `ProofGStart` and `ProofIFStart` are armed only while `< 0`, then set to `-2` on completion; neither is reset in `RestartEncounter` even though their CVar descriptions say “first attack of an encounter.” Other hook progress such as `ProofDodgeStart`, `ProofDrinkStart`, `ProofShiftStart`, and `ProofHitStart` is reset. A second generation with the hook CVar still enabled therefore will not arm guard/iframe hooks again. | `.h:80–82`; `.cpp:265–309,536–537,862–865`; CVar descriptions `.cpp:35–37`. **BUG candidate:** reset these one-shot sentinels at generation restart or narrow their documented scope to once per actor. |

Remaining member-state classification: `ComboGraph` and resolved dependencies are profile/session-immutable; `ComboGateCounter` is a monotonically increasing gate identity (not reset); `OverlayLoggedAt`/`OverlayLastState` are a cross-generation log throttle/cache; `ComboState` and hit baselines are inactive while `bComboActive=false` and overwritten on the next combo start; F11 montage timestamps are inactive after `StopF11Clip` and the hold/active flags are reset. `bFailed` is sticky and restart preconditions require it false. `Health` resets only for a hittable boss; non-hittable fixture health is immutable/unread. These are not restart-path omissions affecting active gameplay based on the inspected consumers, except the explicitly flagged proof-hook sentinels.

## S42: executor counter consumer map

`HitsAccepted`, `HitsGuarded`, `HitsParried`, and `AppliedDamage` increment only on their corresponding accepted contact paths (`RPGFrameworkMoveExecutor.cpp:291–292,413–414`). `HitsAccepted`, `HitsGuarded`, and `HitsParried` are read as baselines/deltas for combo branch outcomes (`RPGFrameworkBossCharacter.cpp:570,768,799,815`); accepted/parried totals feed terminal classification and RESULT (`:615–618,884`); accepted hits plus applied damage feed the invariant (`:615`). `CARD_END` also prints `hitsAccepted` and `appliedDamage` (`RPGFrameworkMoveExecutor.cpp:206`), but those are executor-lifetime totals rather than per-card totals. Its label may be misread as card-scoped; document that scope or rename in a later schema-compatible change. 

`CardAcceptedHits` and `CardParriedHits` are separate card-local counters reset at each `StartCard` (`RPGFrameworkMoveExecutor.cpp:128`); they determine whether the finished card contacted (`RPGFrameworkMoveExecutor.h:45`) and whether fatigue counts a whiff (`RPGFrameworkBossCharacter.cpp:586`). They do not reset or substitute for lifetime counters at `Rearm`.

## S43: player component acquisitions and release

| Acquisition | Release / lifecycle | Finding |
|---|---|---|
| `Status.Invulnerable` via `URPGIFrameMonitor` | EndPlay calls `RemoveTag`, then clears `bTag`/`bOwnedNow` unconditionally (`RPGIFrameMonitor.cpp:157–165`); `RemoveTag` returns success and says failed removals should retain ownership (`:124–127`). | **BUG candidate:** a failed removal while the owner pawn survives ends retries and loses the local ownership record. `OnEncounterReset` correctly retains state unless removal succeeds (`:146–155`). |
| `Status.ParryActive` via `URPGPlayerParry` | EndPlay retries tag removal at most five times (`RPGPlayerParry.cpp:182–186`); failed attempts keep `bTagOn` for the next tick/EndPlay (`:196–199`). Stamina rollback/refund likewise has a five-attempt bound (`:147–185`). | Bounded retry is explicit; persistent pack API failure at teardown can still leave the tag or stamina value unresolved. |
| Hyperarmor immunity effect via `URPGSwingTracker` | EndPlay calls `SetHyperArmor(false)` (`RPGSwingTracker.cpp:127–133`), which calls `RemoveImmunity`; its Blueprint call result is ignored (`:336–354`). | Cleanup is attempted, but the component cannot report/retain a failed removal. |
| Pack collision `OnHit` delegate | `URPGHitIntake::EndPlay` calls `Unbind` (`RPGHitIntake.cpp:172–175,343–361`). | Matched removal is present. Two next-tick finalizers use `CreateUObject` without stored timer handles (`:465,506`); EndPlay does not cancel or drain `Pending`, so dynamic component removal before the next tick deserves a focused teardown regression. |
| Combat context participant record | Participant EndPlay calls subsystem `UnbindActor`; subsystem deinit clears records (`RPGEncounterBinding.cpp:185–188,201–204`). | Matched release is present. |
| Enhanced Input actions | Dodge, riposte, and player-parry components bind on the pawn's `UEnhancedInputComponent` (`RPGDodgeTiming.cpp:129`, `RPGRiposteInput.cpp:45`, `RPGPlayerParry.cpp:58`). | No binding handles are retained and no `EndPlay` unbind is present. The input component is pawn-owned, so whole-pawn teardown ends both; dynamic component removal while the pawn/input component survives can leave inert bindings and repeated attach can accumulate them. No lifecycle test was run. |

Other inspected cleanup: `RPGBossCloseClipSwap::EndPlay` restores its montage override (`RPGBossCloseClipSwap.cpp:59–62`); `URPGAttackTracker::EndPlay` restores telegraph play rate (`RPGAttackTracker.cpp:321–324`); `URPGBossDeath::EndPlay` limits remains spawning to a dead actor being destroyed outside world teardown (`RPGBossDeath.cpp:117–129`).

## S44: world subsystem and timer teardown

- `URPGPlayerMovesSubsystem` removes its actor-spawned delegate in `Deinitialize` and restores the fixed editor frame rate (`RPGPlayerMovesSubsystem.cpp:53,68–75`).
- `URPGLegendSubsystem` cancels hit stop/slow motion before removing its core ticker; its tick also self-removes when effects end (`RPGLegend.cpp:66–74,92–101,228–246`). The owner encounter is weak and generation checked.
- `URPGCombatContextSubsystem` owns no timer/delegate; it resets records and invalidates its world session in `Deinitialize` (`RPGEncounterBinding.cpp:196–204`).
- No world subsystem retains a timer handle. Adjacent non-subsystem timers: `URPGHitIntake` and `URPGBossLook`/`URPGBossStagger` use next-tick `CreateUObject` delegates; weak UObject binding avoids a raw dangling callback, but component EndPlay does not explicitly cancel them. `RPGSevarogDirector` removes its actor-spawn handler on EndPlay and its delayed Niagara lambda captures weak effect/world references (`RPGSevarogDirector.cpp:42,50–56,81–88`); that VFX can still occur after the director component ends if the world remains alive.

## S45: Enhanced Input ownership

The three source registrations are exactly the bindings listed above. They are stored on the pawn's input component, while callbacks target UObject components. None records the returned binding handle or removes by handle. Current project attachment is once per pawn in `RPGPlayerMovesSubsystem::Attach`; no repeated-attach behavior was exercised. Static risk is limited to component-only teardown/re-attach during a still-live pawn; whole-pawn teardown owns both input component and callbacks. `bBound` suppresses re-registering while the component remains attached, but also means replacing the pawn's InputComponent in place will not refresh the binding.

## Limits

This is a source-only lifecycle audit. Dynamic component removal, failed Blueprint tag/attribute APIs, and world teardown ordering were not executed in Unreal. Findings above are review candidates for Lead; no behavior or project files were changed beyond this audit note and tracking docs.
