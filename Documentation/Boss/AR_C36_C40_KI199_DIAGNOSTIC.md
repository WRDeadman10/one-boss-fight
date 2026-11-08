# AR-C36–C40 — KI-199 first-dodge observation boundary

## Scope

The current `Scripts/Editor/probe_first_dodge_after_draw.py` is an active PIE probe: it enters combat, sends R2 draw input, sends dodge input, moves the pawn in the moving case, and ends PIE. It is not read-only. This batch adds only a post-press observation snapshot inside that existing scenario. It does not add calls that inject, consume, activate, reorder, or dispatch input. No pack `InputBuffer` internals or root cause are inferred.

`first_dodge_snapshot()` reports fields available through the existing project/editor APIs: case and attempt labels, press/backstep counters, dodge stage, current montage and position, and the reported buffered-input tag. The tag is obtained through the reflected `Get Buffered Input Tag` call already used by this probe; this audit verifies call placement and the returned observation only, not the Blueprint/plugin implementation's internal semantics. Existing movement/input injection and `end_play()` remain in the driver outside the snapshot helper.

## Observable events and boundaries

| Event | Probe fields | Interpretation limit |
|---|---|---|
| Draw ready | `draw_ready`, attempt, combat enabled, current montage | Confirms the project's readiness readback; does not identify pack input-buffer state. |
| Before dodge press | case, press ordinal, velocity, last/pending movement-input sizes, buffered tag | Movement values are project-side samples at the press boundary. |
| Immediately after one input tick | buffered tag before/after, case, press ordinal | A changed tag is correlation only; it does not prove which plugin callback consumed or retained it. |
| First-press samples | `stage_label=post_press_observation`, active montage/position, moved distance, stage, press/backstep counters, buffered tag | Repeated samples observe the first 0.75 s after the first press; montage absence is not itself a root-cause diagnosis. |
| Result | first standing/moving montage-seen, moved distance, counters; two repeat result lines | Separates first press from later presses in this process; no montage assignment is performed. |

The new helper is called only from the already existing first-attempt sampling window. `test_probe_first_dodge_after_draw_contract.py` parses the helper AST to reject input-injection, activation, buffer-consumption, dispatch, or lifecycle mutation calls and checks that the input down/tick/up sequence remains before the observation call. This does not certify the entire probe as non-mutating; the probe necessarily changes gameplay state to create the scenario.

## Minimal Lead observation matrix

Run one fresh process per row with the approved BUILD-263-or-later runtime identity and one unchanged probe revision. Set `FIRST_DODGE_CASE` before launching the probe; use the same encounter route/configuration, startup, draw cadence, controller, and machine conditions for the paired first/repeat observations. Repeat the matrix on legacy and selected-data routes only when Lead has both routes ready.

| Route | Process case | Inputs and captures |
|---|---|---|
| legacy | standing | Fresh process; normal R2 draw; first immediate dodge; two repeats. |
| legacy | moving | Fresh process; normal R2 draw; same bounded forward movement before first dodge; two repeats. |
| selected-data | standing | Same as legacy standing; route identity recorded. |
| selected-data | moving | Same as legacy moving; route identity recorded. |

The first press and repeats in a single process distinguish first-use behavior from that process's later controls. Cross-route differences remain descriptive until same-build, same-settings receipts are reviewed. No montage is assigned, no threshold/input mapping is changed, and no new retry behavior is proposed by this batch.

## Stop and return checklist

Stop a row as incomplete if `draw_ready` is false, route/build identity is absent, the requested case label is invalid, first-press observables or normal completion are missing, or the log indicates an error. Retain failed logs; do not silently substitute a row. Return the exact command/environment, build and source identity, route, case, raw-log SHA-256, full log, and separate first/repeat summaries. A missing buffered-tag read remains `UNKNOWN` and must not be treated as an empty tag.

Before attributing a cause to Enhanced Input, the pack input buffer, activation ordering, or route data, Lead must provide same-build route receipts and the relevant runtime diagnostics. Any runtime mutation/retry change needs its own bounded hypothesis, acceptance rule, and separate review. KI-199 remains open for cause and package proof.

## Offline validation

`python -m unittest Scripts.Editor.test_probe_first_dodge_after_draw_contract -v` covers the new snapshot helper's AST boundary, sample labeling, first/repeat distinction, and the fact that the surrounding PIE probe remains state-changing. It does not launch Unreal or validate runtime behavior.
