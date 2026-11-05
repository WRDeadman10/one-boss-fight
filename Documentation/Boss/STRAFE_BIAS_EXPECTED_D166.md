# Opt-in strafe direction bias expected sheet (Queue D166)

Status: protocol only. No bias, parameter, or default change is authorized. Review direction-bias values and default-off behavior before implementation. Live Editor/packaged proof is Lead-owned. Test only on open geometry; cage-wall scripts and wall-bound behavior are explicitly outside this protocol.

## Claim and boundary

The proposed opt-in bias changes direction preference for boss strafing on open geometry. The balanced/default control must remain unchanged when the option is off. Bias must not cause wall/cage interaction claims, alter attack eligibility/selection, target, damage, hit counts, range rules, or cause stuck recovery. No bias weight or preference is selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video and hashes | **Expected:** unique IDs and immutable evidence hashes. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, boss/player/profile identity. **Observed:** pending. |
| Open geometry | **Expected:** measured floor and nav extent around the entire strafe path; record wall/cage distance and prove neither constrains the path. **Observed:** pending. If geometry is cage/wall constrained, invalidate this protocol run. |
| Target and strafe state | **Expected:** fixed target trajectory, range, phase, card and strafe interval; capture direction candidate, seed and start/end transforms. **Observed:** pending. |
| Feature state | **Expected:** balanced control toggle off/read-back; exact reviewed bias settings when enabled. **Observed:** pending. |

## Paired cases

Repeat matched strafe intervals on the same open floor, with the same target path, seed and encounter state; change only the reviewed bias setting.

| Row | Required evidence | Pass condition |
|---|---|---|
| Balanced control | Capture left/right candidate scores, selected direction, movement distance, range and outcome over repeated intervals with feature off. | Establishes balanced distribution/behavior; no cage-wall condition is used. |
| Configured bias | Repeat under the reviewed bias; capture identical fields and exact setting. | Direction frequencies or scores reflect the approved bias over the approved sample plan; movement remains valid and attack semantics unchanged. |
| Bias disabled regression | Turn option off and repeat control after enabled run. | Balanced/default behavior returns and matches initial control within reviewed tolerance. |
| Invalid geometry exclusion | If wall/cage proximity is encountered unexpectedly, log geometry and abort classification. | Mark invalid for D166; do not treat a wall script, collision, or stuck flip as evidence for open-geometry direction bias. |

## Evidence interpretation and limits

- **Measured:** candidate scores, seed, selected direction, coordinates/range, movement and attack outcomes with raw references; geometry measurements and screenshots.
- **Inferred:** bias effect only from the approved sample size and comparison metric; a small number of varied directions does not establish a distribution.
- **Manual:** whether direction preference is perceptible and movement looks natural.
- This sheet does not specify a bias magnitude, statistical threshold, or acceptable sample count. Those must be reviewed before interpreting a positive claim. It makes no cage/wall claim.

## Failure and stop conditions

Fail if default changes, configured bias is ignored or over-applied relative to the approved metric, movement becomes invalid/stuck, or attack/target semantics change. Stop if open geometry cannot be proven, cage-wall scripts are active, seed/candidate evidence is absent, or bias values/sample criteria have not been approved. Invalid setup is inconclusive.

## Verification boundary

Expected protocol only. No setting/source/asset changes, tests/build/Editor execution, or runtime claims. Implementation is not authorized before review.
