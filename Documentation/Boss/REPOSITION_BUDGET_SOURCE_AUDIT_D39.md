# Reposition budget source audit (Queue D39)

Scope: distinguish out-of-band reposition attempts from in-band turn-in-place, trace the attempt cap and reset, and map no-candidate behavior to tests/telemetry. Static review only; no tests/build/Editor run.

## Source behavior

- Profile validation permits `RepositionMax` from 0 through 8, requires F5 lane when positive, bounds finite `RepositionTurnDegPerSecond` to 0–720, and requires max/rate enabled or disabled together (`Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:90-93`; declaration/default `RPGBossFrameworkProfile.h:144-147`). `RPGFrameworkRuntimeTests.cpp:437-444` tests valid endpoints/representatives, invalid max/rate, enable mismatch, and non-F5 refusal.
- Two no-candidate situations differ. When the target is inside the authored band but outside the selector cone, with reposition enabled, the actor turns in place at the authored rate; it has a separate hard 3-second timeout then fails `Framework.Selector.NoCandidate` (`RPGFrameworkBossCharacter.cpp:464-478`). This turn does not increment `RepositionsInARow` and has no authored count cap.
- When no card is chosen outside the band, `RepositionsInARow < RepositionMax` permits a controller walk back toward the band; the attempt count increments before path start and is logged. If the controller/path cannot start, the encounter fails. If the attempt cap is exhausted, the next `bAsked && ChosenIndex == INDEX_NONE` path fails closed (`RPGFrameworkBossCharacter.cpp:480-495`). Exact walk-arrival/status logic is in that block.
- A successfully started card resets `RepositionsInARow=0` (`RPGFrameworkBossCharacter.cpp:521`). Encounter restart also resets it (`:864`). No separate reset on merely reaching band is recorded; an eligible successful card is the reset boundary.

## Coverage and interpretation

Existing automation covers profile-domain validity, not actor-level attempt progression, exact cap exhaustion, failed path start, arrival followed by selector retry, or reset after a successful card. `reposition`/`reposition_turn` telemetry distinguishes walk attempts and turn start/end; the final no-candidate refusal is generic and does not report exhausted attempt count in the cited branch. Treat the exact cap as a source fact (maximum eight walks between successful card starts), not a runtime witness. In-band turning has its own fixed 3-second fail-closed behavior, not the count budget.
