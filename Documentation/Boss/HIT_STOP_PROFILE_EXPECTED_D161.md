# Opt-in hit-stop profile expected sheet (Queue D161)

Status: protocol only. No hit-stop profile or behavior is implemented/enabled by this sheet. Owner/Lead must approve duration, scope and time-domain semantics before implementation. Live Editor/packaged proof is Lead-owned.

## Claim and boundary

The proposed opt-in profile applies a bounded hit-stop after the reviewed contact. The no-hitstop run is the control. The enabled profile may change only the approved presentation-time behavior for the bounded interval; it must not change hit acceptance, damage, attack identity, resource values, event counts, parry/guard outcome, or terminal state. Whether actors, animation, input, timers, world time, and audio are frozen or continue is a product/technical decision not made here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/video/audio and hashes | **Expected:** unique ID; preserve captures and hash after run. **Observed:** pending. |
| Build/map/actors/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile, attacker/target identity. **Observed:** pending. |
| Contact identity | **Expected:** same attack, instance, target, hit key, accepted outcome and seed in both pairs. **Observed:** pending. |
| Profile state and bounds | **Expected:** default-off control; exact approved enabled profile, max duration and time semantics recorded. **Observed:** UNKNOWN until approved. |
| Clock evidence | **Expected:** monotonic real-time timestamps plus relevant game/world/animation clocks and pause/dilation state. **Observed:** pending. |

## Paired cases

Reset to a matched state and repeat the same accepted contact with hit-stop disabled/enabled. Change only the approved profile toggle/configuration.

| Row | Required evidence | Pass condition |
|---|---|---|
| No-hitstop control | Capture contact, hit result, damage/resources, attack progression and timing with feature off. | Establishes baseline hit and downstream event sequence. |
| Enabled bounded hit-stop | Capture hit-stop start/end, real-time and game-time duration, relevant clock/dilation values, attack state, and same combat fields. | Pause/freeze duration stays within the approved finite bound and follows reviewed scope; no repeated/unbounded stop. Hit acceptance, damage, counts and terminal semantics match control. |
| No accepted contact | Exercise a rejected/non-impact case where safely available. | Hit-stop does not start absent the reviewed trigger. |
| Cleanup/abort | Exercise death, interruption, restart or teardown during the interval where safely reachable. | Hit-stop restores the approved time state and does not leak into later generation or pause unrelated actors beyond policy. |

## Evidence interpretation and limits

- **Measured:** accepted hit and gameplay counters with raw line references; stop-start/end timestamps on monotonic and game clocks; captured video/audio and time state.
- **Inferred:** bounded duration only from a clock whose behavior during hit-stop is understood. A game clock that freezes cannot measure real elapsed duration by itself.
- **Manual:** perceived impact, readability and whether input/audio/camera behavior matches the approved intent.
- No numeric duration, actor scope, world-time policy, input policy or sound policy is approved here. Do not infer performance improvement from a subjective pause.

## Failure and stop conditions

Do not enable implementation/test acceptance before duration bound and time semantics are approved. After approval, fail if default-on, trigger is not an accepted contact, duration exceeds bound, state is not restored, unrelated gameplay outcomes change, or effects leak across restart. Stop if clocks cannot distinguish real and game time or the profile needs unreviewed gameplay choices. Missing evidence remains UNKNOWN.

## Verification boundary

Expected protocol only. No profile value chosen, source/UI/assets changes, tests/build/Editor run, or runtime claim. Implementation is not authorized before review.
