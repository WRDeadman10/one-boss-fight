# Queue D123 — parry-cost property test proposal

Date: 2026-11-03  
Scope: deterministic test design from current pure cost rules; no source/test edits or execution.

## Contract from source

`RPGParryCostRules.h` defines `CanPress(Stamina, Cost)` for finite nonnegative values with `Stamina >= Cost`. `StaminaAfter` returns zero for invalid/negative inputs; otherwise it subtracts full cost for a non-parry or half cost for a parry and clamps at zero. `ParryRefund` adds half the paid cost and caps at `MaxStamina`; invalid input returns zero. Existing `RPGParryCostTests.cpp` covers representative exact/insufficient values, invalid values, half/full costs, zero floor, and refund cap.

The component charges full cost before attempting the parry; failed cooldown presses attempt rollback; successful parries later refund half. That write/retry lifecycle is not exercised by a pure helper property and must not be inferred from it.

## Proposed bounded property

- Use fixed `FRandomStream` seed and 128 cases. Generate finite, nonnegative stamina, cost, and max-stamina values in explicit small harness ranges to avoid overflow and make decimal comparisons deterministic; those bounds are not gameplay limits.
- For `Stamina >= Cost`, assert `CanPress` is true; for `Stamina < Cost`, assert false. For all valid pairs, assert both `StaminaAfter` results remain in `[0, Stamina]` and `StaminaAfter(false) <= StaminaAfter(true)`.
- Derive conservation from the helper's explicit net-cost operation: within the non-saturating region, `Stamina - StaminaAfter(false) == Cost` and `Stamina - StaminaAfter(true) == Cost * .5`. At/near zero, assert the clamp and do not incorrectly require exact cost conservation when a direct helper call has insufficient stamina.
- For valid `Stamina`, `MaxStamina`, and `Cost`, assert `ParryRefund` lies in `[0, MaxStamina]` and is monotone nondecreasing in the input stamina until capped. Include below-cap and cap-reaching partitions. State explicitly that `MaxStamina < Stamina` is accepted by the helper and immediately caps output; component attribute validity is a separate contract.
- Keep NaN/infinity, negatives, and values near floating-point overflow as named explicit cases, not part of the generated domain. The component's fallback branch when maximum-stamina read fails (`After += PaidCost * .5`) differs from `ParryRefund` and is not represented by this pure helper property.

## Acceptance / limits

The proposal defines deterministic bounded generation, refusal, stamina bounds, half/full-cost conservation where unsaturated, and refund cap behavior from source. It does not claim component-level charge/rollback/refund reliability or a passed test.
