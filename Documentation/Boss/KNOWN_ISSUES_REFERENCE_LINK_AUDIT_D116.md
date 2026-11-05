# Known-issues reference and status audit — D116

**Scope:** current recent open-issue slice KI-172–KI-180, plus a cross-list disposition scan of closed/resolved entries. Static review only; no reproductions or tests.

| Issue | Source / status check | Disposition |
|---|---|---|
| KI-172 | `RPGHitIntake.cpp` still schedules `FinalizePending` next tick (lines 465, 506); the recorded source finding says encounter reset does not clear this queue. | Open, unreproduced; no closure claimed. |
| KI-173 | `RPGBossStagger.cpp:572,576` still uses a next-tick `CreateUObject` callback; no retained request-generation/timer handle is named in the start path. | Open, unreproduced; no closure claimed. |
| KI-174 | `RPGFrameworkBossCharacter.cpp:601` compares combo pause to an absolute world-time deadline; the off-arena early return path can skip normal Tick work. | Open, opt-in intent unspecified. |
| KI-175 | `RPGPlayerParry.h:65` retains `RPGParry::FState`; source has no lifecycle reset on pawn reuse/respawn. | Open, pawn lifecycle unobserved. |
| KI-176 | `RPGPlayerParry.cpp:167-168` uses a half-cost refund without a max clamp if the maximum-stamina read fails. | Open, reachability unverified. |
| KI-177 | `RPGFrameworkBossCharacter.cpp` retains pending parry-recovery fields and defers their consumption to a neutral tick; stagger/reset ordering still needs a stateful fixture. | Open, unverified. |
| KI-178 | C-757 saturation/test change is present; Lead reports BUILD-187 full suite 335/335 and records the fail-closed note in `TEST_PLAN.md:771` (C-758). | Stale pending status corrected to Lead-verified/resolved; ordinary gameplay reachability remains an evidence limit. |
| KI-179 | Watchdog runtime code remains in executor `TickComponent`; the harness comments that BUILD-185 did not observe it in a transient world and no longer asserts the path. | Open automation gap; no claim runtime code is absent. |
| KI-180 | `RPGBossReactiveDodgeRules.h:17` still computes `RecentHits - HitsToStart + 1` in `int32` before conversion. | Open pending the fix/test in the next Source task ordered by C-758. |

The current open statuses above remain open where reproduction, owner intent, lifecycle evidence, or automated coverage is outstanding. The closed/resolved rows in the issue table have an adjacent disposition in their description/workaround or status (milestone/build/date, owner option, source/test change, accepted workaround, or explicit residual scope); none was newly closed by this audit. KI-178 was the material stale status found and corrected to C-758 / BUILD-187 evidence.

**Acceptance result:** recent open references and statuses are reconciled; KI-178 reflects completed Lead validation and KI-180 remains open for the ordered Source fix. Closed-status dispositions remain cited. Static only.
