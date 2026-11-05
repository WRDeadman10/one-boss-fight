# E167 owner-scoped protocol: fatigue profile

## Owner decision
Owner decides if player-pattern fatigue belongs in the shipped boss, its triggers, grace count, minimum rate, and approved profile.

## Default and invariants
Keep fatigue disabled by default (zero floor) unless explicitly approved. If enabled, it may scale rate only within validated bounds; it must not bypass eligibility, shorten authored active windows, alter damage, or persist state across encounter reset.

## Paired evidence and rollback
Lead compares default-off control against an enabled profile under repeated player whiffs, with equal move/loadout and logs for rate scale, attempts, reset, and performance. Roll back by restoring zero floor and prior profile values. Protocol only; no implementation authorized.
