# WP8 — isolated step 2 draft

2026-10-25. NOT BUILT / NOT RUN. Draft core, **not an integrated replacement** for the current attachment path. X118 claim; mirrored code in `Codex/Drafts/Source/OneBossFight/Player/RPGEncounterBinding.*` stays outside UBT discovery until Claude promotes it. No live source, map, asset or startup behaviour changed.

## Assumptions

Explicit placed actor references are the binding authority. No class-name search, first-actor fallback or Boss01 substitution exists in this draft. A content snapshot retains the same GI epoch; world/session/encounter/slot/generation identity lives in a world subsystem. Stable content digest is supplied by the offline manifest producer, not generated from a random session Guid. Draft digest validation is structural, not a trusted provenance attestation.

The strict pre-BeginPlay requirement deliberately rejects late non-deferred spawns and any already attached consumer. It must not silently retrofit live actors. Binding and configuration happen while the actor is not begun; the caller must schedule the whole batch before starting play. Callback adapters are native, reviewed code: no arbitrary property ImportText or Blueprint execution from the manifest. The manifest carries records; it does not itself hydrate private constants.

C119 update: production compilation now loads and strongly leases explicit skeleton/animation references, rejects missing or mismatched animation skeletons; BindEncounter checks actual participant mesh compatibility and matching GI content epoch/explicit definition. This is a conservative supported-skeleton gate, not proof of vertex deformation/retargeting/foot/weapon geometry. Synthetic plain-actor factory is automation-only and explicitly labeled, not an asset-authored bypass. Full dependent cook/pose and retargeted canary readback still belongs to Claude's evidence gate.

## Implemented draft and D07 coverage

| Contract | Draft symbol | State / boundary |
|---|---|---|
| immutable metadata / GI epoch lease | FRPGParticipantConfig; CompileParticipant | Value-copy stats/phases/field provenance, shared const content. Lifecycle/stagger/riposte/bleed/presentation/move typed records still need expansion; not claimed complete D02 schema |
| atomic binding validation | BindEncounter | Validates whole encounter before publishing records; duplicates, cross-world, late actors, missing explicit targets/configs rejected |
| pre-registration hydration | CreateConfigureRegister | All plans validated, all components allocated/configured before any register; strong leases protect temporary components; rejects existing consumers |
| no second mutable gameplay owner | FRecord | Stores identity/config/readiness only, not HP/posture/phase/attack/cooldown mirrors |
| associated resolution | ResolveTarget / ResolveEncounter | Requester association and exact encounter slot, no actor iterator |
| reset generation / teardown | OnGenerationChanged / UnbindActor / Deinitialize | Updates whole encounter keys once supplied by existing reset owner; stale handles rejected; unbind invalidates entire affected encounter only |
| reflection | reflected definition, explicit binding actor, subsystem | No reflected shared pointers, TFunction or optional native types |
| private/constructor parity | FRPGParityField + RequiredFields | Presence validation only. Completeness against D01 and actual values is NOT proved by this transport |

## Integration seams — not applied

1. `RPGPlayerMovesSubsystem.cpp` PostInitialize/OnWorldBeginPlay/OnActorSpawned and Attach: replace **boss** attachment only after explicit binding readiness, not merely its IsPackBoss predicate. Existing player and unbound pack mob behaviour stays unchanged. Context must initialize before this subscription. Existing loop cannot run ahead of hydration. Deferred spawning requires a proven route before FinishSpawning, not an assumption about OnActorSpawned.
2. `RPGBossEncounter.cpp` BeginPlay must require hydrated participant, and ResetEncounter must notify context immediately after its existing Generation increment. Do NOT increment generation in the context independently or replace its reset/health authority. Existing delayed 2000 HP enforcement remains unchanged, including the pack overwrite.
3. Replace actual first-boss consumers: `RPGHitIntake.cpp:214/400` (actual target eligibility plus association), `RPGRiposteInput.cpp:59`, `RPGBuildLoadout.cpp:590`, `UI/RPGBuildSelect.cpp:313`, `Arena/RPGFogGate.cpp:91`. These line numbers were read from the current files; no edits. Local player0 and boss-global assumptions elsewhere still require closure before claiming two real duels.
4. Typed adapters must cover **every** D01 scalar/path/constructor/private first read, including look/music/death/stagger/bleed/specials/trace/HUD and phase ability prefix, not just the four stat fields. Readiness must be published for the complete batch before actual gameplay BeginPlay. No native component may fall back to hardcoded Boss01 data in strict mode.

EDITOR NEEDED: a recorded placed/deferred lifecycle trace showing the bind/configure/register/BeginPlay order and all consumer first reads, plus instance EnemyInfo precedence. This is required to promote the seams, not evidence that the existing source is broken. Current draft cannot safely replace all attachment without these adapters and traces. Registration callbacks are not a rollback transaction; failure poisons the context and is reported, never claimed to undo gameplay side effects.

## D06/D08 checklist

D06 R1 identity/ability counts retained (no grant edits); R2 baseline source/binary identity remains Claude's gate; R3 animation/sidecar domains untouched; R4 origin/instance precedence recorded but importer pending; R5 clean baseline failures classified in C112-C114, no guessed contamination; R6 no acceptance by missing report. D08 strict data publication stays step1's responsibility; fourth-build shared-weapon limitation unchanged; no row/layout/equip or pack edits in this package. D07 full private-field migration, manifest completeness and consumer rewiring remain OPEN rather than marked implemented by scaffold.

## Claude commands and API ledger

After step1 is accepted, review/promote only the agreed draft paths and integration patches, then (editor closed) `powershell -ExecutionPolicy Bypass -File Scripts/Rebuild.ps1 -Tests`. **Do not copy drafts wholesale into live Source during the step1 gate.** Run `Scripts/RunDrivers.ps1` full gate after actual integration. WP10 supplies focused driver/test contracts. No engine command run by Codex.

Engine headers read: `Components/ActorComponent.h` (RegisterComponent, IsRegistered, HasBegunPlay, DestroyComponent), `GameFramework/Actor.h` (HasActorBegunPlay, FindComponentByClass, GetComponents), `Engine/World.h` (world context), `Subsystems/WorldSubsystem.h` (world owner/lifecycle), `UObject/StrongObjectPtr.h` (temporary GC leases). Core containers/FGuid/TSharedPtr are native, not reflected fields. Remaining module/ABI review is WP11; headers alone are not a build pass.
