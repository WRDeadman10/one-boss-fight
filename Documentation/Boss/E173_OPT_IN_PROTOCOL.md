# E173 owner-scoped protocol: selector repeat penalty

## Owner decision
Owner decides whether selector anti-repeat scoring is enabled in a shipped profile, including penalty and memory length. Current audit indicates it is explicit config; this protocol governs future profile opt-in/tuning.

## Default and invariants
Preserve current profile behavior unless approved. Any optional tuning must remain within validated penalty/memory bounds and may only affect score preference, not hard eligibility, cooldown, combo graph outcomes, or real-start accounting.

## Paired evidence and rollback
Lead compares unchanged profile control and approved tuning under repeated equal-card choices, checking bounded memory, reset/new generation, cooldown, and combo-start accounting. Roll back to prior penalty/memory values. Protocol only; no implementation authorized.
