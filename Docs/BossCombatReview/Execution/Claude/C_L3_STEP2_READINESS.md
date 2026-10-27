# C-L3: step 2 promotion readiness review (Claude, implementer; REVIEW ONLY)

Date 2026-10-26. Scope: `Codex/PROMOTION_STEP2.md` (HOLD) against the live code of `Source/OneBossFight` as read today. Nothing applied, built or run for this note: it is a code reading. `PROMOTION_STEP2_SCAFFOLD.patch` and `PROMOTION_STEP3_SCAFFOLD.patch` stay unapplied.

## 1. What the live code does today (facts read from source)

- `URPGPlayerMovesSubsystem::IsPackBoss` (`Player/RPGPlayerMovesSubsystem.cpp:93`) is a class-name walk for `BP_ExampleGreatSwordBoss_C`. It is the single boss identity test.
- `URPGPlayerMovesSubsystem::Attach` (same file, from line 128) runs per pawn. Boss branch registers, in this exact order, with `NewObject` + `RegisterComponent` guarded by `FindComponentByClass`: footsteps, boss music, RPGBossStagger, RPGBossPhases, RPGBossEncounter, RPGBossDormantWake, RPGBossPosture, `URPGBossDeath::Attach(OwnClip)`, RPGBossLook, RPGBossBleed, RPGAttackTracker, RPGBossCloseClipSwap, RPGBossShockwave, RPGBossLowSweep, RPGBossHealPunish, `URPGDamageResolver::FindOrAdd`, RPGTraceGuard, RPGTraceAudit, RPGBossHud, RPGCombatDebug, RPGBossLegend (the comment on Legend says it polls tracker/phases/stagger/HUD, so it is deliberately last). The player branch (camera rig, riposte, dodge timing, swing tracker, hit intake, loadout, select, flask HUD, iframe monitor) shares the function.
- Boss components resolve each other by `FindComponentByClass` at use time (Phases -> Encounter/Stagger/Posture; Stagger -> Encounter/Phases/Posture; Encounter -> Death/Stagger/Phases/Posture/Bleed; Posture -> Encounter/Stagger; DormantWake -> Encounter; Death -> Stagger/Posture/Phases/Encounter). Mostly lazy, so strict order is not required between them, but the Legend-last and Death-before-Look order is a documented intent.
- Consumers that decide "the boss" through `IsPackBoss` plus an iterator or `GetAllActorsOfClass`, first match wins: `Arena/RPGFogGate.cpp:93`, `Player/RPGBuildLoadout.cpp:601`, `Player/RPGHitIntake.cpp:216` (watch list) and `:400` (target class test of every pack hit), `Player/RPGRiposteInput.cpp:61`, `UI/RPGBuildSelect.cpp:315`, `Benchmark/RPGBenchmarkRunner.cpp:218`. Several other boss components use `GetPlayerPawn(world, 0)` / `GetPlayerCharacter(.., 0)` for the target (RPGBenchmarkRunner, RPGAttackTracker, RPGBossEncounter, RPGBossHealPunish, RPGBossJavelin, RPGBossLowSweep, RPGBossPhases, RPGBossShockwave, RPGPackNotifies, RPGSevarogDirector).

## 2. Verdict on the HOLD

I agree with HOLD. The scaffold adds an API; the product needs a coordinator, adapters and consumer rewiring that do not exist. Applying the scaffold now would be inert and would give no parity evidence. The risk to the 40 drivers is NOT in the scaffold files but in the seam changes; so the promotion must be a sequence of small, individually gated steps, each leaving the shipped path byte-for-byte behaviour compatible.

## 3. Minimal integration sequence (each step: build, automation, targeted drivers, then one full gate at the end of 2d and of 2g)

2a. Apply the scaffold files only (3 new files). Build with `-Tests`; record discovered automation count. Nothing is wired. Gate: 41 + N automation, no driver run needed (no runtime path touched). Risk: UHT / non-editor compile of the lease types (Codex's own risk table).

2b. Pure refactor, no behaviour change: extract the boss branch of `Attach` into `AttachLegacyBossBundle(AActor*)` keeping the registration order above verbatim, and make `Attach` call it. Prove with the full gate that the output equals today's 39/40 (+KI-106 flake). This creates the single place the coordinator will later suppress.

2c. Coordinator, default OFF: a function `TryAttachBoundEncounter(AActor*)` called BEFORE `AttachLegacyBossBundle`. With an empty binding set it returns "not handled" and the legacy bundle runs. Whole-batch validation first, no partial fallback (suppress the legacy bundle only after the validated batch is accepted, as Codex states). Gate: automation for "empty records attach nothing and suppress nothing"; targeted drivers `pie_builds`, `pie_close_attacks`, `pie_boss_death` smoke.

2d. Typed config adapters, one component per commit, each reproducing the legacy constructor/field values exactly. Order of hazard: Encounter + Phases + Stagger + Posture first (cross-referenced), DormantWake second (WakeClip==0 and authored-wake paths both, per Codex), then Death/Look/Music/HUD, then Bleed/Shockwave/LowSweep/HealPunish/Javelin/Legend. Parity proof per component: legacy defaults vs adapter values compared in an automation test (a table of every UPROPERTY the constructor or `BeginPlay` reads), plus full gate after the last adapter.

2e. Boss01 definition + binding assets (needs owner/lead content scope; new assets only under a project path in the always-cook roots, see KI-084 CookCoverage). Do NOT attempt before 2d parity is green.

2f. Consumer rewiring, one file at a time, behind a facade `URPGEncounterBinding::ResolveBoss(World)` that returns exactly what `IsPackBoss` + first iterator returned when exactly one pack boss exists (legacy test facade, as Codex says). Order: FogGate, BuildSelect, BuildLoadout, RiposteInput, HitIntake (both sites: the watch list AND the per-hit target test at :400, which runs on every pack hit and must stay O(1)), BenchmarkRunner. Player-0 target consumers last (they are many; they need the associated-context target; do not change them before the lookup facade is proven).

2g. Reset/respawn/travel generation: the existing reset owner supplies the generation; deferred spawn before BeginPlay. Needs the real two-GI / travel proof (step 1 open conditions) first, because the generation number rides the epoch/world identity.

## 4. Ownership and order hazards (specific to this code)

H1. Two attachment triggers exist: `PostInitialize` (AddOnActorSpawnedHandler for spawned actors) and `OnWorldBeginPlay` (TActorIterator for actors already placed). A coordinator that runs "before the old calls" must be reachable from BOTH, and idempotent: `FindComponentByClass` guards make the legacy path idempotent today; the coordinator needs the same guard (a per-actor "bound" tag or the generation key), or an actor seen by both triggers is bound twice.
H2. Deferred spawn "before BeginPlay" (the scaffold's respawn transaction) contradicts the current non-deferred respawn path and the OnActorSpawned handler, which fires at spawn, i.e. components would be registered before `ConfigureBeforeRegistration` ran unless the handler is taught about the transaction. This is the main reason I would keep 2g last.
H3. Legend-last / Death-before-Look order must be preserved by the adapters. If the coordinator registers by plan order, the plan order must be the order in section 1 (a test: the component list order of the boss equals the legacy list).
H4. `IsPackBoss` at `RPGHitIntake.cpp:400` is on the hot path of every pack hit; replacing it by a lookup that scans bindings per hit would regress the p99 budget (16.67 ms). Cache the resolved target per generation.
H5. `GetPlayerPawn(0)` targets: with two simultaneous encounters (the whole point of step 2) every one of the ~10 boss components that reads player 0 will pick the same target. For step 2 acceptance with ONE boss this is invisible; the two-duel claim therefore cannot be accepted until those reads go through the context target. Keep the "two actual duels" claim out of step 2 acceptance, as Codex already says.
H6. KI-084: any new `/Game/...` literal (definition/binding asset paths) in Source or tests needs an always-cook directory or a split literal.
H7. Shipping: `URPGTraceAudit` is empty in Shipping and the catalog cvars are non-Shipping; the adapters must not make an observer or cvar part of the validated batch, or Shipping and Development bind different sets (provenance gap already open for step 1).
H8. Operational: every gate step needs the editor closed, a fresh editor for `RunDrivers.ps1`, and a post-run process-tree check; I am the only editor operator, so steps 2b..2g are strictly sequential and each takes roughly 90 minutes of gate time (the full gate after 2d and 2g only, targeted drivers in between).

## 5. Tests to add or require (against current code)

- Automation (editor-free): empty binding set suppresses nothing; whole-batch rejection leaves zero components; duplicate encounter ids; wrong-class actor; late component registration rejected; legacy-order equality (section 1 list, H3); idempotence for double trigger (H1); no strong-lease dereference after owner invalidation (Codex table).
- Driver additions (existing harness, no arena preset changes): after 2d, a driver that records the boss component class list in order and compares to the legacy list; after 2f, a driver that measures the facade lookup cost (per-hit time unchanged) and checks FogGate/Select/Loadout/Riposte/Intake/Benchmark all find the same boss as before.
- Full gate parity: 40 drivers + automation, same known flake (KI-106) only.

## 6. Ready now / not ready

READY now: 2a (scaffold files, inert) and 2b (pure refactor) can start on the lead's word. Both are low risk and give the extraction point. NOT ready: 2c needs the empty-set decision in H1; 2d needs the per-component field tables; 2e needs content scope; 2g needs the two-GI/travel evidence.

Questions for the lead: (1) release 2a+2b as the first promotion block? (2) who writes the per-component field tables for 2d (they are a mechanical reading of the 12 components: I can draft them)? (3) is "two actual duels" explicitly outside step 2 acceptance (H5)?
