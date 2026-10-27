# First-cluster native adapter capability proposal

Codex data-model preparation,2026-10-27. **PROPOSED, NOT APPROVED OR IMPLEMENTED.** Refines PacketC0/D0 after source audits09/14–16 and AG10 bounded acceptance. No change to source, assets, scaffold validation, phase counts, defaults, activation delay or pack runtime grants. No owner decision needed during the current offline queue; resolve these choices explicitly before future adapter acceptance.

## Concrete recommended boundary

Keep generic definition data separate from the capabilities of a particular native adapter. A valid generic definition does not imply every adapter can execute it. After generic compilation, a pure native-plan compiler should either produce a fully typed supported assignment plan or a named UnsupportedNativeCapability result **before component allocation/reservation side effects**. Do not clamp, substitute Boss01 defaults or read provenance strings to turn unsupported data into a working plan.

Proposed result fields: disposition, adapter capability ID/version, definition/schema/content-manifest identity, exact typed input field, unsupported reason, required consumer dependency and underlying source witness reference. The result must not carry mutable health, last-drain time, behavior hold, target actor or network authority as content. These are proposed C++ value semantics, not a new asset-authored class/reflection string API.

| Candidate typed plan area | Recommended native capability condition | Limits / unresolved choice |
|---|---|---|
|Health assignment intent|Explicit intent `ApplyConfiguredMaximum` requires finite desired health>1 for existing Encounter path; values in(0,1] return Unsupported for that intent.|A separately explicit `PreserveLegacyMaximum` policy is a different capability, not a silently overloaded numeric sentinel. Do not add it by default or treat generic MaxHealth as optional. Actual max/current readback and existing0.5 branch behavior still require witness.|
|Posture scalars|Finite positive maximum, finite nonnegative delay/rate, assigned before BeginPlay; explicit native pack-poise compatibility plan.|This matches existing typed domains, but cannot prove pack extended attributes exist, own-pool seeding or effective regen. Preserve configured cadence/runtime timestamp semantics.|
|Phase mapping|Require an explicit mapping from intended transition identity to the native single-threshold phase consumer, with no implicit first/last array-row choice.|Exact cardinality/initial-phase representation is still a schema decision. A typed compiled mapping must reject ambiguity, duplicate mapping or unsupported extra transitions; this does not approve a new global one-phase restriction. Other adapters may support different phase models.|
|Phase multipliers|For the current inverse-effect capability, recommend positive movement/rate factors and damage factor>=1, held constant for that adapter lifetime.|This is a proposed restriction for one reversible native plan, not an approved scaffold change. Supporting subunit damage requires separately reviewed signed-delta ownership/removal semantics; do not change current boss gameplay while extracting it.|
|Stagger/posture/phase interaction|Plan explicitly declares participating consumers and preserves current prerequisite, deferred intake, refill/hold/behavior handoff and reset order.|Optional legacy branches remain legal outside a plan claiming the complete cluster. Do not require Stagger globally merely because the complete-cluster capability needs it. Immutable configuration does not prove runtime object/ability membership stays stable.|
|Participant association|Fixture/plan has explicit source/target role edges; runtime association uses current actor/key/generation and whole-encounter publication barrier.|Boss/Player reciprocity is a reviewed fixture assertion, not a universal schema rule. Per-record registration/hydration is not effective readiness or damage/decision authority.|

Recommend initially compiling only the explicitly reviewed native capability set without claiming all-domain support. Report unsupported generic content precisely; do not relabel all83 requirements N/A or solved. Future support for additional phase models, hold ownership, dynamic ability changes and networking remains required where the reference calls for it, under later scope.

## Keep three evidence layers distinct

1. **Pure compile result:** typed data is well-formed and supported by a named adapter plan; no component/asset mutation. Proposed plan validation must compare exact input fields and dependency capability, not just count manifest field names or accept a SHA-shaped caller string as a derived digest.
2. **Configured/registered state:** actual assignments precede registration/BeginPlay; the whole batch publishes only after required preparation succeeds. Registration success is not positive pack attribute readback; an actor becoming begun cannot be papered over by a later adapter setter.
3. **Runtime parity:** independent effective values, event ordering, rates/attributes, reset/death/hold lifecycle and target isolation observed in authorized fixtures against the pinned legacy baseline. Keep content declaration, configured property and actual pack readback as separate values, not aliases of one default helper.

No new generic wait/timeout or fallback is proposed here. If delayed pack initialization is relevant, use an explicit reviewed lifecycle observation and failure disposition rather than silently extending current startup health enforcement. A semantic change found necessary during parity remains a separately reviewed correction, not an extraction cleanup.

## Unrun compile/assignment review cases

Required future examples: current2000/100/6/13 and native phase defaults preserve plan identity; health0.5/1 are well-formed generic values but unsupported for ApplyConfiguredMaximum; damage0.5 unsupported for this inverse-effect capability; ambiguous phase mapping rejects without assignment; optional-consumer legacy path is distinct from missing required cluster consumer; per-record-ready with pending partner does not publish whole cluster; target self-edge is judged against explicit plan intent rather than global guessed roles.

These are proposed test cases, **NOT RUN**, not a new assertion count or engine acceptance. Supporting observations/source hashes stay in09/14–16 and AG10 report. Review this proposal with the resumed operator's implementation packet before applying any schema/domain guard; all2b+/runtime gates remain in force.

## Source-grounded clarification after AG12 review — 2026-10-27

Native omission is not a neutral health policy: Encounter.h40 defaults BossMaxHealth2000 and Tick90 can apply that value. Merely omitting an assignment does not preserve pack health. Any future explicit PreserveLegacyMaximum capability must name its native compatibility behavior (for example a separately reviewed bypass assignment), not infer it from missing fields or assume pack500. No such policy/assignment is approved here.

Single-transition consumer topology is distinct from phase-array representation: an initial-phase row plus a transition row may be a different schema shape from a transitions-only list. Resolve roles/identity and mapping before count constraints; no unconditional Num==1 rule. Current source exposes configurable PhaseTwoHealthFraction default0.6; fraction0.5 in a hypothetical plan is not approved tuning of current Boss01.

Pure native planning consumes resolved value/dependency metadata after generic asset resolution. Existing generic CompileParticipant loads Skeleton/Animations synchronously (which may allocate or reuse objects and perform I/O); before-component-allocation/mutation is not a zero-engine-allocation promise. Pointer exposure, whole-batch publication and effective gameplay readiness remain separate observed states. Prior proposal hash67de3eb3...a0ce5 is historical after this explicit design-only addendum; no source/scaffold/asset policy changed.
