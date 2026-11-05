# Parry target-filter audit (Queue D D22, 2026-11-03)

## Actual callers

The known production damage callsites resolve against player-controlled targets, not arbitrary overlap actors:

| Caller | Target construction | Resolver result path |
|---|---|---|
| Framework boss delayed parry reaction | Uses the boss's stored player target and calls resolver after a valid parry (`RPGFrameworkBossCharacter.cpp:300–303`). | Adds resolver only to the boss owner, passes the selected target actor. |
| Framework move executor | Captured `Target` player pawn from the framework boss start snapshot (`RPGFrameworkMoveExecutor.cpp` hit resolution callsites around `:290,412`). | Resolver runs only after move geometry/hit filtering. |
| Javelin | `Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(...))`; collision actor must equal that pawn before resolve (`RPGBossJavelin.cpp:134–147`). | Non-player/world collision is treated separately as miss/block. |
| Low sweep | Same player-pawn character cast; geometry tests this pawn and passes it to the resolver (`RPGBossLowSweep.cpp:70–127`). | Other pawns are ignored by the sweep trace. |
| Shockwave | Reads the player pawn; requires it to cast to `ACharacter` before applying its radial result (`RPGBossShockwave.cpp:66–113`). | Per-player radial calculation, then resolver. |

Pack melee hits (A1/A3) use the pack's own weapon-trace/impact decision and do not call this resolver; `RPGDamageResolver.h` documents that boundary. D16/KI-153 is the separate missing witness for the pack's parry branch.

## Target predicates and gaps

`URPGDamageResolver::Resolve` rejects disabled/null/no-world inputs, then requires a readable positive `Attribute.Health`, rejects `Status.Dead`, and checks attacker life/current generation/duplicate/invulnerability/parry (`RPGDamageResolver.cpp:133–158`). It has no explicit `Target != GetOwner()` check, player class check, team/friendly check, or owner-controller identity check. `URPGPlayerParry::IsParrying` only asks whether the given actor has `URPGPlayerParry`; it does not filter class/faction (`RPGPlayerParry.cpp:132–136`). Lead decision C-745: keep `Resolve` caller-owned. Trusted production callers must pass the current player target; do not add self/faction predicates to the resolver now. This is the contract boundary, not a reproduced runtime mis-target.

No inspected test exercises resolver target identity or verifies that a production caller passes the active player target rather than self/friendly actors. Pure `RPGDamageRules::Decide` tests alive/dead/stale/duplicate/invulnerable/parrying booleans but has no actor identity input (`RPGParryTests.cpp:31–39`; `RPGAutomationTests.cpp:159–184`). C-745 orders actor-identity/caller-contract cases in the D13 harness plan; these tests should pin the caller's chosen player target and ignored self/friendly overlaps, without adding identity policy inside `Resolve`.

## Bounded coverage follow-up

In the D13 stateful harness, establish that each relevant caller supplies the active player pawn and ignores boss/self/friendly overlaps before resolution; preserve the caller-owned API contract. Add null/no-health/dead resolver cases where fixture support permits. Do not infer team safety from `Attribute.Health` or `Status.Dead`. Keep pack own-trace proof separate.

## Verification boundary

Static source/test review only; C-745 contract disposition incorporated. Tests/build/Editor were not run; no code changed.
