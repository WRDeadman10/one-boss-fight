# Player subsystem attachment guide (S157)

This guide describes the legacy Advanced ARPG Combat pack attachment path. The subsystem adds components to actors by class-name ancestry, and call order matters because registered components can begin play immediately when added to an actor that is already playing.

## When attachment runs

`URPGPlayerMovesSubsystem` exists only for game worlds. In `PostInitialize`, it registers an actor-spawn callback. `OnWorldBeginPlay` calls its superclass, then walks the pawns already in the world and attaches to each. Actors spawned later are attached by the callback. Thus the same `Attach` function handles placed/preexisting pawns and runtime spawns (`RPGPlayerMovesSubsystem.cpp:42-80`).

## Actor recognition and idempotence

The subsystem walks each actor class and its parents, looking for the exact Blueprint-generated class names `BP_CombatPlayerCharacter_C` or `BP_ExampleGreatSwordBoss_C` (`RPGPlayerMovesSubsystem.cpp:83-105`). This is name-based recognition, not a native C++ base-class check. Normal component registrations are guarded by `FindComponentByClass`, so repeated visits do not add a second instance (`RPGPlayerMovesSubsystem.cpp:164-250,265-302`).

`Attach` gives the player branch precedence: a pack player gets footsteps; otherwise a pack boss gets boss footsteps and the music prelude. The player component set is then considered, and the legacy boss bundle is invoked last. A hypothetical class matching both names follows the player side of the initial `if/else if`, while boss-bundle statements still test `IsPackBoss` individually (`RPGPlayerMovesSubsystem.cpp:140-162,254-303`).

## Registration order

The player branch attaches pack footsteps before the main sequence. Its main components register in this order: camera rig, riposte input, dodge timing, parry, swing tracker, hit intake, build loadout, build selector, flask HUD, and iframe monitor (`RPGPlayerMovesSubsystem.cpp:254-302`).

For a recognized pack boss, footsteps and boss music are the prelude. The later guarded bundle order is stagger, phases, encounter, dormant wake, posture, death, look, bleed, attack tracker, close clip swap, shockwave, low sweep, heal punish, damage resolver, trace guard, trace audit, boss HUD, combat debug, and legend (`RPGPlayerMovesSubsystem.cpp:142-157,162-250,303`). Not every entry has the same guard: most are individually find-or-add; death uses `URPGBossDeath::Attach`, and the resolver uses `FindOrAdd` (`RPGPlayerMovesSubsystem.cpp:188-190,224-234`).

## Input readiness timing

The parry component is registered with the pack-player group, then tries to bind during its `BeginPlay`. Its `TryBind` requires both an `APawn` owner with an installed `UEnhancedInputComponent` and the loaded `IA_Parry` action. If either is missing it returns false. The component ticks and retries until binding succeeds; after success it binds `ETriggerEvent::Started` (`RPGPlayerParry.cpp:17-60`). Component registration therefore does not mean the input action is already bound. The retry handles the pack pawn's input component being created after component `BeginPlay`; this guide makes no claim about the exact frame or successful binding in every controller setup.

## Framework proof boundary

The native `ARPGFrameworkBossCharacter` is not a recognized legacy pack boss: `IsPackBoss` only looks for `BP_ExampleGreatSwordBoss_C` in its ancestry. The proof fixture spawns the native framework boss directly (`RPGPlayerMovesSubsystem.cpp:96-105`; `RPGFrameworkProofFixture.cpp:48,87`). The framework boss owns its own native executor/profile path and is not populated with the legacy boss component bundle by this subsystem. A framework proof target can still be a pack player: the profile target pawn class defaults to `BP_CombatPlayerCharacter_C` (`RPGFrameworkRuntimeTests.cpp:24`). Therefore pack-player attachments may be present on the target pawn while the native framework boss remains on the separate framework path.

## Evidence limit

The citations establish source-level class matching, call order, guards, and parry binding retries. They do not establish which actors were present in a particular packaged level, whether expected assets loaded, or when a live controller installed its input component. Those require runtime evidence.
