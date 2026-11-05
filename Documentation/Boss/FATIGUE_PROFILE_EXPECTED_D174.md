# Opt-in fatigue pressure profile expected sheet (Queue D174)

Status: protocol only. No fatigue tuning or profile is implemented/enabled. Owner approval is required for fatigue thresholds, scale values and tuning. Lead owns live Editor/packaged proof.

## Claim and boundary

The proposed opt-in profile applies a bounded fatigue state/pressure rule from reviewed inputs. Default-off behavior must reproduce the existing baseline. Every fatigue state transition and its exact emitted telemetry must be captured; a hidden/internal state without a reviewed observable is not accepted as proof. Fatigue must not change health/resource values except for explicitly approved rule deltas, and must not alter attack budget, eligibility, phase or terminal behavior outside the approved table. No tuning values are chosen here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs and hashes | **Expected:** unique IDs and immutable evidence/hash. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and generation. **Observed:** pending. |
| Fatigue rule/config | **Expected:** complete owner-approved inputs, thresholds, scale values, bounds and reset policy. **Observed:** UNKNOWN until approval. |
| Observable state | **Expected:** exact fatigue state variable(s), emitted token names/fields and event points. **Observed:** pending; telemetry contract must be reviewed before run. |
| Trigger inputs | **Expected:** controlled clean-finish/contact/phase/restart sequence and any documented fatigue input. **Observed:** pending. |

## Paired cases

Replay the same encounter sequence with feature off and on, changing only the approved profile. Record every fatigue state transition and telemetry row.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default-off control | Capture baseline state, output/telemetry and gameplay for the specified clean/no-contact and contact sequences. | Off mode is deterministic and preserves current behavior; no fatigue telemetry is silently added if policy excludes it. |
| Enabled fatigue transitions | Drive each reviewed transition input; record before/after state, rule inputs, exact emitted token and all fields. | State and telemetry match the approved mapping exactly; each transition is explainable from reviewed inputs. |
| Boundary/repeat | Test approved threshold equality/adjacent behavior and repeat calls/events for one-shot or accumulation policy. | Behavior matches approved threshold and latch/reset rules, without duplicate or unbounded pressure. |
| Phase/restart reset | Exercise phase change and encounter restart with state readback before/after. | Fatigue state resets/retains exactly as approved and never leaks across generation. |
| Gameplay guard | Compare selected attacks, counts, damage, health/resources and terminal outcomes in paired sequences. | Any difference is limited to the explicitly approved fatigue deltas; no hidden gameplay side effect. |

## Evidence interpretation and limits

- **Measured:** inputs, state before/after, exact telemetry token/fields, generation and gameplay outcomes with raw references.
- **Inferred:** transition cause only when all rule inputs and reset state are read back; output token alone does not prove which input triggered it.
- **Manual:** perceived pressure/balance remains an owner judgment, not a telemetry result.
- Until the owner approves tuning/reset rules and the telemetry contract is defined, enabled acceptance is blocked. Do not invent expected telemetry names or values.

## Failure and stop conditions

Do not implement before owner approves tuning and state/reset policy. Fail if off mode changes baseline, telemetry is missing/misnamed, transitions do not match the approved table, fatigue leaks across reset, or unapproved gameplay/resource fields change. Stop if inputs/state cannot be read back. Missing evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No tuning/profile/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before owner approval and review.
