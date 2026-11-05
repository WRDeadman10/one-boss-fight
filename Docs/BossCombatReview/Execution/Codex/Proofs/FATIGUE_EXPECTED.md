# Fatigue feature expected evidence

## PASS telemetry tokens

- `fatigue whiffs=1 scale=1` — first consecutive whiff is within the one-whiff grace allowance; scale remains 1.0.
- `fatigue whiffs=2 scale=0.95` — first reduction after grace.
- `fatigue whiffs=3 scale=0.9` — second reduction after grace.
- For the R15A6 profile (`FatigueGraceWhiffs=1`, `FatigueFloor=0.5`), the rule is `max(0.5, 1 - max(0, whiffs - 1) * 0.05)`. The floor is first reached at 11 consecutive whiffs (`scale=0.5`) and remains 0.5 on later whiffs.
- After a confirmed contact resets the streak: `fatigue whiffs=0 scale=1`.

## Per-instance whiff evidence (manual requirement)

For each instance counted in the streak, inspect its full Open-to-Close window and require no `hit`, `CARD_HIT`, or `guard_state` contact result of Accepted, Guarded, or Parried. A `sweep` record or a `fatigue whiffs=N` line alone does not establish a whiff. Keep the window start/end from `event kind=Open/Close`, all contact rows, and the next `fatigue` row together in the review evidence. After the first real accepted/guarded/parried contact, the next state must reset to zero.

## Current R15A6 evidence status

In `B_FATIGUE/pie_run2_six_shifts/editor_raw.log`, fatigue advances 1/1.00 (`:1791`), 2/0.95 (`:1869`), and 3/0.90 (`:2025`). A source search found no `hit`, `CARD_HIT`, or `guard_state` contact records for instances 1–3. Instance 4 has an Accepted contact at `:2104–2106`, followed by `fatigue whiffs=0 scale=1` at `:2269`, which is the reset control. Therefore this run supports three consecutive whiffs and a reset after contact; it does not reach the configured 0.5 floor. The later run ended `Framework.Selector.NoCandidate` as documented in TASKS/TEST_PLAN, so it is not a clean floor-reaching proof. A future run must sustain 11 consecutive verified whiffs and preserve a complete terminal result before claiming the floor.

## Setup
## Control
## PASS
## FAIL
