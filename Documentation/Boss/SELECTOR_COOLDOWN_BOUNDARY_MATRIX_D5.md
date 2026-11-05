# Selector cooldown boundary matrix (Queue D D5, 2026-11-03)

## Source rule

`FRPGBossMoveSelector::Initialize` accepts each cooldown only when finite and in `[0, 1e6]` (`Player/RPGBossMoveSelector.cpp:21`). `NoteStarted` records a finite nonnegative clock only for a valid candidate index (`:85–90`). During selection, a previously started candidate is refused while `S.ClockSeconds - LastStartClock[I] < CooldownSeconds` (`:55–56`). Therefore equality is eligible. `Reset` clears last-start clocks, repeat history, seed count, and cone memory (`:92–95`).

## Existing test coverage inspected

`FBossMoveSelectorPolicy` (`Tests/RPGBossMoveSelectorTests.cpp:76–82`) starts candidate A at clock 100 with a 2-second cooldown, observes refusal at 101.5, accepts at exactly 102, then resets and accepts on a lower clock (50). This covers strict `<` and reset behavior. `FBossMoveSelectorInit` checks a negative cooldown is rejected. It does not check just-above edge, zero cooldown after a start, invalid `NoteStarted` clocks/index, or a still-cooling candidate losing to an eligible alternative.

## Boundary matrix

| Scenario | Expected source behavior | Coverage status |
|---|---|---|
| First use, any valid clock | No recorded start (`-1` sentinel); cooldown does not apply. | Existing general selector choices cover first use; no dedicated positive cooldown assertion. |
| 2s cooldown at elapsed 1.999s | `Selector.Cooldown`; candidate not scored. | Existing 1.5s case covers the interior. |
| 2s cooldown at elapsed exactly 2.0s | Eligible because comparison is strict `<`. | Existing test covers equality. |
| 2s cooldown at elapsed 2.001s | Eligible. | No dedicated just-above assertion. |
| Zero cooldown after `NoteStarted` | Eligible immediately at same valid monotonic time, subject to model stale-decision constraints. | No dedicated case. |
| Reset then clock earlier than prior start | Cooldown/history are forgotten. | Existing test covers clock 50 after prior start 200. |
| Invalid/negative/nonfinite `NoteStarted` time | Ignored; prior valid start clock and repeat state should remain unchanged. | No direct test found. |
| Invalid candidate index to `NoteStarted` | Ignored; no other candidate history changes. | No direct test found. |
| Cooling candidate with another eligible candidate | Cooling card is traced as refused; another candidate may be selected. | Current cooldown fixture has one candidate, so fallback selection is not directly covered there. |
| Cooldown elapsed but model snapshot stale | Shared model refusal precedes cooldown result; no card selected. | Model stale frame/clock tests exist, but no selector trace precedence assertion was found. |

## Bounded fixture suggestion

Extend the selector policy test with independent fresh selectors for 1.999, 2.0, and 2.001 elapsed seconds; zero cooldown after start; invalid `NoteStarted` timestamp/index preserving a prior valid clock; and one cooling plus one available card. Use increasing model frame/time for every post-start selection so model staleness does not mask cooldown behavior. Keep one explicit stale-model case to lock down refusal precedence. These are test proposals only; no code change or run was made.

## Verification boundary

Inspected selector implementation and automation test source read-only. No source/test code changed; no tests, build, Unreal Editor, PIE, or packaging was run. This matrix reports the implementation's current comparison semantics and the inspected test gaps.
