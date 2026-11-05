# Boss damage resolver

`URPGDamageResolver` centralizes one boss contact against the player. `FRPGDamagePayload` carries the move, attack instance, encounter generation and hit key, so multi-window or repeated contacts can be deduplicated consistently (`RPGDamageResolver.h:28-48`). Outcomes distinguish geometry notes/misses, rejections, accepted damage, parry, and write failure (`RPGDamageResolver.h:11-24`).

## Resolution order

`Resolve` fails closed for invalid target/payload, synchronizes encounter generation, then checks target life and generation freshness before deduplication (`RPGDamageResolver.cpp:133-170`). It checks the parry window before invulnerability and health mutation: a valid parry returns `Parried`, consumes the hit key, notifies the parry component, and applies no HP damage (`:171-185`). Invulnerability is rejected without spending a hit; duplicate/stale/dead contacts likewise do not apply damage (`:157-190`). A health write failure returns `Failed`; only a successful write returns `Accepted` with applied HP (`:186-192`).

Geometry-specific results such as `MissJumped`, `MissWorld`, and `Superseded` are supplied by the executor before/around resolver calls. `Overlap` is an audit observation, not an accepted hit (`RPGDamageResolver.h:11-24`; `RPGFrameworkMoveExecutor.cpp:274-300`).

Audit lines and summary counters can be read through `GetAuditLine`, `GetOutcomeCount`, `GetMoveOutcomeCount`, and `BuildSummaryLine` (`RPGDamageResolver.cpp:193-230`).
