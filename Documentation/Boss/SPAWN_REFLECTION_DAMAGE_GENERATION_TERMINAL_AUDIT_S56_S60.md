# Spawn, reflection, damage, generation, terminal audit (Queue C S56–S60)

Read-only source audit, 2026-11-03. No source behavior or assets changed; no editor/runtime execution.

## S56 — world actor-spawn listener ownership

| Listener | Registration | Removal | Assessment |
|---|---|---|---|
| `URPGSevarogDirector` | `BeginPlay` stores `SpawnHandle` from `AddOnActorSpawnedHandler` (`Boss/RPGSevarogDirector.cpp:34–43`) | `EndPlay` removes that handle from current world (`:50–55`) | Paired; UObject delegate target and component share owner lifetime. |
| `URPGPlayerMovesSubsystem` | `PostInitialize` stores world spawn handle (`Player/RPGPlayerMovesSubsystem.cpp:47–54`) | `Deinitialize` removes it before superclass (`:68–75`) | Paired at subsystem teardown. Existing pawns are separately enumerated at world begin play (`:57–65`). |

## S57 — reflected-call result handling

- Required calls generally preserve failure: phase ability-tag blocking returns `bCalled` and retains prior applied state on failure (`Player/RPGBossPhases.cpp:190–216`); loadout slot blocking reports failure (`Player/RPGBuildLoadout.cpp:630–660`); encounter behavior stop handles the boolean result (`Player/RPGBossEncounter.cpp:179–190`).
- Several calls are intentionally best-effort: projectile ability activation, cosmetic/audio setup, optional combat target reset, and some behavior toggles ignore the return (`Boss/RPGSevarogDirector.cpp:136,232,260,285,331,372`). These paths need per-call contract/context before classifying as bugs.
- Candidate ownership gap remains in phase immunity removal: local ownership clears before reflected removal result is checked/retained (`Player/RPGBossPhases.cpp:216–235`; also S48). No source evidence proves the Blueprint effect remains active.

## S58 — damage outcome consumers

- `URPGDamageResolver::Resolve` makes one central verdict and increments per-move/outcome counters in `Record`; accepted damage writes health and spends the hit, parry spends the hit and notifies the parry component, rejection paths leave health/hit unspent (`Player/RPGDamageResolver.cpp:158–200`). Counts are keyed by move and outcome and can be cleared with the audit (`:210–218`); UI summary displays selected outcome totals (`:220–228`).
- New framework grab consumes the central resolver result and logs outcome/HP applied (`Boss/RPGFrameworkMoveExecutor.cpp:407–415`). Legacy javelin, low-sweep, and shockwave each switch on the same outcome enum and maintain attack-local accepted/parried dispositions (`Player/RPGBossJavelin.cpp:145–165`; `RPGBossLowSweep.cpp:125–150`; `RPGBossShockwave.cpp:110–128`).
- Wave central-priority logic records `Superseded` when central damage already reduced health (`Player/RPGBossShockwave.cpp:~100–125`); geometry misses are recorded separately. Outcome vocabulary includes `Overlap`, `MissJumped`, `MissWorld`, `Superseded`, and `Failed`, so not every enum member is a damage decision. No missing downstream side effect was confirmed in reviewed consumers.

## S59 — generation tokens and stale work

- Framework executor tokens carry encounter ID, generation, and attack instance; the move model rejects callbacks whose active token no longer matches (`Player/RPGBossMoveModel.cpp:88–116`). The stale-callback proof hook submits the previous token and logs refusal (`Boss/RPGFrameworkMoveExecutor.cpp:53,~160–166`).
- Damage payloads snapshot generation when the attack starts, and resolver compares it with current encounter generation before health/parry handling (`Player/RPGDamageResolver.h:~35–50`; `RPGDamageResolver.cpp:150–158`).
- Legacy shockwave stores `LaunchGeneration` and stops on mismatch (`Player/RPGBossShockwave.cpp:153–160`); other move actors use attack instance/state guards. World-level Niagara timer in director is intentionally generation-independent cosmetic work and captures weak effect/world references plus copied location (S47); it is not a combat callback.
- Scope limitation: this is a source trace of the cited callback/payload paths, not a whole-program proof that every third-party Blueprint callback is generation tagged.

## S60 — terminal-state repeat calls

- Framework boss `Die` and `Fail` guard repeat calls with `bDead`/`bFailed` and perform owned walk/movement/executor/clip shutdown once (`Boss/RPGFrameworkBossCharacter.cpp:875–892`). `EndPlay` repeats stop/abort cleanup without a one-shot flag (`:894+`); called APIs are expected to tolerate cleanup repeats, but this was not runtime tested.
- Javelin `Finish` returns immediately once `bFinished` is true (`Player/RPGBossJavelin.cpp:83–100`). `URPGBossDeath::EndPlay` cleanup and several component stop routines were not exhaustively invoked under repeated teardown.
- Candidate for focused idempotence test: component `Stop` methods that emit terminal logs or update counters on repeated calls; source-only scan did not establish a concrete double-side-effect defect.

## Disposition

No confirmed defect in S56–S60. All world spawn handles reviewed are paired. Required reflected-call paths generally expose failure; best-effort exceptions and phase-immunity ownership remain review candidates. Generation checks exist on framework callbacks, damage payloads, and shockwave launch. Framework terminal functions are guarded; repeated EndPlay cleanup behavior remains untested.
