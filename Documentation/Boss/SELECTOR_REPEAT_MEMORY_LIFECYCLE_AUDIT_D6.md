# Selector repeat-memory lifecycle audit (Queue D D6, 2026-11-03)

## Source contract

`NoteStarted(Index, ClockSeconds)` ignores calls when the selector is uninitialized, the index is invalid, or the clock is non-finite/negative (`RPGBossMoveSelector.cpp:85–90`). On accepted calls it stores that candidate's cooldown clock, increments `StartedCount`, removes any prior copy from `Recent`, appends the index, then drops oldest entries until `Recent.Num() <= RepeatMemory`. Scoring multiplies a recent candidate by `RepeatPenalty` (`:60–63`). `Reset` clears cooldown clocks, recent IDs, the tie seed offset, and cone-memory state (`:92–95`).

## Coverage inspected

`FBossMoveSelectorPolicy` verifies equal cards cycle through candidates, memory of two makes the third candidate eligible, and then the oldest candidate becomes eligible again. Its reset case confirms cooldown/history are forgotten. `FBossMoveSelectorBoundedTie` records starts during repeated seeded selections and checks repeatable streams, but does not isolate `StartedCount` reset as the cause of a repeated post-reset tie sequence.

## Lifecycle matrix

| Case | Current source behavior | Test coverage |
|---|---|---|
| Valid new start | Store time, increment tie offset, move ID to newest position. | Anti-repeat policy test covers candidate history; tie test exercises repeated NoteStarted. |
| Same candidate started twice | Remove old occurrence then append once; does not duplicate recent ID. | No direct repeated same-index history assertion found. |
| Memory full | Drop oldest until configured size. | Existing memory-2 cycle checks oldest candidate becomes eligible after a third distinct start. |
| Invalid index or time | Ignore call, leave all history unchanged. | No direct state-preservation test found. |
| Reset | Clear cooldown, history, tie offset, and cone memory. | Existing test verifies cooldown/history outcome; separate cone test verifies cone-memory reset. Tie offset reset is not isolated. |
| `NoteStarted(INDEX_NONE, clock)` after no-choice decision | Ignore; no tie offset or repeat entry added. | No direct no-choice/invalid-index history assertion found. |

## Follow-up test suggestion

Add one bounded fixture with a small candidate list and `RepeatMemory=2`: call `NoteStarted(0)` twice and verify index 0 occupies one recent slot; inject invalid indices and negative/NaN/infinite times and verify the next eligible choice is unchanged; then `Reset`, use a fixed tie seed, and compare the first post-reset sequence to a fresh selector. Keep model frame/time increasing after any actual model start so stale-decision refusals do not mask selector memory. Existing `NoteStarted` is deliberately an observer hook called after real starts; this audit does not propose changing its API.

## Verification boundary

Inspected selector source and test declarations read-only. No source/test code changed; no tests/build/Editor/PIE/package run occurred. The report distinguishes present policy coverage from untested invalid-input and tie-reset cases.
