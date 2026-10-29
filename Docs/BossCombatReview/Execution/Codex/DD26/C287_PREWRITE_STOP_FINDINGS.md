# C287 DD26 pre-write stop-condition findings

Read-only review during C286 verification; NO DD26 production or staged code edits.
The DD25 engine run is independent and remains the first execution priority.

## Stop (a): fixture Fields must gain59 paths

Preflight.cpp:381-401 builds plans and refuses every missing RequiredFields path
as Preflight.MissingRequiredField. Consequently, the existing51-path positive
fixture manifests fail after a twelve-plan expansion unless their independent
literal lists gain59paths. This is already anticipated by the update order, but
the stop clause explicitly includes a fixture whose Fields needs those paths.

Concrete source sites:

| Fixture source | Current path-list / Fields construction | Definition provenance |
|---|---|---|
| RPGBossHydrationPreflightTests.cpp | AllRequiredPaths:79; config Fields.Add:174, generic synthetic Definition Fields:203-205 | BuildConfig is synthetic; optional definition NewObject:195 |
| RPGBossHydrationPreparationTests.cpp | RequiredPaths / BuildConfig:117-138; Fields.Add:138 | hand-built FRPGParticipantConfig, bSyntheticFixture:141 |
| RPGBossProductionPreflightTests.cpp | AllRequiredPaths:104; Fields.Add:191 | transient NewObject definitions:366-367, not authored definition assets |
| RPGBossProductionPreparationTests.cpp | AllRequiredPaths:139; Fields.Add:227 | transient NewObject definitions:488-490 |
| RPGBossWorldPreparationTests.cpp | AllRequiredPaths:136; Fields.Add:220 | transient NewObject definitions:412-414 |
| RPGBossWorldInputCompilerTests.cpp | AllRequiredPaths:196; Fields.Add:284 | transient NewObject definitions:503-505 |

Real meshes/animations/pack character classes in production-shaped fixtures do
NOT make the URPGBossDefinition itself a real authored asset. These cited positive
fixtures create their definitions/configs in memory and populate Fields explicitly.
No authored DA_Boss asset Fields value was loaded/inspected here. Its serialized
manifest contents remain UNKNOWN; no asset edit or engine inspection is released
by this source review. Do not infer that all authored production definitions pass.

## Stop (c): test explicitly dedicated to the five-plan structure

RPGBossHydrationPreflightTests.cpp:986-991 introduces
OneBossFight.Binding.Preflight.ExpandedSubset / FRPGPreflightExpandedTest,
documented as independent five-class/name/count/51-path structure expectations.
At1026-1035 expected arrays enumerate EXACT five classes/names and assert five
plans and leases; at1044 the loop goes to5; at1061 distinct counts are5 and at1064
the union is51. This is an explicit structure regression, not merely incidental
batch teardown arithmetic. Its broader intent can be retained by extending the
independent literals to12/110, but that is precisely the structural test purpose
covered by stop(c), so no unilateral edit is made.

## Preliminary stop (b) check

No matching literal5/10 component-count hardcode found in preparation/registry
with the targeted count grep. Preparation iterates Participant.Plans.Num at146/
197 and sums Member.Owned.Num at369; this is preliminary source evidence, not an
exhaustive proof all downstream consumers are count-independent. No production
scope expansion is proposed from it.

Lead continuation needed: explicitly resolve stop(a) for the six in-memory
fixture manifest updates and stop(c) for ExpandedSubset (extend its structure
expectations under same test name/intent, or retain a separate baseline test).
The ordinary mechanical update order names these sites; this report resolves the
collision with its explicit STOP wording before any DD26 code is written.
No request to weaken assertions, generate expectations from adapters, edit assets,
broaden native/Binding/registry scope, or run an engine inspection.
