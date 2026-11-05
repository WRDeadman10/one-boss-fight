# Opt-in parry streak counter expected sheet (Queue D183)

Status: protocol only. No counter or feature is implemented/enabled. Review what constitutes a streak and every reset trigger before implementation. Live Editor/packaged proof remains Lead-owned.

## Claim and definition boundary

The proposed display mirrors an authoritative underlying consecutive-parry count and is hidden by default. It must not affect parry acceptance, grade, damage, stamina/refund, recovery, or combat. “Streak” is not defined by this sheet: owner/Lead must approve whether only accepted parries increment and which events reset (non-parried contact, miss, phase change, abort, death, restart, timeout). No reset rule is silently assumed.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/screens and hashes | **Expected:** unique IDs, immutable evidence and hash. **Observed:** pending. |
| Build/map/player/boss | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, identities and generation. **Observed:** pending. |
| Count contract | **Expected:** approved increment event, count width/cap, and every reset event mapped to source telemetry. **Observed:** UNKNOWN pending review. |
| Feature state | **Expected:** counter display off by default/read-back; enabled only in paired run. **Observed:** pending. |
| Outcome events | **Expected:** accepted parry, non-parry/miss, phase transition, abort/death/restart as approved; each event/result read back. **Observed:** pending. |

## Paired cases

Replay identical event sequences with display disabled/enabled, changing only the reviewed toggle. Compare displayed value against the independently read authoritative counter after every event, not only at sequence end.

| Row | Required evidence | Pass condition |
|---|---|---|
| Accepted-parry sequence | Record each accepted event, grade, underlying count before/after and screen value. | Display equals the underlying count exactly after each approved increment; no effect on combat. |
| Non-parry/miss | Record refused/no-contact/non-parried outcomes and count after each. | Count behavior matches the approved increment/reset contract; no display-only increment. |
| Each approved reset event | Exercise each listed reset trigger separately; record event, generation and count before/after. | Count resets or persists exactly as approved; no omitted or spurious reset. |
| Default/disabled control | Repeat sequence with display hidden and read back underlying count. | Underlying count and combat outcomes match enabled run; display is absent. |
| Retry/generation | After nonzero count, restart and compare generation/count/readout. | No prior-generation count leaks except where retention is explicitly approved. |

## Evidence interpretation and limits

- **Measured:** event type/outcome, underlying count, generation and displayed value with raw references.
- **Inferred:** parity only if underlying source is independent from the display formatter and sampled at the same event boundary.
- **Manual:** readability and whether the counter is understandable without encouraging unsafe play.
- Until increment/reset/cap semantics are approved, there is no expected numeric streak sequence. A display matching its own internal value is not independent proof.

## Failure and stop conditions

Do not implement acceptance before streak and reset semantics are reviewed. Fail if display differs from underlying count, hidden default changes counting, invalid events increment, an approved reset is missed, or display alters gameplay. Stop if authoritative counter/event sources are unclear. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No counter/UI/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
