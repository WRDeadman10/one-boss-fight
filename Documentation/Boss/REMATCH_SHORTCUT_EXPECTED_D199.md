# Opt-in post-fight rematch shortcut expected sheet (Queue D199)

Status: protocol only. No shortcut or default change is implemented/enabled. Review the shortcut action and default-off behavior before implementation. Live Editor/packaged proof remains Lead-owned.

## Claim and lifecycle boundary

The proposed opt-in shortcut starts a clean new encounter generation after an approved terminal result. Current retry flow remains unchanged when the shortcut is off. Rematch must not bypass terminal classification, re-use stale combat state, duplicate actors, preserve old timers/delegates, or alter map/profile/seed policy. No rematch key, confirmation flow, or persistence policy is selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Old/new run IDs, UTC, logs and hashes | **Expected:** distinct attempt IDs, immutable old/new evidence and post-capture hashes. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and content identity across retry. **Observed:** pending. |
| Terminal result | **Expected:** authoritative win/loss/failure result, generation and terminal timestamp before shortcut becomes available. **Observed:** pending. |
| Shortcut state | **Expected:** off by default/read-back; enabled action and confirmation policy reviewed. **Observed:** pending. |
| Reset snapshot | **Expected:** player/boss actors, health/posture/resources, phase, selector/executor, timers/delegates, input/possession and seed state before and after restart. **Observed:** pending. |

## Paired cases

Compare current retry flow with the shortcut off to the same terminal result followed by the enabled shortcut. Change only the reviewed shortcut action.

| Row | Required evidence | Pass condition |
|---|---|---|
| Current retry control | Record terminal state, retry path, old/new generation IDs and complete reset snapshot. | Establishes existing clean retry behavior. |
| Shortcut rematch | Trigger shortcut only after terminal result; record action, transition, actors and new generation/reset snapshot. | Starts exactly one new generation with clean baseline state and approved map/profile/seed policy; no old state remains. |
| Premature/invalid action | Attempt shortcut before terminal or during transition where safely testable. | Action is refused or ignored per reviewed policy and does not interrupt the active encounter. |
| Repeated shortcut input | Exercise repeated presses during transition under controlled input. | No duplicate encounter/spawn/restart; input is consumed once or refused according to policy. |
| Gameplay-ready boundary | Capture dependencies/profile, possession/input, health/phase and selector readiness before accepting gameplay input. | New encounter is fully initialized before input/AI begins; behavior matches current retry flow. |

## Evidence interpretation and limits

- **Measured:** terminal result, old/new generation, actor/component identities, reset fields, input/readiness events and timestamps with raw references.
- **Inferred:** clean restart only if all relevant mutable run state and async callbacks are checked; actor replacement alone is not proof.
- **Manual:** rematch flow clarity and whether user intent/confirmation is appropriate.
- Seed reuse, map transition, persistence and user confirmation policy are not approved. A new generation ID does not prove all timers/delegates/state were reset.

## Failure and stop conditions

Fail if default retry changes, shortcut works before terminal, repeated input creates multiple runs, new generation inherits stale state, readiness is incomplete, or result classification changes. Stop if reset inventory or seed/map policy is unclear. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No shortcut/source/UI changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
