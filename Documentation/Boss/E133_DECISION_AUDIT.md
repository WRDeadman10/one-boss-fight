# E133 — fatigue inclusion in Gate 4

**Decision needed:** whether Gate 4's acceptance evidence must include an enabled fatigue run and a default-off control. **Authority:** project owner for the Gate 4 acceptance bar; Claude owns execution after that bar is set.

Fatigue is wired into executor card playback: with `FatigueFloor > 0`, the executor computes `RateScale` from `ConsecutiveWhiffs` and multiplies the card play rate (`RPGFrameworkMoveExecutor.cpp:128-136`). The boss updates its whiff count only after a started card finishes cleanly, resets on contact, and clears the count/latch at phase transition and encounter restart (`RPGFrameworkBossCharacter.cpp:582-589,411,800,816,863`). Both fatigue profile fields default to zero/off (`RPGBossFrameworkProfile.h:112-114`). Rule and source evidence do not settle whether Gate 4's packaged/performance/soak acceptance needs a fatigue-enabled scenario; that is an evidence-scope decision. Until decided, Gate 4 remains open and no enabled profile is implied.

Static source/doc audit only; no build/tests run by Codex.
