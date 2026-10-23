# Audit 01 — Static Source Audit

**Scope:** static read-only audit for Brief 05. No editor, build, package, game,
or automation run was started. Findings below are based on source inspection;
runtime behaviour remains for Claude to validate.

## Method

Reviewed `Source/OneBossFight` in the Brief 05 order. The inventory contains
95 `.h`/`.cpp` files and 18,298 physical lines (counted with PowerShell).
Each section records reviewed files and line counts before findings so partial
work remains useful if interrupted.

## Pack

**Read:** `RPGBlueprintCall.h` (179), `RPGPackReflect.h` (64),
`RPGPackTrace.h/.cpp` (50/339), `RPGPackNotifies.h/.cpp` (55/61),
`RPGHideBones.h/.cpp` (19/18), and `RPGBlueprintCall.cpp` (3): **788 lines**.

**Result: no defect found.** Reflection calls initialise and destroy parameter
storage, trace objects are weakly held, reflection failures return fallbacks or
log, and array-element pointers are consumed before a pack call can mutate the
array. The charge notify guards absent character, movement, and target; its
remaining-time denominator is clamped.

## Player — Encounter, Attack Tracker, and Rules

**Read:** `RPGBossEncounter.h/.cpp` (75/306), `RPGAttackTracker.h/.cpp`
(156/365), `RPGAttackKind.h` (56), `RPGBossRules.h` (73), `RPGBossMath.h`
(74), and `RPGBleedRules.h` (63): **1,105 lines**.

**Result: no defect found.** The encounter holds or resumes the AI on all
dormant/reset paths, advances its generation before resets can affect state,
and uses weak ownership for the player. The tracker terminates its active
state on replacement, death, or a stopped montage; its denied montage pointer
is weak. The pure rules guard zero maxima and use clamped or safe-normal
geometry where needed.

**Pure-rule coverage gap for Part B:** existing tests cover ordinary
classifier, posture, transition, bleed, and swing cases, but need explicit
zero/negative and boundary cases for `RPGClassifyAttack`, `RegenStep`,
`SweepTouches`, `RiposteGeometry`, `ResolveBreak`, `ResolveTransition`, and
bleed's ignored-result precedence and saturation behavior.

## Player — Stagger, Posture, and Phases

**Read:** `RPGBossStagger.h/.cpp` (256/915), `RPGBossPosture.h/.cpp`
(113/208), `RPGBossPhases.h/.cpp` (132/580), and
`RPGBossInterrupt.h/.cpp` (12/59): **2,275 lines**.

### A01 — synchronous asset loads occur at fight-state transitions

- **Severity:** latent performance / wrong behaviour on a frame-budgeted build.
- **Confidence:** confirmed by reading; actual hitch size is unmeasured.
- **Evidence:** `Source/OneBossFight/Player/RPGBossStagger.cpp:91-92` says
  `LoadedFall = FallClip.LoadSynchronous();` and
  `LoadedDown = DownClip.LoadSynchronous();`. The same component calls
  `RipostePlayerClip.LoadSynchronous()` and `RiposteBossClip.LoadSynchronous()`
  at `:549-550`. `Source/OneBossFight/Player/RPGBossPhases.cpp:266` loads the
  immunity effect synchronously, and `:296-297` loads the roar clip or montage
  synchronously as phase two begins.
- **Failure scenario:** on the first stance break, riposte, or 60-percent phase
  crossing after a streamed asset has been evicted, the game thread blocks
  loading the animation/effect package exactly when player response matters.
  That can break the Gate 4 p99 <= 16.67 ms target even though every gameplay
  state eventually completes.
- **Concrete fix:** preload the resident clips and immunity class once in
  `BeginPlay` (or request an async load and keep `TObjectPtr` strong references),
  then retain the existing fallback/log behaviour if preloading fails.

Aside from A01, **no defect found** in this group. The stance-break cleanup
routes reset through `EndStagger`, posture holds have explicit release/refill
paths, phase tick ordering explicitly depends on stagger, and delayed riposte
start checks its state before taking over input.

## Player — Hit Intake, Swing, Weapon Table, and Build Loadout

**Read:** `RPGHitIntake.h/.cpp` (134/424), `RPGSwingRules.h` (52),
`RPGSwingTracker.h/.cpp` (142/345), `RPGWeaponAttackTable.h/.cpp` (61/110),
`RPGBuildRules.h` (279), and `RPGBuildLoadout.h/.cpp` (183/831): **2,561
lines**.

**Result: no defect found.** The hit-intake delegate is unbound in `EndPlay`,
pending hit targets are weak, and the next-tick finalizer only retains component
state. Same-frame merge intentionally applies posture/bleed once while leaving
pack weapon damage alone. Build enum bytes are resolved from reflected enums,
the quickslot block is applied only while the boss is awake, and the retry state
does not spend an attempt for a single not-ready equipment call.

**Pure-rule coverage gap for Part B:** `RPGSwingRules` needs invalid-window,
inclusive-end, negative/empty-cost, zero stamina, and refresh-boundary cases.
`RPGBuildRules` needs parse whitespace/quotes/aliases, out-of-range build enum
clamping, `IsVerifying` boundaries, decision precedence, cyclic update choices,
lock truth-table coverage, and HUD descriptions/suffixes.

## Player — Dodge, I-frames, Death, Look, and HUD

**Read:** `RPGDodgeTiming.h/.cpp` (120/304), `RPGIFrameMonitor.h/.cpp`
(109/268), `RPGBossDeath.h/.cpp` (169/457), `RPGBossLook.h/.cpp` (72/175),
and `UI/RPGBossHud.h/.cpp` (181/459): **2,314 lines**.

**Result: no defect found.** The i-frame monitor distinguishes montage-owned
from foreign tags and cleans owned tags on reset/death. Death, look, and HUD
state uses transient strong references or weak actor references appropriately;
the boss HUD deliberately transfers its victory widget before destruction.
The HUD build line reflects the loadout's actual style rather than the requested
build. The dodge component’s input binding is pawn-owned and its active ability
cache is weak.

## Player — Bleed, Special Moves, Damage, Camera, Debug, Trace, and Wiring

**Read:** `RPGBossBleed.h/.cpp` (77/107), `RPGBossClips.h` (56),
`RPGBossDamage.h` (64), `RPGBossHealPunish.h/.cpp` (135/256),
`RPGBossJavelin.h/.cpp` (54/165), `RPGBossLowSweep.h/.cpp` (89/199),
`RPGBossShockwave.h/.cpp` (87/160), `RPGCameraRig.h/.cpp` (59/139),
`RPGCameraShakes.h/.cpp` (67/52), `RPGCombatDebug.h/.cpp` (82/513),
`RPGDamageResolver.h/.cpp` (164/203), `RPGLegend.h/.cpp` (202/500),
`RPGPlayerMovesSubsystem.h/.cpp` (26/257), `RPGRiposteInput.h/.cpp` (36/65),
`RPGTraceAudit.h/.cpp` (100/397), and `RPGTraceGuard.h/.cpp` (79/171):
**4,561 lines**.

**Result: no additional defect found.** Project-created javelins, sweeps, and
waves capture and compare encounter generation before damage resolves. The
damage resolver owns per-instance deduplication. Debug-only draw paths are
behind `!UE_BUILD_SHIPPING`; the trace guard explicitly precedes skeletal mesh
updates and closes the trace on interruption. The subsystem attaches the
components to pack actors without retaining raw cross-frame actor pointers.

## Boss

**Read:** `Boss/RPGSevarogDirector.h/.cpp` (106/479): **585 lines**.

### A02 — retired Sevarog director’s delayed lightning callback has no lifetime or generation guard

- **Severity:** latent wrong behaviour (currently unused component).
- **Confidence:** confirmed by reading; the component is marked unused in
  `Documentation/PROJECT_STATE.md`.
- **Evidence:** `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:82-88`
  creates a local `FTimerHandle` and queues
  `FTimerDelegate::CreateLambda([Effect, WeakWorld, Where]()`; the lambda only
  checks `Effect.IsValid()` and `WeakWorld.IsValid()` before
  `SpawnSystemAtLocation`. `ResetEncounter` does not retain or clear this
  timer, and this class has no encounter generation token.
- **Failure scenario:** if this retired director is reattached and the player
  resets during the calculated bolt delay, the old encounter’s delayed lambda
  still spawns a bolt effect at its old strike location after reset. It can also
  fire after the director owner has ended while the world remains valid.
- **Concrete fix:** do not re-enable the component unchanged. Store a timer
  handle and capture a weak director plus a reset generation; clear the timer
  in `ResetEncounter` and `EndPlay`, and check the token in the callback.

## Combat

**Read:** `Combat/RPGInputTestUtils.h/.cpp` (34/87),
`RPGMontageUtils.h/.cpp` (26/47), and `RPGSkeletonUtils.h/.cpp` (23/54):
**271 lines**.

**Result: no defect found.** Input injection is test-only, montage helpers do
not retain UObject pointers, and skeleton helpers use local reflection values.

## Audio

**Read:** `Audio/RPGArenaAmbience.h/.cpp` (30/37),
`RPGBossMusic.h/.cpp` (91/159), and `RPGFootsteps.h/.cpp` (75/121):
**513 lines**.

**Result: no defect found.** Audio delegates are removed, sound components are
transient, and debug visuals are shipping-guarded.

## Arena

**Read:** `Arena/RPGArenaDressing.h/.cpp`, `RPGEmberField.h/.cpp`,
`RPGFireSource.h/.cpp`, `RPGGreyboxArena.h/.cpp`, `RPGFogGate.h/.cpp`, and
`RPGVictoryLock.h/.cpp`: **1,108 lines**.

### A03 — arena presentation allocates transform arrays every gameplay frame

- **Severity:** unmeasured frame-time risk.
- **Confidence:** high for the allocation; performance impact requires the
  packaged target-hardware profile.
- **Evidence:** `Source/OneBossFight/Arena/RPGEmberField.cpp:100-109` enters
  `void ARPGEmberField::Tick(float DeltaSeconds)` and creates
  `TArray<FTransform> Transforms;` followed by
  `Transforms.Reserve(Embers.Num());`; the fresh array is uploaded by
  `BatchUpdateInstancesTransforms` at `:126`. In each swaying set,
  `Source/OneBossFight/Arena/RPGArenaDressing.cpp:85-100` enters its tick and
  creates `TArray<FTransform> Moved;` followed by
  `Moved.Reserve(Set.Rest.Num());`, then uploads it at `:111`.
- **Failure scenario:** a populated ember field and swaying dressing perform
  heap-backed transform-array allocation/copy work every rendered gameplay
  frame. Allocation churn and repeated render-state updates can worsen p99 on
  the RTX 2060 Super 60-FPS gate, especially with the fight and presentation
  active together.
- **Concrete fix:** keep scratch arrays as actor members and reset/reuse them,
  or move sway to material/instance data. Profile the packaged benchmark before
  accepting or prioritising the change.

No static correctness defect was found in fog-gate/victory-lock ordering or in
the defensive checks around missing arena components.

## Benchmark

**Read:** `Benchmark/RPGFrameStats.h/.cpp` and
`RPGBenchmarkRunner.h/.cpp`: **570 lines**.

### A04 — benchmark default is still the retired 120-FPS release gate

- **Severity:** high release-validation defect.
- **Confidence:** high.
- **Evidence:** `AGENTS.md:3` states `Target packaged 1080p / 60 FPS, p99 <=
  16.67 ms ... 120 FPS is stretch only`; `Documentation/DECISIONS.md:384`
  says `look first, 60 FPS is enough; the 150k triangle budget and the 120 FPS
  target no longer bind.` In contrast,
  `Source/OneBossFight/Benchmark/RPGBenchmarkRunner.h:79` sets
  `float TargetFPS = 120.f;`, `Source/OneBossFight/Benchmark/RPGFrameStats.h:9`
  says `Release target: average >= 120 FPS AND 99th-percentile frame time <=
  8.33 ms.`, and `:40` defaults `MeetsTarget(double TargetFPS = 120.0)`.
- **Failure scenario:** a normal benchmark run using defaults labels a
  60-FPS-release-compliant packaged build as failed, then records the wrong
  gate in `summary.json`. This can block or falsely characterise Gate 4.
- **Concrete fix:** change the defaults and comments to 60 FPS/16.67 ms, or
  require an explicit 60 target at every invocation and reject summaries that
  do not record it. This is **DISAGREES WITH CODE** because documented project
  policy is authoritative over the stale code default.

The percentile implementation, raw wall-clock sampling, uncapped/VSync
restoration paths, and JSON/CSV output were read. No additional static
correctness defect was found. The fight benchmark intentionally heals player
and boss (`RPGBenchmarkRunner.cpp:202`, `:212-223`), so it is appropriate for
a sustained performance envelope, not balance or soak claims.

## Tests and Core

**Read:** `Tests/RPGAutomationTests.cpp`, `Tests/RPGBuildTests.cpp`,
`OneBossFight.h`, and `OneBossFight.cpp`: **1,712 lines**.

Existing automation tests cover the principal happy paths for frame statistics,
posture, transition, attack classification, weapon rows, swing rules, bleed,
legend, arena, pack wiring, cook references, and build decisions. The static
coverage gaps recorded in the Player sections are boundary/precedence coverage,
not evidence that those behaviours are broken. Part B adds isolated header-only
regression tests for those edges without a world, asset, or pack Blueprint.

## Coverage and Findings

| Area | Static coverage | Finding |
|---|---:|---|
| Pack | 788 lines | None found |
| Player encounter/attack/rules | 1,105 lines | None found; pure-rule edge coverage gap |
| Player stagger/posture/phases | 2,275 lines | A01 synchronous first-use asset loads |
| Player hit/swing/table/build | 2,561 lines | None found; pure-rule edge coverage gap |
| Player dodge/iframe/death/look/HUD | 2,314 lines | None found |
| Player remaining systems | 4,561 lines | None found |
| Boss | 585 lines | A02 retired director delayed-effect lifetime |
| Combat | 271 lines | None found |
| Audio | 513 lines | None found |
| Arena | 1,108 lines | A03 transient tick allocations |
| Benchmark | 570 lines | A04 120-FPS release-gate mismatch |
| Tests/Core | 1,712 lines | Boundary additions planned in Part B |

The listed reviewed files total 18,363 physical lines. Sixty-three Player
source lines fall outside the explicit grouped list and were not claimed as
line-by-line coverage. No runtime, build, editor, package, or PIE validation
was performed for this audit.
