# Opt-in deterministic encounter seed expected sheet (Queue D192)

Status: protocol only. No seeded encounter mode or seed behavior is implemented/enabled. Review seed scope, streams, default-off behavior and reset policy before implementation. Live Editor/packaged proof is Lead-owned.

## Claim and scope boundary

The proposed opt-in seed makes the reviewed encounter decisions reproducible for a documented seed and input sequence. It must define exactly which RNG streams/systems consume it and which remain outside scope. Same seed and equivalent state should repeat the scoped decisions; a different-seed control should demonstrate that the seed is actually consumed where expected. Restart behavior must follow the reviewed policy. No seed value, stream scope or restart behavior is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run IDs, UTC, raw logs and hashes | **Expected:** distinct immutable capture per run with post-capture hash. **Observed:** pending. |
| Build/map/profile | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, profile and content identity. **Observed:** pending. |
| Seed and scope | **Expected:** exact seed value, initialization point, consumers/streams, stream split policy and systems explicitly excluded. **Observed:** UNKNOWN pending review. |
| Input/state sequence | **Expected:** initial generation/state, player actions and external inputs matched across runs; capture relevant candidate/branch decisions. **Observed:** pending. |
| Restart policy | **Expected:** specify same seed reuse vs new seed per retry/generation and read back generation/seed on restart. **Observed:** UNKNOWN pending review. |

## Paired cases

Run the identical approved input/state sequence several times with the same seed, then once or more with a different seed. Change only the recorded seed where required.

| Row | Required evidence | Pass condition |
|---|---|---|
| Same-seed replay | Capture seed, generation, initial state, each scoped random decision and resulting encounter sequence across repeats. | Scoped decisions reproduce exactly for equivalent inputs/state/build/content. Unscoped systems are explicitly excluded from determinism claim. |
| Different-seed control | Repeat same inputs/state with another recorded seed; compare the intended seeded decision points. | At least one scoped random choice can vary, or if none varies, classify seed consumption as not demonstrated. No assumption that every different seed must change every result. |
| Restart/retry | Restart from the same baseline and capture seed and new generation under approved policy. | Seed reuse/new-seed behavior matches explicit policy; no stale stream state leaks. |
| Default-off regression | Disable seed mode and replay the existing default route. | Existing default randomness/behavior remains unchanged; no hidden seed is imposed. |

## Evidence interpretation and limits

- **Measured:** seed value, build/content identity, input/state sequence, RNG decisions/stream IDs, outputs and generation with raw references.
- **Inferred:** determinism only within the enumerated seed scope and equivalent executable/content/input state. It does not establish cross-platform or cross-version determinism unless separately tested.
- **Manual:** whether reproducible outcomes are useful to designers; not a correctness proof.
- No stream scope, cross-platform guarantee, seed persistence, or retry policy is approved. Logs of seed value alone do not prove the intended subsystem consumed it.

## Failure and stop conditions

Fail if default behavior changes, same-seed scoped decisions diverge for equivalent conditions, unscoped systems are claimed deterministic, or restart violates policy. Stop if stream consumers cannot be enumerated/read back, content/build differs, or input equivalence is not established. Missing evidence stays UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No seed behavior/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
