# C340 — TargetOnly consumption facts (read-only)

No Source/Content/Config change, engine run, build, compiler rule change, new manifest row or asset save. Source-derived facts; runtime behaviour outside these paths and pack Blueprint consumers are UNKNOWN.

## (a) Definition/config consumption after CompileParticipant

The compiler has NO role argument (RPGEncounterBinding.h:457-459; RPGEncounterBinding.cpp:32-35,152-155). It validates all generic identity/stats/policies/phase/dependency/row requirements before any later TargetOnly distinction, copies every typed record into FRPGParticipantConfig (:118-136), then production-loads skeleton and animations (:137-148). Target-only does not exempt any of those compile checks.

After compilation, in the expanded subset paths:

| Path | Actual TargetOnly consumption |
|---|---|
| CompilePreflight | Request.Config must exist; Content lease identity; Schema, BossId (copied DefinitionId), PresentationId, StableManifestHash shape, nonempty Fields and valid content epoch (HydrationPreflight.cpp:336-351). bSyntheticFixture gates dev-only acceptance; production checks compiled Skeleton, EVERY Animations lease/skeleton identity and actor mesh compatibility (:353-374, CheckCompiledDependencies:171-194). Explicit TargetSlot and actor/world/lifecycle checks apply to all (:264-332). TargetOnly must have no SelectedPhaseId (:425-428). The config lease is retained in output (:442-448). |
| Boss-specific preflight | All twelve adapter/required-path checks sit inside if(bBossCore), :377-424. TargetOnly does NOT consume Stats/EncounterPolicy/StaggerPolicy/PhaseFlow/Fireball/PhaseDependencies/StaggerProfile/DormantWake/Bleed/LowSweep/Shockwave/HealPunish/Look/CloseClipSwap/Death/Phases as native consumer configuration after compile. It receives no plan/class leases; only BossCore builds them (:449-455). Generic compile still validated/copied them earlier. |
| Preparation | PrepareBatch first calls whole-batch CompilePreflight (HydrationPreparation.cpp:242-254). Allocate skips non-BossCore (:138-145); Configure skips non-BossCore (:192-198). Thus no native consumer callback reads TargetOnly typed scalars. Registration validates target world/actor lifecycle, requires no target owned components/plans and continues (:512-545). Plan/config and participant identities stay leased. |
| Preparation registry | Calls PrepareWorldBatch (PreparationRegistry.cpp:491), then checks/reserves original encounter/actor identities, including every plan participant (:509-523). No separate direct TargetOnly scalar/Fields consumer found in this file. It retains the prepared artifact; inherited preflight validation is mandatory. |
| Activation facade | Calls PrepareWorldBatch (Activation.cpp:46) then RegisterOwnedComponents (:65), retains batch/result and routes diagnostics. No separate TargetOnly definition-field consumer or role-aware compile bypass. |
| World input compiler | For EVERY member, a live Definition with Schema1/DefinitionId/PresentationId is required (WorldInputCompiler.cpp:485-503). It production-compiles EVERY definition (:545-572), then assigns same config/role/target/selected-phase to the candidate (:576-584). Role is explicit selection metadata, not passed into CompileParticipant. No definition or config omission for a target-only actor. |

Separate existing context subsystem (not a new call introduced by these facades): BindEncounter requires per-slot configs and compares non-synthetic DefinitionId/Schema, mesh/compiled Skeleton and world-content id, retains Config/TargetSlot (RPGEncounterBinding.cpp:225-253). ResolveTarget uses slot/current/hydrated identities (:282-288). This is not proof those contexts are bound/hydrated by the current DD29 activation facade; that runtime integration remains unmeasured.

## (b) Can the boss omit a target?

NO, a valid boss request cannot compile without another in-batch compiled participant. CompilePreflight rejects empty TargetSlot (TargetMissing :322-324), self-target (:326-328) and absent in-batch target (TargetNotInBatch :330-332). It separately rejects missing config (:336-340). Therefore a single boss cannot target itself/external player0 or bypass target compilation. CompileWorldInput checks ParticipantTargetMissing/SelfTarget/TargetNotInBatch (:469-481), requires every definition (:485-488), every slot selection (:414) and compiles every member (:556).

Important distinction: the counterpart must be an actual valid compiled in-batch participant, but these checks do NOT require its role specifically to equal TargetOnly. Another valid BossCore participant can be an explicit target. There is no absent-target mode in these accepted paths. This says nothing about authorizing a different encounter composition.

## (c) Existing production tests' target

RPGBossProductionPreflightTests.cpp:385-389 creates BOTH definitions transiently with NewObject and FillDefinition; neither is the saved Hero asset. FillDefinition (:173-208) sets valid fixture stats/policies/phase, observed skeleton/animations and ALL110 required paths, even for the player. MakeProductionField (:138-153) explicitly uses fixture metadata: Type=fixture, SourceSHA256=64 c characters, SourcePath='DD14 production preflight fixture, not live provenance', Witness='none: structural membership only'. Those rows are a declared membership fixture, NOT truthful authoring provenance or permission to copy them into a production Hero asset.

CompileProduction (:394-398) invokes the REAL CompileParticipant on BOTH; not CompileSyntheticParticipant. The compiler passes bSynthetic=false (:152-155) and the test asserts both configs have bSyntheticFixture false (:486-488). MakeInput uses BossCore boss and TargetOnly player (:406-407). Thus production compiler/dependency checks run, but the definitions/manifest metadata are test-local fixtures. The saved Hero zero-row failure is fully compatible with those earlier tests.

## (d) Fields consumers beyond compile and boss110-set

YES. Besides compiler row-shape/duplicate/nonempty validation (Binding.cpp:103-115) and copy (:120):

1. CompilePreflight checks Fields.IsEmpty for EVERY role at :347, independent of the boss110 membership loop (:408-423). Changing only CompileParticipant to permit an empty TargetOnly manifest would still fail Preflight.InvalidManifestIdentity under current code.
2. URPGCombatContextSubsystem::CreateConfigureRegister reads Record->Config->Fields to form a FieldPath membership set (Binding.cpp:354), then validates EVERY requested Plan.RequiredFields against it (:363-365). This is a second generic plan-membership consumer, not a fixed110-only boss check. It also rejects empty hydration plans (:349-351); this does not itself establish a target-only Ready path.
3. Definitions/configs declare the array (Binding.h:319,363); leases/records retain it. In runtime C++ searched under Source/OneBossFight (excluding tests), no other FRPGParityField payload consumption was found. The compiler checks Type/source metadata string presence and SHA256 SHAPE, not SourcePath file existence, actual file hash equality or Value-to-typed-field equality. No runtime parsing of FRPGParityField.Value to configure consumers was found in these paths. UNKNOWN: external Blueprint/reflection/tooling use beyond the searched runtime C++.

For TargetOnly, current code requires a structurally complete NONEMPTY manifest but imposes no boss110 required-path union on it. This is a syntax/domain fact, not approval to fabricate one row. Which real Hero-authored field has truthful provenance/witness is the separate A224 authoring investigation. No optionA/B chosen or implemented here.
