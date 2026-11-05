# E179 owner-scoped protocol: poise regeneration prototype

## Owner decision
Owner decides whether poise regeneration is a product feature, its delay/rate/cap, interruption rules, and whether it applies during neutral, attack, or recovery states.

## Default and invariants
Keep the helper unwired and default behavior unchanged. If approved, regeneration remains bounded by maximum poise and must not erase stagger, alter hit accounting, or run through generation reset/terminal states.

## Paired evidence and rollback
Lead compares no-regeneration control with an enabled profile across damage, delay, cap, stagger, recovery, and restart cases; include duplicate-tick and invalid-time controls. Roll back by disabling the profile gate and restoring previous values. Protocol only; no implementation authorized.
