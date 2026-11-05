# Opt-in combo pause profile expected sheet (Queue D170)

Status: protocol only. No combo pause or nonzero profile is implemented/enabled. Review duration, clock domain and snapshot semantics before implementation. Live Editor/packaged verification remains Lead-owned.

## Claim and boundary

The proposed opt-in profile inserts a bounded pause at the approved combo transition point. Default profile remains zero/no pause. The pause may affect presentation timing only; the next card identity, eligibility, target, combo depth and attack budget must match the equivalent no-pause decision. It must not create a new attack, consume/refund budget, mutate selector memory, alter damage, or allow stale generation callbacks. No duration or whether the next card uses a fresh snapshot is decided here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/video and hashes | **Expected:** unique IDs and immutable evidence/hash. **Observed:** pending. |
| Build/map/profile/graph | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, combo root/graph and profile identity. **Observed:** pending. |
| Combo state | **Expected:** initial node, accepted hit count/depth, remaining attack budget, target and candidate/selector inputs recorded. **Observed:** pending. |
| Pause profile | **Expected:** zero/default control and exact approved nonzero value, bound, clock domain and snapshot policy. **Observed:** pending. |
| Generation/timing | **Expected:** generation and real/game-clock timestamps at combo trigger, pause start/end and next-card start. **Observed:** pending. |

## Paired cases

Repeat the same combo-triggering attack and accepted hit from matched initial state, comparing zero/default pause with the approved enabled pause. Change only the profile value.

| Row | Required evidence | Pass condition |
|---|---|---|
| Zero-pause control | Capture trigger, next node/card, target, budget/depth and timing at default zero. | Establishes existing immediate/delayed combo behavior and exact next-card baseline. |
| Enabled bounded pause | Capture pause interval, snapshot inputs, next card, target, budget/depth and generation. | Pause stays within the reviewed bound; equivalent state yields the same next card/eligibility and attack budget as control. No duplicated or skipped attack. |
| Invalidated combo during pause | Where safe, interrupt with state change, phase change, target loss or abort supported by existing flow. | Behavior follows the reviewed freshness/abort policy and cannot start a stale or invalid next card. If policy is unset, stop and leave UNKNOWN. |
| Reset/restart | Restart or change generation while pause is pending. | Old callback is canceled; no pause or combo start leaks into the newer generation. |

## Evidence interpretation and limits

- **Measured:** combo node/card identities, accepted hits, depth/budget, candidate/selector inputs, generation and pause timestamps with raw references.
- **Inferred:** same next card only when decision inputs/snapshot and random seed are equivalent; matching card names without input identity is insufficient.
- **Manual:** perceived rhythm and whether the pause reads as deliberate.
- No numeric pause bound, time domain, snapshot refresh behavior, or product rhythm target is approved. A game clock may stop during pause and cannot alone prove real elapsed duration.

## Failure and stop conditions

Fail if default profile is nonzero, the pause is unbounded, budget/depth changes, next card differs for equivalent decision inputs, duplicate/skipped attack occurs, or stale callback crosses generation. Stop if snapshot semantics, clock domain, or bound has not been approved. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No profile/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
