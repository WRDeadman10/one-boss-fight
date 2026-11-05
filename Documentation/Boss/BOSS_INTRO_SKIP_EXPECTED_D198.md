# Opt-in boss intro skip expected sheet (Queue D198)

Status: protocol only. No skip option or default change is implemented/enabled. Review which intro-only presentation can be skipped and keep encounter setup/readiness invariant. Live Editor/packaged proof remains Lead-owned.

## Claim and setup boundary

The proposed opt-in skip omits only approved intro presentation. It must not bypass boss/player spawn, profile/dependency resolution, possession/input, encounter generation, health/posture initialization, phase state, AI readiness, attack selection, timers, camera setup or telemetry initialization. Default behavior remains the current full intro. This sheet does not declare any intro step presentation-only; that inventory must be reviewed before implementation.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video and hashes | **Expected:** unique IDs and immutable evidence/hash. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile, assets and generation. **Observed:** pending. |
| Feature state | **Expected:** skip option off by default/read-back; enabled only in paired run. **Observed:** pending. |
| Readiness snapshot | **Expected:** boss/player actor and component identities, possession/input, profile/dependency status, health/posture, phase, AI/selector/executor readiness and timer state recorded at intro completion. **Observed:** pending. |
| Intro event identity | **Expected:** exact presentation steps/events omitted by skip, and remaining setup/ready events with timestamps. **Observed:** UNKNOWN until reviewed. |

## Paired cases

Run the same map/profile/build and start conditions once with full intro and once with the reviewed skip option; change only the skip toggle. Compare readiness snapshots at the point gameplay is enabled.

| Row | Required evidence | Pass condition |
|---|---|---|
| Full intro control | Capture each intro and setup event, then gameplay-ready snapshot and initial encounter state. | Establishes authoritative readiness baseline. |
| Enabled skip | Capture omitted presentation events, retained setup events and the same readiness fields at the corresponding ready point. | All encounter setup/readiness fields match the control; only approved presentation is omitted. |
| Immediate player input | Exercise the same manual action at gameplay-ready boundary. | Input is accepted at the same logical state and cannot fire before setup is complete. |
| Repeated start/restart | Exercise a new generation/restart with skip enabled and disabled. | No stale intro state, duplicate setup, missing initialization or cross-generation callback. |
| Failure/asset resolution | Record required dependency/profile load outcomes for both modes. | Skip does not bypass required asset resolution or turn a setup failure into apparent readiness. |

## Evidence interpretation and limits

- **Measured:** setup event identities, actor/component/profile, health/phase/readiness values, generation and timestamps with raw references.
- **Inferred:** setup equivalence only when every required readiness field is read back at the same logical boundary; matching visible positions alone is insufficient.
- **Manual:** whether skipped presentation is acceptable and whether readiness transition feels clear.
- No step is assumed cosmetic until reviewed. A faster start alone does not prove all gameplay initialization ran.

## Failure and stop conditions

Fail if default changes, any readiness field differs, input becomes available before initialization, dependencies are skipped, or restart causes stale/duplicate setup. Stop if the intro event inventory or readiness contract is incomplete. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No intro/asset/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
