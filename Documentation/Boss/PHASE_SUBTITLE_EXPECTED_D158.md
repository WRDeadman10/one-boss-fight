# Opt-in boss phase subtitle expected sheet (Queue D158)

Status: protocol only. No subtitle or feature is implemented/enabled. Review this protocol and default-off behavior before implementation. Live Editor/packaged proof is Lead-owned; player-facing strings, duration, placement, and art remain unselected.

## Claim and source boundary

The proposed subtitle is hidden by default, appears only on an actual boss phase transition, reflects the phase entered, and clears on the reviewed transition/terminal/restart behavior. It is informational only and must not change phase thresholds, transition timing, attacks, damage, input, or boss state. Internal phase identifiers in logs/source are not approved player-facing copy, and source-visible phase state does not prove an authored widget or loaded map behavior.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw log/screenshot path and hashes | **Expected:** unique ID, immutable evidence and post-capture hash. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and phase configuration. **Observed:** pending. |
| Boss/generation/phase | **Expected:** actual boss identity, generation/run ID, phase before/after and transition trigger/time. **Observed:** pending. |
| Feature state | **Expected:** subtitle toggle read back off by default; enabled only in paired run. **Observed:** pending. |
| Presentation setup | **Expected:** fixed display mode/resolution and screenshot or video capture. Record any accessibility/display options. **Observed:** pending. |

## Paired cases

Use matched encounter baselines and identical phase-transition conditions. Change only the reviewed subtitle toggle.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default hidden | Feature off/read-back off; exercise or reach the same phase transition and capture phase state/log plus screen. | No new subtitle is visible; phase transition and gameplay establish baseline. |
| Enabled transition | Repeat the same transition with feature enabled. Capture transition event/time, phase before/after, subtitle text and screen timing. | Subtitle corresponds to the phase actually entered and appears only after the real transition. Timing and gameplay state match the paired control. |
| No transition | Exercise a non-transition interval and a rejected/failed transition attempt where safely available. | No new or incorrect phase subtitle appears. Missing/invalid setup is inconclusive. |
| Restart and terminal cleanup | After subtitle is visible, exercise the approved restart path; separately test terminal completion/failure when available. Capture generation and screen. | Stale subtitle clears at the approved reset/terminal boundary and does not appear in the next generation until a new transition. |

## Evidence interpretation and limits

- **Measured:** phase/generation transitions and timestamps from logs/readback; text and visibility from screenshot/video with timestamps.
- **Inferred:** correspondence between subtitle and phase only when phase identity and generation match. An intended trigger is not evidence of an actual transition.
- **Manual:** wording clarity, legibility, placement, duration, and whether the subtitle obscures combat.
- Do not claim runtime restart cleanup from source alone. Internal phase labels do not establish approved copy; map/widget behavior remains UNKNOWN until live observation.

## Failure and stop conditions

Fail if default-on, subtitle shows the wrong phase, appears without transition, changes gameplay/transition timing, or remains stale after the reviewed reset/terminal path. Stop if the phase event cannot be correlated to a generation, no repeatable transition can be reached, or copy/timing/visual choices need owner approval. Missing or invalid evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No string, UI, asset, or source changes; no test/build/Editor execution, screenshot, or runtime claim. Implementation is not authorized before review.
