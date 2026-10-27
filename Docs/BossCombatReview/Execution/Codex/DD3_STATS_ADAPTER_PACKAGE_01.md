# Next concrete boss-data package: typed native stats adapters

Owner all83 implementation/Data Assets first; after C189 bounded2b evidence. Codex releases Claude **source implementation and diff delivery before build**, not automatic boss activation.

## Exact scope

Add `Source/OneBossFight/Player/RPGBossStatsAdapters.h` and `.cpp`, plus new `Tests/RPGBossStatsAdaptersTests.cpp`. Reuse existing `FRPGBossStatsConfig`, `FRPGParticipantConfig` and native `FRPGComponentPlan` callback mechanism. No existing live source file must change for this first package. If an indispensable missing native seam is found, show the exact small proposed delta before editing it. Do not re-enumerate fields already covered by Step2Preparation02/09/15.

Implement named typed validation and native Encounter/Posture configuration helpers/plan factory. Consume typed Stats fields, never FRPGParityField.Value/ImportText:

| Input | Assignment |
|---|---|
|Stats.MaxHealth|URPGBossEncounter::BossMaxHealth|
|Stats.MaxPosture|URPGBossPosture::PostureMax|
|Stats.PostureRegenDelay|URPGBossPosture::RegenDelaySeconds|
|Stats.PostureRegenRate|URPGBossPosture::RegenPerSecond|

Use exact existing component instance identities and explicit class checks in plan callbacks. Native capability is separate from generic schema validity: all inputs finite; posture maximum positive, regen delay/rate nonnegative. The native health override only applies for >1, so a requested typed health in (0,1] must return a named unsupported-native-override error **before any assignment**, rather than silently claim application. Do not change generic definition compiler's positive-only domain, clamp/round/substitute health, or alter legacy behavior. Values such as1.5 are not rejected for being fractional. This is a backend capability check for an explicit override, not a new global gameplay limit.

Validate the full selected Stats record before any component write. Reject wrong class, already registered, component begun-play, invalid owner or owner begun-play; no mutation on failure. Do not create/register components or touch pack attributes inside configuration helpers. Callback order comes from the future full-cluster planner, not this two-plan subset. Make it explicit that these two plans alone are **not a complete playable boss bundle** and must not mark an encounter ready or suppress legacy components.

Plan RequiredFields must name the actual typed inputs for compatibility with the existing manifest contract. This is still manifest membership/assignment evidence, not independent raw-value/hash derivation. Keep provenance equality and eventual effective pack readback open rather than fabricate them.

## Focused actual test implementation

Use isolated native components/actors, no pack asset saves or live arena. Cover nondefault valid values, independent two-config/two-owner isolation, NaN/Inf and zero/negative edges, explicit health0.5/1 unsupported versus1.5/2000 supported, wrong component class and registered/begun-owner rejection. Snapshot relevant fields before failed calls and assert no partial write. Verify successful callbacks leave components unregistered and do not seed runtime current posture, generation, counters, cached health or hold state. Constructor defaults remain unchanged elsewhere.

Tests prove typed config assignment and rejection, not asynchronous pack health application or Posture.BeginPlay seeding. No synthetic test is called an arena duel. Required future witnesses remain real pack health readback, first BeginPlay/registration chronology and full-cluster reset/phase interactions.

## Delivery and boundary

Claim three new files; preserve dirty work and pin dependencies. Deliver actual code/diff/test cases/hashes for Codex review **before build/automation**. Use the existing reviewed specs as inputs; do not substitute another prose plan. No source changes to PlayerMoves, Binding, Encounter/Posture/Phases/Stagger or their defaults; no coordinator calls, target/reset rewiring, assets/maps/config/scripts, full gate, package or new gameplay. No phase array selection or unapproved multiphase mapping in this stats-only package. Full Phases/Stagger and remaining content adapters follow concrete separate packages.

Claude may update owned TASKS/TEST_PLAN/KNOWN_ISSUES/DECISIONS entries to state2b's exact accepted scope and remaining arena/fullgate gap; preserve historical claims/evidence and never rewrite unrelated entries. Codex does not commit, build or operate the engine. AG remains resting/no new work. Shared actor/target/network authority remains required in the full design; this assignment layer does not implement it.
