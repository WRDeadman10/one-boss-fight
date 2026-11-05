# Opt-in telegraph color accessibility mode expected sheet (Queue D154)

Status: protocol only; no palette or feature is implemented/enabled here. Review this sheet and default-off behavior before implementation. Live Editor/packaged verification is Lead-owned. Any palette values, contrast target, supported color-vision profile, or owner-facing art choice remains unselected.

## Claim and invariant

With the mode off, the existing telegraph presentation is the control. With it on, the approved palette may change telegraph colors only; the same attack must retain identical selection, warning onset/duration, animation/montage timing, parry window, hit window, damage, and terminal outcome. Color must not be the only signal for attack phase or danger. Source `RPGAttackTracker` owns telegraph timing/animation-rate behavior; this sheet does not claim what authored Blueprint or pack materials display in the loaded arena.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw log/screenshot paths and hashes | **Expected:** unique IDs, preserve raw files and bind hashes after capture. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, boss/profile and relevant authored asset identities. **Observed:** pending. |
| Feature state/palette | **Expected:** toggle read back default-off; record exact approved palette/config and material/widget path in enabled run. **Observed:** pending. |
| Attack/timing identity | **Expected:** repeat same attack/card, phase, generation and seed or deterministic setup; record telegraph onset, animation state/rate, parry/hit windows and end. **Observed:** pending. |
| Display/capture | **Expected:** fixed display mode, resolution, brightness/HDR and color settings; record capture method. **Observed:** pending. **Unknown display settings invalidate direct visual comparison.** |

## Paired cases

Reset to the same baseline and compare each attack with the mode off and on, changing only the reviewed palette toggle. Include every telegraph phase intended to be covered (windup, active/contact, recovery as applicable) and at least one parryable attack.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default visual control | Toggle read back off; record actual colors, non-color cues, attack identity, onset/duration, animation rate, parry/hit windows, and screen capture. | Establishes a valid baseline. Missing or inconsistent telegraph setup is inconclusive. |
| Enabled palette | Toggle on; repeat same attack and state; capture same timings and direct visual evidence. | Approved palette is visible and distinguishable under recorded display conditions; a non-color cue still communicates phase/danger; attack identity and all timing/combat fields match control. |
| No-telegraph/refusal or terminal clear | Exercise a refused/not-started attack and a completed/aborted attack where safely reachable. | No stale colored telegraph remains or appears for a non-active attack; the toggle changes presentation only. |

## Evidence interpretation and limits

- **Measured:** attack/phase identity and source-tokenized timing/outcome fields, with raw file/line references; control and enabled screenshots with timestamps.
- **Inferred:** timing/combat equivalence only from paired runs with identical attack identity and setup. Report observed deltas; do not round away potentially meaningful timing changes.
- **Manual:** palette legibility, contrast, non-color cue clarity, flicker/obscuration, and appearance for any intended accessibility profile. A screenshot or token validator cannot establish accessibility for all users.
- Do not claim a particular accessibility standard or supported vision profile unless separately approved and tested. Pack material/Blueprint values and packaged appearance remain UNKNOWN until inspected live.

## Failure and stop conditions

Fail if mode is on by default, attack identity or any timing/combat outcome changes, a phase is communicated by color alone, or the enabled palette is indistinguishable under the recorded setup. Stop if the palette requires an unreviewed art/product choice, the authored material cannot be identified, display conditions vary between pairs, or timing telemetry cannot distinguish an actual change. Invalid setup or missing evidence is inconclusive, not pass.

## Verification boundary

Expected protocol only. No palette choice, source/UI/assets changes, tests/build/Editor execution, screenshots, or runtime claims. Implementation is not authorized before review.
