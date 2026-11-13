# Queue BE Batch 8 — owned-tag cleanup resilience

Date: 2026-11-11  
Status: source/test READY. No BUILD-296 feedback was newer than C-1275 at the mailbox check; no overlapping Lead build was active when the locked validation began.

## Findings and implementation

The shared retry owner already uses a weak actor reference, stops when the actor is gone or being destroyed, and retries only while the reflected removal call fails. Both `URPGIFrameMonitor::EndPlay` and `URPGPlayerParry::EndPlay` schedule retries only after their direct cleanup attempts fail; the parry component performs up to five immediate attempts first.

Hardening: extracted the retry backoff into `RetryDelaySeconds(Attempt)`. Attempts below the normal first attempt now safely use 0.25 seconds without a negative shift; the sequence remains 0.25, 0.5, 1, 2, 4 seconds and stays capped at 4 seconds for later retries. This bounds malformed attempts and preserves the normal schedule.

Added a source contract for invalid/destroying owner refusal, weak-owner timer capture, stop-after-success policy, the retry cap, and both EndPlay callers. Expanded the native retry-policy test over negative, normal, capped, and very large attempt values.

## Verification

- `Scripts/Tools/test_be_x36_x40_owned_tag_cleanup_contract.py`: 6/6 passed; `py_compile` passed.
- Native `OneBossFight.Player.OwnedTagCleanup.RetryPolicy` passed.
- C-1155 Development build exit 0; DD27j-pinned suite 509/509 started and passed, 0 failed; no assets; both locks released.
- Receipt: `Docs/BossCombatReview/Execution/Codex/BE_X36_X40_OWNED_TAG_CLEANUP/Run_20261110_184057/`.

## Evidence limit

The weak-owner gate covers a destroyed or invalid actor lifetime; this generic helper has no encounter-generation identifier, so it does not prove that a still-live reused actor belongs to the same logical encounter generation. No PIE tag removal, actor destruction, or gameplay-tag stack behavior was simulated. Those runtime cases remain outside this source/native validation.
