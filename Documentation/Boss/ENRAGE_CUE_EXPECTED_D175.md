# Opt-in enrage presentation cue expected sheet (Queue D175)

Status: protocol only. No cue or feature is implemented/enabled. Review default-off behavior, cue modality and trigger before implementation. Live Editor/packaged verification remains Lead-owned; this sheet chooses no sound, visual or text asset.

## Claim and rule boundary

The proposed optional cue communicates an already-established enrage state. It must not change enrage threshold, ramp, scale, phase, attack selection, damage, timing or terminal behavior. With cue off, baseline presentation remains unchanged. The cue must be driven by the same approved enrage state transition and not by an unrelated timer or guessed health threshold. Existing pure rule calculations from elapsed time do not prove an authored/runtime cue exists.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/screens/audio and hashes | **Expected:** unique IDs and immutable raw evidence/hash. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and generation. **Observed:** pending. |
| Enrage rule inputs | **Expected:** full elapsed-time/phase/config inputs, rule output/scale and transition timestamp. **Observed:** pending. |
| Cue identity/state | **Expected:** reviewed cue asset/modality and default-off readback; exact trigger and clear policy. **Observed:** UNKNOWN until reviewed. |
| Time evidence | **Expected:** monotonic real time plus game/encounter clock and any pause/dilation state. **Observed:** pending. |

## Paired cases

From identical encounter seeds and state, replay the same elapsed-time/input sequence with cue disabled and enabled; change only the reviewed cue toggle.

| Row | Required evidence | Pass condition |
|---|---|---|
| No-cue control | Record rule inputs/output/scale, phase and transition timing across the enrage interval; capture presentation. | Establishes enrage timing/output baseline; no new optional cue. |
| Enabled cue | Repeat identical sequence; record cue event and direct screen/audio evidence alongside the same rule values/timestamps. | Cue matches actual enrage transition/approved state. Enrage rule values and timing match control exactly within clock measurement limits; no gameplay effect. |
| Before/after transition | Capture immediately before, at and after the enrage transition. | No early cue, duplicate transition cue, or stale cue after reset/terminal state. |
| Reset/restart | Restart before and after enrage where safely available. | Cue state clears and new generation follows the same rule timing as control. |

## Evidence interpretation and limits

- **Measured:** enrage rule inputs/output, phase/generation and timestamps from raw logs; cue appearance/audio from recorded capture.
- **Inferred:** identical rule timing only when matched real/game clock conditions and all relevant inputs are recorded.
- **Manual:** cue clarity, duration, placement, audibility/accessibility and whether it obscures combat.
- A cue event or elapsed-time label alone cannot prove unchanged rule timing. Cue modality, trigger, clear behavior and thresholds are not approved here.

## Failure and stop conditions

Fail if default-on, cue appears outside the actual enrage state, duplicates/sticks after reset, or any enrage value/timing/gameplay outcome differs from control. Stop if enrage input/transition cannot be read back, clocks cannot be compared, or the cue trigger requires unreviewed threshold/presentation decisions. Missing evidence stays UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No cue/threshold/source/asset changes, tests/build/Editor run, or runtime claim. Implementation is not authorized before review.
