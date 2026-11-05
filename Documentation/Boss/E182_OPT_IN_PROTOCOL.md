# E182 owner-scoped protocol: enrage ramp profile

## Owner decision
Owner decides whether an enrage ramp is a shipped feature, its trigger, duration, damage/rate endpoints, and reset ownership.

## Default and invariants
Keep the pure helper unwired and defaults unchanged. Any approved ramp must be bounded, monotonic over its configured interval, neutral outside its active policy as specified, and reset only at the owner-approved lifecycle boundary.

## Paired evidence and rollback
Lead compares baseline against enabled ramp at below/start/interior/end/after and invalid elapsed inputs; verify endpoint values, monotonicity, no duplicate application, and generation reset. Roll back by disabling ramp profile and restoring prior values. Protocol only; no implementation authorized.
