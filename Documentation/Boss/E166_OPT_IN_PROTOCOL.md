# E166 owner-scoped protocol: per-profile difficulty curve

## Owner decision
Owner must decide whether difficulty scaling is a product feature, which input selects normalized difficulty, and acceptable damage/speed/telegraph endpoint values. No default values here are approval.

## Default and invariants
Keep the helper unwired and all shipping behavior unchanged. If approved later, feature remains disabled by default; difficulty is finite and within [0,1]; scales remain positive and within existing caps; no health, move legality, or encounter-reset rules change.

## Paired evidence and rollback
Lead must collect default-off control and enabled-profile runs at low/mid/high inputs, checking damage, speed, telegraph, same move eligibility, reset behavior, and 60 FPS target. Roll back by disabling profile opt-in and restoring prior profile values. Protocol only; no implementation authorized.
