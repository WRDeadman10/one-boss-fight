# DD12 one encounter cluster: actual source first

Claude implementation under renewed all83 objective. Only3 NEW files: Player/RPGBossEncounterClusterAdapters.h/.cpp and Tests/RPGBossEncounterClusterAdaptersTests.cpp. No existing Source edits. Actual implementation/tests/diff before build; no separate prose proposal or field-inventory round.

Purpose: close the last duplicate-component composition gap before combining DD5 with accepted clusters. Existing Stats and EncounterPolicy factories describe the SAME native class and instance. They must not be inserted as separate components. Provide one typed, atomic native assignment for BossMaxHealth, GateRadius and bResetOnPlayerRespawn, with one class/name plan.

## API and behavior

Namespace RPGBossEncounterClusterAdapters: ValidateEncounterCluster(const FRPGParticipantConfig&, FString&), ConfigureEncounterCluster(UActorComponent&, const FRPGParticipantConfig&, FString&), MakeEncounterClusterPlan().

Reuse accepted RPGBossStatsAdapters::ValidateStats on the complete four-stat record and RPGBossEncounterPolicyAdapters::ValidateEncounterPolicy. No new domain/tuning/fallback or generic compiler restriction. ValidateStats retains native health override capability (>1;1.5 valid) and posture positive/fractional/delay-rate semantics. GateRadius finite>=0;0 valid native no-gate. Validation clears diagnostics and checks Stats then EncounterPolicy, reporting their exact existing tokens and paths.

Configure: same lifecycle guard order and exact URPGBossEncounter class as accepted adapters, followed by entire cluster validation BEFORE ANY write. Then one explicit typed write block assigning only BossMaxHealth from Stats.MaxHealth, GateRadius and bResetOnPlayerRespawn from EncounterPolicy. Do not implement by invoking a mutating Stats callback before validating Policy. No partial-write path. Native public fields already provide the required seam; no native/Binding/schema edit is necessary. Any indispensable extra seam requires exact proposed delta before expansion.

Plan class URPGBossEncounter, legacy instance name RPGBossEncounter, callback ConfigureEncounterCluster, required fields exactly Stats.MaxHealth + EncounterPolicy.GateRadius + EncounterPolicy.bResetOnPlayerRespawn. Reuse constants from existing headers. ValidateStats reads the full record for capability/consistency, while Posture plan remains responsible for three posture writes. One encounter plan only; this factory stays unwired until later combined preflight order.

No manifest Value parsing, ImportText/runtime reflection, object creation/registration/BeginPlay, attribute writes/readback, actor/target lookup, timer/reset/dormancy/pack mutation, load, health override execution or gameplay readiness. Leave every other native field/state unchanged. This is authoring assignment, not effective gate/reset/pack health proof.

## Focused tests required

Actual distinct nondefault records A/B, including reset bool toggles and GateRadius0/fractional; plan identity/required fields/callback; manifest Value deliberately contradictory; component identity/count captured after fixture setup and immediately before each call. Compare all three destinations with typed record. No-created-component witness has its existing allocation limit.

Whole-record no-write cases: valid nondefault health with invalid Policy (including NaN/negative radius) and invalid/unsupported Stats with valid nondefault Policy, so both orderings would catch premature writes; preserve all three fields and observable native runtime state. Exercise reused finite/fractional/boundary domains without inventing editor floors or duplicating every old test. Diagnostics clear and error token/path remain specific.

Exactclass/lifecycle/no-owner/registered/begun/destroyed-retained refusal using safe existing Encounter fixtures. Read actual native BeginPlay before using any begun fixture; it may load or create through an unsafe owner. Use isolated plain actors and assert preconditions or report exact obstacle; no weakening guard, no shipped asset or pack changes. Config snapshot/independent components/CDO/unrelated fields remain unchanged. Test one single combined callback assigning all three fields with no duplicate Encounter insertion; do not claim real startup chronology from an array.

No new schema/compiler API is added, so do not create a redundant fake compiler test. Source use of accepted validators must be backed by actual cluster rejections. Use concrete non-abstract wrong-class components. No broad old-test cleanup/unity/config changes.

## Delivery and boundaries

Save full174-file pre-source manifest and relevant existing validator/native/Binding pins; all174 must remain byte-identical. Add exactly3 files and full177-file manifest/Review copies/SHA256 index/actual diff/coverage limits. Preserve intermediate failures if any. No UHT/build/automation until actual source review; no automatic fixes after later execution failures. Test count is reported from actual source/discovery later, not pre-assumed.

Claude alone operates engine after separate scoped verification release; Codex reviews. AG stands by, no git release. No existing Source/config/scripts/content/fixtures/pack edits; no DD5 insertion, wiring/activation/reservation/hydratedReady, PIE/full driver gate/package/noneditor. Next concrete integration after acceptance is a combined preflight of the accepted subset, still explicitly incomplete until all native consumers/dependencies are covered.
