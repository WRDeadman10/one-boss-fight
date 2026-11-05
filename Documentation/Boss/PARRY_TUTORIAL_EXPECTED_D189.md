# Opt-in parry tutorial overlay expected sheet (Queue D189)

Status: protocol only. No tutorial overlay, instructions, or feature is implemented/enabled. Review default-off behavior, instruction content and dismissal/persistence policy before implementation. Live Editor/packaged proof remains Lead-owned.

## Claim and boundary

The proposed opt-in tutorial displays reviewed parry instructions without affecting combat state. It must not open/close parry windows, grant invulnerability, change input, pause/freeze combat, modify damage/resources, or change AI/attack timing. Instructions must describe the actual approved input and timing behavior; no instructional wording, thresholds, tutorial trigger, or player tracking policy is selected here. Do not collect or persist player identity/progress unless separately approved.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/screens and hashes | **Expected:** unique ID and immutable evidence/hash. **Observed:** pending. |
| Build/map/player/input | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, player/controller and real parry binding. **Observed:** pending. |
| Tutorial eligibility/trigger | **Expected:** exact reviewed condition and state, read back independently of overlay. **Observed:** UNKNOWN pending review. |
| Feature and persistence state | **Expected:** overlay off by default/read-back; record toggle, dismissal and any approved local persistence. **Observed:** pending. |
| Combat baseline | **Expected:** parry state/window, input events, AI/attack, health, stamina, posture and clock samples before/during/after. **Observed:** pending. |

## Paired cases

Replay a matched combat/tutorial-trigger scenario with instructions hidden/enabled, changing only the reviewed display toggle. Exercise the existing manual parry input in both cases.

| Row | Required evidence | Pass condition |
|---|---|---|
| Hidden control | Trigger condition and combat-state timeline with overlay off. | No tutorial text appears; establishes baseline. |
| Enabled instructions | Repeat condition; capture exact text, appearance/dismissal and the same combat timeline. | Text matches reviewed instruction; display causes no pause, input, window, timing, resource, AI or outcome change. |
| Dismiss/reopen | If approved, dismiss and re-trigger under reviewed policy; record storage state. | Overlay follows policy, does not alter combat, and stores no unapproved player identity/progress. |
| Outside trigger/reset | Exercise state outside eligibility and restart/new generation. | No out-of-scope tutorial appears; stale overlay clears or persists only as approved. |
| Input guard | Use manual input while overlay is present. | Overlay does not consume, synthesize or automate the parry input. |

## Evidence interpretation and limits

- **Measured:** tutorial trigger, generation, combat/input/resource timeline and direct screenshot/video with raw references.
- **Inferred:** no combat side effect only from matched independent timelines; a static screenshot cannot prove combat continued normally.
- **Manual:** instruction clarity, readability, accessibility and whether text obstructs the fight.
- No lesson text, threshold, tutorial eligibility, dismissal, retention, or telemetry policy is approved. Displaying an instruction does not prove the underlying mechanic behaves as described.

## Failure and stop conditions

Fail if default-on, instructions are inaccurate, display changes combat/input/timing/resources, or unapproved player data is persisted. Stop if the trigger state or input route cannot be independently identified, or instructional content needs owner choice. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No content/UI/source changes, tests/build/Editor execution, tutorial telemetry, or runtime claim. Implementation is not authorized before review.
