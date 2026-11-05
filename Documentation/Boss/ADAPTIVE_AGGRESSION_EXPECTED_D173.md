# Opt-in adaptive aggression expected sheet (Queue D173)

Status: protocol only. No adaptive behavior or telemetry collection is implemented/enabled. Review the explicit input contract, default-off determinism and privacy boundary before implementation. Live Editor/packaged proof remains Lead-owned.

## Claim and boundary

The proposed opt-in behavior changes aggression bands only from an explicitly documented, bounded set of inputs. With the feature off, fixed inputs must reproduce the existing deterministic behavior. It must not silently collect, infer, transmit, or persist player telemetry. Any player-derived input must be named, necessary, disclosed, opt-in and locally bounded; no such input is approved by this sheet. No aggression threshold or gameplay effect is selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs and hashes | **Expected:** unique IDs and immutable evidence hashes. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and generation. **Observed:** pending. |
| Explicit input schema | **Expected:** enumerate every input and source, units, bounds, collection time, storage/retention, and opt-in path. **Observed:** UNKNOWN until reviewed. |
| Fixed-input vector | **Expected:** complete aggression inputs and initial band/state read back; no unlisted player observation. **Observed:** pending. |
| Feature state | **Expected:** adaptive feature off by default/read-back; no hidden telemetry path when off. **Observed:** pending. |

## Paired cases

Use a fixed table of explicit inputs. Replay each vector multiple times with adaptation off, then compare enabled behavior from the same initial state; vary only the reviewed toggle or explicitly approved input.

| Row | Required evidence | Pass condition |
|---|---|---|
| Off deterministic replay | Capture full fixed-input vector, initial band, selected aggression output and result over repeated runs. | Identical inputs/state produce identical outputs with feature off; no unlisted telemetry is read or persisted. |
| Enabled band transitions | For each approved vector, capture input values, band before/after, transition reason and resulting bounded behavior. | Transitions match the reviewed rule table; same vector is deterministic; no state outside approved inputs drives the result. |
| Input boundary | Exercise approved below/equal/above and invalid values, if a rule table defines them. | Boundary behavior matches reviewed source-derived policy; invalid values fail safely without hidden fallback or data collection. |
| Data inspection | Inspect logged/stored fields and network activity within the approved local scope. | Only explicitly approved fields are present, with approved retention; no undisclosed player telemetry or external transmission. |
| Disabled regression | Turn feature off and replay baseline vectors after enabled tests. | Existing default behavior and state are restored exactly. |

## Evidence interpretation and limits

- **Measured:** full explicit input vector, band state/output, build/generation, stored/logged fields and any network activity within reviewed instrumentation; raw references required.
- **Inferred:** deterministic behavior only from repeated identical input/state replay. An unexplained band transition invalidates the inference.
- **Manual:** whether the resulting aggression feels appropriate is owner/Lead judgment, not telemetry evidence.
- The task does not authorize hidden player telemetry. Without an approved input schema and privacy/retention decision, enabled behavior cannot be accepted. Source helper code alone does not prove runtime use.

## Failure and stop conditions

Do not implement before the owner/Lead reviews all inputs and any player-derived collection/retention. Fail if off mode is nondeterministic for fixed inputs, an unlisted input affects behavior, telemetry is collected without opt-in, data is persisted/transmitted beyond approval, or band transitions escape documented bounds. Stop if inputs cannot be independently read back. Missing evidence stays UNKNOWN.

## Verification boundary

Expected protocol only. No threshold choice, telemetry collection, source/profile changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
