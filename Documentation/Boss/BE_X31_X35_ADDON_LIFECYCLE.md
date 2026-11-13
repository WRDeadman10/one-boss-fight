# Queue BE Batch 7 — AreaEffect / ChannelDrain lifecycle coverage

Date: 2026-11-11  
Status: source/test READY. BUILD-296 add-ons were accepted by Claude in C-1275; no rejected add-on behavior was reported for X32 to hotfix.

## Verdict intake and scope

C-1275 reports BUILD-296 GREEN (505/505) and accepts the wrapper library, default-off AreaEffect/ChannelDrain add-ons, retry owners, and property sweeps. This batch therefore made no gameplay behavior change. It adds source-contract checks around the existing lifecycle seams, plus native heal-boundary assertions that use actual resolver-applied HP rather than nominal tick damage.

## Coverage added

- The source contract verifies Abort clears a snare before its idempotence early return, EndPlay clears and aborts, and snare cleanup cancels its timer, restores speed only when it still owns the applied value, then resets ownership state.
- It verifies the delayed AreaEffect marks itself resolved before target/radius early exits, so an out-of-range or invalid target does not reopen the one-shot release.
- It verifies ChannelDrain ticks are driven by card-local animation time, stop at the authored end, and use no independent timer.
- It checks that healing is inside the `Accepted` resolver-outcome branch and consumes `Result.HPApplied` through `CappedHeal`, never `Channel.TickDamage` directly.
- Native ChannelDrain automation now includes partially accepted actual HP loss (`6` applied, `3` healed at 0.5 fraction) and missing-health capping (`1` point when only 1 health is missing).

## Verification

- `Scripts/Tools/test_be_x31_x35_addon_lifecycle_contract.py`: 6/6 passed; `py_compile` passed.
- Existing native `OneBossFight.Framework.MoveCard.AreaEffect` and `OneBossFight.Framework.MoveCard.ChannelDrain` tests both passed.
- C-1155 Development build exit 0; DD27j-pinned full suite 509/509 started and passed, 0 failed; no assets; both locks released.
- Receipt: `Docs/BossCombatReview/Execution/Codex/BE_X31_X35_ADDON_LIFECYCLE/Run_20261110_183601/`.

## Evidence limits

The new lifecycle contract is source-level coverage. It does not simulate Unreal world timers, a pawn being destroyed during a live snare, a real rejected/blocked ChannelDrain hit, or PIE movement restoration. The engine run was a Development build plus automation suite, not live acceptance. Claude owns any live add-on acceptance.
