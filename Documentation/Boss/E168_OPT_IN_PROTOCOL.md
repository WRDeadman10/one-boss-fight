# E168 owner-scoped protocol: punish limiter profile

## Owner decision
Owner decides whether repeated punishes are limited, which events count, and the allowed attempt/cooldown budget.

## Default and invariants
Keep limiter disabled by default. If approved, it may refuse only eligible punish attempts after the configured budget; ordinary neutral selection, defensive recovery, authored animation windows, and target safety must remain unchanged.

## Paired evidence and rollback
Lead compares default-off control and enabled profile with repeated flask/heavy punish opportunities, confirming limiter activation, no false activation, reset at encounter restart, unchanged ordinary routes, and performance. Roll back by disabling the profile gate and restoring prior values. Protocol only; no implementation authorized.
