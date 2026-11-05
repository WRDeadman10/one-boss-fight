# Opt-in impact sound variation expected sheet (Queue D157)

Status: protocol only. No variation system, sound asset, or feature is implemented/enabled. Review the protocol and default-off behavior before implementation. Live Editor/packaged audio proof is Lead-owned; selection pool, weighting, and audio mix remain unselected.

## Claim and invariant

The proposed opt-in variation chooses among approved impact sounds deterministically from a recorded seed while leaving hit semantics unchanged. Same seed and same event identity should replay the same sound choice; a varied seed may select another approved sound. Damage, accepted-hit count, target, hit key, attack identity, stamina/posture effects, and event timing must not change because of sound selection. This sheet does not claim which pack sound assets are currently loaded or authorize replacing/editing them.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, seed, UTC, raw log/audio path and SHA-256 | **Expected:** unique run IDs; record seed and immutable capture hashes. **Observed:** pending. |
| Build/map/actors/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, attacker/target/profile identity. **Observed:** pending. |
| Impact event identity | **Expected:** same attack, event/index, target, hit key and contact conditions across seed pairs. **Observed:** pending. |
| Feature/pool state | **Expected:** toggle read back default-off; enabled run records exact approved pool and configuration. **Observed:** pending; pool and weighting require review. |
| Audio output | **Expected:** fixed output device/volume/sample rate and capture route; identify baseline pack sounds. **Observed:** pending. |

## Paired cases

Repeat identical impact scenarios with the mode off and on. In enabled mode, repeat the same seed/event, then use a different recorded seed for the same event. Keep only the seed changed in the varied-seed comparison.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default-off control | Capture sound and event telemetry with feature off; record damage, accepted hits, target and hit key. | Establishes current sound and gameplay baseline; no new variation behavior is visible/audible. |
| Same-seed replay | Repeat the same enabled event twice with identical seed and event identity. Capture selected sound identity and waveform/audio marker. | Same approved sound choice is made for the same seed/event. Gameplay counters and values remain consistent with baseline. |
| Varied-seed replay | Repeat same event with a different recorded seed; capture selection plus identical gameplay fields. | Sound selection can vary within the reviewed pool; damage, accepted-hit count and other gameplay outcomes remain unchanged. If different seed selects same sound, classify variation as not demonstrated rather than infer failure of determinism. |
| Negative/no-impact control | Run a non-impact or rejected-hit case where safely available. | No impact variation cue is emitted for a rejected/non-impact event; no gameplay mutation occurs. |

## Evidence interpretation and limits

- **Measured:** hit acceptance, attack/event/target/hit-key, damage and counters from logs/readback; seed and selected sound identity from telemetry; captured audio with settings and timestamps.
- **Inferred:** determinism requires repeated same-seed, same-event runs; variation requires a changed selected sound under a different seed, but one pair does not establish statistical distribution or fairness.
- **Manual:** audibility, mix, consistency, and whether variants fit the impact. Record conditions and reviewer.
- Audio logs cannot prove perceived sound; a waveform alone may not identify the loaded authored asset. Do not claim a distribution, sample quality, or cross-platform determinism beyond the observed test.

## Failure and stop conditions

Fail if default-on, same-seed same-event choice changes, a rejected event plays an impact cue, pack sounds are replaced/suppressed, or damage/hit counts/outcome differ. Stop if seeds/event identities cannot be read back, the approved pool is unavailable, audio capture cannot identify selection, or authored pool/mix requires an unreviewed choice. Missing or invalid evidence stays UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No sound pool selection, asset/source changes, tests/build/Editor run, or runtime claim. Implementation is not authorized before review.
