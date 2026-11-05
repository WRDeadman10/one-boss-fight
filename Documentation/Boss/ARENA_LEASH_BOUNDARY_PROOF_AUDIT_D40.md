# Arena leash boundary proof audit (Queue D40)

Scope: map inside/equal/outside radius behavior, arena-center selection, no-leash control, and existing proof coverage. Read-only source/evidence review; no run/build/tests/Editor.

## Source truth table

| Target distance from captured/authored `ArenaOrigin` | `TargetFault` result (if radius > 0) | Leash effect |
|---|---|---|
| `< ArenaRadiusCm` | not `OffArena` from radius gate | ordinary target validation/behavior continues. |
| `== ArenaRadiusCm` | not `OffArena`; comparison is strict `>` | remains inside; no leash start from this check. |
| `> ArenaRadiusCm` | `OffArena` | if profile `bArenaLeash` is enabled, `HandleLeash` starts once, aborts active card/combo, stops owned walk/movement and sends boss to origin; otherwise the normal fault path fails closed. |

`ArenaOrigin` is captured from authored profile center when `bArenaCenterAuthored`, otherwise from target start location (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:66`; profile fields `RPGBossFrameworkProfile.h:149-150,175-176`). `TargetFault` uses planar distance and strict `>` (`RPGFrameworkBossCharacter.cpp:108-116`). On returning inside radius, Tick clears leash state and resumes via a walk-to-band; the boss is considered at center within `AcceptanceCm+30` (`:205-225,248-260`).

## Existing proof and remaining checks

- `Documentation/Boss/ARENA_LEASH_EXPECTED_S115.md` specifies the positive 500 cm outside run, return to 100 cm inside, and a no-leash negative control. It explicitly proposes exact-radius 250 cm and smallest outside 251 cm checks but says the retained run does not test them (`:1-24`). Retained `B_MOV005/pie_leash3` demonstrates outside-to-center-to-inside-resume, not exact boundary.
- `OneBossFight.Framework.Runtime.ArenaProfile` checks valid radius domain and requires a radius when leash is enabled (`Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:698-706`); it does not test target position equality or the actor's leash transition. Source token `arena_leash` records Start/AtCenter/Resume; the schema is state-specific (`validate_framework_proof_logs.py:67`, emitter links `Documentation/Boss/LOG_TOKENS.md:97`). A no-leash control must assert absence of `arena_leash` and continued ordinary behavior.
- `ARENA_LEASH_EXPECTED_S115.md` names the 249/250/251 control plan; observed evidence still needs a run manifest with profile, center source, radius, map, target positions, and actor/run identity. `TargetFault` radius classification occurs whenever radius is positive; `bArenaLeash` controls whether OffArena becomes recovery or fail-closed behavior.

No comparison mismatch is found. The precise missing evidence is inside-only negative control and equality/just-outside actor-level behavior; existing profile validation is not a substitute.
