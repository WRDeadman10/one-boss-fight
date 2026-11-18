# BT-51: Player health and loadout startup diagnosis

Date: 2026-11-16
Scope: read-only trace of Smoke run `Saved/SevarogArenaRoute/Run_20261116_142947_460f96a6`. No source/data edits, build, tests, Editor, PIE, package, commit, or push.

## Findings

Direct Smoke telemetry (retries 3–600): `hp=0 max_hp=1e+06 tag_bound=1 tag_param=AttributeTag style=None`, with a resolved `BP_AttributesComponent_C` and numeric `Value`/double output. This proves the tag was bound for this call and the getter returned 0. It does not by itself prove whether 1e6 is a real authored maximum.

Antigravity's static trace reports that no project-authored character data asset it inspected has a 1e6 health maximum; authored PlayerInfo health uses Base/Max 100. The pack's bare, unequipped attribute map uses CurrentValue 0 / MaxValue 1e6 until initialized. Project corroboration is in `RPGBossFrameworkProfile.h`, `RPGFrameworkProofFixture.cpp`, and KI-150. This makes 1e6 a strongly supported bare-map sentinel in this path.

In the arena Smoke, `BP_AdvancedGameMode_C` spawns `BP_CombatPlayerCharacter`; encounter selection binds the already possessed player as `TargetOnly`. The route does not author target attributes. The Smoke log records `rpg.Build=''`; `RPGBuildLoadout` treats an empty build as no choice and issues no equip call. The driver is passive and injects no input. Therefore the normal input-driven equipment/style path is not triggered: CurrentCombatStyle remains None and health remains 0. The arena route waits for finite positive current health and correctly fails closed; it never spawns the framework boss.

A separate proof fixture writes profile TargetHealth explicitly and reads it back before boss initialization. This is precedent for explicit target preparation, not runtime proof that the arena route currently does so.

## Lead decision and follow-up

Accepted BT-51 diagnosis. Production target preparation must be implemented and reviewed separately: only recognize the exact bare-map sentinel, load a valid selected profile, set max/current from its TargetHealth, read both back, and refuse on any mismatch. Preserve already-positive health and the boss target-alive gate; do not write combat style. Smoke should explicitly request the Starter build to exercise weapon/style startup without viewport input.

Kanban: BT-51 reviewed; BT-52 profile-driven target-health initialization (Antigravity), BT-53 explicit Smoke Starter loadout and runner hash/contract updates (Antigravity), BT-54 lead review, BT-55 locked Development build/full suite, BT-56 fresh Smoke. No playable build or route acceptance is claimed yet.

## BT-52/53 lead source review (2026-11-16)

Initial source review was not accepted yet. BT-52's sentinel classification used `FMath::IsNearlyZero` rather than exact zero, and the readback checks should explicitly reject non-finite values. BT-53 parsed the observed build name but did not make Starter observation an acceptance criterion; its Smoke acceptance receipt also did not bind or verify the updated runner/driver hashes. These are tracked as source-only hotfixes X-2529. No tests, build, Editor, or PIE run for this review.

## BT-52 source acceptance; BT-53 second review hold (2026-11-16)

BT-52 hotfix source review is accepted: sentinel and dead-state classification now require exact current health 0.0; max/current readbacks explicitly require finite values and near-equality to profile TargetHealth. Existing positive health is untouched and failures refuse the route. No build or runtime verification has occurred.

BT-53 requires one more change. Its receipt now stores and verifies the Smoke runner/driver hashes during and after the build/Smoke, but the source-build runner does not compare those hashes with the incoming pre-build lead approval. It could emit an approval for runner/driver contents changed after review. Antigravity is adding those preflight and post-lock comparisons with contract coverage. BT-53 remains in progress; no tests, build, Editor, or PIE run for review.

## BT-53 source acceptance (2026-11-16)

A-1046 completed the requested hash hotfix. Lead review accepted: incoming source-build approval must match the acceptance runner/driver hashes before and after lock acquisition; the resulting route approval carries those hashes; the Smoke runner checks them at preflight, after lock, and after Editor exit; Smoke requires Starter to be observed. Source hash report was independently matched. No tests, build, Editor, or PIE run during this source review. BT-55 is the next gated build/DD27j suite task.
