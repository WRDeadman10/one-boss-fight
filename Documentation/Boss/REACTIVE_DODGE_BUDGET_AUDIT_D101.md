# Reactive dodge budget audit (Queue D101)

**Scope:** static audit of the opt-in reactive-dodge rule and nearby boss dodge state. No tests run.

`Source/OneBossFight/Player/RPGBossReactiveDodgeRules.h:8-22` contains no mutable budget, attempt counter, or attack-generation key. `Chance` is a pure function of heavy/light flag, `RecentHits`, and config; `ShouldDodge` compares a finite roll in [0,1) to that chance. Therefore a per-attack retry budget cannot leak across attack generations in this helper because it does not exist here. The rule is explicitly documented unwired.

`RPGBossReactiveDodgeRulesTests.cpp:9-17` covers defaults, light/below-threshold no chance, increasing chance, configured cap, roll zero/below/equal chance, NaN roll, and invalid max chance. It does not test attack-generation changes because the helper has no generation/state input.

Related but distinct runtime observation: `RPGFrameworkBossCharacter.cpp:120-135` keeps player dodge direction history and dodge timestamps for pattern/aggro reads; `:447-449` prunes aggro timestamps by the configured time window; restart clears `AggroDodgeTimes` and `DodgeHistory` at `:863-865`. This is observation memory, not a reactive dodge attempt budget. No reset on attack generation was found in that path, and no evidence says it should reset there.

**Robustness edge:** `Chance` calculates `RecentHits - HitsToStart + 1` using `int32` before converting to `double` at `:17`. With a valid config and `RecentHits == MAX_int32`, this can overflow signed arithmetic. Ordinary gameplay reachability is unshown; record as a low input-boundary gap and add a pure boundary test before considering a code change. Default `HitsToStart=2` avoids the final +1 overflow at maximum count but arbitrary valid `HitsToStart=0` exposes it.
