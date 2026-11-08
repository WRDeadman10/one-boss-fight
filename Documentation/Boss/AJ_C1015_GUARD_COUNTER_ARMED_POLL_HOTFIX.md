# C-1015 — guard-counter armed-state probe hotfix

## Lead finding

C-1015 reports a live successful guard on the data route in r6: the source logged `successful guarded contact armed guard counter window 0.60 s` after a blocked hit, with `GA_Sword_BlockReaction_C active` and `Status.Blocking`. The probe timed out because it searched `Saved/Logs/*.log`, while the Lead supplied an external `-abslog` path. C-1015 also reports that the player entered the guard phase at 28 HP and died after two boss hits; legacy had no blocked contact before death.

## Changes

- Added Development-only Blueprint-callable `URPGDodgeTiming::IsGuardCounterArmed()`. It queries the same `LastSuccessfulGuardTime`, world game time, and `GuardCounterWindowSeconds` rule used by the R2 input handler.
- The probe polls that API every editor tick and taps R2 on the first armed observation. The file-tail source-log match is retained as supplementary evidence and no longer gates the input.
- C-1015 attempted to refill at guard-phase entry and on every guard tick and included player HP telemetry. C-1016's Lead run found that this implementation looked for `RPGCombatDebug` on the player even though the component is attached to the boss, so the lookup returned `None` and no refill happened. The corrected boss-owned lookup and the split synthetic path are recorded in `AJ_C1016_GUARD_COUNTER_SPLIT_PROBE_HOTFIX.md`.
- Counter evidence now distinguishes API arm observation from whether the optional source log was visible under `Saved/Logs`; boss HP/hit records and player montage remain sampled.

The helper API does not prove the input was accepted or the attack dealt damage. Lead must still build and rerun both routes, and verify the counter montage/fallback, Strong kind, `StrongMeleeAttackData`, boss HP delta (expected about -22 per C-1015), and that the player remains alive through capture. No runtime result is claimed here.

## Validation and handoff

Python AST parsing and scoped `git diff --check` pass. Codex did not run native tests, build, Unreal, or PIE. Lead owns the build and both-route rerun.
