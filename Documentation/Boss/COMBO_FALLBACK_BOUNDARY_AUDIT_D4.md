# Combo fallback boundary audit (Queue D D4, 2026-11-03)

## Result

The source has two combo continuation routes. Both stop combo mode and return to ordinary decision flow when the next card is unavailable or `StartCard` refuses it. The existing C-727 pure test demonstrates the underlying model refusal followed by selection/start of another eligible card. It does not execute either actor route. This is a coverage boundary, not a reported runtime bug.

## Route matrix

| Route | Source behavior | Existing coverage inspected | Remaining boundary |
|---|---|---|---|
| Immediate continuation | `RPGFrameworkBossCharacter.cpp:783–800` finds the next combo node/card, treats `CardIndex == INDEX_NONE` or failed `PrepareNextAttack` as a distinct playback failure, and on `StartCard` refusal sets `bComboActive=false`, logs `combo_end reason=NextCardRefused`, then returns for the next ordinary decision. | `FBossComboFallbackAfterModelRefusal` in `Tests/RPGBossComboFallbackTests.cpp` uses synthetic cards; it calls `Model.Start` for the refused combo card, then `Selector.Select` and `Model.Start` on a fallback card. | The test proves the value-model scenario, not `PrepareNextAttack`, `bComboActive`, telemetry, attack accounting, or a subsequent actor tick. `AttacksDone` increments before `StartCard`, so a refused continuation consumes an attack slot in this path; intended semantics need Lead review. |
| Delayed continuation | A positive `PauseSeconds` stores the pending card and timer (`RPGFrameworkBossCharacter.cpp:787–791`). `StartComboCard` captures a fresh snapshot and, for invalid card index or refused `StartCard`, ends combo with `NextCardRefused` (`:803–813`). | No inspected test invokes the character timer callback or `StartComboCard`. | Target/range/yaw/phase changes during the pause and timer cancellation/reset remain actor-level coverage gaps. `AttacksDone` also increments before the attempted start; whether that consumes the slot on refusal needs Lead review. |
| Non-continue combo step | Any result other than `Continue` clears combo mode and returns to ordinary decision logic (`:770–782`). | Pure combo rules tests cover graph-step outcomes. | Runtime return/tick behavior remains outside pure graph and model tests. |
| Attack budget | Reaching the configured attack count clears combo and logs `combo_end reason=AttackBudget` (`:782`). | Pure budget/graph rules coverage inspected separately. | This is a normal terminal route, not a refusal fallback. |
| Prepare-next failure | Failed `PrepareNextAttack` raises `Framework.Playback.NextAttack` (`:793–794`, `:809`). | Existing tests cover model transitions, not the component wrapper. | This is fatal executor preparation failure, not `NextCardRefused`; keep it separate in any actor fixture. |

## Refusal and fallback test assertions

The current synthetic C-727 case chooses a 60-degree forward card and a 120-degree ordinary card at yaw 50 degrees. It asserts `MoveModel.Cone`, idle model after refusal, preserved refusal trace, ordinary fallback choice, and successful pure-model start with the same fresh snapshot. It does not model the combo graph, attempt count, component state, timer, or actor logs.

For a future actor integration fixture, use separate immediate and delayed cases. Assert (1) exact start-refusal detail, (2) combo inactive and pending-card/timer state cleared as appropriate, (3) no failed `PrepareNextAttack` misreported as a refusal, (4) attack count behavior documented for each path, (5) next normal selector tick can start a valid fallback, and (6) reset/EndPlay cancels delayed work. Use transient synthetic actors/components and no pack assets; if that fixture cannot meet prerequisites safely, document the exact blocker instead of claiming these branches tested.

## Verification boundary

Inspected combo routing, C-727's synthetic test, and existing pure combo rule tests read-only. No source/test code changed; no test/build/Editor/PIE/package run occurred. The audit proves neither live combo fallback nor actor timer behavior.
