# Tie-band seeded proof expectations (S120)

## Deterministic control

Use the selector fixture already specified by `RPGBossMoveSelectorTests.cpp` (`OneBossFight.Framework.Selector.BoundedTie`): three eligible cards with range 50–150 cm, weights A=1.0, B=0.95, C=0.5, snapshot range 100 cm (their midpoint). Range factor is 1, and reset/initial state has no repeat penalty, so scores are exactly 1.0, 0.95, 0.5. Set `TieBand=0`, `TieSeed=12345`, reset before the run, and perform 100 starts. The deterministic control must choose A on every decision; no RNG tie selection is active.

## Paired-seed runs

For each run, initialize a fresh selector and model, reset selector state, and use the same ordered snapshots and call sequence. Invoke `NoteStarted` once after each successful selection so `StartedCount` advances identically. Use `TieBand=0.1`, whose threshold is `best * (1 - 0.1) = 0.9`; A and B belong to the top tier, while C is below it and must never be selected.

- Pair 1: seed 12345 twice for 1000 decisions. The full selected-index sequences must match exactly; all selections must be A or B, and each must occur more than 300 times for the existing distribution check.
- Pair 2: seed 54321 for 1000 decisions, paired against the seed-12345 sequence. The sequence must differ, while C remains absent. This demonstrates seed-dependent choice within the bounded top tier rather than unrestricted weighted choice.
- Narrow-band control: seed 12345, `TieBand=0.02`; threshold 0.98 leaves only A in the tier, so 200 selections must all be A.

The seed input is `TieSeed + StartedCount`; count starts at zero and increments only in `NoteStarted` (`RPGBossMoveSelector.h:68`, `.cpp:78,86–95`). The selected card's index determines its stream draw from the inclusive top-tier index range (`.cpp:72–80`). Keep candidate order, weights, card ranges, snapshot times/order, start notifications, and selector resets identical in paired runs. Do not infer sequence reproducibility from matching aggregate counts alone.

## Evidence boundary

The existing engine-free automation test already encodes these exact pairs and controls in `Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp:102–123`. This checklist turns that test into a timestamp/call-order proof recipe; no separate retained PIE tie-band run was found in the searched Claude execution artifacts. The test proves selector behavior, not profile asset readback or live encounter wiring. Source/evidence review only; no tests or Unreal run by Codex.

## Setup
## Control
## PASS
## FAIL
