# LOS memory lifecycle audit (Queue D41)

Scope: trace loss/regain/timeout timestamps, leash pause, restart, death/failure, and tests. Static source review only; no tests/build/Editor/PIE run.

## Memory and tick lifecycle

- `FLosMemory` contains booleans, `LostAt`, and `LastKnown`; it owns no timer handle or delegate (`Source/OneBossFight/Player/RPGBossTrackRules.h:56`). `LosStep` records last visible position, captures loss time on the first blocked tick, reports timeout once when `Now-LostAt >= SearchSeconds`, updates position and clears loss/timeout on regain (`:58-65`).
- `TickLos` performs one visibility trace per eligible tick and passes world seconds to the pure rule; it returns when LOS is disabled, target invalid, or boss is leashed (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:136-161`). Actor Tick calls it while active (`:340`). Because the deadline uses absolute world time and ticking is skipped during leash, a long leash interval may make a subsequent still-hidden target time out immediately on the first resumed LOS tick. No paused-time policy is stated by the rule; this is an unverified timing boundary, not a reproduced bug.
- `RestartEncounter` resets the memory to a default `FLosMemory` along with generation state (`RPGFrameworkBossCharacter.cpp:861-864`). `Die` and `Fail` do not explicitly clear LOS memory, but they are terminal and the actor's Tick early return stops consuming it; no delayed LOS callback exists. An allowed restart resets it before the next generation. `EndPlay` has no LOS timer to cancel.

## Existing coverage and gaps

- `OneBossFight.Framework.Runtime.LosMemory` verifies last-visible coordinate retention, one Lost event, no event during search, Regained refresh, 2.99 s vs exact 3.0 s timeout, timeout reported once, and regain after timeout (`Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:576-589`). Profile validation covers off/valid range and invalid values (`:590-598`). These are pure rules/profile checks, not actor trace, leash skip, or generation lifecycle tests.
- Missing: world/tick wiring and occluder trace cases; leash skip with elapsed-time crossing; explicit `Los` reset across actor restart/new generation; terminal death/failure no-post-terminal tick evidence; restart following a timed-out memory state. Existing tests support the pure transition semantics only.

No stale asynchronous callback is present. Treat the behavior of an active LOS search across arena-leash pauses as unspecified pending a targeted actor test and Lead intent; no production change is proposed.
