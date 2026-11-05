# E186 owner-scoped protocol: strafe interruption policy

## Owner decision
Owner decides whether strafe budget and stuck-detector state reset identically for stagger, phase hold, target loss, leash correction, and other interruptions.

## Default and invariants
Preserve current reset behavior. Any new policy remains opt-in and must not extend active strafe beyond the configured budget, change attack eligibility, or leak detector state across generation reset.

## Paired evidence and rollback
Lead compares current control with each approved interruption policy using fixed interruption timing and target movement; verify budget accounting, detector reset, resume direction, and generation reset. Roll back by disabling the new policy and restoring current reset rules. Protocol only; no implementation authorized.
