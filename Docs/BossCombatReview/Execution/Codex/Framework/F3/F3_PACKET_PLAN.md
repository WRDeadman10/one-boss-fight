# F3 packet plan — C375, design only

No runtime code, authoring script, map, Data Asset, build or engine operation is included in this delivery. F2 verification is frozen in F2/run_C375. This is the requested concrete files/release plan for review. No damage in F3; F4 owns contact resolution and the single Sevarog life/generation integration. C372 approves NEW project-owned assets and this proof-map name, not overwriting existing assets or changing shipped startup settings.

## Proposed ownership and exact file list

All names below are PROPOSED, absent destinations to recheck before staging. Headers first in every cpp.

| New Source files (pair unless noted) | Responsibility |
|---|---|
| Player/RPGBossFrameworkProfile.h/.cpp | Data Asset descriptor: explicit mesh, skeleton, AnimBP generated class, MoveCard, target pawn class, movement band/speed/acceptance, transform offsets, playback blend values and observation timeout. Validate all dependencies/scalars before runtime publication; zero draft invalid. No arbitrary substitute profile. |
| Boss/RPGFrameworkBossCharacter.h/.cpp | ACharacter with its own Sevarog capsule/mesh/CharacterMovement, explicit Initialize(profile,target,encounter,generation). No pack boss BP/BT/GAS/legacy boss consumers; starts disabled. Own default executor subobject. |
| Boss/RPGFrameworkBossController.h/.cpp | AAIController + walking facade, no behavior tree. Own one request ID; project authored goal to navmesh, require complete path (no partial path success), move into authored band, stop on arrival/commit/abort/failure. |
| Boss/RPGFrameworkMoveExecutor.h/.cpp | UActorComponent owning ONE noncopyable FRPGBossMoveModel and one owned dynamic montage; resolved card gate, observed animation clock, events/logging, idempotent stop and callback generation guards. |
| Boss/RPGFrameworkProofFixture.h/.cpp | Proof-only coordinator and local proof game mode: explicit spawned boss and actual pack gameplay pawn pointers. Player-target publication through the proof game mode possession callback, not player0/search by class. Disabled outside an explicitly initialized proof fixture. No live arena hook. |
| Editor/RPGFrameworkProofAuthoring.h/.cpp | Reviewed editor authoring helper for new level/nav bounds only where Python needs native brush construction; no engine-private reflection tricks. Existing UnrealEd dependency already present under WITH_EDITOR. If verified public Python APIs suffice, OMIT this pair at the source release. |
| Tests/RPGFrameworkRuntimeTests.cpp | Isolated dependency/lifecycle/refusal/cleanup tests, positive resolved asset control, stale callbacks, observed-clock tests, no-damage observer. Names/count specified with actual staged source. |

Existing Source delta proposed for separate review: OneBossFight.Build.cs add NavigationSystem module (AIModule/GameplayTasks/Engine already present); RPGBossMoveModel.h/.cpp and its tests ONLY if the observed-time seam below is approved. Add Event::Kind safe default when touching that header, as C375 requested. No current native Stats/Phase/Stagger/Encounter/PlayerMoves consumer or legacy 12-plan compiler edits. No framework field inserted into the old native preflight.

New offline staged files after source release: Framework/F3/Staging/Authoring/create_framework_proof.py and Framework/F3/Staging/Drivers/probe_framework_move.py; narrow pre/post/lock/one-use launch controls. They remain offline until reviewed promotion/execution. No existing Scripts edit.

## Actual dependencies and verification gates

Pinned disk candidates (C375_SOURCE_AND_ASSET_PINS.json, SHA256 and reopened engine source citations):
- Mesh `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog`.
- Skeleton same directory `Sevarog_Skeleton.Sevarog_Skeleton`.
- AnimBP `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C`.
- Sequence `.../Animations/Swing1_Slow.Swing1_Slow`, inventory line101: length1.7000000477s/rootmotionfalse/zero notifies; FPS UNKNOWN. Do not derive FPS from reported frame count.
- A241 reports Skeleton slot FullBody, actual Sevarog AnimBP FullBody graph node, and existing Swing1_Medium montage FullBody. Treat that as OFFLINE CANDIDATE input, not measured output-pose proof. Existing source montage is only a read-only control, never edited or played as a substitute for our card.
- Socket/bone candidates weapon_r / root_weapon_end_r from A241. F3 must load mesh and verify both exist and are distinct transforms; not a verified damage geometry/hammer alignment. Choose a different pair only through an explicit reviewed asset inspection delta. No traces/damage in F3.

Before an execute release: a read-only editor inspection must show actual object classes, skeleton equality, generated AnimBP class, compiled graph SlotName FullBody, and chosen socket/bone transforms. Freeze raw evidence and dependency hashes. IsSlotActive alone is NOT slot-node proof (AnimInstance.cpp:2281 checks active montage evaluation data). At runtime require nonzero node/global contribution after blend-in and advancing pose; use AnimInstance.h:400/407 GetSlotNodeGlobalWeight/GetSlotMontageGlobalWeight plus socket/bone observations and rendered evidence. A returned montage pointer or IsPlayingSlotAnimation alone is not visible pose proof. Failure keeps boss inactive and reports, never tries DefaultSlot/another AnimBP/pack ability.

Profile resolution occurs explicitly before activation. CompileResolved receives already-loaded exact assets and retains leases. Executor independently requires HasResolvedAssets()==true BEFORE any montage/playback call; metadata-only previews are refused and tested. No implicit load/default substitution in executor. These leases still do not make referenced UObjects externally immutable; freeze asset SHA and require scope ownership/no external writes during proof.

## Animation time seam requiring lead choice

F2 Advance currently takes wall-clock deltas and scales by authored rate (MoveModel.cpp:Advance); actual animation may pause/blend/stop independently. Feeding normal world time into model while montage stalls would report false windows. Proposed narrow reviewed extension: `AdvanceObservedLocal(token, montageLocalSeconds, events,error)` uses the same crossing kernel, rejects reversed/nonfinite time and stale tokens, and makes actual owned Montage_GetPosition authoritative for runtime edges. Preserve and regression-test F2 wall-clock Advance semantics unchanged; do NOT silently reinterpret its units or round/retime the card. ObservedLocal and wall-clock mode cannot mix during one attack. This adds a named clock-mode gate and tests. Alternatives need explicit lead decision before code; recommended = observed-local seam.

Per anim-update ordering, execute observation AFTER skeletal mesh animation evaluation (explicit tick prerequisite). Keep owned montage pointer, check Montage_IsPlaying/position before advancing, and compare blend-out/completion callbacks with attack+generation+montage identity. Early stop/interruption = abort/close; no fabricated successful completion. Model terminal recovery stops ONLY its own montage; other animation is never stopped by broad group/all-montage calls. Sequence playback uses explicit FullBody, explicit blend-in/out, rate and loopcount1 via PlaySlotAnimationAsDynamicMontage (AnimInstance.h:545); section must None for the first sequence slice. No copied F1 montage section timing ambiguity in this sequence-only backend.

## Walking and proof lifecycle

Resolve actual pack gameplay pawn through explicit proof game mode possession handoff; it remains the mannequin gameplay prototype approved C366, not Greystone bridge completion. New Sevarog character is controlled only by native proof controller. Require initialized nav data, grounded collision capsule and valid explicit target before any MoveToLocation. Goal is the target-facing authored band point, projected onto navmesh; no straight teleport/SetActorLocation fallback. Require full path, movement request completion AND measured final range in band; log travel distance and capsule/mesh transforms. Stop walking before montage, rotate only per authored allowed tracking policy until commit, then freeze heading; movement during Active disabled for this in-place first slice. Any target death/destruction, possession change, world teardown, timeout or generation reset aborts request and owned animation, closes model windows, and leaves boss inactive.

No damage component, generic life-state authority, pack-boss BT or old ability driver attached. F3 window events are telemetry only. Proof target HP must remain unchanged. Failure surfaces `[FrameworkProof] ERROR token=...` at Error severity AND on-screen error when viewport exists; movement and selection stay disabled. No silent legacy fallback. Cannot certify on-screen presentation from a null-RHI log.

## New-only Content authoring and execution sequence

Separate scoped releases, each one attempt with lock/fresh safety/pins/raw exits/content+source+binary snapshots. Stop/report before fixes.

1. F3a source review then build/isolated tests. No map or content write.
2. F3b read-only dependency/slot/pose prerequisites probe. Inspection report before choosing final fields. This is not gameplay proof or permission to edit the assets.
3. F3c new-only authoring: `/Game/OneBossFight/FrameworkProof/DA_Sevarog_SwingProof`, `DA_Sevarog_FrameworkProof`, and `/Game/OneBossFight/Levels/L_SevarogFrameworkProof`. Refuse if ANY destination already exists; no delete/recreate, overwrite, save-all or existing material/mesh/BP edit. Built-in engine cube floor plus lights/playerstart/native proof fixture and NavMeshBoundsVolume; build navigation for this new level and save only named new packages. World Partition/external actors disabled so expected delta is bounded (any extra package = STOP unless preapproved). If navigation build needs an additional map-owned package, enumerate its exact destination BEFORE release. Explicit proof-only GameMode override in the NEW level. L_SevarogArena, project default maps/game mode and Config byte-identical. Existing pack assets read-only. No Greystone visual bridge edits.
4. F3d fresh reload plus one scoped runtime proof. Driver explicitly starts the new proof map, retains async Python keepalive if used, waits for own fixture IDs, walks then plays one card, captures pose/movement and abort checks, quits explicitly. No global driver gate/packaging/performance run. One attack per authored trigger, no unreviewed endless selector loop.
5. Lead review followed by full OneBossFight regression/CookCoverage on actual final DLL; expected previous187+F2five+actualF3names, not assumed count. C374 UTS-launcher normalization preserves multiplicity; all other warning drift stops.

Authored proposal values need lead ratification in the source/content release: Swing1_Slow playrate1; commit0.35s, active0.65..1.05s, recovery1.50s; one telemetry window0.65..1.05s; range band250..350cm, cone120deg, speed180cm/s, tracking90deg/s, segment radius8cm, HPDamage0, blends0.10/0.10s, walk timeout10s. These are OUR fixture/design values, not Morgott frame data, observed attack contacts or approved gameplay tuning. Mesh/capsule alignment, capsule dimensions and spawn transforms must come from actual mesh bounds/floor clearance and be frozen before map-save release. This packet does not invent certified geometry.

## Exact proposed measurement schema and acceptance

Every record carries encounter/generation/instance/actor identities where relevant. Proposed lines (not observed output):
`[FrameworkProof] dependencies mesh=... skeleton=... animClass=... sequence=... sourceSha=... slot=FullBody resolved=1`
`[FrameworkProof] slot_graph name=FullBody nodeClass=... verified=1`
`[FrameworkProof] nav request=... projected=... fullPath=... result=...`
`[FrameworkProof] walk start=... end=... distanceCm=... rangeCm=... bandMin=... bandMax=... capsule=... mesh=...`
`[FrameworkProof] playback token=... montage=... rate=... position=... nodeWeight=... montageWeight=... boneTransform=...`
`[FrameworkProof] event token=... kind=Open|Close|Recovery|Finished|Aborted window=... group=... localSeconds=...`
`[FrameworkProof] cleanup reason=... modelIdle=... ownedMontageStopped=... moveRequestStopped=... staleCallbackIgnored=...`
`[FrameworkProof] invariant targetHPBefore=... targetHPAfter=... damageCalls=0 legacyBossComponents=0`
`[FrameworkProof] RESULT outcome=... checks=... failures=...`

Acceptance needs complete-path walking and actual displacement, capsule/mesh/nav agreement, owned montage advancing on verified skeleton/slot, measured visible bone/pose change with rendered capture, correct chronological edges through finish/abort, late callback rejection, no HP change, and cleanup. No damage proof from telemetry. New map != activation of live arena; no Ready/legacy suppression/Shipping/performance/all83 completion from this slice.
