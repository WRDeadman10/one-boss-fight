# E184 owner-scoped protocol: flask threshold profile

## Owner decision
Owner decides whether flask-punish threshold and response are profile-tunable, including evidence window, threshold, and action cap.

## Default and invariants
Keep current profile and behavior unchanged. Any opt-in values remain validated and bounded; the feature may influence selection preference only, not create moves, bypass cooldowns, or alter the player's flask action.

## Paired evidence and rollback
Lead compares control and approved profile under below/equal/above flask counts, expired evidence, invalid inputs, and generation reset. Verify no false punish and no changed ordinary candidate eligibility. Roll back to previous profile values or disable the opt-in. Protocol only; no implementation authorized.
