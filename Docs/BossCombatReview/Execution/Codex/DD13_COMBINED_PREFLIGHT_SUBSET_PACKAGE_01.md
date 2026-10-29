# DD13 combined preflight subset: actual source implementation

Claude SOURCE ONLY release under all83 implementation objective. Edit ONLY existing Player/RPGBossHydrationPreflight.h/.cpp and Tests/RPGBossHydrationPreflightTests.cpp. Save exact three preimages/full177-file manifest first. No other Source/new helper/schema/Binding/native/adapter edits. Actual diff/tests before build, no extra prose proposal loop.

Purpose: integrate the accepted adapters into the existing pure whole-batch kernel, replacing its three limited plans with five combined native plans. This is plan compilation, not runtime wiring or startup activation. Keep public request/role identity semantics; BossCore now means the expanded accepted subset. Update documentation and scope marker to ExpandedNativeSubsetPreflight (or equally explicit name). IsCompletePlayableBundle/IsReservation/IsReady remain FALSE. Preserve prior historical source/tests in preimages, do not overwrite old evidence.

## Deterministic plans and validation

For each BossCore request use ONLY these accepted factories, exactly once each and in legacy-relative creation order:

1. RPGBossStaggerClusterAdapters::MakeStaggerClusterPlan().
2. RPGBossPhasesClusterAdapters::MakePhasesClusterPlan(explicit selected id captured by value).
3. RPGBossEncounterClusterAdapters::MakeEncounterClusterPlan().
4. RPGBossDormantWakeAdapters::MakeDormantWakePlan().
5. RPGBossStatsAdapters::MakePosturePlan().

No separate scalar/profile/flow/policy plans or duplicate Phases/Encounter/Stagger insertion. This array is a deterministic relative plan order, NOT observed registration/BeginPlay chronology.

Before publishing any participant, validate every BossCore config using the full accepted StaggerCluster, PhasesCluster(selected id), EncounterCluster and DormantWake validators. Posture uses the complete Stats validation already included in EncounterCluster. Preserve exact named underlying diagnostics and slot identity, collect failures consistently across participants. Backend capabilities must fail in preflight, even where generic definition compilation accepts the broader domain. Do not clamp, alter shared validators, parse manifest Value, choose first phase or substitute defaults.

Required-field membership is the union of the actual five factories (currently51 unique paths); selected-phase paths come from the explicit selected id. Validate each required path, plan class/name/callback and uniqueness of plan class/instance before publishing; no invalid/duplicate plan silently discarded. Membership is not value derivation or trustworthy hash provenance. No Configure callback invocation, even as a validation probe. No create/register/BindEncounter/context mutation/lookup/attribute read-write/asset load/tick/timer/legacy suppression during compile.

Extend managed consumer collision checks to include URPGBossStagger and URPGBossDormantWake for BossCore actors, retaining existing Phases/Encounter/Posture and the participant guard for every member. TargetOnly still gets zero boss plans and rejects selected phase ids; do not start assigning boss consumers to the player/target. Preserve explicit world/encounter/content lease/slot/actor/target guards, duplicate actor/slot rejection, same-world/late actor refusal, whole-batch output clearing and no partial publication.

Production still fails closed through existing compiled skeleton/all-animation/mesh prerequisite checks. New profile soft refs are structurally validated here, NOT loaded or certified as matching the compiled animation array, mesh or class. State this remaining gap explicitly; do not call an otherwise passing production request a complete playable bundle. Synthetic flag/factory provenance, mutable aliases to const DTOs, caller content lease vs actual GI epoch and manifest derivation remain unresolved at this layer.

## Actual test delta

Retain all existing6 preflight test paths and their prior safety/rejection/dependency assertions; update only fixtures/expectations necessary for the expanded contract, add focused paths if useful. Preserve original negative controls and production prerequisite failures. No weakening existing assertions to get the larger bundle green.

Update synthetic config helpers to carry valid typed defaults/nondefaults for all consumed records and complete manifest membership. Expected class/name/order/count and required-field union must be asserted independently of the implementation under test; do not build both expected and actual exclusively from the same helper. No callbacks execute inside CompilePreflight: capture actor-owned components/context state before/after for success and failure, and assert no new Stagger/Wake along with old consumers. Class leases align one-for-one with plans and retain validated config/content identities.

Positive synthetic batches with target-only plus one or two BossCore members yield exactly5 plans per boss/none per target. Distinct selected phase ids/configs are retained independently; no default first/last phase. Test stable repeat order and no duplicate native classes/names. Exercise manifest omissions across all newly required groups and at least first/last fields of each combined cluster; messages identify the slot and missing path. Typed invalid records and backend-unsupported values in each newly integrated cluster, including late invalid last participant, clear a prior good output and publish nothing for earlier members. Tests must catch a valid Stats+invalid Policy and an invalid Stagger/Wake after other records are valid.

Create isolated already-owned Stagger/Wake components without registering/beginning them; preflight must refuse those BossCore actors by name without mutating any member. Keep world/actor/target/lease/production controls, including null/mismatched animation entry checks and valid dependency control. No engine asset loading or live content fixture released for this package; A165 remains future candidate input only. No BeginPlay chronology claim from array order or source reasoning.

If confirming callback binding needs a separate isolated invocation, mark it explicitly outside CompilePreflight and assert no such invocation occurs during compile. Existing adapter tests already cover field writes; avoid rerunning gameplay or manufacturing broad new corpora.

## Evidence and gate

Deliver actual3-file diff/preimages/Review copies/new full177-file manifest and relevant accepted adapter/native pins/receipts. Exactly174 other Source files unchanged. Report test names and uncovered limits. NO build/UHT/automation until actual source review, no automatic fix/filter/expected-list weakening after failures.

No startup hooks, reservation, context publication, target/reset rewiring, Ready/legacy suppression, production asset creation, engine/PIE/full driver gate/package/noneditor, Config/Scripts/Content/pack or git operations. Actual source next, then separate verification release. Later runtime coordinator and positive production dependency work need concrete reviewed packages; these five consumers still omit other legacy behavior/presentation/audio/death systems.
