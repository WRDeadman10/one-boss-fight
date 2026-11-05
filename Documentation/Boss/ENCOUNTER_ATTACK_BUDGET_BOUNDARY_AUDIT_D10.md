# Encounter attack-budget boundary audit (Queue D D10, 2026-11-03)

## Source contract

Profile validation constrains F5 `AttackCount` to 1–8 (`Player/RPGBossFrameworkProfile.cpp:155`). The normal finish path continues only while `AttacksDone + 1 < AttackCount` (`Boss/RPGFrameworkBossCharacter.cpp:602`); it increments `AttacksDone` before preparing the next attack (`:605–607`). Otherwise it completes the encounter and reports `AttacksDone + 1` in RESULT (`:614–618`).

Combo continuation checks `AttacksDone + 1 >= AttackCount` before asking for another combo step (`:782`). When the budget permits a continuation, both immediate and paused routes increment `AttacksDone` before `PrepareNextAttack` and `StartCard` (`:793`, `:809`). Consequently a refused continuation consumes that ordinal and ordinary selection resumes at the next displayed attack number. Whether that is intentional is a Lead decision already surfaced in D4.

## Tests inspected

`RPGFrameworkRuntimeTests.cpp` validates profile rejection for `AttackCount` values 0, -1, and 9 and uses values 2/3 in profile-validation fixtures. `PhasePoolCannotStarve` checks that phase card-pool cardinality can support an attack count. These tests validate configuration and starvation math, not the live encounter's exact number of starts, finish transitions, or combo-refusal accounting. The pure `RPGBossEncounterLoopTests.cpp` simulates selected model starts/restarts but does not exercise profile `AttackCount` or actor completion logic.

## Boundary table

| Budget | Source-derived normal path | Coverage gap |
|---:|---|---|
| 1 | First completed attack cannot continue because `1 < 1` is false; encounter completes with one ordinal. Combo gate sees `1 >= 1` and ends combo. | No actor-loop test asserts exactly one `StartCard` and one terminal RESULT. |
| 2 | After attack 1, `1 < 2` permits one next attack; after attack 2, `2 < 2` is false and encounter completes. | Profile fixture uses 2 but does not execute the actor loop to count starts. |
| 8 | Seven continuation transitions are permitted; the eighth completion terminates. | No actor-loop maximum-budget count test found. |
| Invalid 0, negative, 9 | Profile validation refuses before encounter use. | Domain rejection is covered; no need for runtime count behavior at invalid values. |
| Combo refusal before a card starts | Counter increments before `StartCard`; if refused, later normal selection uses the next ordinal. | D4 asks Lead whether failed combo continuation consumes budget; pure model fallback test does not settle intent. |
| `PrepareNextAttack` failure | Fails encounter with `Framework.Playback.NextAttack` after increment. | Not the same as card refusal; wrapper/actor test should preserve separate failure identity. |

## Bounded actor-test proposal

Use an isolated synthetic encounter fixture with one eligible card and budgets 1, 2, and 8. Count actual accepted playback starts and terminal result ordinal; test the last permitted start and verify no additional selector attempt occurs after terminal completion. Add a combo route where a continuation is refused and assert the exact ordinal only after Lead decides whether the failed attempt consumes budget. Keep `PrepareNextAttack` failure as a separate fatal case. No live animation or pack content claim should be inferred from a pure model loop.

## Verification boundary

Inspected source and existing test declarations read-only. No source/test code changed and no test/build/Editor/PIE/package run occurred. The report is a source-derived counter map; exact actor start counts remain unverified.
