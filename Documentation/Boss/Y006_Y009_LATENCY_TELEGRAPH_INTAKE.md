# Queue Y Y006–Y009 — latency and telegraph evidence intake

Date: 2026-11-06. Read-only inspection of the Lead run mailbox tail, current latency driver, and retained paired telegraph receipts. No Editor, PIE, game, build, or test run was performed.

## Y006 — six input-to-montage sessions

**WAITING ON LEAD** for the six Legacy/selected sessions at 30/60/120 FPS. No `InputMontageLatency` session logs were found in the searched `Saved`/`Docs` paths or mailbox tail. The existing W-C036 sheet remains a run plan; none of its six samples can be filled from other tests.

## Y007 — what the current latency log measures

`Scripts/Editor/pie_input_montage_latency.py` sets `press_real` during the `arm` callback, injects the action on the next callback, and observes montage state on each Slate post-tick callback (`:96-125`). It logs only the total elapsed time and the `dt` of the callback that detects the montage (`:110-125`). It does not log the first injection timestamp or the intervals across the observation window, so a raw `observed_ms` cannot be decomposed into arm-to-injection and injection-to-first-observation, and the single terminal `tick_s` is not a cadence trace.

Minimal diagnostic change proposal (not applied): record the monotonic time at arm and immediately before the first injected action; maintain max and recent callback `dt` during observation; log those fields with the first changed montage and run identity. Report `arm_to_first_injection_ms`, `first_injection_to_observed_ms`, `total_arm_to_observed_ms`, and the observed callback interval/max. That separates the current scheduling gap from the post-tick sampling bound without calling the result device-to-photon latency.

## Y008/Y009 — retained paired telegraph evidence and A1–A6 gaps

An earlier search scoped to `Saved` missed historical Lead receipts under `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/`. Existing paired driver receipts provide limited historical telemetry, but none is a synchronized tell/player-input/contact video or a reaction-window measurement:

| Move | Historical paired log evidence | Comparator / limitation | Synchronized tell/input/contact capture |
|---|---|---|---|
| A1 | BUILD-220 `pie_telegraph_d5`, `_d2`, `_b220`; timing/rate checks | All three reports have observable mismatches (2/3/4); not parity pass | Missing |
| A2 | Same BUILD-220 `pie_telegraph` pairs; configured windup check | Same observable mismatches; no player response | Missing |
| A3a | Same BUILD-220 `pie_telegraph` pairs; windup/rate checks | Same observable mismatches; no player response | Missing |
| A3b | Branch is described in driver source but no paired A3b trial receipt identified | No A3b measured paired result | Missing |
| A4 | BUILD-221 `pie_a4_low_sweep_t1b` pair reports MATCH; earlier `b220`, `d2`, `r2`, `t1` pairs have mismatch states | Runtime automation parity only; not visual reaction evidence | Missing |
| A5 | BUILD-220 `pie_a5_heal_punish_d5` and BUILD-221 `_t1` paired receipts | Both have observable mismatches (2/1); heal/javelin driver checks are not synchronized player-response video | Missing |
| A6 | BUILD-220 `pie_legend_d5` and BUILD-231 `pie_legend_t2` pair receipts | Runtime Legend checks; not a six-move synchronized response capture | Missing |

The BUILD-220 A1/A2/A3a observations are historical and their parity comparisons fail on typed observables. A4 has one later passing automation pair, but the run is still not a synchronized response capture. Do not conflate any of these logs with fresh after-R6 evidence, visible readability, or a player's reaction window.

## Disposition

Y006 remains WAITING ON LEAD. Y008/Y009 can reuse the historical telemetry as limited source-linked timing evidence, while the six fresh latency sessions and synchronized paired visual/response captures remain unrun. No W-C038 reaction-window or feel status is upgraded.
