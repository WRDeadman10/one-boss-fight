# Selector memory across normal and combo starts (Queue D D15, 2026-11-03)

## Result

The normal selector route and both combo continuation routes all call `Selector.NoteStarted` after `StartCard` succeeds (`RPGFrameworkBossCharacter.cpp:521,799,815`). Therefore each successful start updates the same selector cooldown clock, repeat-history order, and seeded tie offset. Combo continuation bypasses selector choice and its pre-start cooldown/repeat scoring; it does not bypass the post-start memory update. A refusal returns before `NoteStarted`, so failed starts do not affect selector memory. No production change is justified by this comparison.

This corrects stale wording in the earlier parity notes: D1 said combo starts capture no selector memory, and Queue C S1 said they skip selector history. The accurate distinction is that combo starts do not consult selector memory to choose/authorize the authored next card, but successful starts are recorded afterward and influence later normal selections.

## Route comparison

| Route | Selector consult before start | Start snapshot | Post-success update | Refusal behavior |
|---|---|---|---|---|
| Normal decision | `Select` applies model eligibility, candidate cooldown, recent-repeat penalty, and tie selection (`RPGBossMoveSelector.cpp:40–80`). | Reuses decision snapshot and selected trace cone slack (`RPGFrameworkBossCharacter.cpp:518–519`). | `NoteStarted(index, S.ClockSeconds)` after `StartCard` succeeds (`:519–521`); clocks, `StartedCount`, and `Recent` update (`RPGBossMoveSelector.cpp:85–90`). | Start refusal fails before memory update (`:519`). |
| Immediate combo continuation | Authored next node resolves directly to a candidate; no fresh selector scoring/cooldown/repeat gate (`RPGFrameworkBossCharacter.cpp:787–800`). | Current combo-gate snapshot `S`. | Same `NoteStarted` call after successful start (`:799`). | Invalid candidate or refused start ends combo; no memory update (`:795–798`). |
| Delayed combo continuation | Pending card index was resolved from authored edge before pause; no selector scoring/cooldown/repeat gate at wake (`:803–815`). | Fresh `MakeSnapshot()` at pause expiry (`:807`). | Same `NoteStarted` call after successful start (`:815`). | Invalid candidate or refused start ends combo; no memory update (`:811–813`). |

`NoteStarted` validates initialization, candidate index, finite nonnegative clock; accepted records set that candidate's last-start clock, increment tie seed offset, move it to newest position in `Recent`, and evict oldest entries to `RepeatMemory` (`RPGBossMoveSelector.cpp:85–90`). `Select` then uses those clocks/history for normal candidate eligibility/scoring (`:50–64`) and `StartedCount` in the deterministic tie stream (`:72–78`).

## Intent and test boundary

The authored combo edge intentionally bypasses selector policy at the point of choosing its next card. Whether recording that card should affect subsequent normal cooldown/repeat/tie behavior is a design contract not established by these callsites alone. Existing pure selector tests cover the memory mechanics; inspected combo tests cover pure graph/fallback behavior, not the actor's three start callsites as a shared update contract. A bounded actor test should start a normal card, an immediate combo card, and a delayed combo card, assert each successful route updates cooldown/history/tie offset exactly once, then assert refusal leaves those unchanged. Keep the authored-edge choice independent of selector cooldown; do not change runtime behavior without Lead intent.

## Queue E route fixture boundary (2026-11-03)

`RPGBossSelectorRouteLifecycleTests.cpp` adds synthetic model/selector checks that an immediate continuation can start from its current combo snapshot and record that snapshot's clock, and that a delayed pending card is refused at the pre-pause range but accepted from the wake snapshot. The tests also verify subsequent cooldown visibility. They do not instantiate `ARPGFrameworkBossCharacter` or execute its immediate/delayed callsites; those integration claims remain source-derived until an actor-level fixture is added.

## Verification boundary

Static source and documentation review only. No code, automation, build, or Editor changes/execution. `git diff --check` was run on the scoped documentation changes.
