# Opt-in boss reposition pause expected sheet (Queue D165)

Status: protocol only. No pause behavior is implemented or enabled; default route remains unchanged. Review the pause duration, trigger and state-handling policy before implementation. Live Editor/packaged verification remains Lead-owned.

## Claim and boundary

The proposed opt-in pause adds a bounded delay at the reviewed point in the existing boss reposition route. The enabled route must preserve target identity, reposition destination/eligibility, and the attack selection that would follow the same state. The pause must not mutate selector memory, cooldowns, attack budget, phase, health, posture, or player state. No duration, clock domain, snapshot freshness rule, or owner-facing pacing target is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/video/hash | **Expected:** unique IDs and immutable raw evidence hashed after capture. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and generation. **Observed:** pending. |
| Reposition/target state | **Expected:** exact selected reposition route, target identity/transform, initial range, destination and completion reason. **Observed:** pending. |
| Selector state | **Expected:** candidates, seed, cooldown/history and eligibility snapshot immediately before and after pause. **Observed:** pending. |
| Feature state | **Expected:** pause disabled by default/read-back off; enabled run records exact duration and clock semantics. **Observed:** pending. |

## Paired cases

From matched encounter state, compare default route with pause off to the same route with pause on. Change only the reviewed pause toggle/config.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default route | Record reposition and subsequent selected attack, target, selector state and timings with feature off. | Establishes existing route and attack choice baseline. |
| Enabled pause | Record pause start/end on real and game clocks, target/state snapshot, reposition result and selected attack. | Pause is finite/bounded by approved policy and resumes expected route. Attack identity and eligibility match the baseline for an equivalent post-reposition state; no hidden selector-state mutation. |
| State change during pause | If safely reproducible, change target/phase/eligibility during the pause using an existing scenario. | Behavior follows a reviewed fresh-vs-captured snapshot policy; never attacks an invalid/stale target or silently changes selection. If policy is undefined, stop and leave UNKNOWN. |
| Abort/restart | Interrupt or restart during pause where supported. | Pause is canceled/cleared and does not resume in a new generation or retain stale timers. |

## Evidence interpretation and limits

- **Measured:** route, target, candidate/decision identity, eligibility, selector state, timer start/end and generation with raw references.
- **Inferred:** unchanged attack selection only when the post-reposition decision inputs and selector state are equivalent. Matching labels alone do not prove the selector made the same decision under equal input.
- **Manual:** pacing, responsiveness and whether the pause reads as intentional rather than a stall.
- No duration, snapshot policy, clock domain, or pacing threshold is approved. Do not report an intended pause as a measured bounded pause without real-time evidence.

## Failure and stop conditions

Fail if default route changes, pause is unbounded, selector state/cooldown changes because of the pause, attack identity differs for equivalent state, stale target is used, or restart leaves a pause active. Stop if timing policy or snapshot semantics have not been reviewed, or if baseline state cannot be reproduced. Missing/invalid evidence remains UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No parameter/source changes, tests/build/Editor execution, or runtime claims. Implementation is not authorized before review.
