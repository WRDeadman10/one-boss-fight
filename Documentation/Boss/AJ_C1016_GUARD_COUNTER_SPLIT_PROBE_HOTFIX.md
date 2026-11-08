# C-1016 — split guard-counter probe hotfix

## Lead findings

C-1016 reports BUILD-253 GREEN (484/484). r7 never reached the guard phase because the probe looked for `RPGCombatDebug` on the player, while `RPGPlayerMovesSubsystem::AttachBossDiagnostics` attaches it to the pack boss. Thus earlier refill calls found no component. r8 used the boss component, but player death still triggered an encounter reset. C-1016 confirms the real data-route hook already arms in r6; the immediate need is to isolate and prove the counter input/attack path, while retaining a corrected real-contact mode.

## Changes

- Added Development-only Blueprint-callable `URPGDodgeTiming::DebugArmGuardCounter()`, which calls the existing `NotifySuccessfulGuardContact()` path. Shipping builds compile this helper as a no-op.
- Corrected live mode to fetch `RPGCombatDebug` from the boss both at guard entry and during every guard tick; it refills the player and records the player health readback.
- Added `ER_GC_SYNTHETIC=1` mode. It holds the boss with `HoldForTest(true)`, places the player 160 cm along the boss's forward vector and faces the boss. It requires `ER_GC_ASSIGN=1`, transiently assigns `AM_ER_Attack_GuardCounter`, calls `DebugArmGuardCounter()`, verifies `IsGuardCounterArmed()`, and sends R2 in the same editor callback. It samples player montage every tick from the tap through the observation window so short playback is captured, then records hit kind/data, hit count, boss HP delta, and player HP.
- Synthetic output labels the arm as synthetic and suppresses it from the source-guard-contact log detector, so this mode cannot be mistaken for proof of a real blocked hit. With `ER_GC_SYNTHETIC` unset, the existing live-contact path remains enabled with the boss-owned refill component.

## Lead run instructions and acceptance

Run each route in synthetic mode with `ER_GC_SYNTHETIC=1` and `ER_GC_ASSIGN=1`; then run the live mode with `ER_GC_SYNTHETIC` unset to verify the real contact path where reachable. The synthetic result proves only the armed-window-to-R2 montage/damage pipeline. Lead should verify `AM_ER_Attack_GuardCounter`, `Strong`, `StrongMeleeAttackData`, about -22 boss HP, and player survival. The real mode must separately record an actual blocked-contact source event. No runtime success is claimed here.

Python AST parsing and scoped `git diff --check` pass. Codex did not run tests, build, Unreal, or PIE; Lead owns build and both-route runs.
