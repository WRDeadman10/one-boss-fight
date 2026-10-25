# D07 v3 — code-level DD-1 steps 2/3 plan (WP-3)

2026-10-25, Codex. DESIGN ONLY, not implemented. Retains D07 original/v2 contracts except refinements here. Step1 is now authored by Codex, reviewed/built by Claude; its source is not accepted by this design. Step2 starts only after step1's actual baseline/parity/build acceptance. No pack/asset/script writes for step2/3 are authorized here.

## Assumptions

An explicit project-owned level binding holds actor refs; immutable data assets hold participant slot IDs, not universal pointers to level actors. The existing player pawn remains pack-managed; hydration cannot reorder its startup writes. Legacy state owners remain authoritative in DD-1. Reversal is previous complete startup binding plus owned preimages; no mid-fight rebinding. The listed API names are proposed new project APIs, not claims of existing engine methods.

## Step2 classes, signatures and records

```cpp
struct FRPGContentKey { FGuid LocalEpoch; FString StableManifestHash; int32 Schema; };
struct FRPGParticipantKey { FGuid WorldSession, EncounterInstance; FName Slot; uint32 Generation; };
struct FRPGHydrationResult { bool bReady; TArray<FString> Errors, Dependencies; };
struct FRPGParticipantConfig {
  FName BossId, PresentationId; FRPGContentKey Content;
  FRPGBossStats Stats; TArray<FRPGPhaseConfig> Phases;
  FRPGLifecycleConfig Life; FRPGPostureConfig Posture;
  FRPGStaggerConfig Stagger; FRPGRiposteConfig Riposte; FRPGBleedConfig Bleed;
  FRPGPresentationConfig Presentation; TArray<FRPGMoveCompatibility> Moves;
};
class URPGCombatParticipant : public UActorComponent {
  FRPGHydrationResult ConfigureBeforeRegistration(
    TSharedRef<const FRPGParticipantConfig>, const FRPGParticipantKey&,
    URPGCombatContextSubsystem&);
  const FRPGParticipantKey& Key() const;
  bool IsReady() const;
};
class ARPGEncounterBinding : public AActor {
  // serialized project level actor; explicit participant and gate refs, typed soft definition IDs
  TArray<FRPGPlacedParticipantBinding> Participants;
  FRPGHydrationResult ValidateBindings(const FRPGCombatEpoch&) const;
};
class URPGCombatContextSubsystem : public UWorldSubsystem {
  FRPGHydrationResult BindEncounter(const ARPGEncounterBinding&);
  TOptional<FRPGParticipantKey> FindParticipant(const AActor&) const;
  URPGBossEncounter* ResolveEncounter(const AActor& Requester) const;
  AActor* ResolveTarget(const FRPGParticipantKey&, FName TargetSlot) const;
  bool IsCurrent(const FRPGParticipantKey&) const;
  void OnGenerationChanged(AActor&, uint32 NewGeneration);
  void UnbindActor(AActor&, EEndPlayReason::Type);
};
namespace RPGCombatHydration {
  FRPGHydrationResult CompileParticipant(const FRPGBossDefinitionValue&,
    const FRPGEncounterDefinitionValue&, const FRPGPresentationValue&,
    const RPGCombatRegistry::FEpoch&, FRPGParticipantConfig& Out);
  FRPGHydrationResult CreateConfigureRegister(AActor&,
    TSharedRef<const FRPGParticipantConfig>, URPGCombatContextSubsystem&);
}
```

Names `FRPGCombatEpoch` in design prose map to step1's `RPGCombatRegistry::FEpoch`; do not create another global registry. Extend FEpoch with value-copied definition records and per-instance strong dependency leases as needed. Local Guid identifies context only; StableManifestHash identifies shared content across clients. All runtime config fields are const after activation. Runtime HP/posture/phase/cooldown/history/targets/trace sets remain owned once, not placed on definitions or copied into a second mutable mirror.

Data assets: URPGBossDefinition, URPGEncounterDefinition, URPGPresentationDefinition (D02 field groups), each Schema/DefinitionId plus nested structs. URPGBossMoveDefinition/variant manifests are introduced for step3. A config compile gathers type/reference/skeleton/cook dependencies and errors with field paths; missing required definition blocks full publication, never Boss01 substitution. Optional look/icon/music fallbacks remain explicitly the original choices. No client role may make itself authoritative by choosing a definition.

### Exact integration seams and lifecycle order

| Current hook | Proposed change in step2 | Behavior to preserve |
|---|---|---|
| RPGPlayerMovesSubsystem::PostInitialize / OnActorSpawned / OnWorldBeginPlay | Subscribe to explicit binding readiness; call context.BindEncounter once; Attach becomes AttachBoundParticipant(actor,key,config) | Existing placed and late-spawn coverage; unbound pack mobs untouched |
| IsPackBoss / Attach (cpp:93/143+) | Combat identity from context.FindParticipant; old helper only diagnostics/legacy explicit binding adapter | Never classify all same-class enemies as arena boss |
| Attach's immediate NewObject->RegisterComponent paths | Allocate known components unregistered, Configure* for every component, then register in pinned order | BeginPlay cannot consume constructor Boss01 defaults; no duplicate delegates/components |
| RPGBossEncounter::BeginPlay (cpp:66+) | Requires ready participant key/config; home/gate/reset values copied BEFORE register; initial Sleep still same point | Existing0.1s poll, delayed pack HP write/readiness and sleep/wake semantics unchanged |
| Encounter::ResetEncounter | Existing reset remains sole gameplay authority; after its generation increment notify context.OnGenerationChanged | Exactly one generation increment, stale handles invalid, no duplicate health/phase/reset work |
| Encounter::EndPlay / actor destroy | UnbindActor and invalidate pending diagnostic work | No teardown of another actor/world/context |
| BuildLoadout/BuildSelect/HitIntake/RiposteInput/FogGate first-boss searches | ResolveEncounter(requester) or explicit hit target's participant key | Actual association, no actor iteration ambiguity, unchanged single duel outcome |
| Look/music/phase/death/stagger component BeginPlay | Configure typed snapshot before RegisterComponent; required asset leases already retained | Same fallback clips, reverse getup, death mode, attachment transforms and audio |

Registration algorithm: validate all bindings/dependencies -> allocate context and unregistered components -> hydrate all scalar/reference config -> verify no pre-existing registered consumer read defaults -> register in a recorded dependency order -> bind callbacks once -> enable existing poll/tick at the same intended start. A pre-existing component that already consumed defaults is a hard hydration error, not an excuse for post-BeginPlay patching. For spawned actors use an explicitly proven deferred-spawn/config-before-finish route or a project actor bridge; OnActorSpawned by itself is NOT proof of pre-BeginPlay ordering.

Do not introduce a generic pause barrier that delays the boss to conceal ordering differences. Pack controller/ability startup continues unchanged. If this cannot be achieved without a behavior change, report the precise editor trace/owner scope needed and retain the old path until resolved. A G3 scratch override is PIE temporary only; saved arena changes need an exact map claim/preimage, never implied scratch approval.

Tick order: content owner initializes before any consumer resolves epoch; hydration has no repeated gameplay tick. Encounter keeps existing0.1s cadence, tracker keeps existing per-frame tick and notify owner order. New context registry is event-driven for actor/generation changes. Deferred dependency readiness uses existing baseline retry windows, not an invented delay. A compile/load failure leaves the native stack unactivated and diagnostic, never a partially configured attacker.

### Field-source parity manifest

One JSON record per destination field, mandatory fields:

`schema, run_id, definition_id, field_path, type, units, source_path, source_line_or_asset_property, source_sha256, baseline_effective_value, value_origin(default|instance|cvar|harness), precedence, destination_class, destination_property_or_constructor_binding, first_read_site, configure_order, register_order, optional_policy, loaded_dependency_ids, comparison, witness, limitation`.

Example seeds (all values require current pin/readback before import):

| Field | Current source | Copy rule / witness |
|---|---|---|
| Stats.MaxHealth | Encounter MaxHealth + startup retry |2000 pinned effective boss value; record transient pack overwrite separately; dormant wake/reset |
| Posture.Max/RegenDelay/RegenRate | RPGBossPosture.h defaults |100/6/13 preserved; posture_hits/regen/reset |
| Phase[1].Entry/Modifiers | RPGBossPhases.h |0.60 HP, speed/rate1.2, attack1.25; once/reset, no repeated multiplication |
| Move.A4.Query | RPGBossLowSweep.h + E008 |inner60/outer380/height40/+90..-90; no mesh-tip repair |
| Move.A5.CompatibilityRelease | RPGAttackTracker constructor |0.45 nominal;0.47 observed E007, NOT sidecar0.40 |
| Stagger.GetupVariant | RPGBossStagger implementation |Fall reversed at existing rate; not standalone authored GetUp file |
| Presentation.Sword | RPGBossLook + live E008 |current scale1.5/attachment; tested sockets absent, no claim zero total count |
| Encounter.Home/EnemyInfo | placed arena instance |instance override wins over pack CDO; no saved scratch mutation |

A header/property inventory is insufficient: include constructor constants, computed overrides, retry timings, hardcoded labels and each currently loaded path. Manifest records values, provenance and first use; it does not auto-accept intended sidecar values or normalize discrepancies away.

## Step3 classes and signatures

```cpp
struct FRPGTimelineKey { FName MoveId, VariantId; FString AssetHash, AdapterHash;
  FName Slot, Section; int32 Schema; FRPGSegmentMap Segments; };
struct FRPGWindow { FName Id, Semantic; double BeginAnimSec, EndAnimSec;
  FString SourceObjectPath, PayloadHash; };
struct FRPGMarker { FName Id, Semantic; double AnimSec; FString Provenance; };
struct FRPGCompiledTimeline { FRPGTimelineKey Key; TArray<FRPGWindow> Windows;
  TArray<FRPGMarker> Markers; TArray<FRPGDiagnostic> Diagnostics; };
struct FRPGPlaybackObservation { FRPGParticipantKey Participant; uint64 Ordinal;
  FName MoveId, VariantId, Section; double PreviousPos, CurrentPos, GameTime;
  float ActualRate; ERPGTraversalKind Traversal; uint32 LoopOrdinal;
  TOptional<uint64> EngineInstance; TOptional<FRPGAuthoritativeActionKey> Action;
  FRPGLegacyTrackerSample Tracker; EObservedStop StopReason; };
class FRPGTimelineCompiler {
  TResult<TSharedRef<const FRPGCompiledTimeline>, FRPGCompileErrors>
    Compile(const FRPGMoveVariantValue&, const FRPGNotifyExport&, const FRPGCompilePolicy&);
};
class FRPGTimelineCursor {
  TArray<FRPGShadowCrossing> Advance(const FRPGCompiledTimeline&, const FRPGPlaybackObservation&);
  void Close(EObservedStop);
};
class URPGCombatTimelineShadow : public UActorComponent {
  void Configure(TSharedRef<const FRPGCompiledTimelineSet>, const FRPGParticipantKey&);
  void ObserveAfterTracker(const FRPGPlaybackObservation&);
  void FlushReport(FRPGShadowReportSink&);
};
```

No TResult engine API is assumed: the implementation can use an explicit result struct with optional value/errors; this is a project API signature plan. Time domains have explicit units; absence is TOptional/null, never0.0 standing in for missing metadata. Artifact cache immutable, cursor per actor/generation; strong leases pin source objects, weak actor refs invalidate stale callbacks. No shadow cursor owns gameplay effect/trace/input/motion/ability resources.

### Exact tracker hook, with zero gameplay authority

Add `FRPGLegacyTrackerSample GetObservationSnapshot() const` and a bounded Development-only observation delegate at the END of each current Tick path, including early stop/death/INDEX_NONE/veto/branch-denial returns. Prefer a scope-exit snapshot emitter so early returns aren't omitted. It copies current montage/source/section/position, phase/index/currentmove/instance/counters and observed stop reason. Same-asset restart must be observed using engine montage instance when exposed; if not available, label restart identity uncertain rather than guessing from index. No hook changes ordering, doubles Tick, makes a new attack request or writes montage state.

Shadow consumes this copied sample after the tracker in the same game tick through a delegate, not a second polling tick that might sample a different animation pose. A separate passive playback observation is required for Mid01/sprint/retaliation because native tracker returns INDEX_NONE; it records engine metadata and nullable native stage, never fabricates a tracker identity. Exact read-only animation APIs/instance visibility are a Claude editor/header verification item before code claims. G4/G5 remain denied.

Compiler reads existing live notify export or preloaded animation metadata; it never saves notifies/pack montages. Forward `(prev,current]` crossings include both ends of fully skipped windows; initial0 marker handled once; stable ordering for ties. Reverse/loop/restart/section jump are explicit traversal kinds. Unknown jump path becomes inconclusive; no “all skipped markers fired.” Stop/replacement/reset closes diagnostic cursor exactly once without touching a production watchdog. The current tracker may skip Active on a hitch; shadow reports expected-difference/regression candidate, never fixes it in DD-1.

### Shadow report wire format

Header JSON: `schema, run_id, command, source_manifest, dll_hash, map, engine_plugin_ids, requested_source, published_source, content_hash, local_epoch, session_world_ids, net_mode_role, cvars_start/end, presets, log_verbosity, window_state, game_sample_dt, slate_sample_dt, validity, dropped_records, assets/scripts_before/after`.

Playback JSONL: `participant_key, generation, observation_ordinal, authoritative_action(nullable), target/phase/server_time(nullable), source_asset/variant/section, previous/current positions, rate, traversal/loop, legacy_snapshot, compiled_crossings, declared_intent_ref, measured_extraction_ref, engine_timeline_ref, approved_runtime_ref(nullable), expected_difference_id, comparison_status, measured_delta, tolerance_rule, raw_path/line/times, limitation`.

Statuses: MATCH, EXPECTED_LEGACY_ENGINE_DIFFERENCE, UNTRACKED_PACK_PATH, REGRESSION_CANDIDATE, INCONCLUSIVE_SAMPLING, MISSING_METADATA, INVALID_RUN. Zero samples is uncovered, not MATCH. Expected mismatch IDs:

- A2_ENGINE_VS_TRACKER_WINDOWS: two engine collision intervals, tracker only1.93-2.11; keep both.
- A2_OBSERVED_EARLY_TERMINATION: nine Windup cuts/one Active/one Recovery replacement in frozen six-fight sample; T4 persistence about1.388s; replay these observations, never assert future10/11 or force cancellations.
- PACK_UNTRACKED: Mid01/sprint/retaliation missing tracker semantics; natural occurrence not guaranteed by a short run.
- A4_QUERY_VS_BOUNDS_ENDPOINT: production planar query retained; E008 point is an estimate, circular angular error51..174, capsule bottom not measured floor. No visual geometry pass from numeric data.
- A5_INTENT_VS_COMPAT_RELEASE: sidecar0.40 intent versus nominal0.45/first-sampled0.47; no retime.
- FALLBACK_ALIAS_TIMELINE: authored and fallback variants may map to an old shared row; retain true per-variant metadata and report mismatch.

Record actual config per run: natural wake/telegraph differs from driver mode; B warm0/0. Minimized ~3fps timing evidence invalid for its temporal assertions, not for a static path inventory. Cold/new-catalog load and compilation cannot occur on a hit/phase release tick. Comparison disabled leaves no gameplay dependency; enabled logging is bounded and reports dropped observations.

## Step2/3 test plan and implementation units

Step2: new Player/RPGCombatParticipant.*, RPGEncounterBinding.*, RPGCombatContextSubsystem.*, boss/encounter/presentation definition files; narrow configure methods on existing compatibility components and consumer lookup replacements. Unit tests: schema/duplicate/unbound/foreign-world/ambiguous-context/missing-required/dependency errors; three-build epoch compatibility; two participants sharing one definition. PIE: placed-before-start, late/deferred spawn, pre-existing registered consumer rejection, first-read ordering, repeat attach, existing delayed pack HP write, reset twice, simultaneous instances, GC/travel/teardown, actual HUD/music/look/camera/fog association. Existing full gate and focused parity counts retained.

Step3: new RPGCombatTimeline.*, RPGCombatTimelineShadow.*, compiler and cursor tests; tracker observation seam only. Unit tests: disjoint windows, exact endpoints, fully crossed window on hitch, duplicate sample, start0, reverse, loops, section maps/jumps, same-asset restart, stop/reset/destroy/stale generation, missing metadata, hash invalidation and bounded logging. Synthetic frozen trace replay is labeled synthetic. PIE: on/off observer produces identical actual hit/release/state/counters/rotation; untracked playback remains untracked, actual variants/cvars recorded, no asset load on hit. New-content canary and network end-to-end remain later phase proof.

## Evidence, limits, next

Source hooks above inspected in subsystem attachment, Encounter BeginPlay/reset and Tracker Tick. No code from this design implemented, no new engine API asserted tested. Every exact existing file claim, unsafe lifecycle need or map edit must be reviewed before step2. Authority seams start now, phase-specific multiplayer proof grows with P1-P7; P8 is integrated acceptance, not first networking. Claude reviews this specification after step1, not instead of step1 acceptance.
