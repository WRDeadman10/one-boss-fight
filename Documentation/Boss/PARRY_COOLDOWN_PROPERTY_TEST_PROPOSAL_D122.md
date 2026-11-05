# Queue D122 — parry-cooldown property test proposal

Date: 2026-11-03  
Scope: deterministic test design from current press rule; no source/test edits or execution.

## Contract from source

`Source/OneBossFight/Player/RPGParryRules.h` accepts a press only when `Now`, `WindowSeconds`, and `CooldownSeconds` are finite, `WindowSeconds > 0`, and `Now >= State.ReadyAt`. An accepted press sets `OpenedAt = Now` and `ReadyAt = Now + max(WindowSeconds, CooldownSeconds)`. A rejected press returns before mutating state. The cooldown therefore cannot be shorter than the window. `RPGParryCooldownAdjacentBoundaryTests.cpp` already checks `nextafter(ReadyAt, -∞)` refusal/state preservation and exact-ReadyAt acceptance. The 10,000-tick schedule test covers deterministic randomized press scheduling for one fixed pair of durations.

## Proposed bounded property

- Use a fixed `FRandomStream` seed and 128 cases with nonnegative `Now` values and finite positive window/cooldown values. State explicit numerical harness bounds that keep `Now + max(Window,Cooldown)` finite; these are test-domain limits, not new product timing limits.
- For each case, assert a fresh-state press succeeds and `ReadyAt == Now + max(Window,Cooldown)`, hence `ReadyAt >= OpenedAt + WindowSeconds` for the tested representable values.
- Save the resulting state. Assert a press at `nextafter(ReadyAt, -∞)` fails and preserves both fields; assert a press at exact `ReadyAt` succeeds and opens at that time. Assert `nextafter(ReadyAt,+∞)` also succeeds when the computed value is finite.
- Include duration pairs with `CooldownSeconds < WindowSeconds`, equal durations, and `CooldownSeconds > WindowSeconds`; these are relational partitions from `max`, not claimed design thresholds.
- Keep NaN/infinity, nonpositive window, and invalid/overflow boundaries in explicit separate cases. Current `Press` does not check whether the addition overflows, so the proposal must not imply that every finite input is safe; if testing that boundary, first decide whether the intended contract is refusal or saturation.

## Acceptance / limits

The design has a deterministic seed, bounded count, nonnegative-time cases, and next-representable cooldown boundaries. It derives all expectations from the current source expression and does not invent gameplay timings. Proposal only; no test is claimed as added or passing.
