# AA-C08 — Guard counter integration

## Inputs now available

Antigravity delivered ER-A4 `Attack_GuardCounter` with an FBX and review clip (`Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/`). Its metadata reports 0.800 s length, a 100 cm forward step, unchanged yaw, windup at 0.300 s, hit window 0.333–0.533 s, impact at 0.433 s, and recovery at 0.800 s. The clip is delivered for review; it is not yet imported or owner-approved.

## Integration requirements

- Keep today's behavior when the optional clip is unset or unavailable. Do not load the FBX directly at runtime; the Lead imports it to a new project asset after review.
- Trigger only from a confirmed successful block/contact outcome. Holding `Status.Blocking` alone is not enough to arm a counter, because it does not prove an incoming hit was blocked.
- Accept the existing Elden Ring strong-attack tap (`R2`) only within the existing proposed guard-counter window. Keep the pure rules in `RPGGuardCounterRules.h` as proposals until live tuning is accepted.
- Use the delivered notify timings as authoring guidance. The Lead must confirm montage slot, hit delivery route, stamina behavior, target validity, and recovery lockout against the imported asset.
- Instrument block outcome, arm timestamp, counter press, montage selection, hit result, and fallback reason. Counter miss/expiry must clear the arm.

## Source integration status

Implemented in `RPGFrameworkMoveExecutor` and `URPGDodgeTiming`: an accepted contact classified `Guarded` notifies the player component; R2 consumes one successful-block timestamp only inside the counter window. R2 still injects the pack's ordinary strong attack. The optional `GuardCounterMontage` soft field has no default asset. If set, the component temporarily replaces the player's `StrongAttackMontages` entries and restores their serialized values after the montage starts or the one-second safety timeout; if absent or unusable, the pack strong attack remains the animation/damage fallback. The 0.60 s window remains a proposal.

## Test-first / Lead handoff

Existing native rules tests cover accepted window boundaries, invalid timestamps, no-block state, and arm expiry. Added focused source-contract checks for the successful-block call sites, one-shot R2 gate, optional field, strong montage substitution, and restoration. The focused Python suite passed 5/5 with the DLSS contract checks; `git diff --check` passed with line-ending warnings. The native Unreal suite and C-871 compile review/build/PIE remain Lead-owned. ER-A4's motion was rejected by C-960, so its optional field remains empty and the owner has not approved/imported the clip.
