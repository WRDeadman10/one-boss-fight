# Queue BD Batch 4: X16–X20 damage and status lifecycle

## X16 — resolver identity and precedence

`URPGDamageResolver::Resolve` synchronizes encounter generation, builds a key from MoveId/attack instance/hit key, checks target health/death, attacker liveness, generation, duplicate status, invulnerability, and parry before accepting (`RPGDamageResolver.cpp:37–49,134–156`). `RPGDamageRules::Decide` makes the order explicit (`RPGDamageResolver.h:101–109`); guard conversion is applied only to a base accepted blockable hit (`:112–116`). Accepted, parried, and blocked cases spend the key; invulnerable/stale rejections do not (`RPGDamageResolver.cpp:164–194`). This maps the project resolver path, not every pack-originated weapon/ability route.

## X17 — ChannelDrain ticks and abort cleanup

Channel ticks use card-local montage positions and unique `ChannelTick_n` hit keys; damage goes through the shared resolver, and healing occurs only when outcome is Accepted, bounded by accepted HP applied and missing native boss health (`RPGFrameworkMoveExecutor.cpp:475–520`). `Abort` clears the area snare, aborts the model, stops owned playback/movement, and disables ticking; `EndPlay` clears the snare and aborts (`:745–771`). The channel is not an independent repeating timer. Existing source/test reports do not include a world-level failure injection proving no tick after every abort reason; keep that as coverage work, not a confirmed runtime defect.

## X18 — area effect snapshot and resolution

The configured explicit target's ground point is captured at release and the delayed effect resolves against that target once through `URPGDamageResolver` (`RPGFrameworkMoveExecutor.cpp:390–429`). Scope is one explicit duel target; this is not an arbitrary overlap or multi-target field. Snare begins only for accepted effect contact and non-invulnerable target; speed is rebased when another policy changes it and restored conditionally (`:430–470`). Runtime placement/collision acceptance remains Lead-owned.

## X19 — owned-tag retry coverage

Failed EndPlay removals for `Status.Invulnerable` and `Status.ParryActive` transfer to `RPGOwnedTagCleanup` (`RPGIFrameMonitor.cpp:158–167`; `RPGPlayerParry.cpp:237–245`). The helper weakly tracks the actor, retries reflected removal with capped backoff while the owner remains alive, and stops when the reflected call is issued (`RPGOwnedTagCleanup.h:29–81`). Its native test exercises only `ShouldRetry` policy and a small simulated attempt loop (`RPGOwnedTagCleanupTests.cpp:8–24`); it does not exercise timer registration, actor destruction, reflected tag mutation, or actual retry count. I-frame `OnEncounterReset` makes one removal attempt and only clears owned state on success (`RPGIFrameMonitor.cpp:147–156`); failure has no independent timer scheduled in that callback. This is a deterministic coverage gap, not a confirmed failure.

## X20 — temporary speed modifier ownership

Area snare stores baseline and applied speed, then starts a 0.05 s timer (`RPGFrameworkMoveExecutor.cpp:430–440`). If speed differs from the last applied value by more than 0.5, it rebases the baseline and reapplies the scale (`:444–455`). Expiry/abort restores only when the current value still matches the executor's applied value within 0.5, preserving a distinct later writer (`:457–470`). Concurrent exact-value writes, timer ordering, and reset interactions lack live evidence; no race or runtime failure is asserted.

## Scope

Static source and existing test inventory only. No code/tests were changed or run; no build, engine, PIE, asset, lock, commit, or push operation. Supporting reports: `BC_X21_X25_DAMAGE_PARRY_LIFECYCLE.md`, `BC_X31_X35_ADDON_SAFETY.md`.
