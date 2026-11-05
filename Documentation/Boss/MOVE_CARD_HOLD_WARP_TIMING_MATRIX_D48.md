# Move-card hold and warp timing matrix (Queue D D48)

## Boundary matrix

| Field/path | Accepted boundary and rule | Existing test evidence | Runtime consumer / edge |
|---|---|---|---|
| Hold start | Enabled hold: `CommitSeconds <= HoldAtSeconds < ActiveStartSeconds`; duration `0 < min <= max <= 3`. | `HoldStartBoundaryMutation`: exact commit accepted, adjacent float below rejected. `HoldEndBoundary`: float immediately below active start accepted, equality rejected. | `TickHold` starts when `Position >= HoldAtSeconds`, so a tick that advances past the trigger starts the pause at the observed wall-clock time, not retroactively at exact card time. |
| Hold duration/release | Seeded chosen duration lies in `[min,max]`; range validation is separate from card-time start. | `RPGBossCueTests`: deterministic, fixed-duration and domain cases; sweep checks sampled range. | While active, `TickHold` waits while `Now < HoldEndsAt`; release occurs at `Now >= HoldEndsAt`, restores play rate and fires hold-release cues. Watchdog adds the maximum authored hold. |
| Warp start | Enabled warp: `CommitSeconds <= WarpStartSeconds < WarpEndSeconds`. | `WarpStartBoundaryMutation`: exact commit accepted, adjacent float below rejected. | `TickWarp` clips to `Lo=max(previous, start)` and requires a positive overlap `Hi > Lo`; no step at zero-width overlap. |
| Warp end | `WarpEndSeconds <= ActiveEndSeconds`; it must be strictly after start. | `WarpEndBoundary`: exact active end accepted, adjacent float after rejected. `WarpStartBoundaryMutation` supplies a positive interval. | `TickWarp` clips `Hi=min(position,end)`; the end is inclusive as a bounded interval endpoint, but only positive-duration portions move. Later ticks can log summary without applying a step. |
| Warp disabled/easing | Both distance and angle budgets zero disable movement; ease requires positive distance budget. | Base card tests exercise off defaults, valid budgets, equality/ordering and out-of-bound end/start cases. | `TickWarp` returns if neither budget is positive. `WarpEaseInOut` uses the separate `RPGBossApproach::StepCm` curve over normalized window fractions; it does not change start/end validation. |

## Interpretation and gaps

The card validator establishes the authored interval contract; the specialized boundary fixtures test the key exact/adjacent start and end cases. Runtime hold and warp consumers have separate time sources and guards: hold uses observed montage card position to trigger, then absolute world time for its pause; warp advances only over the positive clipped card-time overlap and recomputes the remaining target distance/angle. These are source-derived semantics, not live actor timing proof.

The inspected specialized tests do not assert a runtime tick that lands exactly on or steps across HoldAt, hold release equality, warp zero-width overlap, or a final warp step at `WarpEndSeconds`. The `WarpExactDurationBoundary` fixture tests `WarpStepCm`'s budget/time helper, not MoveCard `TickWarp` scheduling. Keep these distinctions when interpreting the tests. Source/test review only; no tests, build, Unreal, or Editor run.
