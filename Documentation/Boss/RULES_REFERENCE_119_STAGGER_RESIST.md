# Designer reference: phase stagger-resistance scale

`RPGBossStaggerResist::Scale` returns one posture/stagger multiplier for a phase. It is unwired; callers apply the scale to their chosen posture or stagger calculation.

| Parameter | Unit | Default | Valid domain |
|---|---|---:|---|
| `Phase` | phase number | none | 1, 2, or another value (baseline) |
| `PhaseOneScale` | multiplier | 1.0 | finite, 0 to 3 inclusive |
| `PhaseTwoScale` | multiplier | 1.25 | finite, 0 to 3 inclusive |
| Return value | multiplier | 1.0 for unknown phase or invalid scale | configured phase scale |

Phase 1 returns `PhaseOneScale`, phase 2 returns `PhaseTwoScale`, and any other phase returns 1. Invalid scale values also return 1. A valid scale of zero is allowed and fully suppresses the caller's scaled quantity.

Source: [`RPGBossStaggerResistRules.h`](../../Source/OneBossFight/Player/RPGBossStaggerResistRules.h:7), unit tests: [`RPGBossStaggerResistRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossStaggerResistRulesTests.cpp:6).
