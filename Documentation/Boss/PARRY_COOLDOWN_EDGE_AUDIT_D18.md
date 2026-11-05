# Parry cooldown edge audit (Queue D D18, 2026-11-03)

## Contract

`RPGParry::Press` rejects only when `Now < ReadyAt`; equality is accepted. On success it updates both `OpenedAt` and `ReadyAt=Now+max(WindowSeconds,CooldownSeconds)`. A shorter configured cooldown is therefore raised to at least the full window. Invalid time/duration or nonpositive window also refuses before either state field mutates (`Player/RPGParryRules.h:16–20`). The component applies this pure rule after stamina preflight and calls it with world game time (`Player/RPGPlayerParry.cpp:65–104`).

## Existing checks

| Behavior | Current regression coverage | Result / remaining gap |
|---|---|---|
| Exact cooldown boundary | `OneBossFight.Framework.Parry.CooldownAdjacentBoundary` (`RPGParryCooldownAdjacentBoundaryTests.cpp`) uses `nextafter(ReadyAt,-infinity)`, proves the earlier press is refused without changing `OpenedAt`, then proves exact `ReadyAt` succeeds. | Below/equal edge is explicit. The test does not assert the new `ReadyAt` value after the accepted second press. |
| Ordinary refusal and reopening | `OneBossFight.Framework.Parry.Rules` (`RPGParryTests.cpp`) checks at 10.6 refusal and at 10.7 reopening for a .7-second cooldown from 10.0. | Covers concrete equality and that the refused attempt does not open a new window. |
| Cooldown shorter than window | Same Rules test uses window .5/cooldown .1, refuses at .4 and accepts at .5. | Confirms the max(window,cooldown) rule. |
| Rejected-state preservation | `Rules` checks the window stays closed after a cooldown refusal; `PressSchedule` compares both `OpenedAt` and `ReadyAt` across each randomized cooldown refusal. | Pure-rule mutation guard is covered with deterministic seed; no component stamina rollback assertion is part of this test. |
| Encounter/component reset | `FState` default initialization and selector-independent component member are visible in source; there is no parry-state `Reset()` call/API in `URPGPlayerParry`. | No explicit reset test or reset hook. Component lifetime, not boss encounter restart, owns this state; intended respawn/repossess behavior needs product/runtime intent before adding a reset. |

No inclusive/exclusive mismatch was found in cooldown source or current pure tests. `Press` permits a new window at exact `ReadyAt`; the window can be shorter than cooldown but never longer than readiness. Component-level failure paths are separate: insufficient/missing stamina refuses before state mutation, while a stamina-paid cooldown refusal schedules a rollback (`RPGPlayerParry.cpp:65–109`); see D19 for cost coverage.

Lead disposition C-744: record the unverified respawn/repossess state-retention possibility as low KI-175. The component state is currently instance-owned; no claim is made that an actual project respawn reuses the component.

## Verification boundary

Static source and existing-test inspection only. No tests were run and no code changed. The only suggested assertion is to check the second accepted press advances `ReadyAt` from the newly accepted time; current tests already establish the principal boundary and refusal-state preservation.
