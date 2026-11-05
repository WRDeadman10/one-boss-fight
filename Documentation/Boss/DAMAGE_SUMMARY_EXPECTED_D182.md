# Opt-in damage summary HUD expected sheet (Queue D182)

Status: protocol only. No damage summary or feature is implemented/enabled. Review default-off behavior, accepted-hit source and displayed units/rounding before implementation. Live Editor/packaged verification is Lead-owned.

## Claim and accounting boundary

The proposed optional HUD total reconciles to the authoritative accepted-hit damage events for one attempt/generation and resets on retry. It must not count candidates, refused hits, parries without damage, duplicate callbacks or damage to another target unless the reviewed schema explicitly says so. Display must not modify damage, health, score, hit acceptance, attack flow, or retry state. No rounding or aggregation policy is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/screens and hashes | **Expected:** unique ID, immutable raw evidence and post-capture hash. **Observed:** pending. |
| Build/map/profile/target | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and damage target identity. **Observed:** pending. |
| Damage event contract | **Expected:** exact accepted-damage token/source, amount units, target and unique event/hit key; define whether actual health delta or requested payload is authoritative. **Observed:** UNKNOWN pending review. |
| Display contract | **Expected:** approved total type, scope, units, rounding and feature default-off readback. **Observed:** pending. |
| Attempt/generation | **Expected:** run/generation identity at each event and retry; record when aggregation opens/closes/resets. **Observed:** pending. |

## Paired cases

Replay identical combat with summary hidden/enabled, changing only the reviewed display toggle. Independently sum the authoritative accepted-hit events per attempt.

| Row | Required evidence | Pass condition |
|---|---|---|
| Hidden control | Record accepted/refused events, unique hit keys, amounts, target health and attempt ID; screen with feature off. | No new summary appears; establishes baseline event set and health deltas. |
| Enabled accumulation | Repeat same encounter with display enabled; record every event and displayed total over time. | Display equals the agreed sum of accepted events for the same target and generation under approved unit/rounding; refused/duplicate events do not inflate it. |
| Parry/zero-damage/refusal | Exercise cases where an event is parried, rejected or has zero damage, if supported. | Inclusion/exclusion matches the approved event contract; no hidden total changes. |
| Retry reset | After a nonzero total, retry to a new generation and capture before/after values and new events. | Old total clears at the approved reset event; the new attempt starts at baseline and accumulates only its own events. |
| Gameplay guard | Compare health, damage application, hit counts and outcomes with display off/on. | HUD has no gameplay mutation or altered event ordering. |

## Evidence interpretation and limits

- **Measured:** each accepted event ID/key, amount, target/generation and display value with raw line/screenshot references.
- **Inferred:** reconciliation only after the accepted-event set and aggregation rule are declared; rounding is applied once according to the approved policy.
- **Manual:** legibility and whether the number is understandable as damage to the specified target/attempt.
- A damage request/payload is not automatically the same as actual health removed (caps/resistance/overkill may differ). The authoritative metric must be chosen before claiming reconciliation.
- Any damage summary data remains local to the project/repository; do not publish or transmit it, and do not include player identity or identifying host/session data. Any separately shared review copy must be scrubbed while the original remains unchanged locally.

## Failure and stop conditions

Do not implement acceptance until authoritative event, target scope, units and rounding are reviewed. Fail if default-on, displayed total diverges from the approved accepted-event sum, duplicate/refused events count, retry leaks prior damage, or gameplay changes. Stop if accepted amount cannot be distinguished from requested payload or event keys are not unique. Missing evidence stays UNKNOWN.

## Verification boundary

Expected protocol only. No HUD/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
